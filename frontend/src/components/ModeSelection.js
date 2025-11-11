import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { motion } from 'framer-motion';
import { Users, Bot, Copy, Check } from 'lucide-react';
import toast from 'react-hot-toast';
import axios from 'axios';
import './ModeSelection.css';

const ModeSelection = ({ user, onClose }) => {
  const navigate = useNavigate();
  const [selectedMode, setSelectedMode] = useState(null);
  const [roomId, setRoomId] = useState('');
  const [joinRoomId, setJoinRoomId] = useState('');
  const [copied, setCopied] = useState(false);

  const createRoom = async (mode) => {
    try {
      const token = localStorage.getItem('token');
      console.log('Token from localStorage:', token ? 'exists' : 'missing');
      
      if (!token) {
        toast.error('Please login again');
        return;
      }
      
      const response = await axios.post(
        'http://localhost:8000/api/room/create',
        { mode, level: 1 },
        { 
          headers: { 
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json'
          } 
        }
      );
      
      console.log('Room created:', response.data);
      setRoomId(response.data.room_id);
      toast.success(`Room created! ID: ${response.data.room_id}`);
      
      if (mode === 'solo') {
        navigate(`/play/${response.data.room_id}`);
      }
    } catch (error) {
      console.error('Create room error:', error);
      console.error('Error response:', error.response);
      toast.error(error.response?.data?.detail || 'Failed to create room');
    }
  };

  const joinRoom = async () => {
    try {
      const token = localStorage.getItem('token');
      await axios.post(
        'http://localhost:8000/api/room/join',
        { room_id: joinRoomId },
        { headers: { Authorization: `Bearer ${token}` } }
      );
      
      toast.success('Joined room!');
      navigate(`/play/${joinRoomId}`);
    } catch (error) {
      console.error('Join room error:', error);
      toast.error(error.response?.data?.detail || 'Failed to join room');
    }
  };

  const copyRoomId = () => {
    navigator.clipboard.writeText(roomId);
    setCopied(true);
    toast.success('Room ID copied!');
    setTimeout(() => setCopied(false), 2000);
  };

  return (
    <div className="mode-selection-overlay">
      <motion.div
        className="mode-selection-card glass"
        initial={{ opacity: 0, scale: 0.9 }}
        animate={{ opacity: 1, scale: 1 }}
      >
        <h2>🎮 Select Game Mode</h2>
        <p className="mode-subtitle">Choose how you want to play</p>

        <div className="mode-options">
          <motion.div
            className={`mode-option ${selectedMode === 'solo' ? 'selected' : ''}`}
            whileHover={{ scale: 1.05 }}
            onClick={() => {
              setSelectedMode('solo');
              createRoom('solo');
            }}
          >
            <Bot size={48} className="mode-icon" />
            <h3>Solo Mode</h3>
            <p>Challenge yourself against AI</p>
            <div className="mode-badge">🤖 vs AI</div>
          </motion.div>

          <motion.div
            className={`mode-option ${selectedMode === 'duo' ? 'selected' : ''}`}
            whileHover={{ scale: 1.05 }}
            onClick={() => setSelectedMode('duo')}
          >
            <Users size={48} className="mode-icon" />
            <h3>Duo Mode</h3>
            <p>Compete with a friend</p>
            <div className="mode-badge">👥 Multiplayer</div>
          </motion.div>
        </div>

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
              onClick={() => navigate(`/play/${roomId}`)}
            >
              Enter Room
            </button>
          </motion.div>
        )}

        <button className="close-btn" onClick={onClose}>
          ✕
        </button>
      </motion.div>
    </div>
  );
};

export default ModeSelection;
