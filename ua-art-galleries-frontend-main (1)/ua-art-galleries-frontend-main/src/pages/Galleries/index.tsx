import { useMemo, useState } from "react";
import { Link } from "react-router-dom";
import { Search, Heart, ChevronLeft, ChevronRight, BadgeCheck, Ban } from "lucide-react";
import { useGalleriesQuery } from "../../hooks/useGalleriesQuery";
import { useFavorites } from "../../context/FavoritesContext";
import type { Gallery } from "../../api/galleries";
import { useTranslation } from 'react-i18next';
import { getGalleryName, getGalleryCity } from "../../utils/gallery";
import { CustomSelect } from "../../components/shared/CustomSelect";

const PER_PAGE = 18;

const GalleriesPage = () => {
  const { t, i18n } = useTranslation();
  const { data: galleries = [], isLoading } = useGalleriesQuery();
  const { isFavorite, toggleFavorite } = useFavorites();

  const [search, setSearch] = useState("");
  const [city, setCity] = useState("all");
  const [status, setStatus] = useState("all");
  const [year, setYear] = useState("all");
  const [sort, setSort] = useState("alphabetical");
  const [page, setPage] = useState(1);

  /* ---------- CITIES & YEARS ---------- */
  const cities = useMemo(() => {
    const unique = Array.from(
      new Set(galleries.map((g) => getGalleryCity(g, i18n.language)).filter(Boolean))
    );
    return unique;
  }, [galleries, i18n.language]);

  const years = useMemo(() => {
    const unique = Array.from(
      new Set(galleries.map((g) => g.founding_year).filter(Boolean))
    ).sort((a, b) => Number(b) - Number(a));
    return unique as string[];
  }, [galleries]);

  /* ---------- FILTERING & SORTING ---------- */
  const sortedAndFiltered = useMemo(() => {
    const q = search.trim().toLowerCase();

    const filtered = galleries.filter((g) => {
      const name = getGalleryName(g, i18n.language);
      const cityName = getGalleryCity(g, i18n.language);

      const matchSearch =
        !q ||
        name.toLowerCase().includes(q) ||
        cityName.toLowerCase().includes(q);

      const matchCity = city === "all" || cityName === city;
      const matchStatus = status === "all" || (status === "active" ? g.status : !g.status);
      const matchYear = year === "all" || g.founding_year === year;

      return matchSearch && matchCity && matchStatus && matchYear;
    });

    return filtered.sort((a, b) => {
      if (sort === "alphabetical") {
        return getGalleryName(a, i18n.language).localeCompare(getGalleryName(b, i18n.language));
      } else if (sort === "newest") {
        return Number(b.founding_year || 0) - Number(a.founding_year || 0);
      } else if (sort === "oldest") {
        return Number(a.founding_year || 9999) - Number(b.founding_year || 9999);
      }
      return 0;
    });
  }, [galleries, search, city, status, year, sort, i18n.language]);

  /* ---------- PAGINATION ---------- */
  const totalPages = Math.ceil(sortedAndFiltered.length / PER_PAGE);

  const visible = sortedAndFiltered.slice(
    (page - 1) * PER_PAGE,
    page * PER_PAGE
  );

  if (isLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="w-10 h-10 border-4 border-zinc-200 border-t-zinc-900 rounded-full animate-spin"></div>
      </div>
    );
  }

  return (
    <div className="min-h-screen pb-32">
      {/* ---------- HEADER ---------- */}
      <div className="pt-32 pb-20">
        <div className="max-w-6xl mx-auto px-6 space-y-12">
          <h1 className="text-5xl font-black uppercase tracking-tight">
            {t('galleries.title')} <span className="text-zinc-400">{t('galleries.subtitle')}</span>
          </h1>

          {/* SEARCH & FILTERS */}
          <div className="flex flex-col gap-4">
            {/* SEARCH */}
            <div className="relative">
              <Search
                size={18}
                className="absolute left-5 top-1/2 -translate-y-1/2 text-zinc-400 pointer-events-none"
              />
              <input
                value={search}
                onChange={(e) => {
                  setSearch(e.target.value);
                  setPage(1);
                }}
                placeholder={t('galleries.search')}
                className="w-full h-[56px] rounded-2xl border border-zinc-200 pl-[52px] pr-6 text-[15px] outline-none focus:border-zinc-900"
              />
            </div>

            {/* FILTERS GRID */}
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
              <CustomSelect
                value={city}
                onChange={(val) => { setCity(val); setPage(1); }}
                options={[
                  { value: "all", label: t('galleries.allCities') },
                  ...cities.map(c => ({ value: c, label: c }))
                ]}
              />

              <CustomSelect
                value={status}
                onChange={(val) => { setStatus(val); setPage(1); }}
                options={[
                  { value: "all", label: t('events.allStatuses') },
                  { value: "active", label: t('gallery.active') },
                  { value: "inactive", label: t('gallery.inactive') }
                ]}
              />

              <CustomSelect
                value={year}
                onChange={(val) => { setYear(val); setPage(1); }}
                options={[
                  { value: "all", label: t('galleries.allYears') },
                  ...years.map(y => ({ value: y, label: y }))
                ]}
              />

              <CustomSelect
                value={sort}
                onChange={(val) => { setSort(val); setPage(1); }}
                options={[
                  { value: "alphabetical", label: t('galleries.sortAlpha') },
                  { value: "newest", label: t('galleries.sortNewest') },
                  { value: "oldest", label: t('galleries.sortOldest') }
                ]}
              />
            </div>
          </div>
        </div>
      </div>

      <div className="max-w-6xl mx-auto px-6 mb-10 text-xs uppercase tracking-widest text-zinc-400 font-bold">
        {t('common.found')}: {sortedAndFiltered.length}
      </div>

      {/* MAIN CONTENT */}
      {visible.length === 0 ? (
        <div className="max-w-xl mx-auto px-6 py-20 text-center flex flex-col items-center">
          <div className="w-24 h-24 bg-zinc-50 rounded-full flex items-center justify-center mb-6">
            <Search size={32} className="text-zinc-300" />
          </div>
          <h3 className="text-2xl font-black uppercase text-zinc-900 mb-2">{t('galleries.emptyTitle', 'Нічого не знайдено')}</h3>
          <p className="text-zinc-500 font-medium mb-8 leading-relaxed">
            {t('galleries.emptyDesc', 'За вашими критеріями не знайдено жодної галереї. Спробуйте змінити фільтри пошуку.')}
          </p>
          <button 
            onClick={() => { setSearch(""); setCity("all"); setStatus("all"); setYear("all"); setPage(1); }}
            className="px-6 py-3 bg-zinc-900 text-white rounded-xl text-xs font-bold uppercase tracking-widest hover:bg-zinc-800 transition-colors"
          >
            {t('galleries.clearFilters', 'Скинути фільтри')}
          </button>
        </div>
      ) : (
        <div className="max-w-6xl mx-auto px-6 grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-10">
          {visible.map((gallery, index) => (
            <div
              key={gallery.id}
              className="animate-fade-in-up opacity-0"
              style={{ animationDelay: `${Math.min(index * 100, 1000)}ms`, animationFillMode: 'forwards' }}
            >
              <GalleryCard
                gallery={gallery}
                favorite={isFavorite(gallery.slug)}
                onToggle={() =>
                  toggleFavorite({
                    id: gallery.slug,
                    name: getGalleryName(gallery, i18n.language),
                    slug: gallery.slug,
                  })
                }
              />
            </div>
          ))}
        </div>
      )}

      {/* PAGINATION */}
      {totalPages > 1 && (
        <div className="mt-20 flex justify-center items-center gap-4">
          <button
            disabled={page === 1}
            onClick={() => setPage((p) => p - 1)}
            className="p-2 rounded-full border disabled:opacity-30"
          >
            <ChevronLeft size={18} />
          </button>

          {Array.from({ length: totalPages }).map((_, i) => (
            <button
              key={i}
              onClick={() => setPage(i + 1)}
              className={`px-4 py-2 rounded-xl font-bold ${page === i + 1
                ? "bg-zinc-900 text-white"
                : "border border-zinc-200"
                }`}
            >
              {i + 1}
            </button>
          ))}

          <button
            disabled={page === totalPages}
            onClick={() => setPage((p) => p + 1)}
            className="p-2 rounded-full border disabled:opacity-30"
          >
            <ChevronRight size={18} />
          </button>
        </div>
      )}
    </div>
  );
};

/* ---------- CARD ---------- */

const GalleryCard = ({
  gallery,
  favorite,
  onToggle,
}: {
  gallery: Gallery;
  favorite: boolean;
  onToggle: () => void;
}) => {
  const { t, i18n } = useTranslation();
  const name = getGalleryName(gallery, i18n.language);
  const city = getGalleryCity(gallery, i18n.language);

  return (
    <Link
      to={`/galleries/${gallery.slug}`}
      className="group block rounded-[28px] border border-zinc-200 bg-white p-8 hover:border-zinc-900 transition h-full flex flex-col justify-between"
    >
      <div>
        <div className="flex items-start justify-between mb-6">
          <div className="w-12 h-12 rounded-xl bg-zinc-900 text-white flex items-center justify-center font-black overflow-hidden">
            {gallery.image ? (
              <img src={gallery.image} alt={name} className="w-full h-full object-cover" />
            ) : (
              <span>{name && name.length > 0 ? name[0].toUpperCase() : '?'}</span>
            )}
          </div>

          <button
            onClick={(e) => {
              e.preventDefault();
              e.stopPropagation();
              onToggle();
            }}
            className={`transition-colors ${favorite
              ? "text-red-500 hover:text-red-600"
              : "text-zinc-300 hover:text-zinc-900"
              }`}
            aria-label="Toggle favorite"
          >
            <Heart size={18} fill={favorite ? "currentColor" : "none"} />
          </button>
        </div>

        <h3 className="font-black uppercase text-lg leading-tight mb-2">
          {name}
        </h3>

        <p className="text-xs uppercase tracking-widest text-zinc-400 mb-4">
          {city}
        </p>
      </div>

      <div className="pt-4 border-t border-zinc-100 flex items-center justify-between">
        <div className={`flex items-center gap-1.5 px-2 py-1 rounded-md text-[10px] font-black uppercase tracking-wider ${gallery.status ? 'bg-green-50 text-green-700' : 'bg-red-50 text-red-700'}`}>
          {gallery.status ? <BadgeCheck size={12} /> : <Ban size={12} />}
          {gallery.status ? t('gallery.active') : t('gallery.inactive')}
        </div>
      </div>
    </Link>
  );
};

export default GalleriesPage;
