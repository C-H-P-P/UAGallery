import { useMemo } from "react";
import { useGalleriesQuery } from "./useGalleriesQuery";
import { MOCK_EVENTS, type ArtEvent } from "../pages/Events/index";
import type { Gallery } from "../api/galleries";
import { useTranslation } from 'react-i18next';

export interface SearchResults {
    galleries: Gallery[];
    events: ArtEvent[];
    isLoading: boolean;
    hasResults: boolean;
}

export function useGlobalSearch(query: string): SearchResults {
    const { data: galleries = [], isLoading } = useGalleriesQuery();
    const { i18n } = useTranslation();

    const results = useMemo(() => {
        const q = query.trim().toLowerCase();
        const galleriesArray = Array.isArray(galleries) ? galleries : [];

        // Не шукаємо, якщо менше 2 символів
        if (q.length < 2) {
            return { galleries: galleriesArray, events: MOCK_EVENTS };
        }

        // Фільтруємо галереї по різних полях
        const filteredGalleries = galleriesArray.filter(
            (g: Gallery) => {
                const nameUa = g.name_ua?.toLowerCase() || '';
                const nameEn = g.name_en?.toLowerCase() || '';
                const cityUa = g.city_ua?.toLowerCase() || '';
                const cityEn = g.city_en?.toLowerCase() || '';
                const specUa = g.specialization_ua?.toLowerCase() || '';
                const specEn = g.specialization_en?.toLowerCase() || '';

                return nameUa.includes(q) || nameEn.includes(q) || cityUa.includes(q) || cityEn.includes(q) || specUa.includes(q) || specEn.includes(q);
            }
        );

        // Фільтруємо події
        const filteredEvents = MOCK_EVENTS.filter(
            (e) =>
                e.title.toLowerCase().includes(q) ||
                e.galleryName.toLowerCase().includes(q) ||
                e.city.toLowerCase().includes(q)
        );

        return {
            galleries: filteredGalleries,
            events: filteredEvents,
        };
    }, [query, galleries, i18n.language]);

    return {
        ...results,
        isLoading,
        hasResults: results.galleries.length > 0 || results.events.length > 0,
    };
}
