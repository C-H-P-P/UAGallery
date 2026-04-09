import { useState, useRef, useEffect } from "react";
import { Link } from "react-router-dom";
import { Search, MapPin, Calendar } from "lucide-react";
import { useTranslation } from "react-i18next";
import { useGlobalSearch } from "../../hooks/useGlobalSearch";
import { getGalleryName, getGalleryCity } from "../../utils/gallery";

const HomeSearch = () => {
  const { t, i18n } = useTranslation();
  const [searchQuery, setSearchQuery] = useState("");
  const [searchOpen, setSearchOpen] = useState(false);
  const searchRef = useRef<HTMLDivElement | null>(null);

  const { galleries, events, hasResults } = useGlobalSearch(searchQuery);

  useEffect(() => {
    const handleClickOutside = (e: MouseEvent) => {
      if (searchRef.current && !searchRef.current.contains(e.target as Node)) {
        setSearchOpen(false);
      }
    };
    document.addEventListener("mousedown", handleClickOutside);
    return () => document.removeEventListener("mousedown", handleClickOutside);
  }, []);

  const showSearchResults = searchQuery.length >= 2 && searchOpen;

  return (
    <div className="container mx-auto px-4 md:px-6 relative z-40 -mt-10 mb-20" ref={searchRef}>
      <div className="max-w-3xl mx-auto shadow-sm hover:shadow-md transition-shadow duration-300 rounded-[32px] animate-fade-in-up delay-300 border border-zinc-200/60 bg-white">
        <div className="relative group">
          <div className="absolute inset-y-0 left-6 flex items-center pointer-events-none text-zinc-400 group-focus-within:text-zinc-900 transition-colors">
            <Search size={20} strokeWidth={2.5} />
          </div>
          <input
            type="text"
            placeholder={t('header.search')}
            value={searchQuery}
            onChange={(e) => {
              setSearchQuery(e.target.value);
              setSearchOpen(true);
            }}
            onFocus={() => setSearchOpen(true)}
            className="w-full bg-transparent rounded-[32px] pl-[64px] pr-6 py-5 text-[15px] font-medium outline-none placeholder:text-zinc-400 text-zinc-900 focus:bg-white transition-all"
          />

          {showSearchResults && (
            <div className="absolute top-[calc(100%+16px)] left-0 right-0 bg-white/95 backdrop-blur-2xl border border-zinc-100 rounded-[32px] shadow-2xl overflow-hidden z-50 animate-in fade-in slide-in-from-top-4 duration-300 transform-gpu">
              {!hasResults ? (
                <div className="px-6 py-10 text-center text-sm text-zinc-400 font-medium">
                  {t('header.noResults')}
                </div>
              ) : (
                <div className="py-4 max-h-[400px] overflow-y-auto">
                  {galleries.length > 0 && (
                    <div>
                      <div className="px-6 py-3 text-[10px] font-black uppercase tracking-[0.2em] text-zinc-400">
                        {t('nav.galleries')}
                      </div>
                      {galleries.map((g) => {
                        const name = getGalleryName(g, i18n.language);
                        const city = getGalleryCity(g, i18n.language);
                        return (
                          <Link
                            key={g.id}
                            to={`/galleries/${g.slug}`}
                            onClick={() => {
                              setSearchOpen(false);
                              setSearchQuery("");
                            }}
                            className="flex items-center gap-4 px-6 py-4 hover:bg-zinc-50 transition-colors"
                          >
                            <div className="w-12 h-12 bg-zinc-900 text-white rounded-2xl flex items-center justify-center text-lg font-black shrink-0">
                              {name && name.length > 0 ? name[0].toUpperCase() : '?'}
                            </div>
                            <div className="flex-1 min-w-0">
                              <p className="text-base font-bold text-zinc-900 truncate">{name}</p>
                              <p className="flex items-center gap-1.5 text-xs text-zinc-500 mt-1">
                                <MapPin size={12} /> {city}
                              </p>
                            </div>
                          </Link>
                        );
                      })}
                    </div>
                  )}

                  {events.length > 0 && (
                    <div>
                      <div className="px-6 py-3 text-[10px] font-black uppercase tracking-[0.2em] text-zinc-400 border-t border-zinc-100 mt-2 pt-4">
                        {t('nav.events')}
                      </div>
                      {events.map((e) => (
                        <Link
                          key={e.id}
                          to={`/events/${e.id}`}
                          onClick={() => {
                            setSearchOpen(false);
                            setSearchQuery("");
                          }}
                          className="flex items-center gap-4 px-6 py-4 hover:bg-zinc-50 transition-colors"
                        >
                          <div className="w-12 h-12 bg-orange-500 text-white rounded-2xl flex items-center justify-center shrink-0">
                            <Calendar size={20} />
                          </div>
                          <div className="flex-1 min-w-0">
                            <p className="text-base font-bold text-zinc-900 truncate">{e.title}</p>
                            <p className="text-xs text-zinc-500 mt-1 truncate">{e.galleryName}</p>
                          </div>
                        </Link>
                      ))}
                    </div>
                  )}
                </div>
              )}
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default HomeSearch;
