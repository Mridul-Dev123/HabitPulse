import { useEffect, useEffectEvent, useRef, useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import api from '../api';
import { useAuth } from '../contexts/AuthContext';
import './Login.css';

const Login = () => {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const [googleClientId, setGoogleClientId] = useState('');
  const [googleLoading, setGoogleLoading] = useState(true);
  const [googleConfigError, setGoogleConfigError] = useState('');
  const googleButtonRef = useRef(null);
  
  const navigate = useNavigate();
  const { login } = useAuth();

  useEffect(() => {
    let isMounted = true;

    const loadGoogleConfig = async () => {
      try {
        const response = await api.get('/auth/google/config');
        if (isMounted) {
          setGoogleClientId(response.data?.client_id || '');
          setGoogleConfigError('');
        }
      } catch (err) {
        if (isMounted) {
          setGoogleClientId('');
          setGoogleConfigError(
            err.response?.data?.detail ||
            `Unable to reach the auth server at ${api.defaults.baseURL}.`
          );
        }
      } finally {
        if (isMounted) {
          setGoogleLoading(false);
        }
      }
    };

    loadGoogleConfig();

    return () => {
      isMounted = false;
    };
  }, []);

  const handleLogin = async (e) => {
    e.preventDefault();
    setError('');
    setLoading(true);
    
    try {
      // FastAPI OAuth2PasswordRequestForm expects form data
      const formData = new URLSearchParams();
      formData.append('username', username);
      formData.append('password', password);
      
      const response = await api.post('/auth/login', formData, {
        headers: {
          'Content-Type': 'application/x-www-form-urlencoded'
        }
      });
      
      login(response.data.access_token);
      navigate('/dashboard');
    } catch (err) {
      setError(err.response?.data?.detail || 'Login failed. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const handleGoogleCredential = useEffectEvent(async (googleResponse) => {
    if (!googleResponse?.credential) {
      setError('Google login failed. Please try again.');
      return;
    }

    setError('');
    setLoading(true);

    try {
      const response = await api.post('/auth/google', {
        credential: googleResponse.credential
      });

      login(response.data.access_token);
      navigate('/dashboard');
    } catch (err) {
      setError(err.response?.data?.detail || 'Google login failed. Please try again.');
    } finally {
      setLoading(false);
    }
  });

  useEffect(() => {
    if (!googleClientId || !googleButtonRef.current) {
      return undefined;
    }

    let cancelled = false;
    let intervalId;

    const renderGoogleButton = () => {
      if (cancelled || !window.google?.accounts?.id || !googleButtonRef.current) {
        return false;
      }

      window.google.accounts.id.initialize({
        client_id: googleClientId,
        callback: handleGoogleCredential,
      });

      googleButtonRef.current.innerHTML = '';
      window.google.accounts.id.renderButton(googleButtonRef.current, {
        theme: 'outline',
        size: 'large',
        text: 'continue_with',
        shape: 'pill',
        width: 320,
      });

      return true;
    };

    if (!renderGoogleButton()) {
      intervalId = window.setInterval(() => {
        if (renderGoogleButton() && intervalId) {
          window.clearInterval(intervalId);
        }
      }, 300);
    }

    return () => {
      cancelled = true;
      if (intervalId) {
        window.clearInterval(intervalId);
      }
    };
  }, [googleClientId]);

  return (
    <div className="auth-container">
      <div className="auth-card">
        <h2>Welcome to HabitPulse</h2>
        <p>Login to track your habits</p>
        
        {error && <div className="auth-error">{error}</div>}
        
        <form onSubmit={handleLogin} className="auth-form">
          <div className="form-group">
            <label htmlFor="username">Username</label>
            <input
              type="text"
              id="username"
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              required
            />
          </div>
          
          <div className="form-group">
            <label htmlFor="password">Password</label>
            <input
              type="password"
              id="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              required
            />
          </div>
          
          <button type="submit" disabled={loading} className="auth-button">
            {loading ? 'Logging in...' : 'Login'}
          </button>
        </form>

        <div className="auth-divider">
          <span>or</span>
        </div>

        <div className="google-auth-section">
          {googleLoading && (
            <p className="google-auth-status">Loading Google sign-in...</p>
          )}

          {!googleLoading && googleClientId && (
            <div ref={googleButtonRef} className="google-button-container" />
          )}

          {!googleLoading && !googleClientId && (
            <p className="google-auth-status">
              {googleConfigError || 'Google sign-in is unavailable until the server Google client ID is configured.'}
            </p>
          )}
        </div>
        
        <div className="auth-footer">
          <p>Don't have an account? <Link to="/signup">Sign up</Link></p>
        </div>
      </div>
    </div>
  );
};

export default Login;
