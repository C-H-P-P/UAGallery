// src/pages/Home/index.tsx
import HomeHero from '../../components/home/HomeHero.tsx';
import HomeSearch from '../../components/home/HomeSearch.tsx';
import HomeFeaturedGalleries from '../../components/home/HomeFeaturedGalleries.tsx';
import HomeMapView from '../../components/home/HomeMapView.tsx';
import HomeAbout from '../../components/home/HomeAbout.tsx';

const HomePage = () => {
  return (
    <div className="pb-24 space-y-32 animate-in fade-in duration-700">
      <HomeHero />
      <HomeSearch />
      <div className="container mx-auto px-6 space-y-32">
        <HomeFeaturedGalleries /> {/* Замість HomeNews */}
        <HomeMapView />
        <HomeAbout />
      </div>
    </div>
  );
};

export default HomePage;