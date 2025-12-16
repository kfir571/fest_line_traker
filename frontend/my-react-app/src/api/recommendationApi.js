import apiConfig from "../config/apiConfig";
import { getJson } from "./apiClient";

export function getRecommendation(allowed_weekdays, from_hour = 6, to_hour = 10) {
  const params = new URLSearchParams({
    allowed_weekdays: Array.isArray(allowed_weekdays)
      ? allowed_weekdays.join(',')
      : String(allowed_weekdays),
    from_hour: String(from_hour),
    to_hour: String(to_hour),
  });

  const url = `${apiConfig.baseUrl}${apiConfig.endpoints.recommendation}?${params.toString()}`;
  return getJson(url); // מחזיר Promise של JSON
}
