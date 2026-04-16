import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { motion } from 'framer-motion';
import { Lock, CheckCircle, Play, ArrowLeft } from 'lucide-react';
import axios from 'axios';
import toast from 'react-hot-toast';
import './DungeonMap.css';

const levels = [
  // Beginner (1-10)
  { id: 1,  title: 'SELECT Basics',       difficulty: '🟢 Beginner',    x: 50, y: 96, icon: '🏠' },
  { id: 2,  title: 'WHERE Clause',        difficulty: '🟢 Beginner',    x: 30, y: 90, icon: '🔍' },
  { id: 3,  title: 'ORDER BY',            difficulty: '🟢 Beginner',    x: 65, y: 84, icon: '📋' },
  { id: 4,  title: 'LIMIT & OFFSET',      difficulty: '🟢 Beginner',    x: 40, y: 78, icon: '✂️' },
  { id: 5,  title: 'DISTINCT',            difficulty: '🟢 Beginner',    x: 70, y: 72, icon: '🎯' },
  { id: 6,  title: 'AND / OR / NOT',      difficulty: '🟢 Beginner',    x: 25, y: 66, icon: '🔗' },
  { id: 7,  title: 'LIKE & Wildcards',    difficulty: '🟢 Beginner',    x: 55, y: 60, icon: '🃏' },
  { id: 8,  title: 'IN & BETWEEN',        difficulty: '🟢 Beginner',    x: 75, y: 54, icon: '📦' },
  { id: 9,  title: 'NULL Handling',       difficulty: '🟢 Beginner',    x: 35, y: 48, icon: '❓' },
  { id: 10, title: 'Aggregate Functions', difficulty: '🟢 Beginner',    x: 60, y: 42, icon: '🔢' },
  // Intermediate (11-20)
  { id: 11, title: 'GROUP BY',            difficulty: '🟡 Intermediate', x: 20, y: 38, icon: '📊' },
  { id: 12, title: 'HAVING',              difficulty: '🟡 Intermediate', x: 50, y: 34, icon: '🎛️' },
  { id: 13, title: 'INNER JOIN',          difficulty: '🟡 Intermediate', x: 75, y: 30, icon: '🔗' },
  { id: 14, title: 'LEFT & RIGHT JOIN',   difficulty: '🟡 Intermediate', x: 35, y: 26, icon: '↔️' },
  { id: 15, title: 'FULL OUTER JOIN',     difficulty: '🟡 Intermediate', x: 65, y: 22, icon: '🌐' },
  { id: 16, title: 'Subqueries',          difficulty: '🟡 Intermediate', x: 25, y: 18, icon: '🌊' },
  { id: 17, title: 'EXISTS & NOT EXISTS', difficulty: '🟡 Intermediate', x: 55, y: 15, icon: '👁️' },
  { id: 18, title: 'CASE WHEN',           difficulty: '🟡 Intermediate', x: 80, y: 12, icon: '🎭' },
  { id: 19, title: 'String Functions',    difficulty: '🟡 Intermediate', x: 40, y: 9,  icon: '🔤' },
  { id: 20, title: 'Date Functions',      difficulty: '🟡 Intermediate', x: 65, y: 6,  icon: '📅' },
  // Advanced (21-30)
  { id: 21, title: 'CTEs (WITH)',         difficulty: '🔴 Advanced',     x: 20, y: 4,  icon: '🏗️' },
  { id: 22, title: 'Window Functions',    difficulty: '🔴 Advanced',     x: 50, y: 3,  icon: '🪟' },
  { id: 23, title: 'ROW_NUMBER & RANK',   difficulty: '🔴 Advanced',     x: 75, y: 2,  icon: '🏆' },
  { id: 24, title: 'PARTITION BY',        difficulty: '🔴 Advanced',     x: 30, y: 1.5,icon: '🗂️' },
  { id: 25, title: 'Self JOIN',           difficulty: '🔴 Advanced',     x: 60, y: 1,  icon: '🔄' },
  { id: 26, title: 'UNION & INTERSECT',   difficulty: '🔴 Advanced',     x: 15, y: 0.5,icon: '⚡' },
  { id: 27, title: 'Indexes & EXPLAIN',   difficulty: '🔴 Advanced',     x: 45, y: 0.3,icon: '📈' },
  { id: 28, title: 'Transactions',        difficulty: '🔴 Advanced',     x: 70, y: 0.2,icon: '💳' },
  { id: 29, title: 'Recursive CTEs',      difficulty: '🔴 Advanced',     x: 30, y: 0.1,icon: '🌀' },
  { id: 30, title: 'Query Master',        difficulty: '🔴 Advanced',     x: 55, y: 0,  icon: '👑' },
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
            <span className="stat-number">{completedLevels.length}/30</span>
          </div>
          <div className="journey-stat">
            <span className="stat-label">Current</span>
            <span className="stat-number">Level {currentLevel}</span>
          </div>
          <div className="journey-stat">
            <span className="stat-label">Remaining</span>
            <span className="stat-number">{30 - completedLevels.length}</span>
          </div>
        </div>
      </div>
    </div>
  );
};

export default DungeonMap;
