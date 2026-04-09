const UserProfile = ({ sessionData }) => {
  if (!sessionData) return null;

  console.log(sessionData)

  const isGoogle = sessionData.metadata.oauth_provider === "google";
  const userData = sessionData.data;

  const displayInfo = {
    name: isGoogle ? userData.name : (userData.name|| "N/A"),
    email: isGoogle ? userData.email : (userData.username || "N/A"),
    avatar: isGoogle ? userData.picture : null,
    provider: sessionData.metadata.oauth_provider
  };

  return (
    <div style={{
      background: "#fff",
      border: "1px solid #ddd",
      borderRadius: "12px",
      padding: "24px",
      boxShadow: "0 4px 6px rgba(0,0,0,0.05)",
      display: "flex",
      alignItems: "center",
      gap: "20px"
    }}>
      {/* Hiển thị Avatar nếu là Google, nếu không dùng Icon mặc định */}
      <div style={{
        width: "64px",
        height: "64px",
        borderRadius: "50%",
        background: "#eee",
        overflow: "hidden",
        display: "flex",
        alignItems: "center",
        justifyContent: "center",
        fontSize: "24px"
      }}>
        {displayInfo.avatar ? 
          <img src={displayInfo.avatar} alt="avatar" style={{width: '100%'}} /> : 
          "👤"
        }
      </div>

      <div style={{ textAlign: "left" }}>
        <h3 style={{ margin: "0 0 4px 0" }}>{displayInfo.name}</h3>
        <p style={{ margin: "0", color: "#666", fontSize: "14px" }}>{displayInfo.email}</p>
        <span style={{
          marginTop: "8px",
          display: "inline-block",
          padding: "2px 8px",
          background: displayInfo.provider === "google" ? "#4285F4" : "#111",
          color: "#fff",
          borderRadius: "4px",
          fontSize: "10px",
          textTransform: "uppercase",
          fontWeight: "bold"
        }}>
          {displayInfo.provider}
        </span>
      </div>
    </div>
  );
};

export default UserProfile;