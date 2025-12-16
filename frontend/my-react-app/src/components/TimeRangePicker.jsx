import "../App.css";

function TimeRangePicker({ fromHour, toHour, onChange }) {
    const hours = Array.from({ length: 24 }, (_, i) => i); // 0..23

    const handleFromChange = (e) => {
        const newFrom = Number(e.target.value);
        const fixedTo = Math.max(toHour, newFrom + 1); // מבטיח from < to

        if (newFrom !== fromHour || fixedTo !== toHour) {
            onChange(newFrom, fixedTo);
        }
    };

    const handleToChange = (e) => {
        const newTo = Number(e.target.value);
        const fixedFrom = Math.min(fromHour, newTo - 1); // מבטיח from < to

        if (fixedFrom !== fromHour || newTo !== toHour) {
            onChange(fixedFrom, newTo);
        }
    };

    const fmt = (h) => `${String(h).padStart(2, "0")}:00`;

    return (
        <div className="time-range">
            <label className="time-range__label">
                :משעה
                <select className="time-range__select" value={fromHour} onChange={handleFromChange}>
                    {hours.slice(0, 23).map((h) => (
                        <option key={h} value={h}>{fmt(h)}</option>
                    ))}
                </select>
            </label>

            <span className="time-range__dash">—</span>

            <label className="time-range__label">
                :עד שעה
                <select className="time-range__select" value={toHour} onChange={handleToChange}>
                    {hours.slice(1).map((h) => (
                        <option key={h} value={h}>{fmt(h)}</option>
                    ))}
                </select>
            </label>
        </div>
    );
}

export default TimeRangePicker;
