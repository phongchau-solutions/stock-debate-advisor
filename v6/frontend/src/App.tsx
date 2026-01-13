import React from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { MainLayout } from './layouts/MainLayout';
import { FinancialsPage } from './pages/FinancialsPage';
import { StocksPage } from './pages/StocksPage';
import { AnalysisPage } from './pages/AnalysisPage';
import { NewsPage } from './pages/NewsPage';
import { WatchlistPage } from './pages/WatchlistPage';
import { DashboardPage } from './pages/DashboardPage';

const App: React.FC = () => {
  return (
    <BrowserRouter>
      <Routes>
        <Route element={<MainLayout />}>
          <Route index element={<Navigate to="/dashboard" replace />} />
          <Route path="/dashboard" element={<DashboardPage />} />
          <Route path="/analysis" element={<AnalysisPage />} />
          <Route path="/financials" element={<FinancialsPage />} />
          <Route path="/stocks" element={<StocksPage />} />
          <Route path="/news" element={<NewsPage />} />
          <Route path="/watchlist" element={<WatchlistPage />} />
        </Route>
      </Routes>
    </BrowserRouter>
  );
};

export default App;
