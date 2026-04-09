import { ArrowRight, ArrowLeft } from 'lucide-react';
import { useState, useEffect } from 'react';
import { useTranslation } from 'react-i18next';
import heroImage1 from '../../assets/hero/slide1.png';
import heroImage2 from '../../assets/hero/slide2.png';
import heroImage3 from '../../assets/hero/slide3.png';

const HomeHero = () => {
  const { t } = useTranslation();
  const [currentSlideIndex, setCurrentSlideIndex] = useState(0);

  const SLIDES = [
    {
      id: 1,
      titleKey: 'home.hero.slide1.title',
      subtitleKey: 'home.hero.slide1.subtitle',
      image: heroImage1
    },
    {
      id: 2,
      titleKey: 'home.hero.slide2.title',
      subtitleKey: 'home.hero.slide2.subtitle',
      image: heroImage2
    },
    {
      id: 3,
      titleKey: 'home.hero.slide3.title',
      subtitleKey: 'home.hero.slide3.subtitle',
      image: heroImage3
    },
  ];

  const currentSlide = SLIDES[currentSlideIndex];

  // Auto-advance slides every 6 seconds
  useEffect(() => {
    const timer = setInterval(() => {
      setCurrentSlideIndex((prev) => (prev === SLIDES.length - 1 ? 0 : prev + 1));
    }, 6000);
    return () => clearInterval(timer);
  }, [SLIDES.length]);

  return (
    <section className="container mx-auto px-4 md:px-6 pt-6 md:pt-10">
      <div className="relative h-[400px] md:h-[500px] rounded-[32px] md:rounded-[48px] overflow-hidden shadow-2xl group">

        {/* Background Image with Ken Burns Effect */}
        {SLIDES.map((slide, index) => (
          <div
            key={slide.id}
            className={`absolute inset-0 transition-opacity duration-1000 ease-in-out ${index === currentSlideIndex ? 'opacity-100' : 'opacity-0'}`}
          >
            <div className={`absolute inset-0 bg-black/40 z-10`} /> {/* Overlay for text readability */}
            <img
              src={slide.image}
              alt=""
              className={`w-full h-full object-cover transform transition-transform duration-[20000ms] ease-linear ${index === currentSlideIndex ? 'scale-110' : 'scale-100'}`}
            />
          </div>
        ))}

        {/* Content */}
        <div className="absolute inset-x-0 bottom-0 top-0 z-20 flex flex-col items-center justify-center text-center px-6 md:px-20 space-y-6 md:space-y-8">
          {/* Animated Badge */}
          <div
            key={`badge-${currentSlideIndex}`}
            className="animate-fade-in-up px-4 py-1.5 bg-white/20 backdrop-blur-xl border border-white/10 rounded-full text-[10px] md:text-xs font-black uppercase tracking-[0.3em] text-white shadow-lg"
          >
            UA Galleries
          </div>

          {/* Animated Title */}
          <h1
            key={`title-${currentSlideIndex}`}
            className="animate-fade-in-up delay-200 text-4xl md:text-7xl font-black text-white tracking-tighter leading-[1.1] max-w-4xl drop-shadow-xl"
          >
            {t(currentSlide.titleKey)}
          </h1>

          {/* Animated Subtitle */}
          <p
            key={`sub-${currentSlideIndex}`}
            className="animate-fade-in-up delay-400 text-base md:text-xl text-white/80 font-medium max-w-lg leading-relaxed drop-shadow-md"
          >
            {t(currentSlide.subtitleKey)}
          </p>


        </div>

        {/* Navigation Arrows */}
        <div className="absolute inset-x-4 md:inset-x-12 top-1/2 -translate-y-1/2 flex justify-between z-30 opacity-0 group-hover:opacity-100 transition-opacity duration-300">
          <NavButton icon={<ArrowLeft size={20} />} onClick={() => setCurrentSlideIndex(v => v === 0 ? SLIDES.length - 1 : v - 1)} />
          <NavButton icon={<ArrowRight size={20} />} onClick={() => setCurrentSlideIndex(v => v === SLIDES.length - 1 ? 0 : v + 1)} />
        </div>

        {/* Dots Indicator */}
        <div className="absolute bottom-8 left-1/2 -translate-x-1/2 flex gap-3 z-30">
          {SLIDES.map((_, i) => (
            <button
              key={i}
              onClick={() => setCurrentSlideIndex(i)}
              className={`h-1.5 rounded-full transition-all duration-500 ${i === currentSlideIndex ? 'w-10 bg-white' : 'w-2 bg-white/40 hover:bg-white/70'}`}
            />
          ))}
        </div>
      </div>
    </section>
  );
};

const NavButton = ({ icon, onClick }: { icon: React.ReactNode, onClick: () => void }) => (
  <button onClick={onClick} className="w-12 h-12 md:w-14 md:h-14 flex items-center justify-center bg-black/20 backdrop-blur-md border border-white/10 rounded-full text-white hover:bg-white hover:text-black hover:scale-110 transition-all duration-300 shadow-xl">
    {icon}
  </button>
);

export default HomeHero;