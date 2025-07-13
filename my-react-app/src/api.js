import axios from "axios";

const API = axios.create({
  baseURL: "https://health-chatbot-iq6n.onrender.com", // adjust if needed
});

// Add token to every request if present
API.interceptors.request.use((config) => {
  const token = localStorage.getItem("token");
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

export default API;
