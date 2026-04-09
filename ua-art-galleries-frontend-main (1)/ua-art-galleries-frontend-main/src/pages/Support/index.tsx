import { useTranslation } from "react-i18next";
import { Mail, MessageCircle, AlertCircle } from "lucide-react";

const SupportPage = () => {
  const { t } = useTranslation();

  return (
    <div className="min-h-screen pt-32 pb-24">
      <div className="container mx-auto px-6 max-w-4xl">
        <h1 className="text-4xl md:text-5xl font-black uppercase tracking-tight mb-4 text-center">
          {t('footer.links.support', 'Підтримка')}
        </h1>
        <p className="text-center text-zinc-500 font-medium mb-16 max-w-xl mx-auto">
          {t('support.subtitle', 'Виникли труднощі чи маєте пропозиції? Зв\'яжіться з нашою службою підтримки.')}
        </p>

        <div className="grid md:grid-cols-3 gap-6 mb-16">
          <div className="bg-white border border-zinc-100 p-8 rounded-[32px] text-center shadow-[0_8px_30px_rgba(0,0,0,0.04)] hover:shadow-lg transition-shadow">
            <div className="w-16 h-16 bg-blue-50 text-blue-500 rounded-full flex items-center justify-center mx-auto mb-6">
              <Mail size={24} />
            </div>
            <h3 className="font-bold text-lg mb-2">Email</h3>
            <p className="text-zinc-500 text-sm mb-4">Для загальних запитань та співпраці</p>
            <a href="mailto:support@uagalleries.com" className="font-black text-zinc-900 border-b border-black">support@uagalleries.com</a>
          </div>

          <div className="bg-white border border-zinc-100 p-8 rounded-[32px] text-center shadow-[0_8px_30px_rgba(0,0,0,0.04)] hover:shadow-lg transition-shadow">
            <div className="w-16 h-16 bg-green-50 text-green-500 rounded-full flex items-center justify-center mx-auto mb-6">
              <MessageCircle size={24} />
            </div>
            <h3 className="font-bold text-lg mb-2">Telegram</h3>
            <p className="text-zinc-500 text-sm mb-4">Для швидкої технічної підтримки</p>
            <a href="https://t.me/uagalleries_support" target="_blank" rel="noreferrer" className="font-black text-zinc-900 border-b border-black">@uagalleries_support</a>
          </div>

          <div className="bg-white border border-zinc-100 p-8 rounded-[32px] text-center shadow-[0_8px_30px_rgba(0,0,0,0.04)] hover:shadow-lg transition-shadow">
            <div className="w-16 h-16 bg-orange-50 text-orange-500 rounded-full flex items-center justify-center mx-auto mb-6">
              <AlertCircle size={24} />
            </div>
            <h3 className="font-bold text-lg mb-2">Повідомити про помилку</h3>
            <p className="text-zinc-500 text-sm mb-4">Знайшли технічну проблему на сайті?</p>
            <button className="px-6 py-2 bg-zinc-900 text-white font-bold rounded-xl text-xs uppercase tracking-widest hover:bg-zinc-800 transition-colors">
              Заповнити форму
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default SupportPage;
