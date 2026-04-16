import { useState, useEffect, useRef } from 'react';
import { useNavigate } from 'react-router-dom';
import { motion, AnimatePresence } from 'framer-motion';
import { ArrowLeft, Trophy, Zap, Timer, RotateCcw } from 'lucide-react';
import toast from 'react-hot-toast';
import axios from 'axios';
import { API } from '../config';
import './MiniGames.css';

// ─── Game 1: SQL Flashcards (Memory Match) ───────────────────────────────────
const MATCH_PAIRS = [
  { a: 'SELECT', b: 'Retrieve columns' },
  { a: 'WHERE', b: 'Filter rows' },
  { a: 'JOIN', b: 'Combine tables' },
  { a: 'GROUP BY', b: 'Aggregate rows' },
  { a: 'ORDER BY', b: 'Sort results' },
  { a: 'HAVING', b: 'Filter groups' },
  { a: 'DISTINCT', b: 'Remove duplicates' },
  { a: 'LIMIT', b: 'Cap row count' },
];

const SQLMatch = ({ onFinish }) => {
  const buildCards = () => {
    const pool = MATCH_PAIRS.slice(0, 6);
    return [...pool.map((p, i) => ({ id: i * 2, text: p.a, pairId: i })),
            ...pool.map((p, i) => ({ id: i * 2 + 1, text: p.b, pairId: i }))]
      .sort(() => Math.random() - 0.5);
  };

  const [cards, setCards] = useState(buildCards);
  const [flipped, setFlipped] = useState([]);
  const [matched, setMatched] = useState([]);
  const [moves, setMoves] = useState(0);
  const [done, setDone] = useState(false);

  const handleFlip = (card) => {
    if (flipped.length === 2 || flipped.find(c => c.id === card.id) || matched.includes(card.pairId)) return;
    const next = [...flipped, card];
    setFlipped(next);
    if (next.length === 2) {
      setMoves(m => m + 1);
      if (next[0].pairId === next[1].pairId) {
        const newMatched = [...matched, card.pairId];
        setMatched(newMatched);
        setFlipped([]);
        if (newMatched.length === 6) {
          setDone(true);
          const score = Math.max(6, 20 - moves);
          setTimeout(() => onFinish(score, 'sql-match'), 800);
        }
      } else {
        setTimeout(() => setFlipped([]), 900);
      }
    }
  };

  return (
    <div className="mg-game">
      <div className="mg-game-info">
        <span>🃏 Match SQL keywords with their meanings</span>
        <span className="mg-moves">Moves: {moves}</span>
        <span className="mg-progress">{matched.length}/6 matched</span>
      </div>
      <div className="mg-match-grid">
        {cards.map(card => {
          const isFlipped = flipped.find(c => c.id === card.id) || matched.includes(card.pairId);
          return (
            <motion.div
              key={card.id}
              className={`mg-flip-card ${isFlipped ? 'flipped' : ''} ${matched.includes(card.pairId) ? 'matched' : ''}`}
              onClick={() => handleFlip(card)}
              whileHover={!isFlipped ? { scale: 1.05 } : {}}
              whileTap={{ scale: 0.95 }}
            >
              {isFlipped ? card.text : '?'}
            </motion.div>
          );
        })}
      </div>
    </div>
  );
};

// ─── Game 2: SQL Trivia ───────────────────────────────────────────────────────
const TRIVIA = [
  { q: 'Which clause filters rows AFTER grouping?', opts: ['WHERE', 'HAVING', 'FILTER', 'LIMIT'], ans: 'HAVING' },
  { q: 'What does COUNT(*) return?', opts: ['Sum of values', 'Number of rows', 'Max value', 'Average'], ans: 'Number of rows' },
  { q: 'Which JOIN returns all rows from both tables?', opts: ['INNER JOIN', 'LEFT JOIN', 'FULL OUTER JOIN', 'CROSS JOIN'], ans: 'FULL OUTER JOIN' },
  { q: 'What does DISTINCT do?', opts: ['Sorts results', 'Removes duplicates', 'Filters nulls', 'Limits rows'], ans: 'Removes duplicates' },
  { q: 'Which keyword is used for pattern matching?', opts: ['MATCH', 'LIKE', 'SIMILAR', 'REGEX'], ans: 'LIKE' },
  { q: 'What does NULL represent in SQL?', opts: ['Zero', 'Empty string', 'Unknown/missing value', 'False'], ans: 'Unknown/missing value' },
  { q: 'Which function returns the highest value?', opts: ['TOP()', 'HIGHEST()', 'MAX()', 'UPPER()'], ans: 'MAX()' },
  { q: 'What does ORDER BY DESC do?', opts: ['Ascending sort', 'Descending sort', 'Random sort', 'Group sort'], ans: 'Descending sort' },
];

const SQLTrivia = ({ onFinish }) => {
  const [questions] = useState(() => [...TRIVIA].sort(() => Math.random() - 0.5).slice(0, 6));
  const [idx, setIdx] = useState(0);
  const [score, setScore] = useState(0);
  const [selected, setSelected] = useState(null);
  const [timeLeft, setTimeLeft] = useState(15);
  const timerRef = useRef(null);

  useEffect(() => {
    timerRef.current = setInterval(() => {
      setTimeLeft(t => {
        if (t <= 1) {
          clearInterval(timerRef.current);
          advance(false);
          return 15;
        }
        return t - 1;
      });
    }, 1000);
    return () => clearInterval(timerRef.current);
  }, [idx]);

  const advance = (correct) => {
    clearInterval(timerRef.current);
    const newScore = correct ? score + 10 : score;
    if (idx + 1 >= questions.length) {
      setTimeout(() => onFinish(newScore, 'sql-trivia'), 700);
    } else {
      setTimeout(() => { setIdx(i => i + 1); setSelected(null); setTimeLeft(15); }, 700);
    }
    if (correct) setScore(newScore);
  };

  const pick = (opt) => {
    if (selected) return;
    setSelected(opt);
    advance(opt === questions[idx].ans);
  };

  const q = questions[idx];
  const pct = (timeLeft / 15) * 100;

  return (
    <div className="mg-game">
      <div className="mg-game-info">
        <span>❓ Question {idx + 1}/{questions.length}</span>
        <span className="mg-score-live">Score: {score}</span>
        <span className={`mg-timer ${timeLeft <= 5 ? 'urgent' : ''}`}><Timer size={14} /> {timeLeft}s</span>
      </div>
      <div className="mg-timer-bar"><div className="mg-timer-fill" style={{ width: `${pct}%`, background: timeLeft <= 5 ? '#ef4444' : '#10b981' }} /></div>
      <div className="mg-question glass">{q.q}</div>
      <div className="mg-options">
        {q.opts.map(opt => (
          <motion.button
            key={opt}
            className={`mg-option ${selected === opt ? (opt === q.ans ? 'correct' : 'wrong') : ''} ${selected && opt === q.ans ? 'correct' : ''}`}
            onClick={() => pick(opt)}
            whileHover={!selected ? { scale: 1.03 } : {}}
            disabled={!!selected}
          >
            {opt}
          </motion.button>
        ))}
      </div>
    </div>
  );
};

// ─── Game 3: Query Builder ────────────────────────────────────────────────────
const CHALLENGES = [
  { desc: 'Select all columns from users', words: ['SELECT', '*', 'FROM', 'users', 'WHERE', 'ORDER'], answer: ['SELECT', '*', 'FROM', 'users'] },
  { desc: 'Count all rows in orders', words: ['SELECT', 'COUNT(*)', 'FROM', 'orders', 'WHERE', 'GROUP'], answer: ['SELECT', 'COUNT(*)', 'FROM', 'orders'] },
  { desc: 'Get users where age > 25', words: ['SELECT', '*', 'FROM', 'users', 'WHERE', 'age', '>', '25', 'LIMIT'], answer: ['SELECT', '*', 'FROM', 'users', 'WHERE', 'age', '>', '25'] },
];

const QueryBuilder = ({ onFinish }) => {
  const [idx, setIdx] = useState(0);
  const [built, setBuilt] = useState([]);
  const [score, setScore] = useState(0);
  const [feedback, setFeedback] = useState(null);
  const [shuffled, setShuffled] = useState(() => [...CHALLENGES[0].words].sort(() => Math.random() - 0.5));

  const ch = CHALLENGES[idx];

  const addWord = (word) => {
    if (built.includes(word)) return;
    setBuilt([...built, word]);
  };

  const removeWord = (i) => {
    setBuilt(built.filter((_, j) => j !== i));
  };

  const check = () => {
    const correct = JSON.stringify(built) === JSON.stringify(ch.answer);
    setFeedback(correct ? 'correct' : 'wrong');
    if (correct) {
      const newScore = score + 15;
      setScore(newScore);
      if (idx + 1 >= CHALLENGES.length) {
        setTimeout(() => onFinish(newScore, 'query-builder'), 800);
      } else {
        setTimeout(() => {
          setIdx(i => i + 1);
          setBuilt([]);
          setFeedback(null);
          setShuffled([...CHALLENGES[idx + 1].words].sort(() => Math.random() - 0.5));
        }, 800);
      }
    } else {
      setTimeout(() => setFeedback(null), 800);
    }
  };

  return (
    <div className="mg-game">
      <div className="mg-game-info">
        <span>🔨 Challenge {idx + 1}/{CHALLENGES.length}</span>
        <span className="mg-score-live">Score: {score}</span>
      </div>
      <div className="mg-question glass">{ch.desc}</div>

      <div className={`mg-builder-zone ${feedback || ''}`}>
        {built.length === 0 ? <span className="mg-placeholder">Click words below to build your query</span>
          : built.map((w, i) => (
            <motion.span key={i} className="mg-built-word" onClick={() => removeWord(i)}
              initial={{ scale: 0 }} animate={{ scale: 1 }}>
              {w} ✕
            </motion.span>
          ))}
      </div>

      <div className="mg-word-bank">
        {shuffled.map(w => (
          <motion.button
            key={w}
            className={`mg-word ${built.includes(w) ? 'used' : ''}`}
            onClick={() => addWord(w)}
            disabled={built.includes(w)}
            whileHover={{ scale: 1.05 }}
          >
            {w}
          </motion.button>
        ))}
      </div>

      <div className="mg-builder-actions">
        <button className="btn btn-secondary" onClick={() => setBuilt([])}><RotateCcw size={16} /> Clear</button>
        <button className="btn btn-primary" onClick={check} disabled={built.length === 0}>Check Query</button>
      </div>
    </div>
  );
};

// ─── Main MiniGames Component ─────────────────────────────────────────────────
const GAMES = [
  { id: 'sql-match',      title: '🃏 Memory Match',   desc: 'Match SQL keywords with their meanings', points: 60,  color: '#10b981' },
  { id: 'sql-trivia',     title: '❓ SQL Trivia',      desc: 'Answer SQL questions against the clock', points: 100, color: '#8b5cf6' },
  { id: 'query-builder',  title: '🔨 Query Builder',  desc: 'Drag words to build correct SQL queries', points: 45,  color: '#f59e0b' },
];

const MiniGames = ({ user }) => {
  const navigate = useNavigate();
  const [active, setActive] = useState(null);

  const handleFinish = async (score, gameId) => {
    try {
      const res = await axios.post(`${API}/api/mini-game`,
        { game_type: gameId, score },
        { headers: { Authorization: `Bearer ${localStorage.getItem('token')}` } }
      );
      toast.success(`🎉 Game over! +${res.data.points_earned} points`);
    } catch {
      toast.error('Failed to save score');
    }
    setTimeout(() => setActive(null), 1500);
  };

  if (active) {
    const game = GAMES.find(g => g.id === active);
    return (
      <div className="mg-container">
        <div className="mg-header glass">
          <button className="btn btn-secondary" onClick={() => setActive(null)}><ArrowLeft size={16} /> Back</button>
          <h2>{game.title}</h2>
        </div>
        {active === 'sql-match'     && <SQLMatch     onFinish={handleFinish} />}
        {active === 'sql-trivia'    && <SQLTrivia    onFinish={handleFinish} />}
        {active === 'query-builder' && <QueryBuilder onFinish={handleFinish} />}
      </div>
    );
  }

  return (
    <div className="mg-container">
      <div className="mg-header glass">
        <button className="btn btn-secondary" onClick={() => navigate('/dashboard')}><ArrowLeft size={16} /> Back</button>
        <h1>🎮 Mini Games</h1>
        <p>Sharpen your SQL skills and earn bonus points</p>
      </div>

      <div className="mg-grid">
        {GAMES.map((g, i) => (
          <motion.div
            key={g.id}
            className="mg-game-card"
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: i * 0.1 }}
            whileHover={{ y: -6, boxShadow: `0 16px 40px ${g.color}33` }}
            onClick={() => setActive(g.id)}
          >
            <div className="mg-game-card-icon" style={{ background: `${g.color}22`, color: g.color }}>
              {g.title.split(' ')[0]}
            </div>
            <h3>{g.title.slice(2)}</h3>
            <p>{g.desc}</p>
            <div className="mg-card-footer">
              <span className="mg-pts" style={{ color: g.color }}><Zap size={14} /> Up to {g.points} pts</span>
              <button className="btn-play" style={{ background: g.color }}>Play</button>
            </div>
          </motion.div>
        ))}
      </div>
    </div>
  );
};

export default MiniGames;
