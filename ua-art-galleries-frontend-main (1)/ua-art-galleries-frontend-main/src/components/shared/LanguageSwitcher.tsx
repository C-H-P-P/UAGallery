import { useTranslation } from 'react-i18next';
import { useState, useRef, useEffect } from "react";
import { ChevronDown } from "lucide-react";

const LanguageSwitcher = () => {
    const { i18n } = useTranslation();
    const [isOpen, setIsOpen] = useState(false);
    const menuRef = useRef<HTMLDivElement>(null);

    useEffect(() => {
        const handleClickOutside = (e: MouseEvent) => {
            if (menuRef.current && !menuRef.current.contains(e.target as Node)) {
                setIsOpen(false);
            }
        };
        document.addEventListener("mousedown", handleClickOutside);
        return () => document.removeEventListener("mousedown", handleClickOutside);
    }, []);

    const changeLanguage = (lng: string) => {
        i18n.changeLanguage(lng);
        localStorage.setItem('language', lng);
        setIsOpen(false);
    };

    const currentLang = i18n.language;

    return (
        <div className="relative z-50" ref={menuRef}>
            <button 
                className="flex items-center gap-1.5 px-3 py-2 rounded-xl border border-gray-50 bg-white hover:bg-gray-50 transition-all shadow-sm"
            >
                <span 
                    onClick={() => setIsOpen(!isOpen)}
                    className="text-sm font-bold uppercase tracking-widest text-zinc-800 cursor-pointer"
                >
                    {currentLang === 'uk' ? 'UA' : 'ENG'}
                </span>
                <ChevronDown 
                  size={14} 
                  className={`text-zinc-400 transition-transform cursor-pointer ${isOpen ? "rotate-180" : ""}`} 
                  onClick={() => setIsOpen(!isOpen)}
                />
            </button>

            {/* Dropdown */}
            {isOpen && (
                <div className="absolute right-0 top-full mt-2 w-auto min-w-[100px] bg-white border border-gray-100 rounded-xl shadow-lg overflow-hidden animate-in fade-in zoom-in-95 duration-200">
                    <button
                        onClick={() => changeLanguage('uk')}
                        className={`w-full px-4 py-3 text-left text-xs font-bold uppercase tracking-widest hover:bg-gray-50 transition-colors flex items-center justify-center gap-3 ${currentLang === 'uk' ? 'bg-gray-50 text-black' : 'text-zinc-500'
                            }`}
                    >
                        <span>UA</span>
                    </button>
                    <button
                        onClick={() => changeLanguage('en')}
                        className={`w-full px-4 py-3 text-left text-xs font-bold uppercase tracking-widest hover:bg-gray-50 transition-colors flex items-center justify-center gap-3 ${currentLang === 'en' ? 'bg-gray-50 text-black' : 'text-zinc-500'
                            }`}
                    >
                        <span>ENG</span>
                    </button>
                </div>
            )}
        </div>
    );
};

export default LanguageSwitcher;
