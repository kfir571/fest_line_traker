import "../App.css";

function StatusMessage({ variant, children }) {
  return (
    <div
      className={`status-message status-message--${variant}`}
      role="status"
      aria-live="polite"
    >
      {variant === "loading" && <span className="status-message__bar" aria-hidden="true" />}
      {children}
    </div>
  );
}

export default StatusMessage;
