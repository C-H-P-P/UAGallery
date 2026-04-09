import { ArrowRight, MapPin } from 'lucide-react';
import { Link } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
import { useGalleriesQuery } from '../../hooks/useGalleriesQuery';
import { useState, useEffect } from 'react';
import { getGalleryName, getGalleryCity, getGallerySpecialization } from '../../utils/gallery';

const HomeFeaturedGalleries = () => {
  const { t, i18n } = useTranslation();
  const { data: galleries = [] } = useGalleriesQuery();
  const [randomGalleries, setRandomGalleries] = useState<typeof galleries>([]);

  // Randomize galleries only once when data is loaded to prevent re-shuffle on every render
  useEffect(() => {
    if (galleries.length > 0) {
      const shuffled = [...galleries].sort(() => 0.5 - Math.random());
      setRandomGalleries(shuffled.slice(0, 3));
    }
  }, [galleries]);

  if (randomGalleries.length === 0) return null; // Don't render empty section until loaded

  return (
    <section className="space-y-12">
      {/* Заголовок у нашому фірмовому стилі */}
      <div className="flex justify-between items-end border-b border-zinc-100 pb-8">
        <div className="space-y-2">
          <p className="text-[10px] font-black uppercase tracking-[0.3em] text-blue-600">{t('home.featured.badge')}</p>
          <h2 className="text-3xl font-bold text-zinc-900 tracking-tight">{t('home.featured.title')}</h2>
        </div>
        <Link
          to="/galleries"
          className="group flex items-center gap-2 text-sm font-bold text-zinc-500 hover:text-black transition-all"
        >
          {t('home.featured.viewAll')} <ArrowRight size={18} className="group-hover:translate-x-1 transition-transform" />
        </Link>
      </div>

      {/* Сітка карток */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
        {randomGalleries.map((gallery, index) => {
          const name = getGalleryName(gallery, i18n.language);
          const city = getGalleryCity(gallery, i18n.language);
          const specialization = getGallerySpecialization(gallery, i18n.language);

          return (
            <Link
              key={gallery.id}
              to={`/galleries/${gallery.slug}`}
              className="group cursor-pointer relative overflow-hidden rounded-[32px] bg-zinc-50 hover:bg-zinc-100 transition-colors duration-500 animate-fade-in-up opacity-0 block h-[280px] p-8 flex flex-col justify-between border border-transparent hover:border-zinc-200"
              style={{ animationDelay: `${index * 150}ms`, animationFillMode: 'forwards' }}
            >
              {/* Decorative Background Letter */}
              <div className="absolute -bottom-10 -right-10 text-[180px] font-black text-zinc-200/50 group-hover:text-zinc-200/80 group-hover:scale-110 transition-all duration-700 select-none z-0 leading-none">
                {name[0]}
              </div>

              {/* Top: Specialization & Badge */}
              <div className="relative z-10 flex justify-between items-start">
                <div className="flex flex-wrap gap-2">
                  {specialization && (
                    <span className="text-[10px] font-bold uppercase tracking-widest text-zinc-500 border border-zinc-200 px-3 py-1.5 rounded-full bg-white">
                      {/* Temporary Frontend Translation Fix */}
                      {i18n.language === 'en' && specialization === 'Сучасне українське мистецтво' ? 'Contemporary Ukrainian Art' :
                        i18n.language === 'en' && specialization === 'Сучасна українська фотографія' ? 'Contemporary Ukrainian Photography' :
                          specialization}
                    </span>
                  )}
                </div>
                <div className="w-8 h-8 rounded-full bg-white border border-zinc-100 flex items-center justify-center group-hover:bg-zinc-900 group-hover:text-white transition-colors duration-300">
                  <ArrowRight size={14} />
                </div>
              </div>

              {/* Bottom: Info */}
              <div className="relative z-10">
                <div>
                  <h3 className="text-3xl font-black text-zinc-900 tracking-tighter leading-[0.9] mb-4 group-hover:translate-x-1 transition-transform duration-300">
                    {name}
                  </h3>
                  <div className="flex items-center gap-2 text-zinc-500 group-hover:text-zinc-900 transition-colors">
                    <MapPin size={14} />
                    <span className="text-xs font-bold uppercase tracking-wide">{city}, {t('common.country')}</span>
                  </div>
                </div>
              </div>
            </Link>
          );
        })}
      </div>
    </section>
  );
};

export default HomeFeaturedGalleries;