import { Link } from "react-router-dom";
import { ArrowRight, Trash2, BookmarkX, Database } from "lucide-react";
import { useFavorites } from "../../context/FavoritesContext";

const SavedGalleriesPage = () => {
  const { favorites, toggleFavorite } = useFavorites();

  return (
    <div className="max-w-2xl animate-in fade-in duration-700">
      <div className="bg-white/90 backdrop-blur-3xl border border-zinc-100 rounded-[40px] shadow-[0_30px_60px_rgba(0,0,0,0.03)] p-10 space-y-10">

        <header className="flex justify-between items-end border-b border-zinc-50 pb-8">
          <div className="space-y-1.5">
            <div className="flex items-center gap-2 text-zinc-400">
              <Database size={12} />
              <p className="text-[10px] font-black uppercase tracking-[0.25em]">
                Цифровий Реєстр
              </p>
            </div>
            <h2 className="text-2xl font-black text-zinc-900 uppercase tracking-tighter">
              Мій Архів
            </h2>
          </div>
          <div className="text-right">
            <span className="text-3xl font-black text-zinc-100 tabular-nums">
              {favorites.length.toString().padStart(2, "0")}
            </span>
          </div>
        </header>

        {favorites.length > 0 ? (
          <div className="grid gap-3">
            {favorites.map((g) => (
              <div
                key={g.id}
                className="group flex items-center justify-between p-5 bg-zinc-50/50 rounded-[24px] border border-transparent hover:border-zinc-200 hover:bg-white transition-all"
              >
                <div className="flex items-center gap-5">
                  <div className="w-12 h-12 bg-zinc-900 text-white rounded-2xl flex items-center justify-center font-black text-sm group-hover:bg-blue-600 transition-all">
                    {g.name[0]}
                  </div>

                  <div className="space-y-0.5">
                    <h4 className="text-sm font-black text-zinc-800 uppercase tracking-tight group-hover:text-blue-600 transition-colors">
                      {g.name}
                    </h4>
                    <p className="text-[9px] text-zinc-400 font-bold uppercase tracking-widest">
                      ID: {g.id}
                    </p>
                  </div>
                </div>

                <div className="flex items-center gap-3">
                  <button
                    onClick={() => toggleFavorite(g)}
                    className="p-3 text-zinc-300 hover:text-red-500 hover:bg-red-50 rounded-xl transition-all"
                  >
                    <Trash2 size={18} />
                  </button>

                  <Link
                    to={`/galleries/${g.slug}`}
                    className="p-3 bg-white text-zinc-400 border border-zinc-100 rounded-xl hover:text-zinc-900 hover:border-zinc-900 transition-all shadow-sm"
                  >
                    <ArrowRight size={18} strokeWidth={2.5} />
                  </Link>
                </div>
              </div>
            ))}
          </div>
        ) : (
          <div className="py-20 text-center space-y-6">
            <div className="w-20 h-20 bg-zinc-50 rounded-[30px] flex items-center justify-center mx-auto text-zinc-200">
              <BookmarkX size={32} />
            </div>
            <Link
              to="/galleries"
              className="inline-flex items-center gap-2 text-[10px] font-black uppercase tracking-widest text-blue-600 px-6 py-3 bg-blue-50 rounded-full hover:bg-blue-600 hover:text-white transition-all"
            >
              До каталогу <ArrowRight size={12} />
            </Link>
          </div>
        )}
      </div>
    </div>
  );
};

export default SavedGalleriesPage;
