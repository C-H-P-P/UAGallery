import { useQuery } from "@tanstack/react-query";
import { fetchGalleries } from "../api/galleries";
import type { Gallery } from "../api/galleries";

export function useGalleriesQuery() {
  return useQuery<Gallery[]>({
    queryKey: ["galleries"],
    queryFn: fetchGalleries,

    // 🔑 ВАЖЛИВО ДЛЯ МЕНТОРА
    // дані вважаються актуальними 5 хвилин
    // повторний захід на сторінку НЕ робить API-запит
    staleTime: 1000 * 60 * 5,
  });
}
