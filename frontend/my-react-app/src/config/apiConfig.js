const SERVER_IP = "10.100.102.45"; // בלי / בסוף
const SERVER_PORT = 8000;

const apiConfig = {
  baseUrl: `http://${SERVER_IP}:${SERVER_PORT}`,
  endpoints: {
    recommendation: "/api/recommendation",
    graph: "/api/hourly-graph",
  },
};

export default apiConfig;
