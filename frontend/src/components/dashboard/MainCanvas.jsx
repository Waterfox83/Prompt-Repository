import React from 'react';
import './MainCanvas.css';

const MainCanvas = ({ children, className = '', context = null }) => {
  return (
    <div className={`main-canvas ${className}`} data-context={context}>
      {children}
    </div>
  );
};

export default MainCanvas;