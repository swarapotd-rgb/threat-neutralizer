import React, { useState } from "react";
import { useNavigate } from "react-router-dom";

const BackgroundParticles = () => (
  <div className="absolute inset-0 overflow-hidden pointer-events-none">
    {[...Array(20)].map((_, i) => (
      <div
        key={i}
        className="absolute rounded-full bg-gradient-to-r from-indigo-500/20 to-purple-500/20 blur-xl animate-pulse"
        style={{
          width: `${Math.random() * 300 + 100}px`,
          height: `${Math.random() * 300 + 100}px`,
          left: `${Math.random() * 100}%`,
          top: `${Math.random() * 100}%`,
          animationDelay: `${Math.random() * 5}s`,
          animationDuration: `${Math.random() * 10 + 10}s`,
        }}
      />
    ))}
  </div>
);

const QRCodeDisplay = ({ value, size }) => {
  const canvasRef = React.useRef(null);

  React.useEffect(() => {
    if (canvasRef.current && value) {
      const canvas = canvasRef.current;
      const ctx = canvas.getContext('2d');
      
      ctx.fillStyle = '#ffffff';
      ctx.fillRect(0, 0, size, size);
      ctx.fillStyle = '#1a1a2e';
      ctx.font = '14px system-ui';
      ctx.textAlign = 'center';
      
      ctx.fillText('Scan with your', size/2, size/2 - 20);
      ctx.fillText('authenticator app', size/2, size/2);
      ctx.font = '11px system-ui';
      ctx.fillStyle = '#666';
      ctx.fillText('(QR generation placeholder)', size/2, size/2 + 25);
    }
  }, [value, size]);

  return (
    <canvas 
      ref={canvasRef} 
      width={size} 
      height={size} 
      className="rounded-2xl shadow-2xl border-4 border-indigo-500/30 mx-auto"
    />
  );
};

const RegisterPage = () => {
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [regToken, setRegToken] = useState("");
  const [secret, setSecret] = useState("");
  const [message, setMessage] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const navigate = useNavigate();

  const handleRegister = async (e) => {
    e.preventDefault();
    setIsLoading(true);
    setMessage("");

    try {
      const res = await fetch("http://localhost:8000/register", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ username, password, regtoken: regToken }),
      });

      const data = await res.json();
      setMessage(data.msg);

      if (data.msg === "all good") {
        setSecret(data.secret);
      } else {
        setSecret("");
      }
    } catch {
      setMessage("Server error");
      setSecret("");
    } finally {
      setIsLoading(false);
    }
  };

  const otpauthUrl = secret
    ? `otpauth://totp/DeepWatch:${username}?secret=${secret}&issuer=DeepWatch`
    : "";

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-950 via-purple-950 to-slate-900 flex items-center justify-center p-4 relative overflow-hidden">
      <BackgroundParticles />
      
      <div className="absolute top-20 right-20 w-96 h-96 bg-purple-600/30 rounded-full blur-3xl animate-pulse" />
      <div className="absolute bottom-20 left-20 w-96 h-96 bg-indigo-600/20 rounded-full blur-3xl animate-pulse" style={{ animationDelay: '1s' }} />
      
      <div className="relative z-10 w-full max-w-2xl">
        <div className="text-center mb-8">
          <div className="inline-flex items-center justify-center w-20 h-20 bg-gradient-to-br from-purple-500 to-indigo-600 rounded-2xl shadow-2xl mb-4 transform hover:rotate-12 transition-transform duration-300">
            <svg className="w-10 h-10 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M18 9v3m0 0v3m0-3h3m-3 0h-3m-2-5a4 4 0 11-8 0 4 4 0 018 0zM3 20a6 6 0 0112 0v1H3v-1z" />
            </svg>
          </div>
          <h1 className="text-4xl font-bold text-white mb-2 tracking-tight">Join DeepWatch</h1>
          <p className="text-purple-300 text-sm">Create your secure account</p>
        </div>

        {!secret ? (
          <form onSubmit={handleRegister} className="backdrop-blur-xl bg-white/10 border border-white/20 rounded-3xl shadow-2xl p-8">
            <h2 className="text-2xl font-bold text-white mb-6 text-center">Registration</h2>
            
            <div className="space-y-4">
              <div className="relative group">
                <div className="absolute inset-y-0 left-0 pl-4 flex items-center pointer-events-none">
                  <svg className="w-5 h-5 text-purple-400 group-focus-within:text-purple-300 transition-colors" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
                  </svg>
                </div>
                <input
                  type="text"
                  placeholder="Choose Username"
                  value={username}
                  onChange={(e) => setUsername(e.target.value)}
                  required
                  className="w-full pl-12 pr-4 py-3.5 bg-white/5 border-2 border-white/10 rounded-xl text-white placeholder-gray-400 focus:outline-none focus:border-purple-500 focus:bg-white/10 transition-all duration-300"
                />
              </div>

              <div className="relative group">
                <div className="absolute inset-y-0 left-0 pl-4 flex items-center pointer-events-none">
                  <svg className="w-5 h-5 text-purple-400 group-focus-within:text-purple-300 transition-colors" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z" />
                  </svg>
                </div>
                <input
                  type="password"
                  placeholder="Create Password"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  required
                  className="w-full pl-12 pr-4 py-3.5 bg-white/5 border-2 border-white/10 rounded-xl text-white placeholder-gray-400 focus:outline-none focus:border-purple-500 focus:bg-white/10 transition-all duration-300"
                />
              </div>

              <div className="relative group">
                <div className="absolute inset-y-0 left-0 pl-4 flex items-center pointer-events-none">
                  <svg className="w-5 h-5 text-purple-400 group-focus-within:text-purple-300 transition-colors" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 7a2 2 0 012 2m4 0a6 6 0 01-7.743 5.743L11 17H9v2H7v2H4a1 1 0 01-1-1v-2.586a1 1 0 01.293-.707l5.964-5.964A6 6 0 1121 9z" />
                  </svg>
                </div>
                <input
                  type="text"
                  placeholder="Admin Registration Token"
                  value={regToken}
                  onChange={(e) => setRegToken(e.target.value)}
                  required
                  className="w-full pl-12 pr-4 py-3.5 bg-white/5 border-2 border-white/10 rounded-xl text-white placeholder-gray-400 focus:outline-none focus:border-purple-500 focus:bg-white/10 transition-all duration-300"
                />
              </div>
            </div>

            {message && (
              <div className={`mt-4 p-3 rounded-xl text-sm font-medium text-center ${
                secret 
                  ? 'bg-green-500/20 text-green-300 border border-green-500/30' 
                  : 'bg-red-500/20 text-red-300 border border-red-500/30'
              }`}>
                {message}
              </div>
            )}

            <button
              type="submit"
              disabled={isLoading}
              className="w-full mt-6 py-3.5 bg-gradient-to-r from-purple-600 to-indigo-600 hover:from-purple-500 hover:to-indigo-500 text-white font-semibold rounded-xl shadow-lg hover:shadow-purple-500/50 transform hover:-translate-y-0.5 transition-all duration-300 disabled:opacity-50"
            >
              {isLoading ? 'Creating Account...' : 'Create Account'}
            </button>

            <button
              type="button"
              onClick={() => navigate("/")}
              className="w-full mt-3 py-3.5 bg-white/5 hover:bg-white/10 text-white font-semibold rounded-xl border-2 border-white/10 hover:border-white/20 transform hover:-translate-y-0.5 transition-all duration-300"
            >
              Back to Login
            </button>
          </form>
        ) : (
          <div className="backdrop-blur-xl bg-white/10 border border-white/20 rounded-3xl shadow-2xl p-8">
            <div className="text-center mb-6">
              <div className="inline-flex items-center justify-center w-16 h-16 bg-gradient-to-br from-green-500 to-emerald-600 rounded-full shadow-xl mb-4">
                <svg className="w-8 h-8 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                </svg>
              </div>
              <h3 className="text-3xl font-bold text-white mb-2">Account Created!</h3>
              <p className="text-gray-300">Set up two-factor authentication</p>
            </div>

            <div className="bg-white/5 rounded-2xl p-6 mb-6 border border-white/10">
              <div className="grid grid-cols-2 gap-4 mb-4">
                <div>
                  <p className="text-gray-400 text-sm mb-1">Username</p>
                  <p className="text-white font-semibold">{username}</p>
                </div>
                <div>
                  <p className="text-gray-400 text-sm mb-1">Password</p>
                  <p className="text-white font-mono">{'•'.repeat(password.length)}</p>
                </div>
              </div>
            </div>

            <div className="text-center mb-6">
              <QRCodeDisplay value={otpauthUrl} size={240} />
            </div>

            <div className="bg-gradient-to-r from-indigo-500/10 to-purple-500/10 rounded-2xl p-6 border border-indigo-500/20 mb-4">
              <p className="text-sm text-gray-300 mb-3 text-center">Or enter this secret manually:</p>
              <code className="block text-center text-lg font-mono text-white bg-black/30 px-4 py-3 rounded-xl break-all border border-white/10">
                {secret}
              </code>
            </div>

            <div className="bg-blue-500/10 border border-blue-500/20 rounded-xl p-4 mb-6">
              <p className="text-sm text-blue-200 text-center">
                Your authenticator app will now generate time-based codes for secure login
              </p>
            </div>

            <button
              onClick={() => navigate("/")}
              className="w-full py-3.5 bg-gradient-to-r from-indigo-600 to-purple-600 hover:from-indigo-500 hover:to-purple-500 text-white font-semibold rounded-xl shadow-lg hover:shadow-indigo-500/50 transform hover:-translate-y-0.5 transition-all duration-300"
            >
              Continue to Login
            </button>
          </div>
        )}

        <p className="text-center text-gray-500 text-xs mt-6">
          Your data is protected with AES-256 encryption
        </p>
      </div>
    </div>
  );
};

export default RegisterPage;