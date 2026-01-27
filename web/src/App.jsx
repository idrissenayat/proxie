import React from 'react';
import { BrowserRouter, Routes, Route } from 'react-router-dom';
import DashboardPage from './pages/DashboardPage';
import ChatPage from './pages/ChatPage';
import HomePage from './pages/HomePage';
import CreateRequestPage from './pages/CreateRequestPage';
import OffersPage from './pages/OffersPage';
import BookingConfirmPage from './pages/BookingConfirmPage';
import ProviderDashboardPage from './pages/ProviderDashboardPage';
import RequestDetailPage from './pages/RequestDetailPage'; // Provider view
import RequestDetailView from './pages/RequestDetailView'; // Consumer view
import SubmitOfferPage from './pages/SubmitOfferPage';
import ProviderOffersPage from './pages/ProviderOffersPage';
import ProviderProfilePage from './pages/ProviderProfilePage'; // Self view
import PublicProviderProfile from './pages/PublicProviderProfile'; // Consumer view

function App() {
  return (
    <BrowserRouter>
      <div className="bg-black min-h-screen">
        <div className="max-w-phone mx-auto flex flex-col min-h-screen overflow-x-hidden">
          <Routes>
            {/* New Dashboard as Home */}
            <Route path="/" element={<DashboardPage />} />
            <Route path="/chat" element={<ChatPage />} />

            {/* Legacy Home (Forms) */}
            <Route path="/home" element={<HomePage />} />

            {/* Consumer routes */}
            <Route path="/request/new" element={<CreateRequestPage />} />
            <Route path="/request/:id" element={<RequestDetailView />} />
            <Route path="/request/:id/offers" element={<OffersPage />} />
            <Route path="/booking/:id" element={<BookingConfirmPage />} />
            <Route path="/providers/:id" element={<PublicProviderProfile />} />

            {/* Provider routes */}
            <Route path="/provider" element={<ProviderDashboardPage />} />
            <Route path="/provider/request/:id" element={<RequestDetailPage />} />
            <Route path="/provider/offer/new" element={<SubmitOfferPage />} />
            <Route path="/provider/offers" element={<ProviderOffersPage />} />
            <Route path="/provider/profile" element={<ProviderProfilePage />} />
          </Routes>
        </div>
      </div>
    </BrowserRouter>
  );
}

export default App;
