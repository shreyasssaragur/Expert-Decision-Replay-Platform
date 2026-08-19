import React, { useState } from "react";
import API from "../../services/api";
import { useNavigate } from "react-router-dom";

function Register() {
  const [username, setUsername] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [message, setMessage] = useState("");

  const navigate = useNavigate();

  const handleRegister = async (e) => {
    e.preventDefault();
    setMessage("");

    try {
      await API.post("/register", {
        username: username,
        email: email,
        password: password,
      });

      alert("Registration Successful. Please login.");

      navigate("/");
    } catch (error) {
      console.error("Registration Error:", error);

      if (error.response?.data?.detail) {
        const detail = error.response.data.detail;

        if (Array.isArray(detail)) {
          setMessage(
            detail
              .map((item) => item.msg)
              .join(", ")
          );
        } else {
          setMessage(detail);
        }
      } else {
        setMessage("Registration failed");
      }
    }
  };

  return (
    <div style={{ padding: "30px" }}>
      <h1>Expert Decision Replay Platform</h1>

      <h2>Create New Account</h2>

      <form onSubmit={handleRegister}>
        <div>
          <label>Username</label>
          <br />

          <input
            type="text"
            value={username}
            onChange={(e) => setUsername(e.target.value)}
            required
          />
        </div>

        <br />

        <div>
          <label>Email</label>
          <br />

          <input
            type="email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            required
          />
        </div>

        <br />

        <div>
          <label>Password</label>
          <br />

          <input
            type="password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            required
          />
        </div>

        <br />

        <button type="submit">
          Register
        </button>
      </form>

      {message && (
        <p>{message}</p>
      )}

      <br />

      <p>
        Already have an account?
      </p>

      <button
        type="button"
        onClick={() => navigate("/")}
      >
        Back to Login
      </button>
    </div>
  );
}

export default Register;