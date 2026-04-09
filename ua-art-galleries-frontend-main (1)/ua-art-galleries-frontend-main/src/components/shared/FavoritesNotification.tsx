import { useEffect } from "react";
import { useNavigate } from "react-router-dom";
import { Heart, X, ArrowRight, LogIn } from "lucide-react";
import { useTranslation } from "react-i18next";
import { useFavorites } from "../../context/FavoritesContext";

const FavoritesNotification = () => {
    const { t } = useTranslation();
    const navigate = useNavigate();
    const { lastAddedFavorite, clearLastAddedFavorite, loginPromptVisible, closeLoginPrompt } = useFavorites();

    // Auto-close success notification
    useEffect(() => {
        if (lastAddedFavorite) {
            const timer = setTimeout(() => {
                clearLastAddedFavorite();
            }, 5000);
            return () => clearTimeout(timer);
        }
    }, [lastAddedFavorite, clearLastAddedFavorite]);

    // Auto-close login prompt
    useEffect(() => {
        if (loginPromptVisible) {
            const timer = setTimeout(() => {
                closeLoginPrompt();
            }, 7000); // Give user a bit more time to read
            return () => clearTimeout(timer);
        }
    }, [loginPromptVisible, closeLoginPrompt]);

    if (!lastAddedFavorite && !loginPromptVisible) return null;

    // Login Prompt
    if (loginPromptVisible) {
        return (
            <div className="fixed bottom-6 right-6 z-50 animate-fade-in-up">
                <div className="bg-white rounded-2xl shadow-xl border border-zinc-100 p-5 w-[340px] flex flex-col gap-4">

                    {/* Header */}
                    <div className="flex items-start justify-between">
                        <div className="flex items-center gap-3">
                            <div className="w-10 h-10 rounded-full bg-zinc-100 text-zinc-900 flex items-center justify-center shrink-0">
                                <LogIn size={20} />
                            </div>
                            <div>
                                <p className="font-black text-sm uppercase text-zinc-900 leading-tight">
                                    {t('favorites.loginRequiredTitle')}
                                </p>
                                <p className="text-xs text-zinc-500 mt-1">
                                    {t('favorites.loginRequiredDesc')}
                                </p>
                            </div>
                        </div>

                        <button
                            onClick={closeLoginPrompt}
                            className="text-zinc-300 hover:text-zinc-900 transition-colors"
                        >
                            <X size={18} />
                        </button>
                    </div>

                    {/* Action Button */}
                    <button
                        onClick={() => {
                            closeLoginPrompt();
                            navigate('/login');
                        }}
                        className="w-full py-3 bg-zinc-900 text-white rounded-xl font-bold text-xs uppercase tracking-widest flex items-center justify-center gap-2 hover:bg-zinc-800 transition-colors"
                    >
                        {t('auth.login')}
                        <ArrowRight size={14} />
                    </button>
                </div>
            </div>
        );
    }

    // Success Notification
    return (
        <div className="fixed bottom-6 right-6 z-50 animate-fade-in-up">
            <div className="bg-white rounded-2xl shadow-xl border border-zinc-100 p-5 w-[340px] flex flex-col gap-4">

                {/* Header */}
                <div className="flex items-start justify-between">
                    <div className="flex items-center gap-3">
                        <div className="w-10 h-10 rounded-full bg-red-50 text-red-500 flex items-center justify-center shrink-0">
                            <Heart size={20} fill="currentColor" />
                        </div>
                        <div>
                            <p className="font-black text-sm uppercase text-zinc-900 leading-tight">
                                {t('favorites.addedTitle', 'Added to favorites')}
                            </p>
                            <p className="text-xs text-zinc-500 mt-1 line-clamp-1">
                                {lastAddedFavorite?.name}
                            </p>
                        </div>
                    </div>

                    <button
                        onClick={clearLastAddedFavorite}
                        className="text-zinc-300 hover:text-zinc-900 transition-colors"
                    >
                        <X size={18} />
                    </button>
                </div>

                {/* Action Button */}
                <button
                    onClick={() => {
                        clearLastAddedFavorite();
                        navigate('/settings/archive');
                    }}
                    className="w-full py-3 bg-zinc-900 text-white rounded-xl font-bold text-xs uppercase tracking-widest flex items-center justify-center gap-2 hover:bg-zinc-800 transition-colors"
                >
                    {t('favorites.goToFavorites', 'Go to favorites')}
                    <ArrowRight size={14} />
                </button>
            </div>
        </div>
    );
};

export default FavoritesNotification;
