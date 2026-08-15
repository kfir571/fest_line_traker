import "../App.css";
import { useState, useEffect, useRef } from "react";
import DayPicker from "../components/DayPicker.jsx";
import TimeRangePicker from "../components/TimeRangePicker.jsx";
import PriceChart from "../components/PriceChart.jsx";
import RecommendationBox from "../components/RecommendationBox.jsx";
import { getRecommendation } from "../api/recommendationApi";
import { getHourlyGraph } from "../api/hourlyGraphApi";
import GraphSection from "../components/GraphSection.jsx";
import ChevronIcon from "../components/ChevronIcon.jsx";
import { formatTimeLabel } from "../utils/format.js";

const days = [
    { id: 0, label: "א", fullLabel: "יום ראשון" },
    { id: 1, label: "ב", fullLabel: "יום שני" },
    { id: 2, label: "ג", fullLabel: "יום שלישי" },
    { id: 3, label: "ד", fullLabel: "יום רביעי" },
    { id: 4, label: "ה", fullLabel: "יום חמישי" },
    { id: 5, label: "ו", fullLabel: "יום שישי" },
    { id: 6, label: "ש", fullLabel: "יום שבת" },
];

function uiDayToApiDay(uiDay) {
    // ui: 0=Sunday .. 6=Saturday
    // api: 0=Monday .. 6=Sunday
    return (uiDay + 6) % 7;
}

function LandingPage() {
    const [recStatus, setRecStatus] = useState("idle"); // "idle" | "loading" | "success" | "error"
    const [apiRespons, setApiRespons] = useState(null);

    const [graphStatus, setGraphStatus] = useState("idle"); // "idle" | "loading" | "success" | "error"
    const [graphData, setGraphData] = useState([]); // [{time, price}]

    const [selectedDay, setSelectedDay] = useState(new Date().getDay());
    const [fromHour, setFromHour] = useState(6);
    const [toHour, setToHour] = useState(9);

    const hasInteractedRef = useRef(false);

    const handleTimeChange = (newFrom, newTo) => {
        hasInteractedRef.current = true;
        setFromHour(newFrom);
        setToHour(newTo);
    };

    const handleDayChange = (newDay) => {
        hasInteractedRef.current = true;
        setSelectedDay(newDay);
    };

    useEffect(() => {
        if (!hasInteractedRef.current) return;

        const fetchAll = async () => {
            const apiWeekday = uiDayToApiDay(selectedDay);

            setRecStatus("loading");
            setGraphStatus("loading");

            const [recRes, graphRes] = await Promise.allSettled([
                getRecommendation(apiWeekday, fromHour, toHour),
                getHourlyGraph(apiWeekday, fromHour, toHour),
            ]);

            // Recommendation
            if (recRes.status === "fulfilled") {
                setApiRespons(recRes.value);
                setRecStatus("success");
            } else {
                setApiRespons(`שגיאה: ${String(recRes.reason)}`);
                setRecStatus("error");
            }

            // Graph
            if (graphRes.status === "fulfilled") {
                const normalized = (graphRes.value?.data ?? []).map((p) => ({
                    time: p.time_label ?? formatTimeLabel(p.hour, p.minute_bucket ?? 0),
                    price: p.avg_price ?? null,
                }));

                setGraphData(normalized);
                setGraphStatus("success");
            } else {
                setGraphData([]);
                setGraphStatus("error");
            }
        };

        const timer = setTimeout(() => {
            fetchAll();
        }, 300)

        return () => clearTimeout(timer);
    }, [selectedDay, fromHour, toHour]);

    return (
        <div className="landing-page">
            <header className="app-header">
                <div className="app-header__brand">
                    <ChevronIcon className="app-header__mark" />
                    <span>מעקב מחיר הנתיב המהיר</span>
                </div>
                <p className="app-header__tagline">מצא את השעה המשתלמת ביותר לנסיעה</p>
            </header>

            <DayPicker days={days} selectedDay={selectedDay} onChange={handleDayChange} />

            <TimeRangePicker fromHour={fromHour} toHour={toHour} onChange={handleTimeChange} />

            <RecommendationBox status={recStatus} recommendation={apiRespons} />

            <GraphSection status={graphStatus} data={graphData} fromHour={fromHour} toHour={toHour} />

        </div>
    );
}

export default LandingPage;
