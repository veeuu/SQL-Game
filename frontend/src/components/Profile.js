import React from 'react';
import { useNavigate } from 'react-router-dom';
import { ArrowLeft, Award, Star } from 'lucide-react';
import './Profile.css';

const Profile = ({ user, onLogout }) => {
  const navigate = useNavigate();

  const achievements = [
    { id: 1, title: '⚡ Query Novice', description: 'Complete first level', unlocked: true },
    { id: 2, title: '🧙 SQL Wizard', description: 'Score 300+ points', unlocked: true },
    { id: 3, title: '🗡️ Dungeon Explorer', description: 'Reach level 5', unlocked: false },
    { id: 4, title: '👑 Dragon Slayer', description: 'Complete all levels', unlocked: false }
  ];

  return (
    <div className="profile-container">
      <div className="profile-header">
        <button className="btn btn-secondary" onClick={() => navigate('/dashboard')}>
          <ArrowLeft size={16} /> Back
        </button>
        <h1>Profile</h1>
      </div>

      <div className="profile-content">
        <div className="profile-card glass">
          <div className="profile-avatar">
            <div className="avatar-circle">
              {user.username.charAt(0).toUpperCase()}
            </div>
          </div>
          <h2>{user.username}</h2>
          <p className="profile-title">SQL Adventurer</p>
        </div>

        <div className="achievements-section glass">
          <h3><Award size={24} /> Achievements</h3>
          <div className="achievements-grid">
            {achievements.map(achievement => (
              <div 
                key={achievement.id} 
                className={`achievement-card ${achievement.unlocked ? 'unlocked' : 'locked'}`}
              >
                <div className="achievement-icon">{achievement.title.split(' ')[0]}</div>
                <h4>{achievement.title}</h4>
                <p>{achievement.description}</p>
                {achievement.unlocked && <Star className="unlock-badge" size={20} />}
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
};

export default Profile;
