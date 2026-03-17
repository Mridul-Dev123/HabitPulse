import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import api from '../api';
import './Dashboard.css';

const Dashboard = () => {
  const { logout } = useAuth();
  const navigate = useNavigate();
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // In a real app, you might fetch user data or habits here
    setLoading(false);
  }, []);

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  if (loading) {
    return <div className="loading">Loading dashboard...</div>;
  }

  return (
    <div className="dashboard-layout">
      <header className="dashboard-header">
        <div className="logo">HabitPulse</div>
        <button onClick={handleLogout} className="logout-btn">Logout</button>
      </header>
      
      <main className="dashboard-main">
        <h1>Welcome to Your Dashboard</h1>
        <p>This is where your habits will live!</p>
        
        <div className="empty-state">
          <h3>No habits found</h3>
          <p>Start tracking your goals today.</p>
          <button className="add-habit-btn">Create New Habit</button>
        </div>
      </main>
    </div>
  );
};

export default Dashboard;
