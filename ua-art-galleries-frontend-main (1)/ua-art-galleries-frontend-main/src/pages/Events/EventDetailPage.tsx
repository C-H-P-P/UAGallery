import { useEffect, useState } from 'react';
import { useParams, Link } from 'react-router-dom';
import { 
  MapPin, Clock, ArrowLeft, 
  Ticket, Info, Share2, 
  Users, Bell, ExternalLink 
} from 'lucide-react';

// Мок-дані для деталей подій
const MOCK_EVENT_DETAILS = {
  1: {
    title: "Металевий дух: ретроспектива",
    galleryName: "Галерея Кузня",
    gallerySlug: "halereya-kuznya",
    city: "Київ",
    date: "20-25 Грудня 2025",
    time: "18:00",
    category: "Виставка",
    price: "Free",
    description: "Експозиція досліджує еволюцію металевої скульптури в українському мистецтві за останні 30 років. Ви побачите роботи, що змінюють уявлення про матеріал та його пластику.",
    curator: "Олександр Коваль",
    requirements: "Попередня реєстрація не потрібна. Вхід у порядку живої черги."
  },
  2: {
    title: "Digital Art Workshop",
    galleryName: "PinchukArtCentre",
    gallerySlug: "pinchuk-art-centre",
    city: "Київ",
    date: "28 Грудня 2025",
    time: "14:00",
    category: "Воркшоп",
    price: "500 UAH",
    description: "Практичний інтенсив з використання штучного інтелекту в сучасному візуальному мистецтві. Створення концептів та їхня генерація під наглядом експертів.",
    curator: "Марія Левицька",
    requirements: "Наявність власного ноутбука з попередньо встановленим софтом."
  }
};

const EventDetailPage = () => {
  const { id } = useParams<{ id: string }>();
  const [loading, setLoading] = useState(true);
  const event = MOCK_EVENT_DETAILS[Number(id) as keyof typeof MOCK_EVENT_DETAILS];

  useEffect(() => {
    window.scrollTo(0, 0);
    const timer = setTimeout(() => setLoading(false), 500);
    return () => clearTimeout(timer);
  }, [id]);

  if (loading) return (
    <div className="min-h-screen flex items-center justify-center bg-transparent">
      <div className="text-[10px] font-black uppercase tracking-[0.5em] text-zinc-400 animate-pulse">Loading_Event_Data...</div>
    </div>
  );

  if (!event) return (
    <div className="min-h-screen flex flex-col items-center justify-center gap-6">
      <p className="text-zinc-400 font-bold uppercase tracking-widest text-xs">Подію не знайдено</p>
      <Link to="/events" className="text-zinc-800 font-black border-b border-zinc-800 pb-1 text-[10px] uppercase">До всіх подій</Link>
    </div>
  );

  return (
    <div className="min-h-screen bg-transparent pb-32 animate-in fade-in duration-700 font-sans">
      <div className="container mx-auto px-6 max-w-6xl pt-12">
        
        {/* Навігація */}
        <div className="flex justify-between items-center mb-20">
          <Link to="/events" className="group flex items-center gap-3 text-zinc-400 hover:text-zinc-800 transition-all text-[10px] font-black uppercase tracking-widest">
            <ArrowLeft size={14} className="group-hover:-translate-x-1 transition-transform" /> 
            Назад до подій
          </Link>
          <div className="flex gap-4">
            <button className="p-2 text-zinc-400 hover:text-zinc-800 transition-colors"><Bell size={18} /></button>
            <button className="p-2 text-zinc-400 hover:text-zinc-800 transition-colors"><Share2 size={18} /></button>
          </div>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-12 gap-20">
          
          {/* Ліва частина: Основний контент */}
          <div className="lg:col-span-8 space-y-12">
            <div className="space-y-6">
              <div className="flex items-center gap-4">
                <span className="bg-orange-50 text-orange-600 px-3 py-1 rounded-lg text-[9px] font-black uppercase tracking-widest">
                  {event.category}
                </span>
                <div className="h-[1px] flex-grow bg-zinc-100"></div>
              </div>
              <h1 className="text-5xl md:text-7xl font-black text-zinc-800 tracking-tighter uppercase leading-[0.9]">
                {event.title}
              </h1>
            </div>

            <div className="prose prose-zinc max-w-none">
              <h2 className="text-[11px] font-black uppercase tracking-[0.3em] text-zinc-400 mb-6 flex items-center gap-2">
                <Info size={14} /> Про захід
              </h2>
              <p className="text-xl text-zinc-600 leading-relaxed font-medium">
                {event.description}
              </p>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-6 pt-6">
              <div className="p-8 bg-zinc-50 rounded-[40px] border border-zinc-100">
                <Users size={20} className="text-zinc-400 mb-4" />
                <h4 className="text-[10px] font-black uppercase text-zinc-400 mb-2 tracking-widest">Куратор</h4>
                <p className="text-lg font-black text-zinc-800">{event.curator}</p>
              </div>
              <div className="p-8 bg-white border border-zinc-100 rounded-[40px]">
                <Clock size={20} className="text-zinc-400 mb-4" />
                <h4 className="text-[10px] font-black uppercase text-zinc-400 mb-2 tracking-widest">Час початку</h4>
                <p className="text-lg font-black text-zinc-800">{event.time}</p>
              </div>
            </div>
          </div>

          {/* Права частина: Сайдбар з квитками */}
          <aside className="lg:col-span-4 space-y-8">
            <div className="bg-white border border-zinc-100 rounded-[40px] p-10 space-y-10 shadow-sm sticky top-28">
              
              <div className="space-y-6">
                <div className="flex justify-between items-end border-b border-zinc-50 pb-6">
                  <div className="space-y-1">
                    <p className="text-[9px] font-black uppercase text-zinc-400 tracking-widest">Дата проведення</p>
                    <p className="text-xl font-black text-zinc-800 uppercase leading-none">{event.date}</p>
                  </div>
                  <div className="text-right">
                    <p className="text-[24px] font-black text-zinc-800 leading-none">{event.price}</p>
                  </div>
                </div>

                <div className="space-y-6">
                  <Link 
                    to={`/galleries/${event.gallerySlug}`}
                    className="flex items-center gap-4 group cursor-pointer"
                  >
                    <div className="w-12 h-12 rounded-2xl bg-zinc-900 text-white flex items-center justify-center font-black group-hover:bg-blue-600 transition-all">
                      {event.galleryName[0]}
                    </div>
                    <div>
                      <p className="text-[8px] font-black uppercase text-zinc-400 tracking-widest mb-0.5">Локація</p>
                      <p className="text-sm font-bold text-zinc-800 group-hover:text-blue-600 transition-colors flex items-center gap-1">
                        {event.galleryName} <ExternalLink size={12} />
                      </p>
                    </div>
                  </Link>

                  <div className="flex items-center gap-4 text-zinc-500 font-bold text-xs">
                    <div className="w-10 h-10 rounded-full bg-zinc-50 flex items-center justify-center"><MapPin size={16} /></div>
                    {event.city}
                  </div>
                </div>
              </div>

              <div className="space-y-4 pt-6">
                <p className="text-[9px] font-black uppercase text-zinc-400 tracking-widest">Умови входу</p>
                <p className="text-[11px] text-zinc-500 font-medium leading-relaxed italic">
                  {event.requirements}
                </p>
              </div>

              <button className="w-full py-5 bg-zinc-900 text-white rounded-2xl text-[10px] font-black uppercase tracking-[0.3em] hover:bg-orange-600 transition-all shadow-xl shadow-zinc-200/50 flex items-center justify-center gap-3 group">
                <Ticket size={16} className="group-hover:rotate-12 transition-transform" />
                Зарезервувати місце
              </button>
            </div>
          </aside>
        </div>
      </div>
    </div>
  );
};

export default EventDetailPage;