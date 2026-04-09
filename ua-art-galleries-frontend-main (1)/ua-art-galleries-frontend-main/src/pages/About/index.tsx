import { useEffect } from 'react';
import { useLocation } from 'react-router-dom';
import { GraduationCap } from "lucide-react";
import { useTranslation } from 'react-i18next';

const AboutPage = () => {
  const { t } = useTranslation();
  const location = useLocation();

  useEffect(() => {
    if (location.hash === '#team') {
      const el = document.getElementById('team');
      if (el) {
        el.scrollIntoView({ behavior: 'smooth' });
      }
    } else {
      window.scrollTo(0, 0);
    }
  }, [location]);
  return (
    <div className="relative z-0 animate-in fade-in duration-700">

      {/* 1. HERO — Компактний і чистий */}
      <section className="py-20 md:py-28 text-center space-y-6">
        <div className="inline-flex items-center gap-2 px-3 py-1.5 bg-white border border-zinc-200 shadow-sm rounded-full text-zinc-500 text-[10px] font-black uppercase tracking-widest">
          <GraduationCap size={14} className="text-zinc-900" /> {t('about.badge')}
        </div>
        <h1 className="text-5xl md:text-6xl font-black text-zinc-900 tracking-tighter leading-tight">
          {t('about.title')} <br />
          <span className="text-zinc-400">{t('about.subtitle')}</span>
        </h1>
        <div className="max-w-4xl mx-auto px-6">
          <p className="text-zinc-500 font-medium text-lg leading-loose text-center">
            {t('about.description')}
          </p>
        </div>
      </section>

      {/* 2. STATS — "Скляний" блок, який виділяється на текстурному фоні */}
      <section className="container mx-auto px-4 md:px-6 mb-20 flex justify-center">
        <div className="inline-flex flex-col md:flex-row items-center gap-12 md:gap-32 bg-white/70 backdrop-blur-md border border-white shadow-[0_8px_40px_rgba(0,0,0,0.04)] rounded-[40px] py-8 px-16">
            <StatItem label={t('about.activeGalleries')} value="100+" />
            <div className="w-px h-16 bg-zinc-200 hidden md:block"></div>
            <StatItem label={t('about.cities', 'Міст')} value="11" />
        </div>
      </section>

      {/* 3. TEAM SECTION */}
      <section id="team" className="py-20 scroll-mt-20 container mx-auto px-6 max-w-7xl">
        <div className="text-center mb-12 space-y-4">
          <h2 className="text-4xl md:text-5xl font-black uppercase tracking-tighter text-zinc-900">
            {t('about.teamTitle')}
          </h2>
          <p className="text-zinc-400 text-xs font-bold uppercase tracking-widest italic">
            - {t('about.quote')} -
          </p>
        </div>

        <div className="flex flex-wrap justify-center gap-10">
          <TeamMember initial="Y" name={t('about.teamMembers.yulia.name')} role={t('about.teamMembers.yulia.role')} />
          <TeamMember initial="R" name={t('about.teamMembers.rostyslav.name')} role={t('about.teamMembers.rostyslav.role')} />
          <TeamMember initial="N" name={t('about.teamMembers.nazar.name')} role={t('about.teamMembers.nazar.role')} />
          <TeamMember initial="M" name={t('about.teamMembers.mykhailo.name')} role={t('about.teamMembers.mykhailo.role')} />
          <TeamMember initial="S" name={t('about.teamMembers.stanislav.name')} role={t('about.teamMembers.stanislav.role')} />
          <TeamMember initial="R" name={t('about.teamMembers.roman.name')} role={t('about.teamMembers.roman.role')} />
          <TeamMember initial="O" name={t('about.teamMembers.oleksandr.name')} role={t('about.teamMembers.oleksandr.role')} />
          <TeamMember initial="D" name={t('about.teamMembers.dmytro.name')} role={t('about.teamMembers.dmytro.role')} />
          <TeamMember initial="D" name={t('about.teamMembers.danylo.name')} role={t('about.teamMembers.danylo.role')} />
        </div>
      </section>

      {/* 4. MISSION — Акцентний блок */}
      <section className="container mx-auto px-6 pb-24">
        <div className="bg-zinc-900 rounded-[40px] p-12 md:p-16 text-white shadow-2xl relative overflow-hidden">
          <div className="max-w-xl space-y-6 relative z-10">
            <h2 className="text-3xl font-black uppercase">{t('about.ourMission')}</h2>
            <p className="text-zinc-400 text-base font-medium leading-relaxed">
              {t('about.missionText')}
            </p>
          </div>
        </div>
      </section>
    </div>
  );
};

/* --- Компоненти --- */

const StatItem = ({ label, value }: any) => (
  <div className="text-center md:text-left space-y-1">
    <p className="text-3xl font-black text-zinc-900 tracking-tighter">{value}</p>
    <p className="text-[10px] font-bold uppercase tracking-widest text-zinc-400">{label}</p>
  </div>
);

const TeamMember = ({ name, role, initial }: any) => (
  <div className="w-[180px] flex flex-col items-center text-center group">
    <div className="w-20 h-20 bg-zinc-200 rounded-2xl mb-4 flex items-center justify-center font-bold text-xl text-zinc-900 group-hover:scale-110 group-hover:bg-black group-hover:text-white transition-all duration-300 shadow-sm">
      {initial}
    </div>
    <h3 className="font-black text-zinc-900 text-sm leading-tight mb-1.5">{name}</h3>
    <p className="text-[10px] font-bold text-zinc-400 uppercase tracking-widest group-hover:text-black transition-colors">{role}</p>
  </div>
);

export default AboutPage;