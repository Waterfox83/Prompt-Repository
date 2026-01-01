import React from 'react';
import './HeroMissionStatement.css';

const HeroMissionStatement = ({ isFirstTime = false }) => {
  return (
    <div className={`hero-mission ${isFirstTime ? 'hero-mission--animated' : ''}`}>
      <div className="hero-mission__content">
        <h1 className="hero-mission__title">
          Discover AI Prompts That Actually Work
        </h1>
        <p className="hero-mission__subtitle">
          Find proven prompts for ChatGPT, Claude, and other AI tools, shared by developers and creators who've tested them in real projects. 
          Stop starting from scratch—build on what works.
        </p>
      </div>
    </div>
  );
};

export default HeroMissionStatement;