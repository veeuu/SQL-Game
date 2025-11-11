import React, { useState } from 'react';
import { motion } from 'framer-motion';
import { Sword, Mail, Lock, User } from 'lucide-react';
import toast from 'react-hot-toast';
import axios from 'axios';
import './Login.css';

const Login = ({ onLogin }) => {
  const [isRegister, setIsRegister] = useState(false);
  const [formData, setFormData] = useState({
    username: '',
    email: '',
    password: ''
  });

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    try {
      const endpoint = isRegister ? '/api/register' : '/api/login';
      const response = await axios.post(`http://localhost:8000${endpoint}`, formData);
      
      toast.success(isRegister ? 'Welcome to the Dungeon!' : 'Welcome back, Adventurer!');
      onLogin(response.data.token, response.data.username);
    } catch (error) {
      toast.error(error.response?.data?.detail || 'Authentication failed');
    }
  };

  return (
    <div className="login-container">
      <div className="login-background">
        <div className="dungeon-particles"></div>
      </div>
      
      <motion.div 
        className="login-card glass"
        initial={{ opacity: 0, y: 50 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5 }}
      >
        <div className="login-header">
          <motion.div
            animate={{ rotate: [0, 10, -10, 0] }}
            transition={{ duration: 2, repeat: Infinity }}
          >
            <Sword size={48} className="login-icon" />
          </motion.div>
          <h1>SQL Escape</h1>
          <p>The Optimization Dungeon</p>
        </div>

        <form onSubmit={handleSubmit} className="login-form">
          <div className="input-group">
            <User size={20} className="input-icon" />
            <input
              type="text"
              placeholder="Username"
              className="input-field"
              value={formData.username}
              onChange={(e) => setFormData({...formData, username: e.target.value})}
              required
            />
          </div>

          {isRegister && (
            <div className="input-group">
              <Mail size={20} className="input-icon" />
              <input
                type="email"
                placeholder="Email"
                className="input-field"
                value={formData.email}
                onChange={(e) => setFormData({...formData, email: e.target.value})}
                required
              />
            </div>
          )}

          <div className="input-group">
            <Lock size={20} className="input-icon" />
            <input
              type="password"
              placeholder="Password"
              className="input-field"
              value={formData.password}
              onChange={(e) => setFormData({...formData, password: e.target.value})}
              required
            />
          </div>

          <button type="submit" className="btn btn-primary login-btn">
            {isRegister ? 'Begin Your Quest' : 'Enter the Dungeon'}
          </button>
        </form>

        <div className="login-footer">
          <button 
            className="toggle-btn"
            onClick={() => setIsRegister(!isRegister)}
          >
            {isRegister ? 'Already have an account? Login' : "Don't have an account? Register"}
          </button>
        </div>

        <div className="feature-badges">
          <div className="badge">🗺️ 8 Epic Levels</div>
          <div className="badge">🎮 Mini Games</div>
          <div className="badge">🤖 AI Powered</div>
        </div>
      </motion.div>
    </div>
  );
};

export default Login;
