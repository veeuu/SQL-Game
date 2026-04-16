import { useState, useEffect, useRef } from 'react';
import { useNavigate } from 'react-router-dom';
import { motion } from 'framer-motion';
import { Lock, CheckCircle, ArrowLeft } from 'lucide-react';
import axios from 'axios';
import toast from 'react-hot-toast';
import './DungeonMap.css';

const LEVEL_TITLES = [
  'SELECT Basics', 'WHERE Clause', 'ORDER BY', 'LIMIT & OFFSET', 'DISTINCT',
  'AND / OR / NOT', 'LIKE & Wildcards', 'IN & BETWEEN', 'NULL Handling', 'Aggregate Functions',
  'GROUP BY', 'HAVING', 'INNER JOIN', 'LEFT & RIGHT JOIN', 'FULL OUTER JOIN',
  'Subqueries', 'EXISTS & NOT EXISTS', 'CASE WHEN', 'String Functions', 'Date Functions',
  'CTEs (WITH)', 'Window Functions', 'ROW_NUMBER & RANK', 'PARTITION BY', 'Self JOIN',
  'UNION & INTERSECT', 'Indexes & EXPLAIN', 'Transactions', 'Recursive CTEs', 'Query Master',
];

const LEVEL_ICONS = [
  '🏠','🔍','📋','✂️','🎯','🔗','🃏','📦','❓','🔢',
  '📊','🎛️','🔗','↔️','🌐','🌊','👁️','🎭','🔤','📅',
  '🏗️','🪟','🏆','🗂️','🔄','⚡','📈','💳','🌀','👑',
];

const ZONE_COLORS = [
  { bg: '#d1fae5', node: '#10b981', label: '🟢 Beginner',     range: [1, 10] },
  { bg: '#fef3c7', node: '#f59e0b', label: '🟡 Intermediate', range: [11, 20] },
  { bg: '#ede9fe', node: '#8b5cf6', label: '🔴 Advanced',     range: [21, 30] },
];

const getZone = (id) => {
  if (id <= 10) return ZONE_COLORS[0];
  if (id <= 20) return ZONE_COLORS[1];
  return ZONE_COLORS[2];
};

// Build a snake/winding path: 5 per row, alternating left→right, right→left
const buildPath = (total) => {
  const COLS = 5;
  const nodes = [];
  for (let i = 0; i < total; i++) {
    const row = Math.floor(i / COLS);
    const col = i % COLS;
    const isEven = row % 2 === 0;
    const x = isEven ? col : (COLS - 1 - col);
    nodes.push({ id: i + 1, row, col: x });
  }
  return nodes;
};

const DungeonMap = ({ user }) => {
  const navigate = useNavigate();
  const [currentLevel, setCurrentLevel] = useState(1);
  const [completedLevels, setCompletedLevels] = useState([]);
  const [totalLevels, setTotalLevels] = useState(user.total_levels || 30);
  const [hoveredId, setHoveredId] = useState(null);
  const [containerWidth, setContainerWidth] = useState(window.innerWidth - 48);
  const scrollRef = useRef(null);

  useEffect(() => {
    fetchProgress();
    const handleResize = () => {
      if (scrollRef.current) {
        setContainerWidth(scrollRef.current.clientWidth);
      }
    };
    window.addEventListener('resize', handleResize);
    setTimeout(handleResize, 100);
    return () => window.removeEventListener('resize', handleResize);
  }, []);

  const fetchProgress = async () => {
    try {
      const res = await axios.get(`http://localhost:8000/api/progress/${user.username}`);
      setCurrentLevel(res.data.level);
      setCompletedLevels(res.data.completed_levels || []);
      if (res.data.total_levels) setTotalLevels(res.data.total_levels);
    } catch {
      console.error('Failed to fetch progress');
    }
  };

  const getStatus = (id) => {
    if (completedLevels.includes(id)) return 'completed';
    if (id === currentLevel) return 'current';
    if (id < currentLevel) return 'available';
    return 'locked';
  };

  const handleClick = (id) => {
    const status = getStatus(id);
    if (status === 'locked') {
      toast.error('Complete previous levels first!');
      return;
    }
    const gameMode = sessionStorage.getItem('gameMode');
    if (gameMode === 'solo') {
      navigate(`/play/${id}`);
    } else if (gameMode === 'duo') {
      const roomId = sessionStorage.getItem('duoRoomId');
      if (roomId) navigate(`/play/${id}?room=${roomId}`);
      else { toast.error('Create a room first'); navigate('/dashboard'); }
    } else {
      navigate('/dashboard');
    }
  };

  const nodes = buildPath(totalLevels);
  const COLS = 5;
  const rows = Math.ceil(totalLevels / COLS);
  const NODE_SIZE = 72;
  const PADDING = 60;
  // Fill full container width
  const svgW = Math.max(containerWidth, 600);
  const COL_GAP = (svgW - PADDING * 2) / COLS;
  const ROW_GAP = 170;
  const svgH = rows * ROW_GAP + PADDING * 2;

  const nodePos = (n) => ({
    cx: PADDING + n.col * COL_GAP + COL_GAP / 2,
    cy: PADDING + n.row * ROW_GAP + ROW_GAP / 2,
  });

  return (
    <div className="dmap-container">
      {/* Header */}
      <div className="dmap-header glass">
        <button className="btn btn-secondary" onClick={() => navigate('/dashboard')}>
          <ArrowLeft size={16} /> Back
        </button>
        <h1>🗺️ Dungeon Map</h1>
        <div className="dmap-legend">
          {ZONE_COLORS.map(z => (
            <span key={z.label} style={{ color: z.node }}>● {z.label}</span>
          ))}
        </div>
      </div>

      {/* Scrollable map */}
      <div className="dmap-scroll" ref={scrollRef}>
        <svg
          width={svgW}
          height={svgH}
          className="dmap-svg"
          style={{ width: '100%', minHeight: svgH }}
        >
          {/* Zone background bands */}
          {ZONE_COLORS.map((zone) => {
            const startRow = Math.floor((zone.range[0] - 1) / COLS);
            const endRow   = Math.floor((zone.range[1] - 1) / COLS);
            return (
              <rect
                key={zone.label}
                x={0}
                y={PADDING + startRow * ROW_GAP - ROW_GAP * 0.3}
                width={svgW}
                height={(endRow - startRow + 1) * ROW_GAP + ROW_GAP * 0.3}
                fill={zone.bg}
                opacity={0.5}
                rx={16}
              />
            );
          })}

          {/* Path lines */}
          {nodes.slice(0, -1).map((n, i) => {
            const next = nodes[i + 1];
            const p1 = nodePos(n);
            const p2 = nodePos(next);
            const status = getStatus(n.id);
            const done = status === 'completed';
            return (
              <motion.line
                key={`line-${n.id}`}
                x1={p1.cx} y1={p1.cy}
                x2={p2.cx} y2={p2.cy}
                stroke={done ? getZone(n.id).node : '#d1d5db'}
                strokeWidth={done ? 5 : 3}
                strokeLinecap="round"
                strokeDasharray={status === 'locked' ? '8,6' : 'none'}
                initial={{ pathLength: 0, opacity: 0 }}
                animate={{ pathLength: 1, opacity: 1 }}
                transition={{ duration: 0.4, delay: i * 0.03 }}
              />
            );
          })}

          {/* Nodes */}
          {nodes.map((n, i) => {
            const { cx, cy } = nodePos(n);
            const status = getStatus(n.id);
            const zone = getZone(n.id);
            const isHovered = hoveredId === n.id;
            const title = LEVEL_TITLES[(n.id - 1) % LEVEL_TITLES.length];
            const icon  = LEVEL_ICONS[(n.id - 1) % LEVEL_ICONS.length];

            const nodeColor =
              status === 'completed' ? zone.node :
              status === 'current'   ? zone.node :
              status === 'available' ? '#6b7280' : '#d1d5db';

            const bgColor =
              status === 'completed' ? zone.node :
              status === 'current'   ? 'white' :
              status === 'available' ? 'white' : '#f3f4f6';

            const textColor =
              status === 'completed' ? 'white' :
              status === 'current'   ? zone.node :
              status === 'available' ? '#374151' : '#9ca3af';

            return (
              <motion.g
                key={n.id}
                style={{ cursor: status === 'locked' ? 'not-allowed' : 'pointer' }}
                initial={{ scale: 0, opacity: 0 }}
                animate={{ scale: 1, opacity: 1 }}
                transition={{ delay: i * 0.04, type: 'spring', stiffness: 200 }}
                onMouseEnter={() => setHoveredId(n.id)}
                onMouseLeave={() => setHoveredId(null)}
                onClick={() => handleClick(n.id)}
              >
                {/* Glow for current */}
                {status === 'current' && (
                  <circle cx={cx} cy={cy} r={NODE_SIZE / 2 + 8}
                    fill={zone.node} opacity={0.2}>
                    <animate attributeName="r"
                      values={`${NODE_SIZE/2+6};${NODE_SIZE/2+14};${NODE_SIZE/2+6}`}
                      dur="2s" repeatCount="indefinite" />
                    <animate attributeName="opacity"
                      values="0.25;0.05;0.25" dur="2s" repeatCount="indefinite" />
                  </circle>
                )}

                {/* Circle */}
                <circle
                  cx={cx} cy={cy}
                  r={NODE_SIZE / 2}
                  fill={bgColor}
                  stroke={nodeColor}
                  strokeWidth={status === 'current' ? 4 : 2.5}
                  filter={isHovered ? 'drop-shadow(0 6px 12px rgba(0,0,0,0.2))' : undefined}
                />

                {/* Icon */}
                <text x={cx} y={cy - 6} textAnchor="middle" fontSize={22} dominantBaseline="middle">
                  {status === 'locked' ? '🔒' : status === 'completed' ? '✅' : icon}
                </text>

                {/* Level number */}
                <text x={cx} y={cy + 18} textAnchor="middle"
                  fontSize={11} fontWeight="700" fill={textColor}>
                  {n.id}
                </text>

                {/* Label below node */}
                <text x={cx} y={cy + NODE_SIZE / 2 + 16} textAnchor="middle"
                  fontSize={11} fontWeight="600"
                  fill={status === 'locked' ? '#9ca3af' : '#374151'}
                  style={{ maxWidth: COL_GAP - 10 }}>
                  {title.length > 14 ? title.slice(0, 13) + '…' : title}
                </text>

                {/* Hover tooltip */}
                {isHovered && (
                  <g>
                    <rect
                      x={cx - 70} y={cy - NODE_SIZE / 2 - 44}
                      width={140} height={36}
                      rx={8} fill="#1f2937" opacity={0.92}
                    />
                    <text x={cx} y={cy - NODE_SIZE / 2 - 30}
                      textAnchor="middle" fontSize={11} fill="white" fontWeight="600">
                      {title}
                    </text>
                    <text x={cx} y={cy - NODE_SIZE / 2 - 16}
                      textAnchor="middle" fontSize={10} fill={zone.node}>
                      {zone.label} · Level {n.id}
                    </text>
                  </g>
                )}
              </motion.g>
            );
          })}
        </svg>
      </div>

      {/* Footer stats */}
      <div className="dmap-footer glass">
        <div className="dmap-stat">
          <CheckCircle size={18} color="#10b981" />
          <span>{completedLevels.length} / {totalLevels} completed</span>
        </div>
        <div className="dmap-stat">
          <span>🎯 Current: Level {currentLevel}</span>
        </div>
        <div className="dmap-stat">
          <Lock size={18} color="#9ca3af" />
          <span>{totalLevels - completedLevels.length} remaining</span>
        </div>
      </div>
    </div>
  );
};

export default DungeonMap;
