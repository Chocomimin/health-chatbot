import "./AuthForm.css";
import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import API from "../api";

export default function Signup() {
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const navigate = useNavigate();

  const handleSignup = async (e) => {
    e.preventDefault();
    try {
      const res = await API.post("/signup", { username, password });
      localStorage.setItem("token", res.data.token);
      alert("Signup successful!");
      navigate("/chat");
    } catch (err) {
      console.error("Signup failed:", err);
      alert("Signup failed!");
    }
  };

  return (
    <div className="auth-container">
      <form className="auth-form" onSubmit={handleSignup}>
        <h2>Sign Up</h2>
        <label>Username:</label>
        <input
          type="text"
          placeholder="Choose a username"
          value={username}
          onChange={(e) => setUsername(e.target.value)}
          required
        />
        <label>Password:</label>
        <input
          type="password"
          placeholder="Create a password"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
          required
        />
        <button type="submit">Sign Up</button>
        <p>Already have an account? <Link to="/">Login</Link></p>
      </form>
    </div>
  );
}
