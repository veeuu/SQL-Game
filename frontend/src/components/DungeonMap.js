import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { motion, AnimatePresence } from 'framer-motion';
import { Lock, CheckCircle, Play, ArrowLeft, Users, Bot, Copy, Check } from 'lucide-react';
import axios from 'axios';
import toast from 'react-hot-toast';
import './DungeonMap.css';

const levels = [
  { id: 1, title: 'SELECT Basics', difficulty: '🟢 Rookie', x: 50, y: 88, icon: '🏠' },
  { id: 2, title: 'WHERE Clause', difficulty: '🟢 Rookie', x: 30, y: 75, icon: '🔍' },
  { id: 3, title: 'JOIN Tables', difficulty: '🟢 Rookie', x: 50, y: 62, icon: '🔗' },
  { id: 4, title: 'GROUP BY', difficulty: '🟡 Pro', x: 70, y: 50, icon: '📊' },
  { id: 5, title: 'Subqueries', difficulty: '🟡 Pro', x: 50, y: 38, icon: '🌊' },
  { id: 6, title: 'Window Functions', difficulty: '🔴 Optimizer', x: 30, y: 25, icon: '🪟' },
  { id: 7, title: 'Indexes', difficulty: '🔴 Optimizer', x: 60, y: 15, icon: '⚡' },
  { id: 8, title: 'Query Master', difficulty: '🔴 Optimizer', x: 50, y: 5, icon: '👑' }
];

const DungeonMap = ({ user }) => {
  const navigate = useNavigate();
  const [currentLevel, setCurrentLevel] = useState(1);
  const [completedLevels, setCompletedLevels] = useState([]);
  const [hoveredLevel, setHoveredLevel] = useState(null);
  const [showModeSelection, setShowModeSelection] = useState(false);
  const [selectedLevel, setSelectedLevel] = useState(null);
  const [selectedMode, setSelectedMode] = useState(null);
  const [roomId, setRoomId] = useState('');
  const [joinRoomId, setJoinRoomId] = useState('');
  const [copied, setCopied] = useState(false);

  useEffect(() => {
    fetchProgress();
  }, []);

  const fetchProgress = async () => {
    try {
      const response = await axios.get(`http://localhost:8000/api/progress/${user.username}`);
      setCurrentLevel(response.data.level);
      setCompletedLevels(response.data.completed_levels || []);
    } catch (error) {
      console.error('Failed to fetch progress');
    }
  };

  const getLevelStatus = (levelId) => {
    if (completedLevels.includes(levelId)) return 'completed';
    if (levelId === currentLevel) return 'current';
    if (levelId < currentLevel) return 'available';
    return 'locked';
  };

  const handleLevelClick = (level) => {
    const status = getLevelStatus(level.id);
    if (status === 'locked') {
      toast.error('Complete previous levels to unlock this one!');
      return;
    }
    
    // Check if mode is already selected
    const gameMode = sessionStorage.getItem('gameMode');
    
    if (gameMode === 'solo') {
      // Solo mode: Go directly to gameplay, no mode selection
      navigate(`/play/${level.id}`);
    } else if (gameMode === 'duo') {
      // Duo mode: Check if room already created
      const duoRoomId = sessionStorage.getItem('duoRoomId');
      if (duoRoomId) {
        // Room already created, enter with room ID
        navigate(`/play/${level.id}?room=${duoRoomId}`);
      } else {
        // No room yet, show mode selection (shouldn't happen)
        setSelectedLevel(level);
        setShowModeSelection(true);
      }
    } else {
      // No mode selected, show mode selection
      setSelectedLevel(level);
      setShowModeSelection(true);
    }
  };

  const createRoom = async (mode) => {
    try {
      const token = localStorage.getItem('token');
      const response = await axios.post(
        'http://localhost:8000/api/room/create',
        { mode, level: selectedLevel.id },
        { headers: { 'Authorization': `Bearer ${token}` } }
      );
      
      setRoomId(response.data.room_id);
      setSelectedMode(mode);
      toast.success(`Room created! ID: ${response.data.room_id}`);
      
      if (mode === 'solo') {
        navigate(`/play/${selectedLevel.id}?room=${response.data.room_id}`);
      }
    } catch (error) {
      console.error('Create room error:', error);
      toast.error('Failed to create room');
    }
  };

  const joinRoom = async () => {
    try {
      const token = localStorage.getItem('token');
      await axios.post(
        'http://localhost:8000/api/room/join',
        { room_id: joinRoomId },
        { headers: { 'Authorization': `Bearer ${token}` } }
      );
      
      toast.success('Joined room!');
      navigate(`/play/${selectedLevel.id}?room=${joinRoomId}`);
    } catch (error) {
      toast.error('Failed to join room');
    }
  };

  const copyRoomId = () => {
    navigator.clipboard.writeText(roomId);
    setCopied(true);
    toast.success('Room ID copied!');
    setTimeout(() => setCopied(false), 2000);
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
        {/* Clouds */}
        <div className="cloud cloud-1">☁️</div>
        <div className="cloud cloud-2">☁️</div>
        <div className="cloud cloud-3">☁️</div>
        
        {/* Green zone decorations */}
        <div className="map-decoration tree-1">🌳</div>
        <div className="map-decoration tree-2">🌲</div>
        <div className="map-decoration tree-3">🌳</div>
        <div className="map-decoration flower-1">🌸</div>
        <div className="map-decoration flower-2">🌺</div>
        
        {/* Desert zone decorations */}
        <div className="map-decoration cactus-1">🌵</div>
        <div className="map-decoration cactus-2">🌵</div>
        <div className="map-decoration cactus-3">🌵</div>
        <div className="map-decoration planet-1">🪐</div>
        <div className="map-decoration planet-2">🌙</div>

        <svg className="map-paths" viewBox="0 0 100 100" preserveAspectRatio="none">
          {levels.slice(0, -1).map((level, index) => {
            const nextLevel = levels[index + 1];
            const status = getLevelStatus(level.id);
            const nextStatus = getLevelStatus(nextLevel.id);
            const isPathCompleted = status === 'completed' && nextStatus === 'completed';
            
            return (
              <motion.line
                key={`path-${level.id}`}
                x1={level.x}
                y1={level.y}
                x2={nextLevel.x}
                y2={nextLevel.y}
                stroke={isPathCompleted ? '#10b981' : status === 'completed' ? '#a855f7' : '#cbd5e1'}
                strokeWidth="1.2"
                strokeLinecap="round"
                strokeDasharray={status === 'locked' ? '3,3' : '0'}
                initial={{ pathLength: 0 }}
                animate={{ pathLength: 1 }}
                transition={{ duration: 0.8, delay: index * 0.15 }}
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
              transition={{ delay: index * 0.1, type: 'spring', stiffness: 200 }}
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

      <AnimatePresence>
        {showModeSelection && selectedLevel && (
          <motion.div
            className="mode-selection-overlay"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
          >
            <motion.div
              className="mode-selection-card glass"
              initial={{ opacity: 0, scale: 0.9 }}
              animate={{ opacity: 1, scale: 1 }}
              exit={{ opacity: 0, scale: 0.9 }}
            >
              <button className="close-btn" onClick={() => {
                setShowModeSelection(false);
                setSelectedMode(null);
                setRoomId('');
              }}>
                ✕
              </button>

              <h2>🎮 {selectedLevel.title}</h2>
              <p className="mode-subtitle">Choose your game mode</p>

              {!selectedMode && !roomId && (
                <div className="mode-options">
                  <motion.div
                    className="mode-option"
                    whileHover={{ scale: 1.05 }}
                    onClick={() => createRoom('solo')}
                  >
                    <Bot size={48} className="mode-icon" />
                    <h3>Solo Mode</h3>
                    <p>Challenge yourself against AI</p>
                    <div className="mode-badge">🤖 vs AI</div>
                  </motion.div>

                  <motion.div
                    className="mode-option"
                    whileHover={{ scale: 1.05 }}
                    onClick={() => setSelectedMode('duo')}
                  >
                    <Users size={48} className="mode-icon" />
                    <h3>Duo Mode</h3>
                    <p>Compete with a friend</p>
                    <div className="mode-badge">👥 Multiplayer</div>
                  </motion.div>
                </div>
              )}

              {selectedMode === 'duo' && !roomId && (
                <motion.div
                  className="duo-options"
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                >
                  <button
                    className="btn btn-primary"
                    onClick={() => createRoom('duo')}
                  >
                    Create Room
                  </button>
                  
                  <div className="divider">OR</div>
                  
                  <div className="join-room">
                    <input
                      type="text"
                      className="input-field"
                      placeholder="Enter Room ID"
                      value={joinRoomId}
                      onChange={(e) => setJoinRoomId(e.target.value)}
                    />
                    <button
                      className="btn btn-secondary"
                      onClick={joinRoom}
                      disabled={!joinRoomId}
                    >
                      Join Room
                    </button>
                  </div>
                </motion.div>
              )}

              {roomId && selectedMode === 'duo' && (
                <motion.div
                  className="room-created"
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                >
                  <h3>🎉 Room Created!</h3>
                  <div className="room-id-display">
                    <code>{roomId}</code>
                    <button className="copy-btn" onClick={copyRoomId}>
                      {copied ? <Check size={20} /> : <Copy size={20} />}
                    </button>
                  </div>
                  <p>Share this ID with your friend to join</p>
                  <button
                    className="btn btn-primary"
                    onClick={() => navigate(`/play/${selectedLevel.id}?room=${roomId}`)}
                  >
                    Enter Room
                  </button>
                </motion.div>
              )}
            </motion.div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
};

export default DungeonMap;
