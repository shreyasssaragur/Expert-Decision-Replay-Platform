import React, { useState } from "react";
import API from "../../services/api";
import { useNavigate } from "react-router-dom";

function Login() {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const navigate = useNavigate();

  const handleLogin = async (e) => {
    e.preventDefault();

    setLoading(true);
    setError("");

    try {
      const response = await API.post("/login", {
        email: email,
        password: password,
      });

      console.log("Login successful:", response.data);

      localStorage.setItem(
        "user",
        JSON.stringify(response.data)
      );

      // If backend returns a token, store it
      if (response.data.access_token) {
        localStorage.setItem(
          "token",
          response.data.access_token
        );
      }

      navigate("/dashboard");
    } catch (err) {
      console.error("Login Error:", err);

      if (err.response?.data?.detail) {
        const detail = err.response.data.detail;

        if (Array.isArray(detail)) {
          setError(
            detail
              .map((item) => item.msg)
              .join(", ")
          );
        } else {
          setError(detail);
        }
      } else {
        setError("Login Failed. Please check your connection.");
      }
    } finally {
      setLoading(false);
    }
  };

  return (
    <div
      className="d-flex justify-content-center align-items-center"
      style={{
        minHeight: "100vh",
        background:
          "linear-gradient(135deg, #0f172a, #2563eb)",
      }}
    >
      <div
        className="card shadow-lg border-0"
        style={{
          width: "430px",
          borderRadius: "20px",
        }}
      >
        <div className="card-body p-5">

          {/* Header */}
          <div className="text-center mb-4">
            <h2 className="fw-bold text-primary">
              Expert Decision Replay Platform
            </h2>

            <p className="text-muted">
              Sign in to continue
            </p>
          </div>

          {/* Error Message */}
          {error && (
            <div className="alert alert-danger">
              {error}
            </div>
          )}

          {/* Login Form */}
          <form onSubmit={handleLogin}>

            {/* Email */}
            <div className="mb-3">
              <label className="form-label">
                Email
              </label>

              <input
                type="email"
                className="form-control"
                placeholder="Enter your email"
                value={email}
                onChange={(e) =>
                  setEmail(e.target.value)
                }
                required
              />
            </div>

            {/* Password */}
            <div className="mb-2">
              <label className="form-label">
                Password
              </label>

              <input
                type="password"
                className="form-control"
                placeholder="Enter your password"
                value={password}
                onChange={(e) =>
                  setPassword(e.target.value)
                }
                required
              />
            </div>

            {/* Forgot Password */}
            <div className="text-end mb-4">
              <button
                type="button"
                className="btn btn-link p-0 text-decoration-none"
                onClick={() =>
                  navigate("/forgot-password")
                }
              >
                Forgot Password?
              </button>
            </div>

            {/* Login Button */}
            <button
              type="submit"
              className="btn btn-primary w-100"
              disabled={loading}
            >
              {loading
                ? "Logging in..."
                : "Login"}
            </button>

          </form>

          <hr />

          {/* Register */}
          <div className="text-center">

            <p className="mb-2">
              Don't have an account?
            </p>

            <button
              type="button"
              className="btn btn-outline-primary"
              onClick={() =>
                navigate("/register")
              }
            >
              Create New Account
            </button>

          </div>

        </div>
      </div>
    </div>
  );
}

export default Login;