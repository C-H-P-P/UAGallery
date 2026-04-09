import type { Gallery, GalleryDetail } from '../api/galleries';

/**
 * Helper functions to get language-specific fields from Gallery objects
 * based on the current i18n language setting
 */

export function getGalleryName(gallery: Gallery, language: string): string {
    return language === 'en' ? (gallery.name_en || gallery.name_ua || 'Unnamed Gallery') : (gallery.name_ua || gallery.name_en || 'Unnamed Gallery');
}

export function getGalleryCity(gallery: Gallery, language: string): string {
    return language === 'en' ? (gallery.city_en || gallery.city_ua || 'Unknown City') : (gallery.city_ua || gallery.city_en || 'Unknown City');
}

export function getGalleryAddress(gallery: Gallery, language: string): string {
    return language === 'en' ? (gallery.address_en || gallery.address_ua || '') : (gallery.address_ua || gallery.address_en || '');
}

export function getGalleryShortDescription(gallery: Gallery, language: string): string {
    return language === 'en' ? (gallery.short_description_en || gallery.short_description_ua || '') : (gallery.short_description_ua || gallery.short_description_en || '');
}

export function getGallerySpecialization(gallery: Gallery, language: string): string | null {
    return language === 'en' ? gallery.specialization_en : gallery.specialization_ua;
}

// For GalleryDetail
export function getGalleryFullDescription(gallery: GalleryDetail, language: string): any {
    return language === 'en' ? (gallery.full_description_en || gallery.full_description_ua || '') : (gallery.full_description_ua || gallery.full_description_en || '');
}

export function getGalleryFounders(gallery: GalleryDetail, language: string): string | null {
    return language === 'en' ? gallery.founders_en : gallery.founders_ua;
}

export function getGalleryCurators(gallery: GalleryDetail, language: string): string | null {
    return language === 'en' ? gallery.curators_en : gallery.curators_ua;
}

export function getGalleryArtists(gallery: GalleryDetail, language: string): string | null {
    return language === 'en' ? gallery.artists_en : gallery.artists_ua;
}
