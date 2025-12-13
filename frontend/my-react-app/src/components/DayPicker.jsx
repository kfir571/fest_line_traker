import "../App.css";
import ButtonSelectDay from "./ButtonSelectDay.jsx";

function DayPicker({ days, selectedDay, onChange }) {
    return (
        <div className="days-buttons">
            {days.map(({ id, label }) => (
                <ButtonSelectDay
                    key={id}
                    isSelected={id === selectedDay}
                    onClick={() => onChange(id)}
                >
                    {label}
                </ButtonSelectDay>
            ))}
        </div>
    );
}

export default DayPicker;
