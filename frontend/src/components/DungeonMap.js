import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { motion } from 'framer-motion';
import { Lock, CheckCircle, Play, ArrowLeft } from 'lucide-react';
import axios from 'axios';
import './DungeonMap.css';

const levels = [
  { id: 1, title: '🚪 Gate of SELECT', difficulty: '🟢 Rookie', x: 50, y: 85 },
  { id: 2, title: '⚔️ Joins of Doom', difficulty: '🟢 Rookie', x: 30, y: 70 },
  { id: 3, title: '🌊 Subquery Swamp', difficulty: '🟡 Pro', x: 50, y: 55 },
  { id: 4, title: '📊 Aggregation Tower', difficulty: '🟡 Pro', x: 70, y: 45 },
  { id: 5, title: '🪟 Window Cave', difficulty: '🟡 Pro', x: 40, y: 35 },
  { id: 6, title: '🔍 Index Labyrinth', difficulty: '🔴 Optimizer', x: 60, y: 25 },
  { id: 7, title: '🔄 Recursive Depths', difficulty: '🔴 Optimizer', x: 35, y: 15 },
  { id: 8, title: '🐉 Query Dragon', difficulty: '🔴 Optimizer', x: 50, y: 5 }
];

const DungeonMap = ({ user }) => {
  const navigate = useNavigate();
  const [currentLevel, setCurrentLevel] = useState(1);
  const [hoveredLevel, setHoveredLevel] = useState(null);

  useEffect(() => {
    fetchProgress();
  }, []);

  const fetchProgress = async () => {
    try {
      const response = await axios.get(`http://localhost:8000/api/progress/${user.username}`);
      setCurrentLevel(response.data.level);
    } catch (error) {
      console.error('Failed to fetch progress');
    }
  };

  const getLevelStatus = (levelId) => {
    if (levelId < currentLevel) return 'completed';
    if (levelId === currentLevel) return 'current';
    return 'locked';
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
        <svg className="map-paths" viewBox="0 0 100 100" preserveAspectRatio="none">
          {levels.slice(0, -1).map((level, index) => {
            const nextLevel = levels[index + 1];
            const status = getLevelStatus(level.id);
            return (
              <motion.line
                key={`path-${level.id}`}
                x1={level.x}
                y1={level.y}
                x2={nextLevel.x}
                y2={nextLevel.y}
                stroke={status === 'completed' ? '#10b981' : 'rgba(255,255,255,0.2)'}
                strokeWidth="0.5"
                strokeDasharray={status === 'locked' ? '2,2' : '0'}
                initial={{ pathLength: 0 }}
                animate={{ pathLength: 1 }}
                transition={{ duration: 1, delay: index * 0.2 }}
              />
            );
          })}
        </svg>

        {levels.map((level, index) => {
          const status = getLevelStatus(level.id);
          return (
            <motion.div
              key={level.id}
              className={`map-node ${status}`}
              style={{ left: `${level.x}%`, top: `${level.y}%` }}
              initial={{ scale: 0, opacity: 0 }}
              animate={{ scale: 1, opacity: 1 }}
              transition={{ delay: index * 0.1 }}
              whileHover={{ scale: 1.2 }}
              onMouseEnter={() => setHoveredLevel(level)}
              onMouseLeave={() => setHoveredLevel(null)}
              onClick={() => status !== 'locked' && navigate(`/play/${level.id}`)}
            >
              <div className="node-inner">
                {status === 'completed' && <CheckCircle size={24} />}
                {status === 'current' && <Play size={24} />}
                {status === 'locked' && <Lock size={24} />}
              </div>
              <div className="node-label">{level.id}</div>
            </motion.div>
          );
        })}

        {hoveredLevel && (
          <motion.div
            className="level-tooltip glass"
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            style={{
              left: `${hoveredLevel.x}%`,
              top: `${hoveredLevel.y - 15}%`
            }}
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
            <span className="stat-number">{currentLevel - 1}/8</span>
          </div>
          <div className="journey-stat">
            <span className="stat-label">Current</span>
            <span className="stat-number">Level {currentLevel}</span>
          </div>
          <div className="journey-stat">
            <span className="stat-label">Remaining</span>
            <span className="stat-number">{8 - currentLevel + 1}</span>
          </div>
        </div>
      </div>
    </div>
  );
};

export default DungeonMap;
