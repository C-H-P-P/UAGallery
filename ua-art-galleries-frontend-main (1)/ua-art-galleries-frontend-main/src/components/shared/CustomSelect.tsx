import { useState, useRef, useEffect } from 'react';
import { ChevronDown } from 'lucide-react';

interface Option {
    value: string;
    label: string;
}

interface CustomSelectProps {
    value: string;
    onChange: (value: string) => void;
    options: Option[];
    className?: string;
}

export const CustomSelect = ({ value, onChange, options, className = "" }: CustomSelectProps) => {
    const [isOpen, setIsOpen] = useState(false);
    const containerRef = useRef<HTMLDivElement>(null);

    const selectedOption = options.find((o) => o.value === value) || options[0];

    useEffect(() => {
        const handleClickOutside = (event: MouseEvent) => {
            if (containerRef.current && !containerRef.current.contains(event.target as Node)) {
                setIsOpen(false);
            }
        };
        document.addEventListener("mousedown", handleClickOutside);
        return () => document.removeEventListener("mousedown", handleClickOutside);
    }, []);

    return (
        <div className={`relative ${className}`} ref={containerRef}>
            <button
                onClick={() => setIsOpen(!isOpen)}
                className={`w-full h-[56px] px-5 rounded-2xl border bg-white flex items-center justify-between transition-all ${isOpen ? 'border-zinc-900 ring-4 ring-zinc-50' : 'border-zinc-200 hover:border-zinc-400'
                    }`}
            >
                <span className="text-sm font-bold text-zinc-900 truncate pr-4">
                    {selectedOption.label}
                </span>
                <ChevronDown
                    size={16}
                    className={`text-zinc-400 transition-transform duration-300 ${isOpen ? 'rotate-180' : ''}`}
                />
            </button>

            {isOpen && (
                <div className="absolute top-full left-0 right-0 mt-2 bg-white border border-zinc-100 rounded-2xl shadow-xl overflow-hidden z-50 animate-in fade-in zoom-in-95 duration-200">
                    <div className="max-h-[300px] overflow-y-auto py-2">
                        {options.map((option) => (
                            <button
                                key={option.value}
                                onClick={() => {
                                    onChange(option.value);
                                    setIsOpen(false);
                                }}
                                className={`w-full flex items-center justify-between px-5 py-3 text-left transition-colors ${option.value === value
                                        ? 'bg-zinc-50 text-black'
                                        : 'text-zinc-600 hover:bg-zinc-50 hover:text-black'
                                    }`}
                            >
                                <span className="text-sm font-bold">{option.label}</span>
                                {option.value === value && (
                                    <div className="w-1.5 h-1.5 rounded-full bg-black" />
                                )}
                            </button>
                        ))}
                    </div>
                </div>
            )}
        </div>
    );
};
