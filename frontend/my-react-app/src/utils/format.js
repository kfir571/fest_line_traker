export function pad2(n) {
  return String(n).padStart(2, "0");
}

export function formatHourLabel(hour) {
  return `${pad2(hour)}:00`;
}

export function formatTimeLabel(hour, minute = 0) {
  return `${pad2(hour)}:${pad2(minute)}`;
}
