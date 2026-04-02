import React, { useEffect, useState } from "react";
import { Routes, Route, useNavigate } from "react-router-dom";

const API = "http://localhost:5001";

function Home() {
  const [sessionData, setSessionData] = useState(null);

  const loadSession = async () => {
    const res = await fetch(`${API}/session`, {
      credentials: "include",
    });
    if (!res.ok) {
      setSessionData(null);
      return;
    }
    const data = await res.json();
    setSessionData(data);
  };


  const logout = async () => {
    await fetch(`${API}/logout`, {
      method: "POST",
      credentials: "include",
    });
    loadSession();
  };

  useEffect(() => {
    loadSession();
  }, []);

  return (
    <div style={{ maxWidth: 900, margin: "40px auto", fontFamily: "Arial" }}>
      <h1>OAuth 2.0 Demo</h1>
      <p>Demo Authorization Code Grant với Flask + React</p>

      <div style={{ display: "flex", justifyContent: "center", gap: 12, marginBottom: 20 }}>
        {
          !sessionData ?
          <a
          href={`${API}/login`}
          style={{
            padding: "10px 14px",
            background: "#111",
            color: "white",
            textDecoration: "none",
            borderRadius: 8,
          }}
        >
          Login with Demo OAuth
        </a> : 
        <button onClick={logout} style={{ padding: "10px 14px" }}>
          Logout
        </button>
        }
        

        
      </div>

      <div style={{ marginBottom: 24 }}>
        <h3>Session</h3>
        <pre style={{ background: "#f4f4f4", padding: 16, borderRadius: 8 }}>
          {JSON.stringify(sessionData, null, 2)}
        </pre>
      </div>

    </div>
  );
}

function Success() {
  const navigate = useNavigate();

  useEffect(() => {
    const timer = setTimeout(() => navigate("/"), 1000);
    return () => clearTimeout(timer);
  }, [navigate]);

  return (
    <div style={{ maxWidth: 900, margin: "40px auto", fontFamily: "Arial" }}>
      <h1>Login Successful!</h1>
      <p>You will be redirected to home page shortly...</p>
    </div>
  );
}

function App() {
  return (
    <Routes>
      <Route path="/" element={<Home />} />
      <Route path="/success" element={<Success />} />
    </Routes>
  );
}

export default App;