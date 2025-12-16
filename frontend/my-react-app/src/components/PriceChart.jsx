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

function PriceChart({ data }) {
  // Find cheapest price
  const cheapestPoint = data.reduce((min, point) => 
    point.price < min.price ? point : min
  , data[0] || { price: Infinity });

  // Custom tooltip with RTL support
  const CustomTooltip = ({ active, payload }) => {
    if (!active || !payload?.length) return null;
    
    const point = payload[0].payload;
    const isCheapest = point.time === cheapestPoint.time;
    
    return (
      <div style={{
        backgroundColor: 'white',
        padding: '12px',
        border: '2px solid #4FB6AC',
        borderRadius: '8px',
        direction: 'rtl',
        boxShadow: '0 2px 8px rgba(0,0,0,0.15)'
      }}>
        <div style={{ fontWeight: 600, marginBottom: '4px' }}>
          שעה: {point.time}
        </div>
        <div style={{ color: isCheapest ? '#16a34a' : '#0F2C2C' }}>
          מחיר: {point.price} ₪
          {isCheapest && ' ⭐ (הכי זול!)'}
        </div>
      </div>
    );
  };

  return (
    <div className="chart-card">
      <div className="chart-title">גרף מחירים</div>

      <div className="chart-container">
        <ResponsiveContainer width="100%" height="100%">
          <ComposedChart data={data} margin={{ top: 10, right: 30, left: 0, bottom: 0 }}>
            <defs>
              <linearGradient id="priceGradient" x1="0" y1="0" x2="0" y2="1">
                <stop offset="5%" stopColor="#4FB6AC" stopOpacity={0.3}/>
                <stop offset="95%" stopColor="#4FB6AC" stopOpacity={0}/>
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
              stroke="#16a34a" 
              strokeDasharray="5 5"
              label={{ value: 'מחיר מומלץ', position: 'insideTopRight', fill: '#16a34a' }}
            />
            
            <Tooltip content={<CustomTooltip />} />
            
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
              stroke="#4FB6AC" 
              strokeWidth={3} 
              dot={{ r: 4, fill: '#4FB6AC' }}
              activeDot={{ r: 6, fill: '#16a34a' }}
            />
          </ComposedChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
}

export default PriceChart;