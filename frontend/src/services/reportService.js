import API from "./api";

// ======================================
// Get Dashboard Report
// ======================================

export const getDashboardReport = async () => {
  const response = await API.get(
    "/reports/dashboard"
  );

  return response.data;
};

// ======================================
// Get Complete Decision Report
// ======================================

export const getDecisionReportData = async (
  decisionId
) => {
  const response = await API.get(
    `/reports/decision/${decisionId}`
  );

  return response.data;
};