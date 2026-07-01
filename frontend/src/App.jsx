import { BrowserRouter, Routes, Route } from 'react-router-dom';
import LandingPage from './pages/LandingPage';
import LoginPage from './pages/LoginPage';

/**
 * App.jsx — Top-level router shell.
 *
 * Phase 2: /login added.
 * Future phases will add:
 *   /dashboard      (Phase 7)
 *   /employees      (Phase 3)
 *   /projects       (Phase 4)
 *   /leaderboard    (Phase 7)
 */
export default function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/"      element={<LandingPage />} />
        <Route path="/login" element={<LoginPage />} />
        {/* Phase 3+ routes will be registered here */}
      </Routes>
    </BrowserRouter>
  );
}
