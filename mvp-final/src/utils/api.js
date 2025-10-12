export const loginUser = async (username, password, otp) => {
  const res = await fetch("http://localhost:8000/login", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ username, password, totp_code: otp }),
  });
  return await res.json();
};

export const verifyToken = async (token, username, role) => {
  const res = await fetch("http://localhost:8000/verify", {
    method: "POST",
    headers: { 
      "Content-Type": "application/json",
      "Authorization": `Bearer ${token}`
    },
    body: JSON.stringify({ username, role }),
  });
  return await res.json();
};

export const registerUser = async (username, password, regtoken) => {
  const res = await fetch("http://localhost:8000/register", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ username, password, regtoken }),
  });
  return await res.json();
};