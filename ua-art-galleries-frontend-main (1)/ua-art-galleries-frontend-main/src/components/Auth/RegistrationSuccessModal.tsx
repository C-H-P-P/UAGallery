import { useNavigate } from "react-router-dom";
import { CheckCircle2, ArrowRight } from "lucide-react";
import { useTranslation } from "react-i18next";

const RegistrationSuccessModal = ({ onClose }: { onClose: () => void }) => {
    const { t } = useTranslation();
    const navigate = useNavigate();

    return (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-6 bg-black/40 backdrop-blur-sm animate-in fade-in duration-300">
            <div className="bg-white rounded-[32px] p-10 max-w-sm w-full shadow-2xl scale-100 animate-in zoom-in-95 duration-300 flex flex-col items-center text-center">

                {/* Icon Animation Wrapper */}
                <div className="w-20 h-20 bg-green-50 rounded-full flex items-center justify-center mb-6 animate-bounce-slow">
                    <CheckCircle2 size={40} className="text-green-500" />
                </div>

                <h2 className="text-2xl font-black uppercase text-zinc-900 mb-3 tracking-tight">
                    {t('auth.registrationSuccessTitle')}
                </h2>

                <p className="text-zinc-500 font-medium leading-relaxed mb-8">
                    {t('auth.registrationSuccessDesc')}
                </p>

                <button
                    onClick={() => {
                        onClose();
                        navigate('/');
                    }}
                    className="w-full py-4 bg-zinc-900 text-white rounded-2xl font-black uppercase text-xs tracking-[0.15em] hover:bg-zinc-800 hover:scale-[1.02] transition-all duration-300 flex items-center justify-center gap-3 shadow-lg shadow-zinc-200"
                >
                    {t('auth.getStarted')}
                    <ArrowRight size={16} />
                </button>

            </div>
        </div>
    );
};

export default RegistrationSuccessModal;
