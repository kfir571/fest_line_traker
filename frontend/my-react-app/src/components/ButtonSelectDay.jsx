import "../App.css";

function ButtonSelectDay({ children, isSelected, onClick }) {
    return (
        <button
            className={`button-select-day ${isSelected ? "selected" : ""}`}
            onClick={onClick}
            type="button"
        >
            {children}
        </button>
    );
}

export default ButtonSelectDay;
