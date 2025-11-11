import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { motion } from 'framer-motion';
import { ArrowLeft, Zap, Trophy, Timer } from 'lucide-react';
import toast from 'react-hot-toast';
import axios from 'axios';
import './MiniGames.css';

const MiniGames = ({ user }) => {
  const navigate = useNavigate();
  const [selectedGame, setSelectedGame] = useState(null);
  const [gameState, setGameState] = useState(null);

  const games = [
    {
      id: 'sql-match',
      title: '🎯 SQL Match',
      description: 'Match SQL keywords with their functions',
      points: 50,
      icon: '🎯'
    },
    {
      id: 'query-race',
      title: '⚡ Query Race',
      description: 'Type SQL queries as fast as you can',
      points: 100,
      icon: '⚡'
    },
    {
      id: 'index-puzzle',
      title: '🧩 Index Puzzle',
      description: 'Solve optimization puzzles',
      points: 150,
      icon: '🧩'
    }
  ];

  const startGame = (game) => {
    setSelectedGame(game);
    if (game.id === 'sql-match') {
      initSQLMatch();
    } else if (game.id === 'query-race') {
      initQueryRace();
    } else if (game.id === 'index-puzzle') {
      initIndexPuzzle();
    }
  };

  const initSQLMatch = () => {
    const pairs = [
      { keyword: 'SELECT', function: 'Retrieve data' },
      { keyword: 'WHERE', function: 'Filter rows' },
      { keyword: 'JOIN', function: 'Combine tables' },
      { keyword: 'GROUP BY', function: 'Aggregate data' },
      { keyword: 'ORDER BY', function: 'Sort results' },
      { keyword: 'HAVING', function: 'Filter groups' }
    ];
    
    const shuffled = [...pairs.map(p => p.keyword), ...pairs.map(p => p.function)]
      .sort(() => Math.random() - 0.5);
    
    setGameState({
      pairs,
      cards: shuffled,
      selected: [],
      matched: [],
      score: 0,
      moves: 0
    });
  };

  const initQueryRace = () => {
    const queries = [
      'SELECT * FROM users',
      'SELECT name, email FROM customers WHERE city = "NYC"',
      'SELECT COUNT(*) FROM orders GROUP BY customer_id',
      'SELECT a.name, b.amount FROM users a JOIN orders b ON a.id = b.user_id'
    ];
    
    setGameState({
      queries,
      currentIndex: 0,
      input: '',
      startTime: Date.now(),
      score: 0
    });
  };

  const initIndexPuzzle = () => {
    const puzzles = [
      {
        question: 'Which column should be indexed for: SELECT * FROM users WHERE email = ?',
        options: ['id', 'email', 'name', 'created_at'],
        correct: 'email'
      },
      {
        question: 'Best index for: SELECT * FROM orders WHERE customer_id = ? AND status = ?',
        options: ['customer_id', 'status', 'customer_id, status', 'id'],
        correct: 'customer_id, status'
      }
    ];
    
    setGameState({
      puzzles,
      currentIndex: 0,
      score: 0
    });
  };

  const handleSQLMatchClick = (card, index) => {
    if (gameState.selected.length === 2 || gameState.matched.includes(card)) return;
    
    const newSelected = [...gameState.selected, { card, index }];
    setGameState({ ...gameState, selected: newSelected });
    
    if (newSelected.length === 2) {
      const [first, second] = newSelected;
      const isMatch = gameState.pairs.some(
        p => (p.keyword === first.card && p.function === second.card) ||
             (p.function === first.card && p.keyword === second.card)
      );
      
      setTimeout(() => {
        if (isMatch) {
          const newMatched = [...gameState.matched, first.card, second.card];
          const newScore = gameState.score + 10;
          setGameState({
            ...gameState,
            matched: newMatched,
            selected: [],
            score: newScore,
            moves: gameState.moves + 1
          });
          
          if (newMatched.length === gameState.cards.length) {
            finishGame(newScore);
          }
        } else {
          setGameState({
            ...gameState,
            selected: [],
            moves: gameState.moves + 1
          });
        }
      }, 500);
    }
  };

  const handleQueryRaceInput = (e) => {
    const input = e.target.value;
    setGameState({ ...gameState, input });
    
    if (input === gameState.queries[gameState.currentIndex]) {
      const newIndex = gameState.currentIndex + 1;
      const newScore = gameState.score + 20;
      
      if (newIndex >= gameState.queries.length) {
        finishGame(newScore);
      } else {
        setGameState({
          ...gameState,
          currentIndex: newIndex,
          input: '',
          score: newScore
        });
        toast.success('Correct! Next query...');
      }
    }
  };

  const handleIndexPuzzleAnswer = (answer) => {
    const puzzle = gameState.puzzles[gameState.currentIndex];
    const isCorrect = answer === puzzle.correct;
    
    if (isCorrect) {
      const newScore = gameState.score + 30;
      const newIndex = gameState.currentIndex + 1;
      
      if (newIndex >= gameState.puzzles.length) {
        finishGame(newScore);
      } else {
        setGameState({
          ...gameState,
          currentIndex: newIndex,
          score: newScore
        });
        toast.success('Correct!');
      }
    } else {
      toast.error('Try again!');
    }
  };

  const finishGame = async (finalScore) => {
    try {
      const response = await axios.post(
        'http://localhost:8000/api/mini-game',
        { game_type: selectedGame.id, score: finalScore },
        { headers: { token: user.token } }
      );
      
      toast.success(`Game complete! Earned ${response.data.points_earned} points!`);
      setTimeout(() => {
        setSelectedGame(null);
        setGameState(null);
      }, 2000);
    } catch (error) {
      toast.error('Failed to save score');
    }
  };

  if (selectedGame && gameState) {
    return (
      <div className="mini-game-play">
        <div className="game-header">
          <button className="btn btn-secondary" onClick={() => setSelectedGame(null)}>
            <ArrowLeft size={16} /> Back
          </button>
          <h2>{selectedGame.title}</h2>
          <div className="game-score">
            <Trophy size={20} />
            <span>{gameState.score}</span>
          </div>
        </div>

        <div className="game-content">
          {selectedGame.id === 'sql-match' && (
            <div className="match-grid">
              {gameState.cards.map((card, index) => (
                <motion.div
                  key={index}
                  className={`match-card ${
                    gameState.matched.includes(card) ? 'matched' : ''
                  } ${
                    gameState.selected.some(s => s.index === index) ? 'selected' : ''
                  }`}
                  onClick={() => handleSQLMatchClick(card, index)}
                  whileHover={{ scale: 1.05 }}
                  whileTap={{ scale: 0.95 }}
                >
                  {card}
                </motion.div>
              ))}
            </div>
          )}

          {selectedGame.id === 'query-race' && (
            <div className="query-race">
              <div className="target-query glass">
                <h3>Type this query:</h3>
                <code>{gameState.queries[gameState.currentIndex]}</code>
              </div>
              <input
                type="text"
                className="input-field race-input"
                value={gameState.input}
                onChange={handleQueryRaceInput}
                placeholder="Start typing..."
                autoFocus
              />
              <div className="race-progress">
                Query {gameState.currentIndex + 1} of {gameState.queries.length}
              </div>
            </div>
          )}

          {selectedGame.id === 'index-puzzle' && (
            <div className="index-puzzle">
              <div className="puzzle-question glass">
                <h3>{gameState.puzzles[gameState.currentIndex].question}</h3>
              </div>
              <div className="puzzle-options">
                {gameState.puzzles[gameState.currentIndex].options.map((option, index) => (
                  <motion.button
                    key={index}
                    className="btn btn-secondary puzzle-option"
                    onClick={() => handleIndexPuzzleAnswer(option)}
                    whileHover={{ scale: 1.05 }}
                    whileTap={{ scale: 0.95 }}
                  >
                    {option}
                  </motion.button>
                ))}
              </div>
            </div>
          )}
        </div>
      </div>
    );
  }

  return (
    <div className="mini-games-container">
      <div className="games-header">
        <button className="btn btn-secondary" onClick={() => navigate('/dashboard')}>
          <ArrowLeft size={16} /> Back
        </button>
        <h1>🎮 Mini Games</h1>
        <p>Earn bonus points and sharpen your SQL skills</p>
      </div>

      <div className="games-grid">
        {games.map((game, index) => (
          <motion.div
            key={game.id}
            className="game-card glass"
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: index * 0.1 }}
            whileHover={{ scale: 1.05 }}
            onClick={() => startGame(game)}
          >
            <div className="game-icon">{game.icon}</div>
            <h3>{game.title}</h3>
            <p>{game.description}</p>
            <div className="game-points">
              <Zap size={16} />
              <span>Up to {game.points} points</span>
            </div>
            <button className="btn btn-primary">Play Now</button>
          </motion.div>
        ))}
      </div>
    </div>
  );
};

export default MiniGames;
