import "../App.css";
import StatusMessage from "./StatusMessage.jsx";
import { pad2 } from "../utils/format.js";

function RecommendationBox({ status, recommendation }) {
  if (status === "idle") {
    return (
      <StatusMessage variant="idle">
        בחר יום וטווח שעות כדי לקבל המלצה
      </StatusMessage>
    );
  }

  if (status === "loading") {
    return (
      <StatusMessage variant="loading">
        טוען המלצה...
      </StatusMessage>
    );
  }

  if (status === "error") {
    return (
      <StatusMessage variant="error">
        שגיאה: לא התקבלה תשובה מהשרת.
      </StatusMessage>
    );
  }

  // success
  const results = recommendation?.results;
  if (!Array.isArray(results) || results.length === 0) {
    return (
      <StatusMessage variant="empty">
        אין נתונים עבור היום וטווח השעות שנבחרו — נסה טווח אחר.
      </StatusMessage>
    );
  }

  const best =
    results.find((r) => r.rank === 1) ??
    results.reduce((min, r) => (r.rank < min.rank ? r : min), results[0]);

  const hh = pad2(best.hour);
  const mm = pad2(best.minute_bucket ?? 0);

  return (
    <div className="card">
      <div className="recommendation-title">המלצה</div>
      <div className="recommendation-main">
        השעה המומלצת ביותר: <strong>{hh}:{mm}</strong>
      </div>
      <div className="recommendation-sub">
        מחיר ממוצע: {best.avg_price} ₪ | דגימות: {best.sample_count}
      </div>
    </div>
  );
}

export default RecommendationBox;
