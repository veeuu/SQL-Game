import { useState } from 'react';
import { API, WS } from '../config';
import { motion, AnimatePresence } from 'framer-motion';
import { Mail, Lock, User, Target } from 'lucide-react';
import toast from 'react-hot-toast';
import axios from 'axios';
import './Login.css';

const CHALLENGE_OPTIONS = [
  { days: 15,  label: '15 Days',  desc: 'Quick Sprint',    emoji: '⚡', color: '#10b981' },
  { days: 30,  label: '30 Days',  desc: 'Monthly Goal',    emoji: '🎯', color: '#3b82f6' },
  { days: 60,  label: '60 Days',  desc: 'Deep Dive',       emoji: '🔥', color: '#f59e0b' },
  { days: 100, label: '100 Days', desc: 'SQL Master Path', emoji: '👑', color: '#8b5cf6' },
];

const Login = ({ onLogin }) => {
  const [isRegister, setIsRegister] = useState(false);
  const [step, setStep] = useState(1); // 1 = form, 2 = challenge picker
  const [formData, setFormData] = useState({ username: '', email: '', password: '' });
  const [challengeDays, setChallengeDays] = useState(null);
  const [customDays, setCustomDays] = useState('');

  const handleFormSubmit = async (e) => {
    e.preventDefault();
    if (isRegister) {
      // Go to challenge picker before registering
      setStep(2);
    } else {
      await doLogin();
    }
  };

  const doLogin = async () => {
    try {
      const res = await axios.post(`${API}/api/login`, formData);
      toast.success('Welcome back, Adventurer!');
      onLogin(res.data.token, res.data.username, res.data.total_levels);
    } catch (err) {
      toast.error(err.response?.data?.detail || 'Authentication failed');
    }
  };

  const doRegister = async (days) => {
    try {
      const res = await axios.post(`${API}/api/register`, {
        ...formData,
        total_levels: days,
      });
      toast.success(`🎉 ${days}-Day Challenge started! Let's go!`);
      onLogin(res.data.token, res.data.username, res.data.total_levels);
    } catch (err) {
      toast.error(err.response?.data?.detail || 'Registration failed');
    }
  };

  const handleChallengeSelect = (days) => {
    setChallengeDays(days);
    doRegister(days);
  };

  const handleCustomSubmit = () => {
    const d = parseInt(customDays);
    if (!d || d < 5 || d > 365) {
      toast.error('Enter a number between 5 and 365');
      return;
    }
    doRegister(d);
  };

  return (
    <div className="login-container">
      <motion.div
        className="login-card glass"
        initial={{ opacity: 0, y: 50 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5 }}
      >
        <div className="login-header">
          <h1>⚔️ SQL Dungeon</h1>
          <p>The AI-Powered SQL Challenge</p>
        </div>

        <AnimatePresence mode="wait">
          {step === 1 && (
            <motion.form
              key="form"
              onSubmit={handleFormSubmit}
              className="login-form"
              initial={{ opacity: 0, x: -20 }}
              animate={{ opacity: 1, x: 0 }}
              exit={{ opacity: 0, x: 20 }}
            >
              <div className="input-group">
                <User size={20} className="input-icon" />
                <input
                  type="text"
                  placeholder="Username"
                  className="input-field"
                  value={formData.username}
                  onChange={(e) => setFormData({ ...formData, username: e.target.value })}
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
                    onChange={(e) => setFormData({ ...formData, email: e.target.value })}
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
                  onChange={(e) => setFormData({ ...formData, password: e.target.value })}
                  required
                />
              </div>

              <button type="submit" className="btn btn-primary login-btn">
                {isRegister ? 'Next: Choose Challenge →' : 'Enter the Dungeon'}
              </button>
            </motion.form>
          )}

          {step === 2 && (
            <motion.div
              key="challenge"
              className="challenge-picker"
              initial={{ opacity: 0, x: 20 }}
              animate={{ opacity: 1, x: 0 }}
              exit={{ opacity: 0, x: -20 }}
            >
              <div className="challenge-picker-header">
                <Target size={28} />
                <h2>Choose Your Challenge</h2>
                <p>How many levels do you want to conquer?</p>
              </div>

              <div className="challenge-options">
                {CHALLENGE_OPTIONS.map((opt) => (
                  <motion.button
                    key={opt.days}
                    className="challenge-option"
                    style={{ '--accent': opt.color }}
                    whileHover={{ scale: 1.04, y: -4 }}
                    whileTap={{ scale: 0.97 }}
                    onClick={() => handleChallengeSelect(opt.days)}
                  >
                    <span className="opt-emoji">{opt.emoji}</span>
                    <span className="opt-label">{opt.label}</span>
                    <span className="opt-desc">{opt.desc}</span>
                    <span className="opt-levels">{opt.days} levels</span>
                  </motion.button>
                ))}
              </div>

              <div className="custom-days">
                <p>Or enter a custom number:</p>
                <div className="custom-input-row">
                  <input
                    type="number"
                    min="5"
                    max="365"
                    placeholder="e.g. 45"
                    className="input-field"
                    value={customDays}
                    onChange={(e) => setCustomDays(e.target.value)}
                  />
                  <button className="btn btn-primary" onClick={handleCustomSubmit}>
                    Start
                  </button>
                </div>
              </div>

              <button className="back-btn" onClick={() => setStep(1)}>
                ← Back
              </button>
            </motion.div>
          )}
        </AnimatePresence>

        {step === 1 && (
          <div className="login-footer">
            <button className="toggle-btn" onClick={() => { setIsRegister(!isRegister); setStep(1); }}>
              {isRegister ? 'Already have an account? Login' : "Don't have an account? Register"}
            </button>
          </div>
        )}
      </motion.div>
    </div>
  );
};

export default Login;
