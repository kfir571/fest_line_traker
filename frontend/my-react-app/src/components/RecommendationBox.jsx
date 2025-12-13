import "../App.css";

function RecommendationBox({ selectedDay, fromHour, toHour, recommendation }) {
    if (!recommendation) {
        return (
            <div className="recommendation-box hint">
                בחר יום וטווח שעות כדי לקבל המלצה
            </div>
        );
    }

    return (
        <div className="recommendation-box">
            {recommendation}
            <div className="recommendation-time">
                {String(fromHour).padStart(2, "0")}:00–{String(toHour).padStart(2, "0")}:00
            </div>
        </div>
    );
}

export default RecommendationBox;
