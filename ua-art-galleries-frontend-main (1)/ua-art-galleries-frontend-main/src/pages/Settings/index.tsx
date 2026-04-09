import { Outlet } from "react-router-dom";
import SettingsSidebar from "./SettingsSidebar";
import { useAuth } from "../../hooks/useAuth";

const SettingsLayout = () => {
  const { user, isLoading } = useAuth();

  if (isLoading) return <div className="flex justify-center pt-20 text-zinc-400 font-bold tracking-widest uppercase text-xs">Завантаження архіву...</div>;
  if (!user) return null;

  return (
    <div className="min-h-screen bg-white">
      <div className="container mx-auto px-6 py-16 max-w-6xl">
        <div className="flex flex-col md:flex-row items-start gap-16">
          
          {/* Ліва частина: Тепер без великого заголовка над сайдбаром */}
          <div className="w-full md:w-64 sticky top-24 pt-2">
            <SettingsSidebar />
          </div>

          {/* Права частина: Контент */}
          <main className="flex-1 w-full">
            <Outlet />
          </main>
          
        </div>
      </div>
    </div>
  );
};

export default SettingsLayout;