import React from 'react';
import { Globe, ChevronRight, Monitor } from "lucide-react";
import { useTranslation } from 'react-i18next';

const GeneralSettingsPage = () => {
  const { t, i18n } = useTranslation();

  const toggleLanguage = () => {
    const newLang = i18n.language === 'uk' ? 'en' : 'uk';
    i18n.changeLanguage(newLang);
  };

  return (
    <div className="max-w-2xl animate-in fade-in duration-700">

      {/* Скляна картка, як у ChangePassword */}
      <div className="bg-white/90 backdrop-blur-2xl border border-gray-100 rounded-[32px] shadow-[0_20px_50px_rgba(0,0,0,0.05)] p-8 space-y-10">

        {/* Заголовок */}
        <section className="space-y-1">
          <p className="text-[10px] font-black uppercase tracking-[0.25em] text-zinc-500">{t('settings.system')}</p>
          <h2 className="text-xl font-bold text-black">{t('settings.general')}</h2>
        </section>

        {/* Списоком налаштувань */}
        <div className="space-y-2">

          <SettingItem
            icon={<Globe size={18} />}
            label={t('settings.language')}
            value={i18n.language === 'uk' ? 'Українська' : 'English'}
            onClick={toggleLanguage}
          />

          <SettingItem
            icon={<Monitor size={18} />}
            label={t('settings.theme')}
            value={t('settings.systemTheme')}
          />



        </div>

        {/* Кнопка збереження */}
        <button className="w-full py-4 bg-black text-white rounded-2xl text-[11px] font-black uppercase tracking-[0.2em] hover:bg-neutral-800 transition-all duration-300">
          {t('settings.saveChanges')}
        </button>
      </div>
    </div>
  );
};

/* Рядок налаштування з вибором */
const SettingItem = ({ icon, label, value, onClick }: { icon: React.ReactNode, label: string, value: string, onClick?: () => void }) => (
  <button onClick={onClick} className="w-full flex items-center justify-between p-4 rounded-2xl hover:bg-gray-50 transition-colors group">
    <div className="flex items-center gap-4">
      <div className="text-zinc-400 group-hover:text-black transition-colors">{icon}</div>
      <span className="text-sm font-bold text-black">{label}</span>
    </div>
    <div className="flex items-center gap-2">
      <span className="text-xs font-semibold text-zinc-400">{value}</span>
      <ChevronRight size={14} className="text-zinc-300" />
    </div>
  </button>
);


export default GeneralSettingsPage;