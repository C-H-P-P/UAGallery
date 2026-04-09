
import { useEffect, useMemo } from "react";
import { MapContainer, TileLayer, Marker, Popup, useMap } from "react-leaflet";
import L from "leaflet";
import "leaflet/dist/leaflet.css";
import { MapPin } from "lucide-react";
import { useTranslation } from "react-i18next";
import { GALLERY_COORDINATES, CITY_COORDINATES, seededRandom } from "../../utils/maps";
import { getGalleryName, getGalleryCity, getGalleryAddress } from "../../utils/gallery";
import type { Gallery } from "../../api/galleries";

// --- Icons ---
const pinSvg = encodeURIComponent(`
<svg width="30" height="42" viewBox="0 0 30 42" fill="none" xmlns="http://www.w3.org/2000/svg">
  <path d="M15 0C6.71573 0 0 6.71573 0 15C0 26.25 15 42 15 42C15 42 30 26.25 30 15C30 6.71573 23.2843 0 15 0Z" fill="#18181B"/>
  <circle cx="15" cy="15" r="6" fill="white"/>
</svg>
`);

const galleryIcon = new L.Icon({
    iconUrl: `data:image/svg+xml;charset=utf-8,${pinSvg}`,
    iconSize: [30, 42],
    iconAnchor: [15, 42],
    popupAnchor: [0, -36],
});

// --- Map Controller ---
const MapController = ({ center }: { center: [number, number] }) => {
    const map = useMap();

    useEffect(() => {
        map.setView(center, 15, { animate: true });
    }, [center, map]);

    return null;
};

// --- Component ---
interface GalleryMapProps {
    gallery: Gallery;
}

const GalleryMap = ({ gallery }: GalleryMapProps) => {
    const { i18n } = useTranslation();

    const coords = useMemo(() => {
        let lat = gallery.latitude;
        let lng = gallery.longitude;

        // 1. Try Specific Lookup
        if ((lat == null || lng == null) && gallery.slug && GALLERY_COORDINATES[gallery.slug]) {
            [lat, lng] = GALLERY_COORDINATES[gallery.slug];
        }

        // 2. Try City Lookup
        if ((lat == null || lng == null)) {
            const cityName = getGalleryCity(gallery, i18n.language);
            if (cityName && CITY_COORDINATES[cityName]) {
                const [cityLat, cityLng] = CITY_COORDINATES[cityName];
                // Use deterministic jitter
                const latJitter = (seededRandom(gallery.slug + 'lat') - 0.5) * 0.01;
                const lngJitter = (seededRandom(gallery.slug + 'lng') - 0.5) * 0.01;

                lat = cityLat + latJitter;
                lng = cityLng + lngJitter;
            }
        }

        return (lat != null && lng != null) ? [lat, lng] as [number, number] : null;
    }, [gallery, i18n.language]);

    if (!coords) return null;

    const name = getGalleryName(gallery, i18n.language);
    const city = getGalleryCity(gallery, i18n.language);
    const address = getGalleryAddress(gallery, i18n.language);

    return (
        <div className="h-[400px] w-full rounded-[32px] overflow-hidden border border-zinc-100 shadow-sm relative z-0">
            <MapContainer
                center={coords}
                zoom={15}
                className="h-full w-full"
                zoomControl={false}
                scrollWheelZoom={false}
            >
                <TileLayer url="https://{s}.basemaps.cartocdn.com/light_all/{z}/{x}/{y}{r}.png" />
                <MapController center={coords} />

                <Marker position={coords} icon={galleryIcon}>
                    <Popup closeButton={false} className="custom-popup">
                        <div className="p-3 min-w-[180px]">
                            <h4 className="font-black text-zinc-800 text-sm leading-tight">{name}</h4>
                            <p className="flex items-center gap-1.5 text-[10px] font-bold text-zinc-400 uppercase mt-1">
                                <MapPin size={10} /> {city}
                            </p>
                            {address && (
                                <p className="text-[10px] text-zinc-500 mt-1">{address}</p>
                            )}
                        </div>
                    </Popup>
                </Marker>
            </MapContainer>
        </div>
    );
};

export default GalleryMap;
