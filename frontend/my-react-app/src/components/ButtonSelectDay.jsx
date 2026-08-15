import "../App.css";

function ButtonSelectDay({ children, isSelected, onClick, ariaLabel }) {
    return (
        <button
            className={`button-select-day ${isSelected ? "selected" : ""}`}
            onClick={onClick}
            type="button"
            aria-pressed={isSelected}
            aria-label={ariaLabel}
        >
            {children}
        </button>
    );
}

export default ButtonSelectDay;
