import React, { createContext, useContext, useEffect, useState } from "react";
import { getFavorites, toggleFavorite as toggleFavoriteAPI } from "../api/favorites";
import { useAuth } from "./AuthContext";

type Favorite = {
  id: string;
  name: string;
  slug: string;
};

interface FavoritesContextType {
  favorites: Favorite[];
  toggleFavorite: (gallery: Favorite) => void;
  isFavorite: (slug: string) => boolean;
  isLoading: boolean;
  lastAddedFavorite: Favorite | null;
  clearLastAddedFavorite: () => void;
  loginPromptVisible: boolean;
  closeLoginPrompt: () => void;
}

const FavoritesContext = createContext<FavoritesContextType | undefined>(
  undefined
);

export const FavoritesProvider: React.FC<{ children: React.ReactNode }> = ({
  children,
}) => {
  const [favorites, setFavorites] = useState<Favorite[]>([]);
  const [favoriteSlugs, setFavoriteSlugs] = useState<string[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [lastAddedFavorite, setLastAddedFavorite] = useState<Favorite | null>(null);
  const [loginPromptVisible, setLoginPromptVisible] = useState(false);
  const { user } = useAuth();

  // Завантажити улюблені галереї при монтуванні або зміні користувача
  useEffect(() => {
    if (user) {
      loadFavorites();
    } else {
      // Очистити улюблені якщо користувач вийшов
      setFavorites([]);
      setFavoriteSlugs([]);
    }
  }, [user]);

  const loadFavorites = async () => {
    try {
      setIsLoading(true);
      const slugs = await getFavorites();
      setFavoriteSlugs(slugs);
      // Конвертуємо slugs у Favorite об'єкти (тимчасово)
      const favs = slugs.map(slug => ({
        id: slug,
        slug: slug,
        name: slug
      }));
      setFavorites(favs);
    } catch (error) {
      console.error("Failed to load favorites:", error);
    } finally {
      setIsLoading(false);
    }
  };

  const isFavorite = (slug: string) => {
    return favoriteSlugs.includes(slug);
  };

  const toggleFavorite = async (gallery: Favorite) => {
    console.log('toggleFavorite called with:', gallery);
    console.log('Current user:', user);

    if (!user) {
      // Якщо користувач не авторизований, показуємо вікно входу
      console.warn("User must be logged in to save favorites");
      setLoginPromptVisible(true);
      return;
    }

    try {
      console.log('Calling API to toggle favorite for slug:', gallery.slug);
      const result = await toggleFavoriteAPI(gallery.slug);
      console.log('API response:', result);

      // Оновити локальний стан
      if (result.is_favorite) {
        console.log('Adding to favorites');
        setFavorites(prev => [...prev, gallery]);
        setFavoriteSlugs(prev => [...prev, gallery.slug]);
        setLastAddedFavorite(gallery); // Встановлюємо останню додану галерею
      } else {
        console.log('Removing from favorites');
        setFavorites(prev => prev.filter(f => f.slug !== gallery.slug));
        setFavoriteSlugs(prev => prev.filter(s => s !== gallery.slug));
      }
    } catch (error) {
      console.error("Failed to toggle favorite:", error);
    }
  };

  const clearLastAddedFavorite = () => {
    setLastAddedFavorite(null);
  };

  const closeLoginPrompt = () => {
    setLoginPromptVisible(false);
  };

  return (
    <FavoritesContext.Provider
      value={{
        favorites,
        toggleFavorite,
        isFavorite,
        isLoading,
        lastAddedFavorite,
        clearLastAddedFavorite,
        loginPromptVisible,
        closeLoginPrompt
      }}
    >
      {children}
    </FavoritesContext.Provider>
  );
};

export const useFavorites = () => {
  const ctx = useContext(FavoritesContext);
  if (!ctx) {
    throw new Error("useFavorites must be used within FavoritesProvider");
  }
  return ctx;
};
