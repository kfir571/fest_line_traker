import "../App.css";
import PriceChart from "./PriceChart.jsx";
import StatusMessage from "./StatusMessage.jsx";

function GraphSection({ status, data, fromHour, toHour }) {
    if (status === "idle") {
        return (
            <StatusMessage variant="idle">
                בחר יום וטווח שעות כדי להציג גרף
            </StatusMessage>
        );
    }

    if (status === "loading") {
        return (
            <StatusMessage variant="loading">
                טוען גרף...
            </StatusMessage>
        );
    }

    if (status === "error") {
        return (
            <StatusMessage variant="error">
                שגיאה: לא התקבלה תשובה מהשרת עבור הגרף.
            </StatusMessage>
        );
    }

    // success
    if (!Array.isArray(data) || data.length === 0) {
        return (
            <StatusMessage variant="empty">
                אין נתונים להצגה בגרף עבור הטווח שנבחר — נסה טווח אחר.
            </StatusMessage>
        );
    }

    return <PriceChart data={data} fromHour={fromHour} toHour={toHour} />;
}

export default GraphSection;
