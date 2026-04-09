import { Link } from "react-router-dom";
import { useTranslation } from 'react-i18next';
import { ArrowLeft } from "lucide-react";

const ContactsPage = () => {
    const { t } = useTranslation();
    return (
        <div className="container mx-auto px-6 py-32 max-w-4xl">
            <Link to="/" className="inline-flex items-center gap-2 text-zinc-500 hover:text-black transition-colors mb-16 font-bold text-xs uppercase tracking-widest">
                <ArrowLeft size={14} /> {t('common.backToHome') || 'Back'}
            </Link>

            <div className="grid md:grid-cols-2 gap-16">
                <div className="space-y-8">
                    <h1 className="text-5xl font-black text-zinc-900 uppercase tracking-tighter">
                        {t('contacts.title') || "Контакти"}
                    </h1>
                    <p className="text-zinc-500 font-medium text-lg leading-relaxed">
                        Ми завжди раді почути ваші ідеї, пропозиції або запитання. Зв'яжіться з нами будь-яким зручним способом.
                    </p>
                </div>

                <div className="space-y-6">
                    <ContactItem label="Email" value="hello@uagalleries.com" />
                    <ContactItem label="Instagram" value="@uagalleries" />
                    <ContactItem label="Telegram" value="@uagalleries_bot" />
                    <ContactItem label="Address" value="Lviv, Ukraine" />
                </div>
            </div>
        </div>
    );
};

const ContactItem = ({ label, value }: { label: string, value: string }) => (
    <div className="flex items-center justify-between p-6 bg-white border border-zinc-100 rounded-[24px] hover:border-zinc-300 transition-colors cursor-default">
        <span className="text-xs font-black uppercase tracking-widest text-zinc-400">{label}</span>
        <span className="font-bold text-zinc-900">{value}</span>
    </div>
);

export default ContactsPage;
