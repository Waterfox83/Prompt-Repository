import React from 'react';
import './HeroMissionStatement.css';

const HeroMissionStatement = ({ isFirstTime = false }) => {
  return (
    <div className={`hero-mission ${isFirstTime ? 'hero-mission--animated' : ''}`}>
      <div className="hero-mission__content">
        <h1 className="hero-mission__title">
          AI Use Cases That Help. AI Prompts That Work.
        </h1>
        <p className="hero-mission__subtitle">
          Centralize, share, and discover the best AI prompts and innovative usecases across Pega. Turn your individual wins into team assets. Build on what works.
        </p>
      </div>
    </div>
  );
};

export default HeroMissionStatement;