import React, { useState } from 'react';
import { API, WS } from '../config';
import { useNavigate } from 'react-router-dom';
import { motion } from 'framer-motion';
import { Users, Bot, ArrowRight, X, Copy, Check } from 'lucide-react';
import axios from 'axios';
import toast from 'react-hot-toast';
import './ModeSelectionEntry.css';

const ModeSelectionEntry = ({ onClose }) => {
  const navigate = useNavigate();
  const [selectedMode, setSelectedMode] = useState(null);
  const [showDuoOptions, setShowDuoOptions] = useState(false);
  const [roomId, setRoomId] = useState('');
  const [joinRoomId, setJoinRoomId] = useState('');
  const [copied, setCopied] = useState(false);

  const handleModeSelect = (mode) => {
    if (mode === 'solo') {
      sessionStorage.setItem('gameMode', 'solo');
      navigate('/map');
    } else {
      setSelectedMode('duo');
      setShowDuoOptions(true);
    }
  };

  const createRoom = async () => {
    try {
      const token = localStorage.getItem('token');
      if (!token) {
        toast.error('Please login again');
        navigate('/login');
        return;
      }
      
      const response = await axios.post(
        `${API}/api/room/create`,
        { mode: 'duo', level: 1 },
        { headers: { 'Authorization': `Bearer ${token}` } }
      );
      
      setRoomId(response.data.room_id);
      sessionStorage.setItem('gameMode', 'duo');
      toast.success(`Room created! ID: ${response.data.room_id}`);
    } catch (error) {
      console.error('Create room error:', error);
      if (error.response?.status === 401) {
        toast.error('Session expired. Please login again');
        navigate('/login');
      } else {
        toast.error(error.response?.data?.detail || 'Failed to create room');
      }
    }
  };

  const joinRoom = async () => {
    if (!joinRoomId.trim()) {
      toast.error('Please enter a room ID');
      return;
    }
    
    try {
      const token = localStorage.getItem('token');
      if (!token) {
        toast.error('Please login again');
        navigate('/login');
        return;
      }
      
      await axios.post(
        `${API}/api/room/join`,
        { room_id: joinRoomId },
        { headers: { 'Authorization': `Bearer ${token}` } }
      );
      
      const roomResponse = await axios.get(`${API}/api/room/${joinRoomId}`);
      const roomLevel = roomResponse.data.level;
      
      sessionStorage.setItem('gameMode', 'duo');
      toast.success('Joined room!');
      navigate(`/play/${roomLevel}?room=${joinRoomId}`);
    } catch (error) {
      console.error('Join room error:', error);
      if (error.response?.status === 401) {
        toast.error('Session expired. Please login again');
        navigate('/login');
      } else if (error.response?.status === 404) {
        toast.error('Room not found or already started');
      } else {
        toast.error(error.response?.data?.detail || 'Failed to join room');
      }
    }
  };

  const copyRoomId = () => {
    navigator.clipboard.writeText(roomId);
    setCopied(true);
    toast.success('Room ID copied!');
    setTimeout(() => setCopied(false), 2000);
  };

  const enterRoomAndSelectLevel = () => {
    // For duo mode, go directly to gameplay with Gemini-generated challenges
    // Use level 1 as default (Gemini will generate appropriate challenges)
    sessionStorage.setItem('duoRoomId', roomId);
    sessionStorage.setItem('gameMode', 'duo');
    navigate(`/play/1?room=${roomId}`);
  };

  return (
    <motion.div
      className="mode-entry-overlay"
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      exit={{ opacity: 0 }}
    >
      <motion.div
        className="mode-entry-card glass-gaming"
        initial={{ scale: 0.8, opacity: 0 }}
        animate={{ scale: 1, opacity: 1 }}
        exit={{ scale: 0.8, opacity: 0 }}
      >
        <button className="close-btn-gaming" onClick={onClose}>
          <X size={24} />
        </button>

        <div className="mode-entry-header">
          <h1 className="mode-entry-title">⚔️ Enter the SQL Dungeon</h1>
          <p className="mode-entry-subtitle">
            {showDuoOptions ? 'Create or Join a Room' : 'Choose your battle mode'}
          </p>
        </div>

        {!showDuoOptions ? (
          <div className="mode-options-grid">
            <motion.div
              className="mode-card solo-mode"
              whileHover={{ scale: 1.05, y: -10 }}
              whileTap={{ scale: 0.95 }}
              onClick={() => handleModeSelect('solo')}
            >
              <div className="mode-icon-wrapper">
                <Bot size={64} className="mode-icon" />
              </div>
              <h2>Solo Quest</h2>
              <p>Challenge yourself against AI</p>
              <ul className="mode-features">
                <li>🎯 30 Progressive Levels</li>
                <li>🤖 AI-Powered Hints</li>
                <li>⭐ Earn XP & Coins</li>
                <li>📈 Track Your Progress</li>
              </ul>
              <button className="mode-select-btn">
                Start Solo <ArrowRight size={20} />
              </button>
            </motion.div>

            <motion.div
              className="mode-card duo-mode"
              whileHover={{ scale: 1.05, y: -10 }}
              whileTap={{ scale: 0.95 }}
              onClick={() => handleModeSelect('duo')}
            >
              <div className="mode-icon-wrapper">
                <Users size={64} className="mode-icon" />
              </div>
              <h2>Duo Battle</h2>
              <p>Compete with friends in real-time</p>
              <ul className="mode-features">
                <li>⚔️ Best of 3 Rounds</li>
                <li>🏆 2x Points for Winner</li>
                <li>⚡ Real-Time Competition</li>
                <li>🎮 Different Query Each Round</li>
              </ul>
              <button className="mode-select-btn">
                Start Duo <ArrowRight size={20} />
              </button>
            </motion.div>
          </div>
        ) : (
          <div className="duo-room-options">
            {!roomId ? (
              <>
                <button className="btn-large btn-create" onClick={createRoom}>
                  Create New Room
                </button>
                
                <div className="divider-text">OR</div>
                
                <div className="join-room-section">
                  <input
                    type="text"
                    className="room-input"
                    placeholder="Enter Room ID"
                    value={joinRoomId}
                    onChange={(e) => setJoinRoomId(e.target.value)}
                  />
                  <button
                    className="btn-large btn-join"
                    onClick={joinRoom}
                    disabled={!joinRoomId.trim()}
                  >
                    Join Room
                  </button>
                </div>
                
                <button className="btn-back" onClick={() => setShowDuoOptions(false)}>
                  ← Back to Mode Selection
                </button>
              </>
            ) : (
              <div className="room-created">
                <h3>🎉 Room Created!</h3>
                <div className="room-id-box">
                  <code>{roomId}</code>
                  <button className="copy-btn-inline" onClick={copyRoomId}>
                    {copied ? <Check size={20} /> : <Copy size={20} />}
                  </button>
                </div>
                <p>Share this ID with your friend</p>
                <button className="btn-large btn-enter" onClick={enterRoomAndSelectLevel}>
                  Start Battle (AI Challenges)
                </button>
              </div>
            )}
          </div>
        )}

        <div className="mode-entry-footer">
          <p>💡 You can switch modes anytime from the dashboard</p>
        </div>
      </motion.div>
    </motion.div>
  );
};

export default ModeSelectionEntry;
