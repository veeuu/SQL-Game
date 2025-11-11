import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { motion } from 'framer-motion';
import { ArrowLeft, Play, Lightbulb, CheckCircle, XCircle, Zap, Trophy } from 'lucide-react';
import toast from 'react-hot-toast';
import axios from 'axios';
import './GamePlay.css';

const GamePlay = ({ user }) => {
  const { level } = useParams();
  const navigate = useNavigate();
  const [challenge, setChallenge] = useState(null);
  const [query, setQuery] = useState('');
  const [solutionType, setSolutionType] = useState('simple');
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [showHint, setShowHint] = useState(false);
  const [currentHintIndex, setCurrentHintIndex] = useState(0);

  useEffect(() => {
    fetchChallenge();
  }, [level]);

  const fetchChallenge = async () => {
    try {
      const response = await axios.get('http://localhost:8000/api/challenges');
      const challenges = response.data.challenges;
      const currentChallenge = challenges.find(c => c.level === parseInt(level));
      setChallenge(currentChallenge);
    } catch (error) {
      console.error('Failed to fetch challenge:', error);
      toast.error('Failed to load challenge');
    }
  };

  const runQuery = async () => {
    if (!query.trim()) {
      toast.error('Please write a query first');
      return;
    }

    setLoading(true);
    try {
      const token = localStorage.getItem('token');
      const response = await axios.post(
        'http://localhost:8000/api/submit-query',
        {
          query,
          level: parseInt(level),
          solution_type: solutionType
        },
        {
          headers: { 'Authorization': `Bearer ${token}` }
        }
      );

      setResult(response.data);
      if (response.data.success) {
        toast.success(`✅ Query executed! +${response.data.points_earned} points`);
      } else {
        toast.error('Query failed');
      }
    } catch (error) {
      console.error('Query error:', error);
      toast.error(error.response?.data?.error || 'Failed to execute query');
      setResult({ success: false, error: error.response?.data?.error });
    } finally {
      setLoading(false);
    }
  };

  const getHint = () => {
    if (challenge && currentHintIndex < challenge.hints.length) {
      setShowHint(true);
      toast.info(challenge.hints[currentHintIndex]);
      setCurrentHintIndex(currentHintIndex + 1);
    } else {
      toast.info('No more hints available');
    }
  };

  if (!challenge) {
    return (
      <div className="gameplay-container">
        <div className="loading-screen">
          <div className="loader"></div>
        </div>
      </div>
    );
  }

  return (
    <div className="gameplay-container">
      <div className="gameplay-header glass">
        <button className="btn btn-secondary" onClick={() => navigate('/dashboard')}>
          <ArrowLeft size={16} /> Back
        </button>
        <div className="header-info">
          <h1>{challenge.title}</h1>
          <span className="difficulty-badge">{challenge.difficulty}</span>
        </div>
        <div className="header-stats">
          <div className="stat">
            <Trophy size={16} />
            <span>{challenge.points} pts</span>
          </div>
          <div className="stat">
            <Zap size={16} />
            <span>{challenge.coins} coins</span>
          </div>
        </div>
      </div>

      <div className="gameplay-content">
        <div className="challenge-section glass">
          <h2>📖 Challenge</h2>
          <p className="story">{challenge.story}</p>
          <div className="objective">
            <strong>Objective:</strong> {challenge.objective}
          </div>
          <div className="concept">
            <strong>Concept:</strong> {challenge.concept}
          </div>
        </div>

        <div className="solution-type-selector glass">
          <h3>Solution Type</h3>
          <div className="type-buttons">
            <button
              className={`type-btn ${solutionType === 'simple' ? 'active' : ''}`}
              onClick={() => setSolutionType('simple')}
            >
              Simple Solution
            </button>
            <button
              className={`type-btn ${solutionType === 'optimized' ? 'active' : ''}`}
              onClick={() => setSolutionType('optimized')}
            >
              Optimized Solution
              {challenge.difficulty !== 'Beginner' && <span className="required">*Required</span>}
            </button>
          </div>
        </div>

        <div className="editor-section glass">
          <div className="editor-header">
            <h3>✍️ SQL Editor</h3>
            <div className="editor-actions">
              <button className="btn btn-secondary" onClick={getHint}>
                <Lightbulb size={16} /> Hint ({challenge.hints.length - currentHintIndex} left)
              </button>
              <button 
                className="btn btn-primary" 
                onClick={runQuery}
                disabled={loading}
              >
                <Play size={16} /> {loading ? 'Running...' : 'Run Query'}
              </button>
            </div>
          </div>
          <textarea
            className="sql-editor"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder="Write your SQL query here..."
            spellCheck={false}
          />
        </div>

        {result && (
          <motion.div
            className={`result-section glass ${result.success && result.correct ? 'success' : result.success ? 'warning' : 'error'}`}
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
          >
            <div className="result-header">
              {result.success && result.correct ? (
                <>
                  <CheckCircle size={24} />
                  <h3>Perfect! ✨</h3>
                </>
              ) : result.success ? (
                <>
                  <XCircle size={24} />
                  <h3>Incorrect Output</h3>
                </>
              ) : (
                <>
                  <XCircle size={24} />
                  <h3>Error</h3>
                </>
              )}
            </div>
            {result.success ? (
              <div className="result-details">
                <p>Execution Time: {result.execution_time?.toFixed(2)}ms</p>
                {result.correct ? (
                  <>
                    <p className="points-earned">Points Earned: +{result.points_earned} 🏆</p>
                    <p className="coins-earned">Coins Earned: +{result.coins_earned} 💰</p>
                    <p className="success-message">{result.message}</p>
                  </>
                ) : (
                  <>
                    <p className="warning-message">{result.message}</p>
                    <div className="comparison">
                      <div className="result-data">
                        <h4>Your Output:</h4>
                        <pre>{JSON.stringify(result.results, null, 2)}</pre>
                      </div>
                      <div className="result-data">
                        <h4>Expected Output:</h4>
                        <pre>{JSON.stringify(result.expected, null, 2)}</pre>
                      </div>
                    </div>
                  </>
                )}
              </div>
            ) : (
              <div className="error-message">
                <p>{result.error}</p>
                <p className="hint-text">💡 Make sure the table exists and your syntax is correct</p>
              </div>
            )}
          </motion.div>
        )}
      </div>
    </div>
  );
};

export default GamePlay;
