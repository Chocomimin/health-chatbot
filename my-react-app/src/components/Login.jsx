import "./AuthForm.css"; // Import the CSS
import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import API from "../api";

export default function Login() {
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const navigate = useNavigate();

  const handleLogin = async () => {
    try {
      const res = await API.post("/login", { username, password });
      localStorage.setItem("token", res.data.token);
      alert("Login successful!");
      navigate("/chat");
    } catch (err) {
      console.error("Login failed:", err);
      alert("Login failed!");
    }
  };

  return (
    <div className="auth-container">
      <form className="auth-form" onSubmit={(e) => { e.preventDefault(); handleLogin(); }}>
        <h2>Login</h2>
        <label>Username:</label>
        <input placeholder="Username" onChange={(e) => setUsername(e.target.value)} />
        <label>Password:</label>
        <input type="password" placeholder="Password" onChange={(e) => setPassword(e.target.value)} />
        <button type="submit">Login</button>
        <p>Don't have an account? <Link to="/signup">Sign Up</Link></p>
      </form>
    </div>
  );
}
