import "../App.css";
import ButtonSelectDay from "./ButtonSelectDay.jsx";

function DayPicker({ days, selectedDay, onChange }) {
    return (
        <div className="days-buttons" role="group" aria-label="בחירת יום בשבוע">
            {days.map(({ id, label, fullLabel }) => (
                <ButtonSelectDay
                    key={id}
                    isSelected={id === selectedDay}
                    onClick={() => onChange(id)}
                    ariaLabel={fullLabel ?? label}
                >
                    {label}
                </ButtonSelectDay>
            ))}
        </div>
    );
}

export default DayPicker;
