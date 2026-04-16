import { useState, useEffect } from 'react';
import { API } from '../config';
import { useNavigate, useLocation } from 'react-router-dom';
import { motion, AnimatePresence } from 'framer-motion';
import { Map, Gamepad2, User, Trophy, Zap, Target, LogOut, Play } from 'lucide-react';
import axios from 'axios';
import ModeSelectionEntry from './ModeSelectionEntry';
import './Dashboard.css';

const Dashboard = ({ user, onLogout }) => {
  const navigate = useNavigate();
  const location = useLocation();
  const [progress, setProgress] = useState({ level: 1, score: 0, energy: 100, total_queries: 0, completed_levels: [], total_levels: 30 });
  const [activity, setActivity] = useState([]);
  const [matches, setMatches] = useState([]);
  const [showModeSelection, setShowModeSelection] = useState(false);

  // Re-fetch every time dashboard is visited (including back navigation)
  useEffect(() => {
    fetchProgress();
    fetchActivity();
    fetchMatches();
  }, [location.key]);

  const fetchProgress = async () => {
    try {
      const response = await axios.get(`${API}/api/progress/${user.username}`);
      setProgress(response.data);
    } catch (error) {
      console.error('Failed to fetch progress');
    }
  };

  const fetchActivity = async () => {
    try {
      const response = await axios.get(`${API}/api/activity/${user.username}`);
      setActivity(response.data);
    } catch (error) {
      console.error('Failed to fetch activity');
    }
  };

  const fetchMatches = async () => {
    try {
      const res = await axios.get(`${API}/api/matches/${user.username}`);
      setMatches(res.data.matches || []);
    } catch {}
  };

  const getMonthGrid = () => {
    const days_to_show = progress.total_levels || 30;
    const map = {};
    activity.forEach(a => { map[a.date] = a.queries; });

    const days = [];
    for (let i = 0; i < days_to_show; i++) {
      const d = new Date();
      d.setDate(d.getDate() - i);
      const key = d.toISOString().split('T')[0];
      days.push({
        date: key,
        label: d.toLocaleDateString('en-US', { month: 'short', day: 'numeric' }),
        count: map[key] || 0,
        dayIndex: i + 1,
      });
    }
    return days;
  };

  const getColor = (count) => {
    if (count === 0) return '#e5e7eb';
    if (count < 3)  return '#86efac';
    if (count < 6)  return '#4ade80';
    if (count < 10) return '#16a34a';
    return '#14532d';
  };

  return (
    <div className="dashboard-container">
      <nav className="dashboard-nav glass">
        <div className="nav-brand">
          <h2>🗝️ SQL Dungeon</h2>
        </div>
        <div className="nav-user">
          <span>Welcome, {user.username}</span>
          <button className="btn btn-secondary" onClick={onLogout}>
            <LogOut size={16} /> Logout
          </button>
        </div>
      </nav>

      <div className="dashboard-content">
        <div className="stats-grid">
          <motion.div 
            className="stat-card glass"
            whileHover={{ scale: 1.05 }}
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.1 }}
          >
            <div className="stat-icon" style={{ background: '#3b82f6' }}>
              <Target size={24} />
            </div>
            <div className="stat-info">
              <h3>Current Level</h3>
              <p className="stat-value">{progress.level}/{progress.total_levels}</p>
            </div>
          </motion.div>

          <motion.div 
            className="stat-card glass"
            whileHover={{ scale: 1.05 }}
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.2 }}
          >
            <div className="stat-icon" style={{ background: '#10b981' }}>
              <Trophy size={24} />
            </div>
            <div className="stat-info">
              <h3>Total Score</h3>
              <p className="stat-value">{progress.score}</p>
            </div>
          </motion.div>

          <motion.div 
            className="stat-card glass"
            whileHover={{ scale: 1.05 }}
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.3 }}
          >
            <div className="stat-icon" style={{ background: '#f59e0b' }}>
              <Play size={24} />
            </div>
            <div className="stat-info">
              <h3>Levels Completed</h3>
              <p className="stat-value">{progress.completed_levels?.length || 0}/{progress.total_levels}</p>
            </div>
          </motion.div>

          <motion.div 
            className="stat-card glass"
            whileHover={{ scale: 1.05 }}
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.35 }}
          >
            <div className="stat-icon" style={{ background: '#8b5cf6' }}>
              <Zap size={24} />
            </div>
            <div className="stat-info">
              <h3>Queries Solved</h3>
              <p className="stat-value">{progress.total_queries || 0}</p>
            </div>
          </motion.div>
        </div>

        <motion.div 
          className="activity-section"
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.4 }}
        >
          <div className="activity-header">
            <div>
              <h3>{progress.total_queries || 0} queries solved this month</h3>
              <p className="activity-subtitle">Keep building your SQL skills every day</p>
            </div>
          </div>

          <div className="month-grid" style={{ gridTemplateColumns: `repeat(${Math.min(progress.total_levels || 30, 15)}, 1fr)` }}>
            {getMonthGrid().map((day) => (
              <div
                key={day.date}
                className="month-cell"
                style={{ background: getColor(day.count) }}
                title={day.count > 0 ? `${day.count} queries on ${day.label}` : day.label}
              >
                <span className="cell-day">{day.dayIndex}</span>
                {day.count > 0 && <span className="cell-count">{day.count}</span>}
              </div>
            ))}
          </div>

          <div className="month-legend">
            <span>Less</span>
            {['#e5e7eb','#86efac','#4ade80','#16a34a','#14532d'].map(c => (
              <div key={c} className="legend-box" style={{ background: c }} />
            ))}
            <span>More</span>
          </div>
        </motion.div>

        {/* Match History */}
        {matches.length > 0 && (
          <motion.div className="match-history glass"
            initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.45 }}>
            <h3>⚔️ Recent Duo Matches</h3>
            <div className="match-list">
              {matches.map((m) => (
                <div key={m.room_id} className={`match-row ${m.won ? 'win' : 'loss'}`}>
                  <div className="match-result-badge">{m.won ? '🏆 WIN' : '😔 LOSS'}</div>
                  <div className="match-vs">
                    <span className="match-you">{user.username}</span>
                    <span className="match-score">{m.my_score} — {m.opp_score}</span>
                    <span className="match-opp">{m.opponent}</span>
                  </div>
                  <div className="match-meta">
                    Best of {m.total_rounds} · {new Date(m.created_at).toLocaleDateString()}
                  </div>
                </div>
              ))}
            </div>
          </motion.div>
        )}

        <div className="action-grid">          <motion.div 
            className="action-card glass primary-action"
            whileHover={{ scale: 1.05 }}
            onClick={() => setShowModeSelection(true)}
            initial={{ opacity: 0, x: -20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ delay: 0.5 }}
          >
            <Map size={48} className="action-icon" />
            <h3>Enter Dungeon</h3>
            <p>Choose your battle mode</p>
          </motion.div>

          <motion.div 
            className="action-card glass"
            whileHover={{ scale: 1.05 }}
            onClick={() => navigate('/mini-games')}
            initial={{ opacity: 0, x: -20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ delay: 0.7 }}
          >
            <Gamepad2 size={48} className="action-icon" />
            <h3>Mini Games</h3>
            <p>Earn bonus coins</p>
          </motion.div>

          <motion.div 
            className="action-card glass"
            whileHover={{ scale: 1.05 }}
            onClick={() => navigate('/profile')}
            initial={{ opacity: 0, x: -20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ delay: 0.8 }}
          >
            <User size={48} className="action-icon" />
            <h3>Profile</h3>
            <p>View achievements</p>
          </motion.div>
        </div>
      </div>

      <AnimatePresence>
        {showModeSelection && (
          <ModeSelectionEntry onClose={() => setShowModeSelection(false)} />
        )}
      </AnimatePresence>
    </div>
  );
};

export default Dashboard;
