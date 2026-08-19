import API from "./api";

const getAuditLogs = async () => {
  const user = JSON.parse(localStorage.getItem("user"));

  const response = await API.get("/audit-logs", {
    params: {
      user_id: user.user_id,
    },
  });

  return response.data;
};

export default getAuditLogs;