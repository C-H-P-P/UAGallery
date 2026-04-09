import { useEffect, useState } from "react";
import { useParams, Link, useNavigate } from "react-router-dom";
import { ArrowLeft, MapPin, Mail, Phone, Globe, Instagram, Lock, Clock, Calendar, BadgeCheck, Ban, Heart, Info, Users, ExternalLink } from "lucide-react";
import { useTranslation } from "react-i18next";
import { useAuth } from "../../context/AuthContext";
import { useFavorites } from "../../context/FavoritesContext";
import { documentToReactComponents } from '@contentful/rich-text-react-renderer';
import type { Document } from '@contentful/rich-text-types';

import { fetchGalleryBySlug } from "../../api/galleries";
import type { GalleryDetail } from "../../api/galleries";
import {
  getGalleryName,
  getGalleryCity,
  getGalleryAddress,
  getGalleryShortDescription,
  getGalleryFullDescription,
  getGallerySpecialization,
  getGalleryArtists,
} from "../../utils/gallery";
import GalleryMap from "../../components/gallery/GalleryMap";

const GalleryPage = () => {
  const { slug } = useParams<{ slug: string }>();
  const { t, i18n } = useTranslation();
  const { isAuth } = useAuth();
  const { isFavorite, toggleFavorite } = useFavorites();
  const navigate = useNavigate();

  const [gallery, setGallery] = useState<GalleryDetail | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(false);

  useEffect(() => {
    window.scrollTo(0, 0);
  }, []);

  useEffect(() => {
    if (!slug) return;

    setLoading(true);
    setError(false);

    fetchGalleryBySlug(slug)
      .then(setGallery)
      .catch(() => setError(true))
      .finally(() => setLoading(false));
  }, [slug]);

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="w-10 h-10 border-4 border-zinc-200 border-t-zinc-900 rounded-full animate-spin"></div>
      </div>
    );
  }

  if (error || !gallery) {
    return (
      <div className="min-h-screen flex flex-col items-center justify-center gap-6">
        <p className="text-zinc-400 font-bold uppercase tracking-widest text-[10px]">
          {t('gallery.notFound')}
        </p>
        <Link
          to="/galleries"
          className="text-zinc-800 font-black uppercase text-[10px] tracking-widest border-b border-zinc-800"
        >
          {t('gallery.return')}
        </Link>
      </div>
    );
  }

  const name = getGalleryName(gallery, i18n.language);
  const city = getGalleryCity(gallery, i18n.language);
  const address = getGalleryAddress(gallery, i18n.language);
  const shortDesc = getGalleryShortDescription(gallery, i18n.language);
  const fullDesc = getGalleryFullDescription(gallery, i18n.language);
  const specialization = getGallerySpecialization(gallery, i18n.language);
  const artists = getGalleryArtists(gallery, i18n.language);

  return (
    <div className="min-h-screen bg-transparent pb-32 animate-in fade-in duration-700 font-sans">
      <div className="container mx-auto px-6 max-w-6xl pt-12">
        <Link
          to="/galleries"
          className="group inline-flex items-center gap-3 text-zinc-400 hover:text-zinc-800 text-[10px] font-black uppercase tracking-widest mb-12"
        >
          <ArrowLeft size={14} className="group-hover:-translate-x-1 transition-transform" />
          {t('gallery.backToGalleries')}
        </Link>

        {gallery.cover_image && (
          <div className="rounded-[40px] overflow-hidden shadow-sm aspect-[21/9] mb-12">
            <img
              src={gallery.cover_image}
              alt={name}
              className="w-full h-full object-cover"
            />
          </div>
        )}

        <div className="grid grid-cols-1 lg:grid-cols-12 gap-20">
          
          {/* Main Content */}
          <div className="lg:col-span-8 space-y-12">
            
            <div className="flex items-start justify-between gap-6">
              <div className="flex items-center gap-6">
                <div className="w-24 h-24 bg-zinc-900 text-white rounded-[32px] flex items-center justify-center text-4xl font-black shadow-xl shrink-0 overflow-hidden">
                  {gallery.image ? (
                    <img src={gallery.image} alt="Logo" className="w-full h-full object-cover" />
                  ) : (
                    <span>{name[0].toUpperCase()}</span>
                  )}
                </div>
                <div>
                  <h1 className="text-4xl md:text-6xl font-black text-zinc-800 tracking-tighter uppercase leading-[0.9] mb-4">
                    {name}
                  </h1>
                  <div className="flex items-center gap-2">
                    <MapPin size={16} className="text-zinc-400" />
                    <span className="text-base font-bold text-zinc-500">{city}, {address}</span>
                  </div>
                </div>
              </div>
            </div>

            {(shortDesc || fullDesc) && (
              <div className="prose prose-zinc max-w-none">
                <h2 className="text-[11px] font-black uppercase tracking-[0.3em] text-zinc-400 mb-6 flex items-center gap-2">
                  <Info size={14} /> Про галерею
                </h2>
                {shortDesc && <p className="text-xl text-zinc-600 leading-relaxed font-medium mb-6">{shortDesc}</p>}
                {fullDesc && (
                  <div className="text-lg text-zinc-500 leading-relaxed font-medium">
                    {typeof fullDesc === 'string'
                      ? <div className="whitespace-pre-wrap">{fullDesc}</div>
                      : documentToReactComponents(fullDesc as Document)
                    }
                  </div>
                )}
              </div>
            )}

            <div className="grid grid-cols-1 md:grid-cols-2 gap-6 pt-6">
              <div className="p-8 bg-zinc-50 rounded-[40px] border border-zinc-100">
                <Users size={20} className="text-zinc-400 mb-4" />
                <h4 className="text-[10px] font-black uppercase text-zinc-400 mb-2 tracking-widest">{t('gallery.founded')}</h4>
                <p className="text-2xl font-black text-zinc-800">{gallery.founding_year || '—'}</p>
              </div>
              <div className="p-8 bg-white border border-zinc-100 rounded-[40px]">
                {gallery.status ? <BadgeCheck size={20} className="text-green-500 mb-4" /> : <Ban size={20} className="text-red-500 mb-4" />}
                <h4 className="text-[10px] font-black uppercase text-zinc-400 mb-2 tracking-widest">Статус</h4>
                <p className={`text-lg font-black ${gallery.status ? 'text-green-600' : 'text-red-600'}`}>{gallery.status ? t('gallery.active') : t('gallery.inactive')}</p>
              </div>
            </div>

            <div className="relative pt-12 border-t border-zinc-200 mt-12">
              {!isAuth && (
                <div className="absolute inset-0 z-10 bg-gradient-to-b from-white/60 to-white flex items-center justify-center pt-20">
                  <div className="bg-white p-8 rounded-[32px] shadow-2xl border border-zinc-100 max-w-md text-center">
                    <div className="w-16 h-16 bg-blue-50 text-blue-600 rounded-2xl flex items-center justify-center mx-auto mb-6">
                      <Lock size={32} />
                    </div>
                    <h3 className="text-xl font-bold mb-2">{t('gallery.loginToView')}</h3>
                    <p className="text-zinc-500 mb-8">{t('gallery.loginDesc')}</p>
                    <button
                      onClick={() => navigate('/login')}
                      className="w-full py-4 bg-black text-white rounded-xl font-bold uppercase text-xs tracking-widest hover:bg-zinc-800 transition-colors shadow-lg"
                    >
                      {t('gallery.loginBtn')}
                    </button>
                  </div>
                </div>
              )}

              <div className={`space-y-16 ${!isAuth ? 'blur-md select-none opacity-40' : ''}`}>
                <section>
                  <h3 className="text-2xl font-black uppercase mb-8 flex items-center gap-3">
                    <Calendar size={24} className="text-zinc-400" />
                    {t('gallery.exhibitions')}
                  </h3>
                  <div className="p-12 bg-zinc-50 rounded-[32px] text-center border border-dashed border-zinc-200">
                    <p className="text-zinc-400 font-medium">No active exhibitions</p>
                  </div>
                </section>

                <section>
                  <h3 className="text-2xl font-black uppercase mb-8 flex items-center gap-3">
                    <Globe size={24} className="text-zinc-400" />
                    {t('gallery.artists')}
                  </h3>
                  {artists ? (
                    <div className="p-8 bg-zinc-50 rounded-[32px] text-zinc-800 leading-relaxed font-medium">
                      {artists}
                    </div>
                  ) : (
                    <div className="p-12 bg-zinc-50 rounded-[32px] text-center border border-dashed border-zinc-200">
                      <p className="text-zinc-400 font-medium">No artists info</p>
                    </div>
                  )}
                </section>
              </div>
            </div>

          </div>

          {/* Sidebar */}
          <aside className="lg:col-span-4 space-y-8">
            <div className="bg-white border border-zinc-100 rounded-[40px] p-10 space-y-8 shadow-sm lg:sticky top-28">
              
              <div className="flex gap-3 justify-center">
                <button
                  onClick={() => {
                    if (navigator.share) {
                      navigator.share({
                        title: name,
                        text: shortDesc || 'Check out this gallery!',
                        url: window.location.href,
                      }).catch(console.error);
                    } else {
                      navigator.clipboard.writeText(window.location.href);
                      alert("Лінк скопійовано!");
                    }
                  }}
                  className="w-14 h-14 rounded-full border-2 border-zinc-100 flex items-center justify-center shrink-0 text-zinc-400 hover:bg-zinc-50 hover:text-zinc-900 transition-colors"
                  aria-label="Share"
                >
                  <Globe size={20} />
                </button>
                <button
                  onClick={() =>
                    toggleFavorite({
                      id: gallery.slug,
                      name: getGalleryName(gallery, i18n.language),
                      slug: gallery.slug,
                    })
                  }
                  className={`flex-1 h-14 rounded-full border-2 flex items-center justify-center gap-2 transition-colors font-bold uppercase tracking-widest text-xs ${isFavorite(gallery.slug)
                      ? "border-red-100 bg-red-50 text-red-500 hover:bg-red-100"
                      : "border-zinc-100 text-zinc-400 hover:border-zinc-900 hover:text-zinc-900"
                    }`}
                >
                  <Heart size={20} fill={isFavorite(gallery.slug) ? "currentColor" : "none"} />
                  {isFavorite(gallery.slug) ? 'В архіві' : 'Зберегти'}
                </button>
              </div>

              <div className="space-y-6 pt-6 border-t border-zinc-50">
                <div className="space-y-1">
                  <p className="text-[9px] font-black uppercase text-zinc-400 tracking-widest">{t('gallery.specialization')}</p>
                  <p className="text-sm font-bold text-zinc-800 uppercase leading-relaxed">{specialization || '—'}</p>
                </div>

                <div className="space-y-4">
                  <p className="text-[9px] font-black uppercase text-zinc-400 tracking-widest">{t('gallery.contacts')}</p>
                  <div className="space-y-3">
                    {gallery.phone && (
                      <a href={`tel:${gallery.phone}`} className="flex items-center gap-3 text-sm font-bold text-zinc-800 hover:text-blue-600 transition-colors">
                        <div className="w-8 h-8 rounded-full bg-zinc-50 flex items-center justify-center shrink-0"><Phone size={14} className="text-zinc-400"/></div>
                        {gallery.phone}
                      </a>
                    )}
                    {gallery.email && (
                      <a href={`mailto:${gallery.email}`} className="flex items-center gap-3 text-sm font-bold text-zinc-800 hover:text-blue-600 transition-colors truncate">
                        <div className="w-8 h-8 rounded-full bg-zinc-50 flex items-center justify-center shrink-0"><Mail size={14} className="text-zinc-400"/></div>
                        <span className="truncate">{gallery.email}</span>
                      </a>
                    )}
                    {gallery.website && (
                      <a href={gallery.website} target="_blank" rel="noreferrer" className="flex items-center gap-3 text-sm font-bold text-zinc-800 hover:text-blue-600 transition-colors">
                        <div className="w-8 h-8 rounded-full bg-zinc-50 flex items-center justify-center shrink-0"><ExternalLink size={14} className="text-zinc-400"/></div>
                        {t('gallery.website')}
                      </a>
                    )}
                    {gallery.social_links?.instagram && (
                      <a href={gallery.social_links.instagram} target="_blank" rel="noreferrer" className="flex items-center gap-3 text-sm font-bold text-zinc-800 hover:text-blue-600 transition-colors">
                        <div className="w-8 h-8 rounded-full bg-zinc-50 flex items-center justify-center shrink-0"><Instagram size={14} className="text-zinc-400"/></div>
                        Instagram
                      </a>
                    )}
                  </div>
                </div>

                <div className="space-y-4 pt-4 border-t border-zinc-50">
                   <p className="text-[9px] font-black uppercase text-zinc-400 tracking-widest">{t('gallery.workingHours')}</p>
                   <div className="flex items-center gap-3">
                      <div className="w-8 h-8 rounded-full bg-zinc-50 flex items-center justify-center shrink-0"><Clock size={14} className="text-zinc-400"/></div>
                      <div>
                        <p className="font-bold text-sm text-zinc-800">11:00 — 19:00</p>
                        <p className="text-[10px] text-zinc-400 uppercase tracking-widest">Понеділок — Неділя</p>
                      </div>
                   </div>
                </div>
              </div>

              {/* Map */}
              <div className="h-40 rounded-[24px] overflow-hidden border border-zinc-100">
                 <GalleryMap gallery={gallery} />
              </div>

            </div>
          </aside>
        </div>

      </div>
    </div>
  );
};

export default GalleryPage;
