import { useState, useMemo } from "react";
import { Link } from "react-router-dom";
import {
  Search, Filter, Calendar, LayoutGrid,
  ArrowRight, Sparkles
} from "lucide-react";
import { useTranslation } from 'react-i18next';

export type EventCategory = "Виставка" | "Воркшоп" | "Відкриття" | "Лекція";

export interface ArtEvent {
  id: number;
  title: string;
  galleryName: string;
  city: string;
  date: string;
  category: EventCategory;
  image: string;
  price: string;
}

export const MOCK_EVENTS: ArtEvent[] = [
  { id: 1, title: 'Металевий дух: ретроспектива', galleryName: 'Галерея Кузня', city: 'Київ', date: '20-25 Грудня 2025', category: "Виставка", price: "Free", image: "https://images.unsplash.com/photo-1579783902614-a3fb3927b6a5?auto=format&fit=crop&q=80&w=800" },
  { id: 2, title: 'Digital Art Workshop', galleryName: 'PinchukArtCentre', city: 'Київ', date: '28 Грудня 2025', category: "Воркшоп", price: "Paid", image: "https://images.unsplash.com/photo-1550751827-4bd374c3f58b?auto=format&fit=crop&q=80&w=800" },
  { id: 3, title: 'Ніч у музеї ССМ', galleryName: 'Музей ССМ', city: 'Одеса', date: '30 Грудня 2025', category: "Відкриття", price: "Free", image: "https://images.unsplash.com/photo-1544531586-fde5298cdd40?auto=format&fit=crop&q=80&w=800" },
  { id: 4, title: 'Живопис старого Львова', galleryName: 'Арт-центр Світ', city: 'Львів', date: '05-10 Січня 2026', category: "Виставка", price: "Paid", image: "https://images.unsplash.com/photo-1578301978693-85fa9c0320b9?auto=format&fit=crop&q=80&w=800" },
];

const EventsPage = () => {
  const { t } = useTranslation();
  const [search, setSearch] = useState("");
  const [selectedCity, setSelectedCity] = useState(t('events.allCities'));
  const [selectedCategory, setSelectedCategory] = useState<string>(t('events.allTypes'));
  const [isFilterOpen, setIsFilterOpen] = useState(false);

  const filtered = useMemo(() => {
    return MOCK_EVENTS.filter(e => {
      const matchesSearch = e.title.toLowerCase().includes(search.toLowerCase()) ||
        e.galleryName.toLowerCase().includes(search.toLowerCase());
      const matchesCity = selectedCity === "Усі міста" || e.city === selectedCity;
      const matchesCategory = selectedCategory === "Усі типи" || e.category === selectedCategory;
      return matchesSearch && matchesCity && matchesCategory;
    });
  }, [search, selectedCity, selectedCategory]);

  return (
    <div className="min-h-screen bg-transparent pb-28 animate-in fade-in duration-700">
      <section className="bg-white/40 backdrop-blur-sm border-b border-zinc-200/50 py-16">
        <div className="container mx-auto px-6 max-w-6xl space-y-10">
          <div className="space-y-2">
            <h1 className="text-4xl md:text-5xl font-black text-zinc-800 tracking-tighter uppercase leading-none">{t('events.title')}</h1>
          </div>

          <div className="flex flex-col lg:flex-row gap-4">
            <div className="relative flex-1">
              <Search size={18} className="absolute left-5 top-1/2 -translate-y-1/2 text-zinc-400" />
              <input
                type="text"
                placeholder={t('events.search')}
                className="w-full bg-white border border-zinc-200 rounded-2xl py-4 pl-14 pr-6 outline-none focus:border-zinc-800 transition-all text-base shadow-sm font-medium"
                value={search}
                onChange={(e) => setSearch(e.target.value)}
              />
            </div>
            <button
              onClick={() => setIsFilterOpen(!isFilterOpen)}
              className={`flex items-center gap-3 px-8 py-4 rounded-2xl text-xs font-bold uppercase border transition-all ${isFilterOpen ? "bg-zinc-800 text-white border-zinc-800 shadow-xl" : "bg-white text-zinc-600 border-zinc-200 hover:bg-zinc-50"
                }`}
            >
              <Filter size={16} /> {t('events.filters')}
            </button>
          </div>

          {isFilterOpen && (
            <div className="p-8 bg-white border border-zinc-100 rounded-[32px] shadow-2xl grid grid-cols-1 md:grid-cols-2 gap-10 animate-in slide-in-from-top-2">
              <FilterSelect label={t('events.city')} value={selectedCity} onChange={setSelectedCity} options={[t('events.allCities'), "Київ", "Львів", "Одеса"]} />
              <div className="space-y-4">
                <p className="text-[10px] font-black uppercase tracking-[0.2em] text-zinc-400">{t('events.eventType')}</p>
                <div className="flex flex-wrap gap-2">
                  {["Усі типи", "Виставка", "Воркшоп", "Відкриття", "Лекція"].map(cat => (
                    <button key={cat} onClick={() => setSelectedCategory(cat)} className={`px-4 py-2 rounded-xl text-[10px] font-black uppercase transition-all ${selectedCategory === cat ? "bg-zinc-800 text-white shadow-lg" : "bg-zinc-100 text-zinc-400 hover:bg-zinc-200"}`}>{cat}</button>
                  ))}
                </div>
              </div>
            </div>
          )}
        </div>
      </section>

      <section className="container mx-auto px-6 max-w-6xl mt-16">
        <div className="flex items-center gap-2 text-zinc-500 font-bold text-[10px] uppercase tracking-[0.25em] mb-10">
          <LayoutGrid size={14} /> {t('events.foundEvents', { count: filtered.length })}
        </div>
        {filtered.length === 0 ? (
          <div className="max-w-xl mx-auto py-20 text-center flex flex-col items-center">
            <div className="w-24 h-24 bg-zinc-50 rounded-full flex items-center justify-center mb-6">
              <Calendar size={32} className="text-zinc-300" />
            </div>
            <h3 className="text-2xl font-black uppercase text-zinc-900 mb-2">{t('events.emptyTitle', 'Подій не знайдено')}</h3>
            <p className="text-zinc-500 font-medium mb-8 leading-relaxed">
              {t('events.emptyDesc', 'За обраними критеріями подій немає.')}
            </p>
            <button 
              onClick={() => { setSearch(""); setSelectedCity(t('events.allCities')); setSelectedCategory(t('events.allTypes')); }}
              className="px-6 py-3 bg-zinc-900 text-white rounded-xl text-xs font-bold uppercase tracking-widest hover:bg-zinc-800 transition-colors"
            >
              {t('events.clearFilters', 'Очистити пошук')}
            </button>
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
            {filtered.map(event => <EventCard key={event.id} event={event} />)}
          </div>
        )}
      </section>
    </div>
  );
};

const FilterSelect = ({ label, value, onChange, options }: any) => (
  <div className="space-y-4">
    <p className="text-[10px] font-black uppercase tracking-[0.2em] text-zinc-400">{label}</p>
    <select value={value} onChange={(e) => onChange(e.target.value)} className="w-full bg-zinc-50 rounded-xl p-3 text-sm font-bold outline-none cursor-pointer">
      {options.map((o: string) => <option key={o} value={o}>{o}</option>)}
    </select>
  </div>
);

const EventCard = ({ event }: { event: ArtEvent }) => (
  <Link
    to={`/events/${event.id}`}
    className="group bg-white/80 backdrop-blur-sm border border-zinc-100 rounded-[32px] overflow-hidden hover:bg-white hover:shadow-[0_40px_80px_-20px_rgba(0,0,0,0.08)] transition-all duration-500 flex flex-col h-full"
  >
    <div className="relative h-56 bg-zinc-200 overflow-hidden">
      <img src={event.image} alt={event.title} className="w-full h-full object-cover transition-transform duration-700 group-hover:scale-110 opacity-90 group-hover:opacity-100" />
      <div className="absolute top-5 left-5 bg-white/90 backdrop-blur-md px-3 py-1.5 rounded-xl text-[9px] font-black uppercase text-zinc-800">{event.category}</div>
    </div>
    <div className="p-8 space-y-5 flex-grow">
      <div className="space-y-3">
        <div className="flex items-center gap-2 text-orange-600 font-black text-[10px] uppercase tracking-widest"><Calendar size={12} /> {event.date}</div>
        <h3 className="text-xl font-black tracking-tight text-zinc-800 group-hover:text-orange-600 transition-colors">{event.title}</h3>
      </div>
      <div className="space-y-2 border-t border-zinc-50 pt-5 text-zinc-400 font-bold text-xs uppercase tracking-wider flex items-center gap-2">
        <Sparkles size={14} className="text-zinc-300" /> {event.galleryName}
      </div>
    </div>
    <div className="px-8 pb-8 pt-2">
      <div className="w-full py-4 bg-zinc-50 rounded-2xl flex items-center justify-center gap-3 text-[10px] font-black uppercase text-zinc-400 group-hover:bg-zinc-800 group-hover:text-white transition-all">
        Детальніше <ArrowRight size={16} />
      </div>
    </div>
  </Link>
);

export default EventsPage;