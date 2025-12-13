import "../App.css";
import { useState } from "react";
import DayPicker from "../components/DayPicker.jsx";
import TimeRangePicker from "../components/TimeRangePicker.jsx";
import PriceChart from "../components/PriceChart.jsx";
import RecommendationBox from "../components/RecommendationBox.jsx";
import { getRecommendation } from "../api/recommendationApi";

const demoGraphData = [
    { time: "06:00", price: 18 },
    { time: "07:00", price: 15 },
    { time: "08:00", price: 21 },
    { time: "09:00", price: 17 },
];
const days = [
    { id: 0, label: "א" },
    { id: 1, label: "ב" },
    { id: 2, label: "ג" },
    { id: 3, label: "ד" },
    { id: 4, label: "ה" },
    { id: 5, label: "ו" },
    { id: 6, label: "ש" },
];

function LandingPage() {
  const [apiRespons, setApiRespons] = useState(null);
  const [selectedDay, setSelectedDay] = useState(new Date().getDay());
  const [fromHour, setFromHour] = useState(6);
  const [toHour, setToHour] = useState(9);

  const handleTimeChange = async (newFrom, newTo) => {
    setFromHour(newFrom);
    setToHour(newTo);

    try {
      const data = await getRecommendation(selectedDay, newFrom, newTo);
      setApiRespons(JSON.stringify(data));
    } catch (e) {
      setApiRespons(`שגיאה: ${String(e)}`);
    }
  };

  return (
    <div className="landing-page">
      <DayPicker
        days={days}
        selectedDay={selectedDay}
        onChange={setSelectedDay}
      />

      <TimeRangePicker
        fromHour={fromHour}
        toHour={toHour}
        onChange={handleTimeChange}
      />

      <RecommendationBox
        selectedDay={selectedDay}
        fromHour={fromHour}
        toHour={toHour}
        recommendation={apiRespons} // זמנית, עד שתעבד את המבנה
      />

      <PriceChart data={demoGraphData} />
    </div>
  );
} export default LandingPage