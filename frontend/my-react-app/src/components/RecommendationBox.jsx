import "../App.css";

const pad2 = (n) => String(n).padStart(2, "0");

function RecommendationBox({ status, recommendation }) {
  if (status === "idle") {
    return (
      <div className="recommendation-box hint">
        בחר יום וטווח שעות כדי לקבל המלצה
      </div>
    );
  }

  if (status === "loading") {
    return (
      <div className="recommendation-box hint">
        טוען המלצה...
      </div>
    );
  }

  if (status === "error") {
    return (
      <div className="recommendation-box error">
        שגיאה: לא התקבלה תשובה מהשרת.
      </div>
    );
  }

  // success
  const results = recommendation?.results;
  if (!Array.isArray(results) || results.length === 0) {
    return (
      <div className="recommendation-box error">
        אין נתונים זמינים לטווח שבחרת.
      </div>
    );
  }

  const best =
    results.find((r) => r.rank === 1) ??
    results.reduce((min, r) => (r.rank < min.rank ? r : min), results[0]);

  const hh = pad2(best.hour);
  const mm = pad2(best.minute_bucket ?? 0);

  return (
    <div className="recommendation-box">
      <div className="recommendation-title">המלצה</div>
      <div className="recommendation-main">
        השעה המומלצת ביותר: <strong>{hh}:{mm}</strong>
      </div>
      <div className="recommendation-sub">
        מחיר ממוצע: {best.avg_price} ₪ | דגימות: {best.sample_count}
      </div>
    </div>
  );
}

export default RecommendationBox;
