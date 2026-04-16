import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { motion } from 'framer-motion';
import { Lock, CheckCircle, Play, ArrowLeft } from 'lucide-react';
import axios from 'axios';
import toast from 'react-hot-toast';
import './DungeonMap.css';

const levels = [
  { id: 1, title: 'SELECT Basics',      difficulty: '🟢 Rookie',    x: 50, y: 88, icon: '🏠' },
  { id: 2, title: 'WHERE Clause',       difficulty: '🟢 Rookie',    x: 30, y: 75, icon: '🔍' },
  { id: 3, title: 'JOIN Tables',        difficulty: '🟢 Rookie',    x: 50, y: 62, icon: '🔗' },
  { id: 4, title: 'GROUP BY',           difficulty: '🟡 Pro',       x: 70, y: 50, icon: '📊' },
  { id: 5, title: 'Subqueries',         difficulty: '🟡 Pro',       x: 50, y: 38, icon: '🌊' },
  { id: 6, title: 'Window Functions',   difficulty: '🔴 Optimizer', x: 30, y: 25, icon: '🪟' },
  { id: 7, title: 'Indexes',            difficulty: '🔴 Optimizer', x: 60, y: 15, icon: '⚡' },
  { id: 8, title: 'Query Master',       difficulty: '🔴 Optimizer', x: 50, y: 5,  icon: '👑' },
];

const DungeonMap = ({ user }) => {
  const navigate = useNavigate();
  const [currentLevel, setCurrentLevel] = useState(1);
  const [completedLevels, setCompletedLevels] = useState([]);
  const [hoveredLevel, setHoveredLevel] = useState(null);

  useEffect(() => {
    fetchProgress();
  }, []);

  const fetchProgress = async () => {
    try {
      const res = await axios.get(`http://localhost:8000/api/progress/${user.username}`);
      setCurrentLevel(res.data.level);
      setCompletedLevels(res.data.completed_levels || []);
    } catch {
      console.error('Failed to fetch progress');
    }
  };

  const getLevelStatus = (id) => {
    if (completedLevels.includes(id)) return 'completed';
    if (id === currentLevel) return 'current';
    if (id < currentLevel) return 'available';
    return 'locked';
  };

  const handleLevelClick = (level) => {
    if (getLevelStatus(level.id) === 'locked') {
      toast.error('Complete previous levels to unlock this one!');
      return;
    }

    const gameMode = sessionStorage.getItem('gameMode');

    if (gameMode === 'solo') {
      navigate(`/play/${level.id}`);
    } else if (gameMode === 'duo') {
      const duoRoomId = sessionStorage.getItem('duoRoomId');
      if (duoRoomId) {
        navigate(`/play/${level.id}?room=${duoRoomId}`);
      } else {
        // Room not created yet — send back to dashboard to pick mode
        toast.error('Please create or join a room first');
        navigate('/dashboard');
      }
    } else {
      // No mode chosen — send to dashboard
      navigate('/dashboard');
    }
  };

  return (
    <div className="dungeon-map-container">
      <div className="map-header">
        <button className="btn btn-secondary" onClick={() => navigate('/dashboard')}>
          <ArrowLeft size={16} /> Back
        </button>
        <h1>🗺️ Dungeon Map</h1>
        <div className="map-legend">
          <span><CheckCircle size={16} /> Completed</span>
          <span><Play size={16} /> Current</span>
          <span><Lock size={16} /> Locked</span>
        </div>
      </div>

      <div className="map-canvas">
        <div className="cloud cloud-1">☁️</div>
        <div className="cloud cloud-2">☁️</div>
        <div className="cloud cloud-3">☁️</div>
        <div className="map-decoration tree-1">🌳</div>
        <div className="map-decoration tree-2">🌲</div>
        <div className="map-decoration tree-3">🌳</div>
        <div className="map-decoration flower-1">🌸</div>
        <div className="map-decoration flower-2">🌺</div>
        <div className="map-decoration cactus-1">🌵</div>
        <div className="map-decoration cactus-2">🌵</div>
        <div className="map-decoration planet-1">🪐</div>
        <div className="map-decoration planet-2">🌙</div>

        <svg className="map-paths" viewBox="0 0 100 100" preserveAspectRatio="none">
          {levels.slice(0, -1).map((level, i) => {
            const next = levels[i + 1];
            const done = getLevelStatus(level.id) === 'completed';
            const nextDone = getLevelStatus(next.id) === 'completed';
            return (
              <motion.line
                key={`path-${level.id}`}
                x1={level.x} y1={level.y}
                x2={next.x}  y2={next.y}
                stroke={done && nextDone ? '#10b981' : done ? '#a855f7' : '#cbd5e1'}
                strokeWidth="1.2"
                strokeLinecap="round"
                strokeDasharray={getLevelStatus(level.id) === 'locked' ? '3,3' : '0'}
                initial={{ pathLength: 0 }}
                animate={{ pathLength: 1 }}
                transition={{ duration: 0.8, delay: i * 0.15 }}
              />
            );
          })}
        </svg>

        {levels.map((level, i) => {
          const status = getLevelStatus(level.id);
          return (
            <motion.div
              key={level.id}
              className={`map-node ${status}`}
              style={{ left: `${level.x}%`, top: `${level.y}%` }}
              initial={{ scale: 0, opacity: 0 }}
              animate={{ scale: 1, opacity: 1 }}
              transition={{ delay: i * 0.1, type: 'spring', stiffness: 200 }}
              onMouseEnter={() => setHoveredLevel(level)}
              onMouseLeave={() => setHoveredLevel(null)}
              onClick={() => handleLevelClick(level)}
            >
              <div className="node-inner">
                <span style={{ fontSize: '32px' }}>{level.icon}</span>
              </div>
              <div className="node-label">{level.title}</div>
            </motion.div>
          );
        })}

        {hoveredLevel && (
          <motion.div
            className="level-tooltip glass"
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            style={{ left: `${hoveredLevel.x}%`, top: `${hoveredLevel.y - 15}%` }}
          >
            <h4>{hoveredLevel.title}</h4>
            <p>{hoveredLevel.difficulty}</p>
          </motion.div>
        )}
      </div>

      <div className="map-info glass">
        <h3>Your Journey</h3>
        <div className="journey-stats">
          <div className="journey-stat">
            <span className="stat-label">Completed</span>
            <span className="stat-number">{completedLevels.length}/8</span>
          </div>
          <div className="journey-stat">
            <span className="stat-label">Current</span>
            <span className="stat-number">Level {currentLevel}</span>
          </div>
          <div className="journey-stat">
            <span className="stat-label">Remaining</span>
            <span className="stat-number">{8 - completedLevels.length}</span>
          </div>
        </div>
      </div>
    </div>
  );
};

export default DungeonMap;
