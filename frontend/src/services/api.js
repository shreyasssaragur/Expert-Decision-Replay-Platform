import axios from "axios";

const API = axios.create({
    baseURL: "https://expert-decision-replay-platform-akm3.onrender.com",
    headers: {
        "Content-Type": "application/json",
    },
});

// Request Interceptor
API.interceptors.request.use(
    (config) => {
        const token = localStorage.getItem("token");

        if (token) {
            config.headers.Authorization = `Bearer ${token}`;
        }

        return config;
    },
    (error) => Promise.reject(error)
);

// Response Interceptor
API.interceptors.response.use(
    (response) => response,
    (error) => {
        console.error("API Error:", error.response || error.message);
        return Promise.reject(error);
    }
);

export default API;