import React from 'react';
import './DashboardLayout.css';

const DashboardLayout = ({ sidebar, topBar, mainContent, isMobileSidebarOpen = false }) => {
  return (
    <div className={`dashboard-layout ${isMobileSidebarOpen ? 'mobile-sidebar-open' : ''}`}>
      {/* Zone 1: Sidebar - Fixed 260px width */}
      <aside className={`dashboard-sidebar ${isMobileSidebarOpen ? 'mobile-open' : ''}`}>
        {sidebar}
      </aside>

      {/* Zone 2: Top Bar - 60px height */}
      <header className="dashboard-topbar">
        {topBar}
      </header>

      {/* Zone 3: Main Canvas - Flexible content area */}
      <main className="dashboard-main">
        {mainContent}
      </main>
    </div>
  );
};

export default DashboardLayout;