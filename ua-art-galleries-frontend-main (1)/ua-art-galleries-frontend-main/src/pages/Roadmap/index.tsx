import { Link } from "react-router-dom";
import { useTranslation } from 'react-i18next';
import { ArrowLeft } from "lucide-react";

const RoadmapPage = () => {
    const { t } = useTranslation();
    return (
        <div className="container mx-auto px-6 py-32 max-w-4xl text-center">
            <Link to="/" className="inline-flex items-center gap-2 text-zinc-500 hover:text-black transition-colors mb-8 font-bold text-xs uppercase tracking-widest">
                <ArrowLeft size={14} /> {t('common.backToHome') || 'Back'}
            </Link>
            <h1 className="text-4xl font-black uppercase mb-4">Roadmap</h1>
            <p className="text-zinc-500">Development plan and future updates will be posted here.</p>
        </div>
    );
};

export default RoadmapPage;
