import API from "./api";

export const getDocuments = () =>
  API.get("/documents");

export const getDocumentsByDecision = (decisionId) =>
  API.get(`/decisions/${decisionId}/documents`);

export const uploadDocument = (formData) =>
  API.post(
    "/documents/upload",
    formData,
    {
      headers: {
        "Content-Type": "multipart/form-data",
      },
    }
  );

export const deleteDocument = (id) =>
  API.delete(`/documents/${id}`);

export const downloadDocument = (id) => {
  window.open(
    `${API.defaults.baseURL}/documents/download/${id}`,
    "_blank"
  );
};