import "../App.css";
import {
  Line,
  XAxis,
  YAxis,
  Tooltip,
  ResponsiveContainer,
  CartesianGrid,
  ReferenceLine,
  Area,
  ComposedChart,
} from "recharts";
import { formatHourLabel } from "../utils/format.js";

// Kept in sync with the --color-primary / --color-accent tokens in index.css.
// Recharts renders these directly into SVG attributes, which can't reliably
// consume CSS custom properties, so the values are duplicated here.
const COLOR_PRIMARY = "#0E6E4E";
const COLOR_ACCENT = "#E8A33D";
const COLOR_TEXT = "#16201B";

function CustomTooltip({ active, payload, cheapestPoint }) {
  if (!active || !payload?.length) return null;

  const point = payload[0].payload;
  const isCheapest = point._idx === cheapestPoint._idx;

  return (
    <div style={{
      backgroundColor: 'white',
      padding: '12px 14px',
      borderInlineStart: `4px solid ${isCheapest ? COLOR_ACCENT : COLOR_PRIMARY}`,
      borderRadius: '8px',
      direction: 'rtl',
      boxShadow: '0 8px 20px rgba(15,32,27,0.14)'
    }}>
      <div style={{ fontWeight: 600, marginBottom: '4px' }}>
        שעה: {point.time}
      </div>
      <div style={{ color: isCheapest ? COLOR_ACCENT : COLOR_TEXT }}>
        מחיר: {point.price} ₪
        {isCheapest && ' — הכי משתלם'}
      </div>
    </div>
  );
}

function renderDot(cheapestPoint) {
  return (props) => {
    const { cx, cy, payload, index } = props;
    if (payload.price == null) return null;

    if (payload._idx === cheapestPoint._idx) {
      return (
        <path
          key={`dot-${index}`}
          d={`M ${cx} ${cy - 7} L ${cx + 7} ${cy} L ${cx} ${cy + 7} L ${cx - 7} ${cy} Z`}
          fill={COLOR_ACCENT}
          stroke="#fff"
          strokeWidth={1.5}
        />
      );
    }

    return <circle key={`dot-${index}`} cx={cx} cy={cy} r={3} fill={COLOR_PRIMARY} />;
  };
}

function PriceChart({ data, fromHour, toHour }) {
  // The hourly data can contain multiple points that render the same "time"
  // label (a pre-existing upstream data quirk). Recharts resolves tooltip/axis
  // lookups by the x-axis value, so a duplicate label makes hover ambiguous —
  // _idx gives each point a unique axis key while the tick still displays `time`.
  const chartData = data.map((point, idx) => ({ ...point, _idx: idx }));

  // Find the cheapest price in the selected range
  const cheapestPoint = chartData.reduce((min, point) =>
    point.price < min.price ? point : min
  , chartData[0] || { price: Infinity });

  const hasRange = fromHour != null && toHour != null;

  return (
    <div className="card chart-card">
      <div className="chart-title">גרף מחירים</div>
      {hasRange && (
        <div className="chart-subtitle">
          טווח נבחר: {formatHourLabel(fromHour)}–{formatHourLabel(toHour)}
        </div>
      )}

      <div className="chart-container" aria-label="גרף מחירי הנתיב המהיר לפי שעה" role="img">
        <ResponsiveContainer width="100%" height="100%">
          <ComposedChart data={chartData} margin={{ top: 10, right: 95, left: 0, bottom: 0 }}>
            <defs>
              <linearGradient id="priceGradient" x1="0" y1="0" x2="0" y2="1">
                <stop offset="5%" stopColor={COLOR_PRIMARY} stopOpacity={0.25}/>
                <stop offset="95%" stopColor={COLOR_PRIMARY} stopOpacity={0}/>
              </linearGradient>
            </defs>

            <CartesianGrid strokeDasharray="3 3" stroke="#E4E8E5" />
            <XAxis
              dataKey="_idx"
              type="category"
              tickFormatter={(idx) => chartData[idx]?.time ?? ''}
              tick={{ fontSize: 12, fill: "#5C6B62" }}
              stroke="#C7D0CB"
            />
            <YAxis
              tick={{ fontSize: 12, fill: "#5C6B62" }}
              stroke="#C7D0CB"
              label={{ value: 'מחיר (₪)', angle: -90, position: 'insideLeft' }}
            />

            {/* Highlight cheapest price */}
            <ReferenceLine
              y={cheapestPoint.price}
              stroke={COLOR_ACCENT}
              strokeDasharray="5 5"
              label={{ value: 'משתלם', position: 'insideTopRight', fill: COLOR_ACCENT }}
            />

            <Tooltip content={<CustomTooltip cheapestPoint={cheapestPoint} />} />

            {/* Area under the line */}
            <Area
              type="monotone"
              dataKey="price"
              fill="url(#priceGradient)"
              stroke="none"
            />

            {/* Main line */}
            <Line
              type="monotone"
              dataKey="price"
              stroke={COLOR_PRIMARY}
              strokeWidth={3}
              dot={renderDot(cheapestPoint)}
              activeDot={{ r: 6, fill: COLOR_PRIMARY, stroke: '#fff', strokeWidth: 2 }}
            />
          </ComposedChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
}

export default PriceChart;
