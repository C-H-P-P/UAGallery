import { useTranslation } from "react-i18next";
import { ChevronDown } from "lucide-react";
import { useState } from "react";

const FAQPage = () => {
  const { t } = useTranslation();
  const [openIndex, setOpenIndex] = useState<number | null>(0);

  const faqs = [
    {
      q: t('faq.q1', 'Як додати свою галерею до бази?'),
      a: t('faq.a1', 'Щоб додати галерею, перейдіть до розділу "Для галерей" або "Приєднатись / Зареєструватись" та заповніть форму заявки. Наша команда перевірить інформацію та зв\'яжеться з вами для подальших кроків.')
    },
    {
      q: t('faq.q2', 'Чи можу я зберігати галереї у свій архів?'),
      a: t('faq.a2', 'Так, після реєстрації та входу до системи ви можете натискати на іконку "сердечка" біля будь-якої галереї. Вона буде збережена у вашому особистому кабінеті в розділі "Мій архів".')
    },
    {
      q: t('faq.q3', 'Які переваги мають зареєстровані користувачі?'),
      a: t('faq.a3', 'Авторизовані користувачі можуть бачити повну інформацію про галереї, включаючи поточні виставки, список митців та публікації, а також мають можливість зберігати галереї до обраного.')
    },
    {
      q: t('faq.q4', 'Чи є інформація на сайті безкоштовною?'),
      a: t('faq.a4', 'Так, користування базою даних Ukrainian Galleries є абсолютно безкоштовним як для користувачів, так і для інституцій.')
    }
  ];

  return (
    <div className="min-h-screen pt-32 pb-24">
      <div className="container mx-auto px-6 max-w-3xl">
        <h1 className="text-4xl md:text-5xl font-black uppercase tracking-tight mb-4 text-center">
          {t('footer.links.faq', 'FAQ')}
        </h1>
        <p className="text-center text-zinc-500 font-medium mb-12">
          {t('faq.subtitle', 'Відповіді на найпоширеніші запитання')}
        </p>

        <div className="space-y-4">
          {faqs.map((faq, index) => {
            const isOpen = openIndex === index;
            return (
              <div 
                key={index} 
                className={`border rounded-2xl overflow-hidden transition-all duration-300 ${isOpen ? 'border-zinc-300 bg-white shadow-sm' : 'border-zinc-100 bg-zinc-50 hover:border-zinc-200'}`}
              >
                <button
                  onClick={() => setOpenIndex(isOpen ? null : index)}
                  className="w-full flex items-center justify-between p-6 text-left"
                >
                  <span className="font-bold text-zinc-900 pr-4">{faq.q}</span>
                  <ChevronDown className={`shrink-0 text-zinc-400 transition-transform duration-300 ${isOpen ? 'rotate-180' : ''}`} />
                </button>
                <div 
                  className={`overflow-hidden transition-all duration-300 ${isOpen ? 'max-h-96 opacity-100' : 'max-h-0 opacity-0'}`}
                >
                  <div className="p-6 pt-0 text-zinc-500 font-medium leading-relaxed">
                    {faq.a}
                  </div>
                </div>
              </div>
            );
          })}
        </div>
      </div>
    </div>
  );
};

export default FAQPage;
