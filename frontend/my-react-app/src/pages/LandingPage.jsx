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
    const [recStatus, setRecStatus] = useState("idle");  // "idle" | "loading" | "success" | "error"
    const [apiRespons, setApiRespons] = useState(null);
    const [selectedDay, setSelectedDay] = useState(new Date().getDay());
    const [fromHour, setFromHour] = useState(6);
    const [toHour, setToHour] = useState(9);

    const handleTimeChange = async (newFrom, newTo) => {
        setFromHour(newFrom);
        setToHour(newTo);

        setRecStatus("loading");
        try {
            const data = await getRecommendation(selectedDay, newFrom, newTo);
            setApiRespons(data);
            setRecStatus("success");
        } catch (e) {
            setApiRespons(`שגיאה: ${String(e)}`);
            setRecStatus("error");
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
                status={recStatus}
                recommendation={apiRespons} // זמנית
            />

            <PriceChart data={demoGraphData} />
        </div>
    );
} export default LandingPage