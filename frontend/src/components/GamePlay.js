import React from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { ArrowLeft } from 'lucide-react';
import './GamePlay.css';

const GamePlay = ({ user }) => {
  const { level } = useParams();
  const navigate = useNavigate();

  return (
    <div className="gameplay-container">
      <div className="gameplay-header">
        <button className="btn btn-secondary" onClick={() => navigate('/map')}>
          <ArrowLeft size={16} /> Back to Map
        </button>
        <h1>Level {level}</h1>
      </div>
      <div className="gameplay-content glass">
        <p>Game play interface - Connect to your existing Streamlit app or build React version</p>
      </div>
    </div>
  );
};

export default GamePlay;
