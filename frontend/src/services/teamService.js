import API from "./api";

export const getUsers = async () => {
  const res = await API.get("/users");
  return res.data;
};

export const updateRole = async (id, role) => {
  const res = await API.put(
    `/users/${id}/role`,
    { role }
  );

  return res.data;
};

export const deleteUser = async (id) => {
  const res = await API.delete(
    `/users/${id}`
  );

  return res.data;
};