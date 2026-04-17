import React, { useState, useEffect } from 'react';
import { HashRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { Toaster } from 'react-hot-toast';
import axios from 'axios';
import { API } from './config';
import Login from './components/Login';
import Dashboard from './components/Dashboard';
import DungeonMap from './components/DungeonMap';
import GamePlay from './components/GamePlay';
import MiniGames from './components/MiniGames';
import Profile from './components/Profile';
import './App.css';

function App() {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const token = localStorage.getItem('token');
    const username = localStorage.getItem('username');
    if (token && username) {
      // Restore session and refresh progress from server
      axios.get(`${API}/api/progress/${username}`)
        .then(res => {
          const total_levels = res.data.total_levels || 30;
          localStorage.setItem('total_levels', total_levels);
          setUser({ token, username, total_levels });
        })
        .catch(() => {
          // Token may be expired — clear session
          localStorage.removeItem('token');
          localStorage.removeItem('username');
          localStorage.removeItem('total_levels');
        })
        .finally(() => setLoading(false));
    } else {
      setLoading(false);
    }
  }, []);

  const handleLogin = (token, username, totalLevels = 30) => {
    localStorage.setItem('token', token);
    localStorage.setItem('username', username);
    localStorage.setItem('total_levels', totalLevels);
    setUser({ token, username, total_levels: totalLevels });
  };

  const handleLogout = () => {
    localStorage.removeItem('token');
    localStorage.removeItem('username');
    localStorage.removeItem('total_levels');
    setUser(null);
  };

  if (loading) {
    return (
      <div className="loading-screen">
        <div className="loader"></div>
      </div>
    );
  }

  return (
    <Router future={{ v7_startTransition: true, v7_relativeSplatPath: true }}>
      <div className="App">
        <Toaster position="top-right" />
        <Routes>
          <Route 
            path="/login" 
            element={!user ? <Login onLogin={handleLogin} /> : <Navigate to="/dashboard" />} 
          />
          <Route 
            path="/dashboard" 
            element={user ? <Dashboard user={user} onLogout={handleLogout} /> : <Navigate to="/login" />} 
          />
          <Route 
            path="/map" 
            element={user ? <DungeonMap user={user} /> : <Navigate to="/login" />} 
          />
          <Route 
            path="/play/:level" 
            element={user ? <GamePlay user={user} /> : <Navigate to="/login" />} 
          />
          <Route 
            path="/mini-games" 
            element={user ? <MiniGames user={user} /> : <Navigate to="/login" />} 
          />
          <Route 
            path="/profile" 
            element={user ? <Profile user={user} onLogout={handleLogout} /> : <Navigate to="/login" />} 
          />
          <Route path="/" element={<Navigate to={user ? "/dashboard" : "/login"} />} />
        </Routes>
      </div>
    </Router>
  );
}

export default App;
