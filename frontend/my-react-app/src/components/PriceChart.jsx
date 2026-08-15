import "../App.css";
import {
  LineChart,
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

// Kept in sync with the --color-primary / --color-success tokens in index.css.
// Recharts renders these directly into SVG attributes, which can't reliably
// consume CSS custom properties, so the values are duplicated here.
const COLOR_PRIMARY = "#4FB6AC";
const COLOR_SUCCESS = "#16a34a";
const COLOR_TEXT = "#0F2C2C";

function CustomTooltip({ active, payload, cheapestPoint }) {
  if (!active || !payload?.length) return null;

  const point = payload[0].payload;
  const isCheapest = point.time === cheapestPoint.time;

  return (
    <div style={{
      backgroundColor: 'white',
      padding: '12px',
      border: `2px solid ${COLOR_PRIMARY}`,
      borderRadius: '8px',
      direction: 'rtl',
      boxShadow: '0 2px 8px rgba(0,0,0,0.15)'
    }}>
      <div style={{ fontWeight: 600, marginBottom: '4px' }}>
        שעה: {point.time}
      </div>
      <div style={{ color: isCheapest ? COLOR_SUCCESS : COLOR_TEXT }}>
        מחיר: {point.price} ₪
        {isCheapest && ' ⭐ (הכי זול!)'}
      </div>
    </div>
  );
}

function PriceChart({ data }) {
  // Find cheapest price
  const cheapestPoint = data.reduce((min, point) =>
    point.price < min.price ? point : min
  , data[0] || { price: Infinity });

  return (
    <div className="card chart-card">
      <div className="chart-title">גרף מחירים</div>

      <div className="chart-container" aria-label="גרף מחירי דלק לפי שעה" role="img">
        <ResponsiveContainer width="100%" height="100%">
          <ComposedChart data={data} margin={{ top: 10, right: 65, left: 0, bottom: 0 }}>
            <defs>
              <linearGradient id="priceGradient" x1="0" y1="0" x2="0" y2="1">
                <stop offset="5%" stopColor={COLOR_PRIMARY} stopOpacity={0.3}/>
                <stop offset="95%" stopColor={COLOR_PRIMARY} stopOpacity={0}/>
              </linearGradient>
            </defs>

            <CartesianGrid strokeDasharray="3 3" stroke="#E0E0E0" />
            <XAxis
              dataKey="time"
              tick={{ fontSize: 12 }}
              stroke="#666"
            />
            <YAxis
              tick={{ fontSize: 12 }}
              stroke="#666"
              label={{ value: 'מחיר (₪)', angle: -90, position: 'insideLeft' }}
            />

            {/* Highlight cheapest price */}
            <ReferenceLine
              y={cheapestPoint.price}
              stroke={COLOR_SUCCESS}
              strokeDasharray="5 5"
              label={{ value: 'מחיר מומלץ', position: 'insideTopRight', fill: COLOR_SUCCESS }}
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
              dot={{ r: 4, fill: COLOR_PRIMARY }}
              activeDot={{ r: 6, fill: COLOR_SUCCESS }}
            />
          </ComposedChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
}

export default PriceChart;
