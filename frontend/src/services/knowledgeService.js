import API from "./api";

// ======================================
// Get Knowledge Repository
// ======================================

export const getKnowledgeRepository = async () => {
  const response = await API.get("/knowledge");

  return response.data;
};

// ======================================
// Get Single Knowledge Decision
// ======================================

export const getKnowledgeDecision = async (decisionId) => {
  const response = await API.get(
    `/knowledge/${decisionId}`
  );

  return response.data;
};