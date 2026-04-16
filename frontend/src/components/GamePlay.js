import { useState, useEffect, useRef } from 'react';
import { useParams, useNavigate, useSearchParams } from 'react-router-dom';
import { motion, AnimatePresence } from 'framer-motion';
import { ArrowLeft, Play, Lightbulb, CheckCircle, XCircle, Zap, Trophy, ArrowRight, Users, Wifi, WifiOff } from 'lucide-react';
import toast from 'react-hot-toast';
import axios from 'axios';
import { API, WS } from '../config';
import './GamePlay.css';

// ─── Solo Mode ────────────────────────────────────────────────────────────────
const SoloPlay = ({ user, level, navigate }) => {
  const [challenge, setChallenge] = useState(null);
  const [query, setQuery] = useState('');
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [hintIndex, setHintIndex] = useState(0);

  useEffect(() => {
    setResult(null); setQuery(''); setHintIndex(0);
    axios.get(`${API}/api/challenge/${level}`)
      .then(r => setChallenge(r.data))
      .catch(() => toast.error('Failed to load challenge'));
  }, [level]);

  const runQuery = async () => {
    if (!query.trim()) return toast.error('Write a query first');
    setLoading(true);
    try {
      const res = await axios.post(`${API}/api/submit-query`, {
        query, level: parseInt(level),
        challenge_objective: challenge?.objective || '',
        solution_query: challenge?.solution_query || '',
      }, { headers: { Authorization: `Bearer ${localStorage.getItem('token')}` } });

      setResult(res.data);
      if (res.data.correct) toast.success(`✅ Correct! +${res.data.points_earned} pts`);
      else if (res.data.error) toast.error(`SQL Error`);
      else toast.error('Incorrect — try again!');
    } catch (e) {
      toast.error(e.response?.data?.detail || 'Failed');
    } finally { setLoading(false); }
  };

  const showHint = () => {
    if (!challenge?.hints?.length) return;
    if (hintIndex < challenge.hints.length) {
      toast(challenge.hints[hintIndex], { icon: '💡', duration: 6000 });
      setHintIndex(h => h + 1);
    } else toast('No more hints!', { icon: '🤷' });
  };

  if (!challenge) return <div className="gameplay-container"><div className="loading-screen"><div className="loader" /></div></div>;

  return (
    <div className="gameplay-container">
      <div className="gameplay-header glass">
        <button className="btn btn-secondary" onClick={() => navigate('/dashboard')}><ArrowLeft size={16} /> Back</button>
        <div className="header-info">
          <h1>{challenge.title}</h1>
          <span className="difficulty-badge">{challenge.difficulty}</span>
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
          <div className="objective"><strong>🎯 Objective:</strong> {challenge.objective}</div>
        </div>

        <div className="editor-section glass">
          <div className="editor-header">
            <h3>✍️ SQL Editor</h3>
            <div className="editor-actions">
              <button className="btn btn-secondary" onClick={showHint} disabled={(challenge.hints?.length || 0) - hintIndex === 0}>
                <Lightbulb size={16} /> Hint ({(challenge.hints?.length || 0) - hintIndex} left)
              </button>
              <button className="btn btn-primary" onClick={runQuery} disabled={loading}>
                <Play size={16} /> {loading ? 'Running...' : 'Run Query'}
              </button>
            </div>
          </div>
          <textarea className="sql-editor" value={query} onChange={e => setQuery(e.target.value)}
            placeholder="Write your SQL query here..." spellCheck={false} />
        </div>

        {result && (
          <motion.div className={`result-section glass ${result.correct ? 'success' : result.error ? 'error' : 'warning'}`}
            initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }}>
            <div className="result-header">
              {result.correct ? <><CheckCircle size={24} /><h3>Correct! ✨</h3></> : <><XCircle size={24} /><h3>{result.error ? 'SQL Error' : 'Incorrect'}</h3></>}
            </div>
            {result.error ? <p className="error-message">{result.error}</p> : (
              <div className="result-details">
                <p>Execution time: {result.execution_time?.toFixed(2)}ms</p>
                {result.correct && result.points_earned > 0 && <p className="points-earned">+{result.points_earned} points 🏆</p>}
                {result.feedback && <p className="feedback">{result.feedback}</p>}
                {result.correct && result.next_level && (
                  <div className="next-level-wrap">
                    {result.next_level <= (result.total_levels || 30) ? (
                      <button className="btn btn-next-level" onClick={() => { setResult(null); setQuery(''); setHintIndex(0); navigate(`/play/${result.next_level}`); }}>
                        Next Level <ArrowRight size={18} />
                      </button>
                    ) : (
                      <button className="btn btn-next-level" onClick={() => navigate('/map')}>🏆 Challenge Complete!</button>
                    )}
                  </div>
                )}
                {result.results?.length > 0 && (
                  <div className="result-table-wrap">
                    <h4>Query Results:</h4>
                    <table className="result-table">
                      <thead><tr>{result.columns?.map(c => <th key={c}>{c}</th>)}</tr></thead>
                      <tbody>{result.results.slice(0, 20).map((row, i) => <tr key={i}>{row.map((cell, j) => <td key={j}>{String(cell ?? '')}</td>)}</tr>)}</tbody>
                    </table>
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

// ─── Duo Mode ─────────────────────────────────────────────────────────────────
const DuoPlay = ({ user, level, roomId, navigate }) => {
  const [challenge, setChallenge] = useState(null);
  const [query, setQuery] = useState('');
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [hintIndex, setHintIndex] = useState(0);
  const [roomData, setRoomData] = useState(null);
  const [wsConnected, setWsConnected] = useState(false);
  const [opponentTyping, setOpponentTyping] = useState(false);
  const [opponentSubmitted, setOpponentSubmitted] = useState(false);
  const [roundResult, setRoundResult] = useState(null);
  const [matchOver, setMatchOver] = useState(null);
  const [gameStarted, setGameStarted] = useState(false); // both players present
  const ws = useRef(null);
  const typingTimer = useRef(null);

  const myUserId = (() => {
    try { return JSON.parse(atob(localStorage.getItem('token').split('.')[1])).user_id; } catch { return null; }
  })();

  useEffect(() => {
    fetchChallenge();
    fetchRoom();
    connectWS();

    // Poll room status every 2s in case WebSocket message was missed
    const poll = setInterval(() => {
      if (!gameStarted) fetchRoom();
    }, 2000);

    return () => {
      ws.current?.close();
      clearInterval(poll);
    };
  }, [roomId]);

  const fetchChallenge = async () => {
    try {
      const res = await axios.get(`${API}/api/room/${roomId}/challenge`);
      setChallenge(res.data);
    } catch { toast.error('Failed to load challenge'); }
  };

  const fetchRoom = async () => {
    try {
      const res = await axios.get(`${API}/api/room/${roomId}`);
      setRoomData(res.data);
      // Polling fallback: if host already started, transition to game
      if (res.data.status === 'started' || res.data.status === 'completed') {
        setGameStarted(true);
      }
    } catch {}
  };

  const connectWS = () => {
    if (!myUserId) return;
    ws.current = new WebSocket(`${WS}/ws/${roomId}/${myUserId}`);
    ws.current.onopen = () => { setWsConnected(true); toast.success('Connected to room'); };
    ws.current.onclose = () => setWsConnected(false);
    ws.current.onerror = () => setWsConnected(false);
    ws.current.onmessage = (e) => {
      const msg = JSON.parse(e.data);
      if (msg.type === 'player_connected') {
        toast.success('Opponent joined!');
        fetchRoom();
      }
      if (msg.type === 'match_started') {
        toast.success('Match started! ⚔️');
        // fetchChallenge is already called on mount, just show the game
        fetchChallenge();
        setGameStarted(true);
      }
      if (msg.type === 'typing_indicator') setOpponentTyping(msg.is_typing);
      if (msg.type === 'opponent_submitted') { setOpponentSubmitted(true); toast('Opponent submitted!', { icon: '⚡' }); }
      if (msg.type === 'round_won') {
        setRoundResult({ won: msg.winner_id === myUserId, score1: msg.player1_score, score2: msg.player2_score, round: msg.round_number });
        fetchRoom();
      }
      if (msg.type === 'match_over') {
        setMatchOver({ winner_id: msg.winner_id, score1: msg.player1_score, score2: msg.player2_score });
      }
      if (msg.type === 'next_round') {
        setRoundResult(null); setOpponentSubmitted(false);
        setQuery(''); setResult(null); setHintIndex(0);
        fetchChallenge(); fetchRoom();
        toast.success(`Round ${msg.round_number} starting!`);
      }
    };
  };

  const sendTyping = (isTyping) => {
    if (ws.current?.readyState === WebSocket.OPEN)
      ws.current.send(JSON.stringify({ type: 'typing', is_typing: isTyping }));
  };

  const handleQueryChange = (e) => {
    setQuery(e.target.value);
    sendTyping(true);
    clearTimeout(typingTimer.current);
    typingTimer.current = setTimeout(() => sendTyping(false), 1000);
  };

  const runQuery = async () => {
    if (!query.trim()) return toast.error('Write a query first');
    setLoading(true);
    if (ws.current?.readyState === WebSocket.OPEN)
      ws.current.send(JSON.stringify({ type: 'query_submitted' }));
    try {
      const res = await axios.post(`${API}/api/duo/submit`, {
        query, level: parseInt(level), room_id: roomId,
        challenge_objective: challenge?.objective || '',
        solution_query: challenge?.solution_query || '',
      }, { headers: { Authorization: `Bearer ${localStorage.getItem('token')}` } });

      setResult(res.data);
      if (res.data.correct) {
        if (res.data.is_round_winner) toast.success(`🏆 Round won! +${res.data.points_earned} pts`);
        else toast.success(`✅ Correct! +${res.data.points_earned} pts`);
      } else if (res.data.error) toast.error(`SQL Error: ${res.data.error}`);
      else toast.error('Incorrect — try again!');
    } catch (e) {
      toast.error(e.response?.data?.detail || 'Failed');
    } finally { setLoading(false); }
  };

  const nextRound = async () => {
    try {
      await axios.post(`${API}/api/room/${roomId}/next-round`, {},
        { headers: { Authorization: `Bearer ${localStorage.getItem('token')}` } });
    } catch (e) { toast.error('Failed to advance round'); }
  };

  const showHint = () => {
    if (!challenge?.hints?.length) return;
    if (hintIndex < challenge.hints.length) {
      toast(challenge.hints[hintIndex], { icon: '💡', duration: 6000 });
      setHintIndex(h => h + 1);
    } else toast('No more hints!', { icon: '🤷' });
  };

  const opponentName = roomData
    ? (roomData.creator_id === myUserId ? roomData.opponent_name : roomData.creator_name) || 'Waiting...'
    : 'Waiting...';

  const myScore = roomData ? (roomData.creator_id === myUserId ? roomData.player1_score : roomData.player2_score) : 0;
  const oppScore = roomData ? (roomData.creator_id === myUserId ? roomData.player2_score : roomData.player1_score) : 0;
  const isCreator = roomData?.creator_id === myUserId;
  const bothPresent = !!(roomData?.opponent_id);

  if (!challenge) return <div className="gameplay-container"><div className="loading-screen"><div className="loader" /></div></div>;

  return (
    <div className="gameplay-container duo-container">
      {/* Header */}
      <div className="duo-header glass">
        <button className="btn btn-secondary" onClick={() => navigate('/dashboard')}><ArrowLeft size={16} /> Exit</button>
        <div className="duo-title">
          {gameStarted && <><h2>{challenge.title}</h2><span className="difficulty-badge">{challenge.difficulty}</span></>}
          {gameStarted && <span className="round-badge">Round {roomData?.current_round || 1}/{roomData?.total_rounds || 3}</span>}
          {!gameStarted && <h2>⚔️ Duo Battle Lobby</h2>}
        </div>
        {gameStarted && (
          <div className="duo-scoreboard">
            <div className="score-player you">{user.username}<span className="score-num">{myScore}</span></div>
            <div className="score-vs">VS</div>
            <div className="score-player opp">{opponentName}<span className="score-num">{oppScore}</span></div>
          </div>
        )}
        <div className={`ws-status ${wsConnected ? 'on' : 'off'}`}>
          {wsConnected ? <Wifi size={16} /> : <WifiOff size={16} />}
        </div>
      </div>

      {/* LOBBY — shown until both players present and creator starts */}
      {!gameStarted ? (
        <div className="duo-lobby glass">
          <div className="lobby-players">
            <div className="lobby-player ready">
              <div className="lobby-avatar">👤</div>
              <p className="lobby-name">{user.username}</p>
              <span className="ready-badge">✅ Ready</span>
            </div>
            <div className="lobby-vs">⚔️</div>
            <div className={`lobby-player ${bothPresent ? 'ready' : 'waiting'}`}>
              <div className="lobby-avatar">{bothPresent ? '👤' : '⏳'}</div>
              <p className="lobby-name">{bothPresent ? opponentName : 'Waiting...'}</p>
              {bothPresent
                ? <span className="ready-badge">✅ Ready</span>
                : <span className="waiting-badge">Not joined yet</span>}
            </div>
          </div>

          <div className="lobby-room-code">
            <p>Share this Room Code</p>
            <div className="room-code-row">
              <code>{roomId}</code>
              <button className="btn btn-secondary" onClick={() => { navigator.clipboard.writeText(roomId); toast.success('Copied!'); }}>Copy</button>
            </div>
          </div>

          {isCreator && bothPresent && (
            <button className="btn btn-start-match" onClick={() => {
              // Broadcast to opponent that match is starting
              if (ws.current?.readyState === WebSocket.OPEN) {
                ws.current.send(JSON.stringify({ type: 'start_match' }));
              }
              setGameStarted(true);
            }}>
              ⚔️ Start Match!
            </button>
          )}
          {!isCreator && bothPresent && <p className="waiting-host">⏳ Waiting for host to start the match...</p>}
          {!bothPresent && <p className="waiting-host">Share the code above with your opponent</p>}
        </div>
      ) : (
        <>
          {/* Challenge */}
          <div className="challenge-section glass">
            <p className="story">{challenge.story}</p>
            <div className="objective"><strong>🎯 Objective:</strong> {challenge.objective}</div>
          </div>

          {/* Split screen */}
          <div className="duo-split">
            {/* My panel */}
            <div className="duo-panel glass">
              <div className="panel-label you-label"><Users size={16} /> {user.username} (You)</div>
              <textarea className="sql-editor" value={query} onChange={handleQueryChange}
                placeholder="Write your SQL query here..." spellCheck={false}
                disabled={!!roundResult || !!matchOver} />
              <div className="panel-footer">
                <button className="btn btn-secondary" onClick={showHint} disabled={(challenge.hints?.length || 0) - hintIndex === 0}>
                  <Lightbulb size={16} /> Hint ({(challenge.hints?.length || 0) - hintIndex})
                </button>
                <button className="btn btn-primary" onClick={runQuery} disabled={loading || !!roundResult || !!matchOver}>
                  <Play size={16} /> {loading ? 'Running...' : 'Submit'}
                </button>
              </div>
              {result && !result.error && (
                <div className={`inline-result ${result.correct ? 'correct' : 'wrong'}`}>
                  {result.correct ? '✅' : '❌'} {result.feedback}
                </div>
              )}
              {result?.error && <div className="inline-result wrong">⚠️ {result.error}</div>}
            </div>

            {/* Opponent panel */}
            <div className="duo-panel glass opponent-panel">
              <div className="panel-label opp-label"><Users size={16} /> {opponentName}</div>
              <div className="opponent-status-area">
                {opponentSubmitted ? (
                  <div className="opp-submitted"><span>⚡</span><p>Submitted!</p></div>
                ) : opponentTyping ? (
                  <div className="opp-typing">
                    <div className="typing-dots"><span /><span /><span /></div>
                    <p>Typing...</p>
                  </div>
                ) : (
                  <div className="opp-thinking"><p>🤔 Thinking...</p></div>
                )}
              </div>
            </div>
          </div>
        </>
      )}

      {/* Round Result Modal */}
      <AnimatePresence>
        {roundResult && !matchOver && (
          <motion.div className="modal-overlay" initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }}>
            <motion.div className="round-modal glass" initial={{ scale: 0.8 }} animate={{ scale: 1 }}>
              <div className="round-result-icon">{roundResult.won ? '🎯' : '😔'}</div>
              <h2>{roundResult.won ? 'Round Won!' : 'Round Lost'}</h2>
              <div className="round-score">{roundResult.score1} — {roundResult.score2}</div>
              {roomData?.current_round < roomData?.total_rounds && (
                <button className="btn btn-primary" onClick={nextRound}>Next Round →</button>
              )}
            </motion.div>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Match Over Modal */}
      <AnimatePresence>
        {matchOver && (
          <motion.div className="modal-overlay" initial={{ opacity: 0 }} animate={{ opacity: 1 }}>
            <motion.div className="match-modal glass" initial={{ scale: 0.8 }} animate={{ scale: 1 }}>
              <div className="match-icon">{matchOver.winner_id === myUserId ? '🏆' : '😔'}</div>
              <h2>{matchOver.winner_id === myUserId ? 'Victory!' : 'Defeated!'}</h2>
              <p>{matchOver.winner_id === myUserId ? 'You won the match!' : `${opponentName} won`}</p>
              <div className="final-score">{matchOver.score1} — {matchOver.score2}</div>
              <button className="btn btn-primary" onClick={() => navigate('/dashboard')}>Return to Dashboard</button>
            </motion.div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
};

// ─── Router ───────────────────────────────────────────────────────────────────
const GamePlay = ({ user }) => {
  const { level } = useParams();
  const navigate = useNavigate();
  const [searchParams] = useSearchParams();
  const roomId = searchParams.get('room');

  if (roomId) return <DuoPlay user={user} level={level} roomId={roomId} navigate={navigate} />;
  return <SoloPlay user={user} level={level} navigate={navigate} />;
};

export default GamePlay;
