import apiConfig from "../config/apiConfig";
import { getJson } from "./apiClient";

export function getHourlyGraph(weekday, from_hour = 6, to_hour = 10, holiday_mode = "all") {
  const params = new URLSearchParams({
    weekday: String(weekday),
    from_hour: String(from_hour),
    to_hour: String(to_hour),
    holiday_mode: String(holiday_mode),
  });

  const url = `${apiConfig.baseUrl}${apiConfig.endpoints.graph}?${params.toString()}`;
  return getJson(url);
}
