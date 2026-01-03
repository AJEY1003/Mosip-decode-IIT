import React, { useEffect } from 'react';
import { BrowserRouter as Router, Routes, Route, useLocation } from 'react-router-dom';
import Header from './components/Header';
import { NewFooter } from './components/NewFooter';
import Home from './pages/Home';
import UploadPage from './pages/UploadNew'; // Updated to use new upload component
import FormsPage from './pages/Forms';
import ValidationSimple from './pages/ValidationSimple';
import WalletPage from './pages/Wallet';
import ITRFilingPage from './pages/ITRFiling';
import QRTest from './pages/QRTest';
import ValidationResult from './pages/ValidationResult';
import ITRDashboard from './pages/ITRDashboard';

const ScrollToTop = () => {
  const { pathname } = useLocation();
  useEffect(() => {
    window.scrollTo(0, 0);
  }, [pathname]);
  return null;
};

const App = () => {
  return (
    <Router>
      <ScrollToTop />
      <div className="app-min-height">
        <Header />
        <main>
          <Routes>
            <Route path="/" element={<Home />} />
            <Route path="/upload" element={<UploadPage />} />
            <Route path="/forms" element={<FormsPage />} />
            <Route path="/validation" element={<ValidationSimple />} />
            <Route path="/validation-result" element={<ValidationResult />} />
            <Route path="/dashboard" element={<ITRDashboard />} />
            <Route path="/dashboard-demo" element={<ITRDashboard />} />
            <Route path="/wallet" element={<WalletPage />} />
            <Route path="/itr" element={<ITRFilingPage />} />
            <Route path="/qr-test" element={<QRTest />} />
          </Routes>
        </main>
        <NewFooter />
      </div>
    </Router>
  );
};

export default App;
