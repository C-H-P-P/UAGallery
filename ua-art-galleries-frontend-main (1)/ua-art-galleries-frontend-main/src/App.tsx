import { Routes, Route, useLocation, Navigate } from "react-router-dom";
import { useEffect } from "react";

import React, { Suspense } from "react";

// 1. Провайдери та Захист
import ProtectedRoute from "./components/ProtectedRoute";

// 2. Спільні компоненти
import Header from "./components/shared/Header";
import Footer from "./components/shared/Footer";
import BackgroundDecorator from "./components/shared/BackgroundDecorator";
import FavoritesNotification from "./components/shared/FavoritesNotification";

// 3. Сторінки (Lazy Loading)
const HomePage = React.lazy(() => import("./pages/Home"));
const GalleriesPage = React.lazy(() => import("./pages/Galleries"));
const GalleryPage = React.lazy(() => import("./pages/Gallery"));
const AboutPage = React.lazy(() => import("./pages/About"));
const EventsPage = React.lazy(() => import("./pages/Events"));
const EventDetail = React.lazy(() => import("./pages/Events/EventDetailPage"));
const AuthPage = React.lazy(() => import("./pages/Auth"));
const ProfilePage = React.lazy(() => import("./pages/Profile"));

// 4. Налаштування та Архів (Lazy Loading)
const SettingsLayout = React.lazy(() => import("./pages/Settings"));
const ChangePasswordPage = React.lazy(() => import("./pages/Settings/ChangePassword"));
const GeneralSettingsPage = React.lazy(() => import("./pages/Settings/GeneralSettingsPage"));
const SavedGalleriesPage = React.lazy(() => import("./pages/Galleries/SavedGalleriesPage"));
const RoadmapPage = React.lazy(() => import("./pages/Roadmap"));
const ContactsPage = React.lazy(() => import("./pages/Contacts"));
const PartnersPage = React.lazy(() => import("./pages/Partners"));
const FAQPage = React.lazy(() => import("./pages/FAQ"));
const SupportPage = React.lazy(() => import("./pages/Support"));

// Компонент для автоматичного прокручування вгору
const ScrollToTop = () => {
  const { pathname } = useLocation();
  useEffect(() => {
    window.scrollTo(0, 0);
  }, [pathname]);
  return null;
};

const AppContent = () => {
  const location = useLocation();
  // Перевіряємо, чи ми на сторінці логіну, щоб приховати футер
  const isAuthPage = location.pathname === "/login";

  return (
    <div className="flex flex-col min-h-screen relative font-sans selection:bg-zinc-900 selection:text-white">
      <ScrollToTop />
      <BackgroundDecorator />
      <Header />

      {/* Глобальні сповіщення */}
      <FavoritesNotification />

      <main className="flex-grow w-full relative z-10">
        <div
          key={location.pathname.startsWith('/settings') || location.pathname.startsWith('/profile') ? 'settings' : location.pathname}
          className={
            location.pathname.startsWith('/settings') || location.pathname.startsWith('/profile')
              ? "animate-in fade-in duration-500"
              : "animate-fade-in-up"
          }
        >
          <Suspense fallback={<div className="h-screen w-full flex items-center justify-center"><div className="w-8 h-8 border-4 border-black border-t-transparent rounded-full animate-spin"></div></div>}>
            <Routes>
              {/* Публічні маршрути */}
              <Route path="/" element={<HomePage />} />
              <Route path="/about" element={<AboutPage />} />
              <Route path="/galleries" element={<GalleriesPage />} />
              <Route path="/galleries/:slug" element={<GalleryPage />} />
              <Route path="/events" element={<EventsPage />} />
              <Route path="/events/:id" element={<EventDetail />} />
              <Route path="/roadmap" element={<RoadmapPage />} />
              <Route path="/contacts" element={<ContactsPage />} />
              <Route path="/partners" element={<PartnersPage />} />
              <Route path="/faq" element={<FAQPage />} />
              <Route path="/support" element={<SupportPage />} />
              <Route path="/login" element={<AuthPage />} />

              {/* Захищені маршрути */}
              <Route element={<ProtectedRoute />}>
                <Route element={<SettingsLayout />}>
                  {/* Default /settings redirects to /settings/profile or we can just mount ProfilePage there, but let's be explicit */}
                  <Route path="/settings" element={<Navigate to="/settings/profile" replace />} />
                  <Route path="/settings/profile" element={<ProfilePage />} />
                  <Route path="/settings/general" element={<GeneralSettingsPage />} />
                  <Route path="/settings/password" element={<ChangePasswordPage />} />
                  <Route path="/settings/archive" element={<SavedGalleriesPage />} />
                </Route>
              </Route>

              {/* 404 */}
              <Route path="*" element={
                <div className="text-center py-40">
                  <h1 className="text-9xl font-black text-zinc-100 uppercase tracking-tighter select-none">404</h1>
                  <p className="text-zinc-400 font-bold uppercase tracking-widest text-[10px] mt-4">Дані не знайдено в архіві</p>
                </div>
              } />
            </Routes>
          </Suspense>
        </div>
      </main>

      {!isAuthPage && <Footer />}
    </div>
  );
};

function App() {
  return (
    <AppContent />
  );
}

export default App;
