import { BrowserRouter, Routes, Route } from 'react-router-dom';
import LandingPage from './pages/LandingPage';

/**
 * App.jsx — Top-level router shell.
 *
 * Phase 0: single route to the placeholder landing page.
 * Future phases will add:
 *   /login          (Phase 2)
 *   /dashboard      (Phase 7)
 *   /employees      (Phase 3)
 *   /projects       (Phase 4)
 *   /leaderboard    (Phase 7)
 */
export default function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<LandingPage />} />
        {/* Phase 2+ routes will be registered here */}
      </Routes>
    </BrowserRouter>
  );
}
