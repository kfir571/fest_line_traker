import "../App.css";
import { useState, useEffect, useRef } from "react";
import DayPicker from "../components/DayPicker.jsx";
import TimeRangePicker from "../components/TimeRangePicker.jsx";
import PriceChart from "../components/PriceChart.jsx";
import RecommendationBox from "../components/RecommendationBox.jsx";
import { getRecommendation } from "../api/recommendationApi";
import { getHourlyGraph } from "../api/hourlyGraphApi";
import GraphSection from "../components/GraphSection.jsx";

const days = [
    { id: 0, label: "א" },
    { id: 1, label: "ב" },
    { id: 2, label: "ג" },
    { id: 3, label: "ד" },
    { id: 4, label: "ה" },
    { id: 5, label: "ו" },
    { id: 6, label: "ש" },
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

            try {
                const [recData, graphRes] = await Promise.all([
                    getRecommendation(apiWeekday, fromHour, toHour),
                    getHourlyGraph(apiWeekday, fromHour, toHour),
                ]);

                // Recommendation
                setApiRespons(recData);
                setRecStatus("success");

                // Graph normalize: backend -> recharts format
                const normalized = (graphRes?.data ?? []).map((p) => ({
                    time: p.time_label ?? `${String(p.hour).padStart(2, "0")}:${String(p.minute_bucket ?? 0).padStart(2, "0")}`,
                    price: p.avg_price ?? null,
                }));

                setGraphData(normalized);
                setGraphStatus("success");
            } catch (e) {
                // Keep recommendation error consistent with existing UI
                setApiRespons(`שגיאה: ${String(e)}`);
                setRecStatus("error");

                setGraphData([]);
                setGraphStatus("error");
            }
        };

        fetchAll();
    }, [selectedDay, fromHour, toHour]);

    return (
        <div className="landing-page">
            <DayPicker days={days} selectedDay={selectedDay} onChange={handleDayChange} />

            <TimeRangePicker fromHour={fromHour} toHour={toHour} onChange={handleTimeChange} />

            <RecommendationBox status={recStatus} recommendation={apiRespons} />

            <GraphSection status={graphStatus} data={graphData} />

        </div>
    );
}

export default LandingPage;
