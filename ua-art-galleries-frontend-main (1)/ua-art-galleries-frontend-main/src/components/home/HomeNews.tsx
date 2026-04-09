import { ArrowUpRight } from 'lucide-react';

const HomeNews = () => {
  return (
    <section className="space-y-10">
      <div className="flex justify-between items-end border-b border-zinc-100 pb-6">
        <div className="space-y-1">
          <p className="text-[10px] font-black uppercase tracking-[0.2em] text-zinc-400">Події та оновлення</p>
          <h2 className="text-3xl font-bold text-zinc-900 tracking-tight">Новини мистецтва</h2>
        </div>
        <button className="text-sm font-bold flex items-center gap-2 hover:gap-3 transition-all">
          Усі новини <ArrowUpRight size={18} />
        </button>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
        {[1, 2, 3].map((item) => (
          <div key={item} className="group cursor-pointer space-y-4">
            <div className="aspect-[4/3] bg-zinc-100 rounded-[32px] overflow-hidden relative">
              <div className="absolute inset-0 bg-zinc-900/0 group-hover:bg-zinc-900/10 transition-colors" />
            </div>
            <div className="space-y-2">
              <p className="text-[10px] font-black text-blue-600 uppercase tracking-widest">Виставка • 12 Січня</p>
              <h3 className="text-xl font-bold tracking-tight group-hover:underline underline-offset-4">Сучасний львівський пейзаж: Нові імена</h3>
            </div>
          </div>
        ))}
      </div>
    </section>
  );
};

export default HomeNews;