import { LogOut, ShieldCheck, User, Mail, AtSign } from "lucide-react";
import { useNavigate } from "react-router-dom";
import { useAuth } from "../../hooks/useAuth";

const ProfilePage = () => {
  const navigate = useNavigate();
  const { user, logout } = useAuth();

  if (!user) return null;

  const initial = (user.first_name || user.username || "U")[0].toUpperCase();

  return (
    <div className="max-w-3xl animate-in fade-in slide-in-from-right-4 duration-700">
      <div className="bg-white/90 backdrop-blur-2xl border border-gray-100 rounded-[32px] shadow-[0_20px_50px_rgba(0,0,0,0.04)] p-10 space-y-10">
        
        <section className="flex flex-col md:flex-row items-center gap-8 pb-8 border-b border-gray-50 text-center md:text-left">
          <div className="w-20 h-20 bg-zinc-900 text-white rounded-[24px] flex items-center justify-center text-2xl font-black shadow-xl">
            {initial}
          </div>
          <div className="space-y-1">
            <p className="text-[10px] font-black uppercase tracking-[0.2em] text-blue-600">Особистий профіль</p>
            <h2 className="text-3xl font-black text-zinc-900 tracking-tighter uppercase leading-none">
              {user.first_name} {user.last_name}
            </h2>
            <div className="flex items-center justify-center md:justify-start gap-2 text-zinc-400 text-sm font-bold">
              <AtSign size={13} strokeWidth={3} />
              <span>{user.username}</span>
            </div>
          </div>
        </section>

        <section className="grid md:grid-cols-2 gap-x-12 gap-y-10">
          <InfoField label="Електронна пошта" value={user.email} icon={<Mail size={14} />} />
          <InfoField label="Ім'я" value={user.first_name} icon={<User size={14} />} />
          <InfoField label="Прізвище" value={user.last_name} icon={<User size={14} />} />
          <InfoField 
            label="Статус акаунта" 
            value={user.is_active ? "Активний" : "Неактивний"} 
            icon={<ShieldCheck size={14} />} 
            isStatus 
          />
        </section>

        <div className="pt-8 border-t border-gray-50 flex justify-between items-center">
          <p className="text-[10px] font-black text-zinc-300 uppercase tracking-[0.3em]">ID: {user.id}</p>
          <button
            onClick={() => { logout(); navigate("/login"); }}
            className="flex items-center gap-2 text-zinc-400 hover:text-red-500 font-black text-[10px] uppercase tracking-widest transition-all"
          >
            <LogOut size={16} /> Вийти з системи
          </button>
        </div>
      </div>
    </div>
  );
};

const InfoField = ({ label, value, icon, isStatus = false }: any) => (
  <div className="space-y-3 group">
    <div className="flex items-center gap-2 text-[10px] font-black uppercase tracking-widest text-zinc-400 group-hover:text-blue-600 transition-colors">
      {icon} {label}
    </div>
    <p className={`text-base font-bold border-b border-zinc-50 pb-2 transition-all group-hover:border-zinc-200 ${
      isStatus && value === "Активний" ? "text-blue-600" : "text-zinc-800"
    }`}>
      {value || "—"}
    </p>
  </div>
);

export default ProfilePage;