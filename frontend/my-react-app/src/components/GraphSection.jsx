import "../App.css";
import PriceChart from "./PriceChart.jsx";

function GraphSection({ status, data }) {
    if (status === "idle") {
        return (
            <div className="recommendation-box hint">
                בחר יום וטווח שעות כדי להציג גרף
            </div>
        );
    }

    if (status === "loading") {
        return (
            <div className="recommendation-box hint">
                טוען גרף...
            </div>
        );
    }

    if (status === "error") {
        return (
            <div className="recommendation-box error">
                שגיאה: לא התקבלה תשובה מהשרת עבור הגרף.
            </div>
        );
    }

    // success
    if (!Array.isArray(data) || data.length === 0) {
        return (
            <div className="recommendation-box error">
                אין נתונים זמינים לגרף בטווח שבחרת.
            </div>
        );
    }

    return <PriceChart data={data} />;
}

export default GraphSection;
