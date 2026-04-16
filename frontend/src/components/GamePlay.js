import { useState, useEffect } from 'react';
import { useParams, useNavigate, useSearchParams } from 'react-router-dom';
import { motion } from 'framer-motion';
import { ArrowLeft, Play, Lightbulb, CheckCircle, XCircle, Zap, Trophy, ArrowRight } from 'lucide-react';
import toast from 'react-hot-toast';
import axios from 'axios';
import './GamePlay.css';

const API = 'http://localhost:8000';

const GamePlay = ({ user }) => {
  const { level } = useParams();
  const navigate = useNavigate();
  const [searchParams] = useSearchParams();
  const roomId = searchParams.get('room');

  const [challenge, setChallenge] = useState(null);
  const [query, setQuery] = useState('');
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [hintIndex, setHintIndex] = useState(0);

  useEffect(() => {
    setResult(null);
    setQuery('');
    setHintIndex(0);
    fetchChallenge();
  }, [level, roomId]);

  const fetchChallenge = async () => {
    try {
      const url = roomId
        ? `${API}/api/room/${roomId}/challenge`
        : `${API}/api/challenge/${level}`;
      const res = await axios.get(url);
      setChallenge(res.data);
    } catch (err) {
      console.error('Failed to fetch challenge:', err);
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
      const endpoint = roomId ? `${API}/api/duo/submit` : `${API}/api/submit-query`;

      const res = await axios.post(
        endpoint,
        {
          query,
          level: parseInt(level),
          solution_type: 'simple',
          room_id: roomId || undefined,
          challenge_objective: challenge?.objective || '',
          solution_query: challenge?.solution_query || '',
        },
        { headers: { Authorization: `Bearer ${token}` } }
      );

      setResult(res.data);

      if (res.data.correct) {
        const pts = res.data.points_earned || 0;
        if (roomId && res.data.is_round_winner) {
          toast.success(`🏆 Round won! +${pts} points`);
        } else if (pts > 0) {
          toast.success(`✅ Correct! +${pts} points`);
        } else {
          toast.success('✅ Correct!');
        }
      } else if (res.data.error) {
        toast.error(`SQL Error: ${res.data.error}`);
      } else {
        toast.error('Incorrect — try again!');
      }
    } catch (err) {
      const msg = err.response?.data?.detail || 'Failed to execute query';
      toast.error(msg);
      setResult({ error: msg });
    } finally {
      setLoading(false);
    }
  };

  const showHint = () => {
    if (!challenge?.hints?.length) return;
    if (hintIndex < challenge.hints.length) {
      toast(challenge.hints[hintIndex], { icon: '💡', duration: 6000 });
      setHintIndex(hintIndex + 1);
    } else {
      toast('No more hints!', { icon: '🤷' });
    }
  };

  if (!challenge) {
    return (
      <div className="gameplay-container">
        <div className="loading-screen"><div className="loader" /></div>
      </div>
    );
  }

  const hintsLeft = (challenge.hints?.length || 0) - hintIndex;

  return (
    <div className="gameplay-container">
      <div className="gameplay-header glass">
        <button className="btn btn-secondary" onClick={() => navigate('/dashboard')}>
          <ArrowLeft size={16} /> Back
        </button>
        <div className="header-info">
          <h1>{challenge.title}</h1>
          <span className="difficulty-badge">{challenge.difficulty}</span>
          {roomId && <span className="duo-badge">⚔️ Duo — Round {challenge.round}</span>}
        </div>
        <div className="header-stats">
          <div className="stat"><Trophy size={16} /><span>{challenge.points} pts</span></div>
          <div className="stat"><Zap size={16} /><span>{challenge.concept}</span></div>
        </div>
      </div>

      <div className="gameplay-content">
        <div className="challenge-section glass">
          <h2>📖 Challenge</h2>
          <p className="story">{challenge.story}</p>
          <div className="objective">
            <strong>🎯 Objective:</strong> {challenge.objective}
          </div>
        </div>

        <div className="editor-section glass">
          <div className="editor-header">
            <h3>✍️ SQL Editor</h3>
            <div className="editor-actions">
              <button className="btn btn-secondary" onClick={showHint} disabled={hintsLeft === 0}>
                <Lightbulb size={16} /> Hint ({hintsLeft} left)
              </button>
              <button className="btn btn-primary" onClick={runQuery} disabled={loading}>
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
            className={`result-section glass ${result.correct ? 'success' : result.error ? 'error' : 'warning'}`}
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
          >
            <div className="result-header">
              {result.correct
                ? <><CheckCircle size={24} /><h3>Correct! ✨</h3></>
                : <><XCircle size={24} /><h3>{result.error ? 'SQL Error' : 'Incorrect'}</h3></>
              }
            </div>

            {result.error ? (
              <p className="error-message">{result.error}</p>
            ) : (
              <div className="result-details">
                <p>Execution time: {result.execution_time?.toFixed(2)}ms</p>
                {result.correct && result.points_earned > 0 && (
                  <p className="points-earned">+{result.points_earned} points 🏆</p>
                )}
                {result.feedback && <p className="feedback">{result.feedback}</p>}

                {/* Next Level button */}
                {result.correct && result.next_level && !roomId && (
                  <div className="next-level-wrap">
                    {result.next_level <= 8 ? (
                      <button
                        className="btn btn-next-level"
                        onClick={() => {
                          setResult(null);
                          setQuery('');
                          setHintIndex(0);
                          navigate(`/play/${result.next_level}`);
                        }}
                      >
                        Next Level <ArrowRight size={18} />
                      </button>
                    ) : (
                      <button className="btn btn-next-level" onClick={() => navigate('/map')}>
                        🏆 All Levels Complete! Return to Map
                      </button>
                    )}
                  </div>
                )}

                {result.results?.length > 0 && (
                  <div className="result-table-wrap">
                    <h4>Query Results:</h4>
                    <table className="result-table">
                      <thead>
                        <tr>
                          {result.columns?.map((col) => <th key={col}>{col}</th>)}
                        </tr>
                      </thead>
                      <tbody>
                        {result.results.slice(0, 20).map((row, i) => (
                          <tr key={i}>
                            {row.map((cell, j) => <td key={j}>{String(cell ?? '')}</td>)}
                          </tr>
                        ))}
                      </tbody>
                    </table>
                    {result.results.length > 20 && (
                      <p className="truncated">Showing 20 of {result.results.length} rows</p>
                    )}
                  </div>
                )}
              </div>
            )}
          </motion.div>
        )}
      </div>
    </div>
  );
};

export default GamePlay;
