import { http } from "./http";

// API функції для роботи з улюбленими галереями

export async function getFavorites(): Promise<string[]> {
    const data = await http<{ favorites: string[] }>("/api/favorites/", {
        auth: true,
    });
    return data.favorites;
}

export async function toggleFavorite(slug: string): Promise<{ is_favorite: boolean }> {
    const data = await http<{ detail: string; is_favorite: boolean }>("/api/favorites/toggle/", {
        method: "POST",
        auth: true,
        body: { slug },
    });
    return data;
}
