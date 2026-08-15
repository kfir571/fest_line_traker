import "../App.css";

function StatusMessage({ variant, children }) {
  return (
    <div
      className={`status-message status-message--${variant}`}
      role="status"
      aria-live="polite"
    >
      {children}
    </div>
  );
}

export default StatusMessage;
