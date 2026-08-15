# backend/api/routes_analytics.py

from flask import Blueprint, jsonify, request
from api.db import get_db_connection
from .config_api import (
    WEEKDAY_NAMES_HE, 
    DEFAULT_MAX_RESULTS, 
    MIN_SAMPLE_COUNT_FOR_RECOMMENDATION
)

analytics_bp = Blueprint("analytics", __name__)


# ------------------------------------------------------------
# 1) HEALTHCHECK
# ------------------------------------------------------------
@analytics_bp.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "ok"})


# ------------------------------------------------------------
# 2) WEEKLY STATS — Main endpoint for weekly-day analytics.
# NOTE: Not used in MVP UI. Reserved for future analytics.
# ------------------------------------------------------------
@analytics_bp.route("/weekly-stats", methods=["GET"])
def weekly_stats():
    """
    Returns aggregated statistics from weekly_stats table
    for a specific weekday (0 = Monday … 6 = Sunday).

    Query parameters:
        weekday (required): integer 0–6
        holiday_mode (optional): 'all' / 'holiday' / 'non_holiday'
    """

    #Read and validate query parameters
    weekday = request.args.get("weekday", type=int)
    holiday_mode = request.args.get("holiday_mode", default="all", type=str)
    print(f"{weekday=}")
    if weekday is None or weekday < 0 or weekday > 6:
        return jsonify({"error": "weekday parameter must be 0–6"}), 400

    #Build WHERE filter according to holiday_mode
    holiday_filter = ""
    if holiday_mode == "holiday":
        holiday_filter = "AND is_holiday = TRUE"
    elif holiday_mode == "non_holiday":
        holiday_filter = "AND is_holiday = FALSE"
    # If holiday_mode == "all" -> no filter is added

    #Execute SQL query
    query = f"""
        SELECT
            weekday,
            hour,
            minute_bucket,
            avg_price,
            min_price,
            max_price,
            sample_count,
            days_count,
            is_holiday,
            holiday_sector
        FROM weekly_stats
        WHERE weekday = %s
        {holiday_filter}
        ORDER BY hour, minute_bucket;
    """

    conn = get_db_connection()
    with conn.cursor() as cur:
        cur.execute(query, (weekday,))
        rows = cur.fetchall()
    conn.close()

    #Convert SQL rows to JSON-friendly structure
    results = []
    for r in rows:
        results.append({
            "hour": r[1],
            "minute_bucket": r[2],
            "avg_price": float(r[3]),
            "min_price": float(r[4]),
            "max_price": float(r[5]),
            "sample_count": r[6],
            "days_count": r[7],
            "is_holiday": r[8],
            "holiday_sector": r[9],
        })

    #Convert weekday index to Hebrew name (Monday=0)
    weekday_he = WEEKDAY_NAMES_HE[weekday]

    return jsonify({
        "weekday": weekday,
        "weekday_name_he": weekday_he,
        "holiday_mode": holiday_mode,
        "slots": results
    })

@analytics_bp.route("/recommendation", methods=["GET"])
def recommendation():
    """
    Returns best (cheapest) time slots across selected weekdays and hours,
    based on aggregated data in weekly_stats.

    Query parameters:
        from_hour (required): int (e.g. 6)
        to_hour   (required): int (e.g. 22)
            NOTE: to_hour is treated as an EXCLUSIVE upper bound (range is [from_hour:00, to_hour:00)).
        allowed_weekdays (required): comma-separated list of 0..6.
            Example: "0,1,2,3,4" (Mon-Fri).
            Default: all 0..6.
        holiday_mode (optional): 'all' / 'holiday' / 'non_holiday'
            Default: 'all'.
        max_results (optional): int, how many top slots to return.
            Default: DEFAULT_MAX_RESULTS (e.g. 3).
    """

    #Read and validate query parameters 
    from_hour = request.args.get("from_hour", type=int)
    to_hour = request.args.get("to_hour", type=int)
    max_results = request.args.get("max_results", type=int)
    holiday_mode = request.args.get("holiday_mode", default="all", type=str)
    allowed_weekdays_param = request.args.get("allowed_weekdays", type=str)

    # Apply defaults if not provided
    if from_hour is None:
        return jsonify({"error": "from_hour is required"}), 400
    if to_hour is None:
        return jsonify({"error": "to_hour is required"}), 400
    if max_results is None or max_results <= 0:
        max_results = DEFAULT_MAX_RESULTS

    holiday_mode = holiday_mode.lower().strip()

    allowed_modes = {"all", "holiday", "non_holiday"}
    if holiday_mode not in allowed_modes:
        return jsonify({"error": "holiday_mode must be one of: all, holiday, non_holiday"}), 400


    # Validate hour range
    # from_hour: 0..23
    # to_hour:   1..24  (exclusive upper bound)
    # from_hour == to_hour is always invalid (not treated as a 24h range).
    # from_hour > to_hour is a valid overnight range that crosses into the next weekday.
    # to_hour == 24 always means "end of the same day" and can never be an overnight case,
    # since from_hour's max (23) is always < 24.
    if (
        from_hour < 0 or from_hour > 23
        or to_hour < 1 or to_hour > 24
        or from_hour == to_hour
    ):
        return jsonify({
            "error": "Invalid hour range (from_hour/to_hour). "
                     "from_hour must be 0..23, to_hour must be 1..24, and from_hour must not equal to_hour."
        }), 400

    is_overnight = from_hour > to_hour

    # Parse allowed_weekdays (comma-separated list) or use all 0..6
    if allowed_weekdays_param:
        try:
            allowed_weekdays = [
                int(x) for x in allowed_weekdays_param.split(",") if x.strip() != ""
            ]
        except ValueError:
            return jsonify({"error": "allowed_weekdays must be a comma-separated list of integers 0..6."}), 400
        
        if not allowed_weekdays:
            return jsonify({
                "error": "allowed_weekdays must include at least one value (0..6)"
            }), 400
    else:
        return jsonify({"error": "allowed_weekdays is required"}), 400

        

    # Validate weekday values
    if any(w < 0 or w > 6 for w in allowed_weekdays):
        return jsonify({"error": "allowed_weekdays values must be between 0 and 6."}), 400

    #Build holiday filter 
    holiday_filter = ""
    if holiday_mode == "holiday":
        holiday_filter = "AND is_holiday = TRUE"
    elif holiday_mode == "non_holiday":
        holiday_filter = "AND is_holiday = FALSE"
    # 'all' → no filter

    #Build and execute SQL query
    # NOTE: to_hour is EXCLUSIVE. We filter by minutes since midnight:
    #   bucket_min = hour*60 + minute_bucket
    #   keep: from_hour*60 <= bucket_min < to_hour*60
    #
    # Overnight ranges (from_hour > to_hour) span two segments per selected weekday:
    #   - the selected weekday itself, from from_hour to end of day
    #   - the following weekday ((w+1) % 7 for each selected w), from start of day to to_hour
    # Both segments are matched in one query so ranking/LIMIT stay in SQL over the combined
    # row set — no separate queries or Python-side merging.
    if is_overnight:
        next_weekdays = [(w + 1) % 7 for w in allowed_weekdays]
        query = f"""
            SELECT
                weekday,
                hour,
                minute_bucket,
                avg_price,
                min_price,
                max_price,
                sample_count,
                days_count,
                is_holiday,
                holiday_sector
            FROM weekly_stats
            WHERE
                (
                    (weekday = ANY(%s) AND ((hour * 60) + COALESCE(minute_bucket, 0)) >= (%s * 60))
                    OR
                    (weekday = ANY(%s) AND ((hour * 60) + COALESCE(minute_bucket, 0)) <  (%s * 60))
                )
                AND sample_count >= %s
                {holiday_filter}
            ORDER BY avg_price ASC, hour ASC, minute_bucket ASC
            LIMIT %s;
        """
        params = (
            allowed_weekdays,
            from_hour,
            next_weekdays,
            to_hour,
            MIN_SAMPLE_COUNT_FOR_RECOMMENDATION,
            max_results,
        )
    else:
        query = f"""
            SELECT
                weekday,
                hour,
                minute_bucket,
                avg_price,
                min_price,
                max_price,
                sample_count,
                days_count,
                is_holiday,
                holiday_sector
            FROM weekly_stats
            WHERE
                weekday = ANY(%s)
                AND ((hour * 60) + COALESCE(minute_bucket, 0)) >= (%s * 60)
                AND ((hour * 60) + COALESCE(minute_bucket, 0)) <  (%s * 60)
                AND sample_count >= %s
                {holiday_filter}
            ORDER BY avg_price ASC, hour ASC, minute_bucket ASC
            LIMIT %s;
        """
        params = (
            allowed_weekdays,
            from_hour,
            to_hour,
            MIN_SAMPLE_COUNT_FOR_RECOMMENDATION,
            max_results,
        )

    conn = get_db_connection()
    try:
        with conn.cursor() as cur:
            cur.execute(query, params)
            rows = cur.fetchall()
    except Exception:
        return jsonify({"error": "database_error"}), 500
    finally:
        conn.close()

    #Convert rows to result list 
    results = []
    for idx, r in enumerate(rows, start=1):
        w = r[0]
        results.append({
            "rank": idx,
            "weekday": w,
            "weekday_name_he": WEEKDAY_NAMES_HE[w],
            "hour": r[1],
            "minute_bucket": r[2],
            "avg_price": float(r[3]) if r[3] is not None else None,
            "min_price": float(r[4]) if r[4] is not None else None,
            "max_price": float(r[5]) if r[5] is not None else None,
            "sample_count": r[6],
            "days_count": r[7],
            "is_holiday": r[8],
            "holiday_sector": r[9],
        })

    #Build constraints object for the response
    constraints = {
        "from_hour": from_hour,
        "to_hour": to_hour,
        "allowed_weekdays": sorted(set(allowed_weekdays)),
        "holiday_mode": holiday_mode,
        "max_results": max_results,
        "min_sample_count": MIN_SAMPLE_COUNT_FOR_RECOMMENDATION,
        "to_hour_is_exclusive": True,
    }

    #Step 6: Return final JSON
    return jsonify({
        "constraints": constraints,
        "results": results,
    })

@analytics_bp.route("/hourly-graph", methods=["GET"])
def hourly_graph():
    """
    Returns a time-series (hour + minute_bucket) for graph visualization
    based on weekly_stats table.

    Query parameters:
        weekday (required): integer 0..6
        from_hour (required): int 0..23
        to_hour (required): int 1..24 (EXCLUSIVE upper bound)
        holiday_mode (optional): 'all' / 'holiday' / 'non_holiday' (default: 'all')
    """

    #Read parameters 
    weekday = request.args.get("weekday", type=int)
    from_hour = request.args.get("from_hour", type=int)
    to_hour = request.args.get("to_hour", type=int)
    holiday_mode = request.args.get("holiday_mode", default="all", type=str).lower().strip()

    #Validate required params 
    if weekday is None:
        return jsonify({"error": "weekday is required"}), 400
    if from_hour is None:
        return jsonify({"error": "from_hour is required"}), 400
    if to_hour is None:
        return jsonify({"error": "to_hour is required"}), 400

    # Validate weekday range
    if weekday < 0 or weekday > 6:
        return jsonify({"error": "weekday must be an integer between 0 and 6"}), 400

    # Validate holiday_mode
    allowed_modes = {"all", "holiday", "non_holiday"}
    if holiday_mode not in allowed_modes:
        return jsonify({"error": "holiday_mode must be one of: all, holiday, non_holiday"}), 400

    # Validate hour range
    # from_hour == to_hour is always invalid (not treated as a 24h range).
    # from_hour > to_hour is a valid overnight range that crosses into the next weekday
    # ((weekday + 1) % 7). to_hour == 24 always means "end of the same day" and can never
    # be an overnight case, since from_hour's max (23) is always < 24.
    if (
        from_hour < 0 or from_hour > 23
        or to_hour < 1 or to_hour > 24
        or from_hour == to_hour
    ):
        return jsonify({
            "error": "Invalid hour range (from_hour/to_hour). "
                     "from_hour must be 0..23, to_hour must be 1..24, and from_hour must not equal to_hour."
        }), 400

    is_overnight = from_hour > to_hour

    #Build holiday filter
    holiday_filter = ""
    if holiday_mode == "holiday":
        holiday_filter = "AND is_holiday = TRUE"
    elif holiday_mode == "non_holiday":
        holiday_filter = "AND is_holiday = FALSE"

    #Execute SQL
    # Overnight ranges (from_hour > to_hour) span two segments: the selected weekday from
    # from_hour to end of day, then the following weekday ((weekday + 1) % 7) from start of
    # day to to_hour. The CASE in ORDER BY keeps the first segment before the second so
    # results stay chronological across the day boundary — plain "hour ASC" would otherwise
    # sort the next day's 00:xx rows before the current day's 22:xx rows.
    if is_overnight:
        next_weekday = (weekday + 1) % 7
        query = f"""
            SELECT
                hour,
                minute_bucket,
                avg_price,
                min_price,
                max_price,
                sample_count,
                days_count
            FROM weekly_stats
            WHERE
                (
                    (weekday = %s AND ((hour * 60) + COALESCE(minute_bucket, 0)) >= (%s * 60))
                    OR
                    (weekday = %s AND ((hour * 60) + COALESCE(minute_bucket, 0)) <  (%s * 60))
                )
                {holiday_filter}
            ORDER BY
                CASE WHEN weekday = %s THEN 0 ELSE 1 END,
                hour ASC,
                minute_bucket ASC;
        """
        params = (weekday, from_hour, next_weekday, to_hour, weekday)
    else:
        query = f"""
            SELECT
                hour,
                minute_bucket,
                avg_price,
                min_price,
                max_price,
                sample_count,
                days_count
            FROM weekly_stats
            WHERE weekday = %s
              AND ((hour * 60) + COALESCE(minute_bucket, 0)) >= (%s * 60)
              AND ((hour * 60) + COALESCE(minute_bucket, 0)) <  (%s * 60)
              {holiday_filter}
            ORDER BY hour ASC, minute_bucket ASC;
        """
        params = (weekday, from_hour, to_hour)

    conn = get_db_connection()
    try:
        with conn.cursor() as cur:
            cur.execute(query, params)
            rows = cur.fetchall()
    except Exception:
        return jsonify({"error": "database_error"}), 500
    finally:
        conn.close()

    #Format response
    graph_data = []
    for r in rows:
        hour = int(r[0])
        minute_bucket = int(r[1] or 0)
        graph_data.append({
            "hour": hour,
            "minute_bucket": minute_bucket,
            "time_label": f"{hour:02d}:{minute_bucket:02d}",
            "avg_price": float(r[2]) if r[2] is not None else None,
            "min_price": float(r[3]) if r[3] is not None else None,
            "max_price": float(r[4]) if r[4] is not None else None,
            "sample_count": r[5],
            "days_count": r[6],
        })

    return jsonify({
        "weekday": weekday,
        "weekday_name_he": WEEKDAY_NAMES_HE[weekday],
        "from_hour": from_hour,
        "to_hour": to_hour,
        "to_hour_is_exclusive": True,
        "holiday_mode": holiday_mode,
        "data": graph_data
    })
