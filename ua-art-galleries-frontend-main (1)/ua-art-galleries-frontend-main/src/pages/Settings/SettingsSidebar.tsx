import { Link, useLocation } from "react-router-dom";
import { User, Lock, Bookmark, Settings } from "lucide-react";
import { useTranslation } from "react-i18next";

const SettingsSidebar = () => {
  const location = useLocation();
  const { t } = useTranslation();

  const menu = [
    { path: "/settings/profile", label: t("settings.sidebar.profile", "Профіль"), icon: <User size={20} /> },
    { path: "/settings/general", label: t("settings.sidebar.general", "Налаштування"), icon: <Settings size={20} /> },
    { path: "/settings/password", label: t("settings.sidebar.security", "Безпека"), icon: <Lock size={20} /> },
    { path: "/settings/archive", label: t("settings.sidebar.archive", "Мій Архів"), icon: <Bookmark size={20} /> },
  ];

  return (
    <aside className="w-full lg:w-64 space-y-2">
      <div className="bg-white rounded-[32px] p-4 shadow-sm border border-zinc-100 flex flex-col gap-1">
        {menu.map((item) => {
          const isActive = location.pathname === item.path;
          return (
            <Link
              key={item.path}
              to={item.path}
              className={`flex items-center gap-3 px-4 py-3 rounded-2xl transition-all duration-300 font-bold text-sm ${
                isActive
                  ? "bg-zinc-900 text-white shadow-md"
                  : "text-zinc-500 hover:bg-zinc-50 hover:text-zinc-900"
              }`}
            >
              {item.icon}
              {item.label}
            </Link>
          );
        })}
      </div>
    </aside>
  );
};

export default SettingsSidebar;