
// Mapping specific gallery slugs to coordinates
export const GALLERY_COORDINATES: Record<string, [number, number]> = {
    // Kyiv
    'pinchukartcentre': [50.4418, 30.5222],
    'mystetskyi-arsenal': [50.4363, 30.5540],
    'national-art-museum': [50.4495, 30.5305],
    'khanenko-museum': [50.4410, 30.5144],
    'the-naked-room': [50.4501, 30.5234],
    'arttsentr-ya-halereya-kyyiv': [50.4600, 30.5000], // Ya Gallery
    'avangarden-gallery': [50.4550, 30.4900],
    'shcherbenko-art-centre': [50.4365, 30.5160],
    'voloshyn-gallery': [50.4420, 30.5150],

    // Lviv
    'lviv-gallery': [49.8377, 24.0254],
    'iconart': [49.8420, 24.0320],
    'pm-gallery': [49.8400, 24.0300],
    'dzyga': [49.8430, 24.0330],

    // Odesa
    'ofam': [46.4947, 30.7303], // Odesa Fine Arts Museum
    'dymchuk-gallery': [50.4600, 30.5100], // Dymchuk Gallery (Kyiv)
    'invogue': [46.4800, 30.7400],

    // Dnipro
    'halereya-artsvit-v-stinakh-dccc': [48.4647, 35.0462], // Artsvit

    // Kharkiv
    'yermilov': [50.0050, 36.2300],
    'municipal-kh': [50.0000, 36.2350],
};

// Mapping cities to coordinates
export const CITY_COORDINATES: Record<string, [number, number]> = {
    // Ukrainian cities (Ukrainian)
    'Київ': [50.4501, 30.5234],
    'Львів': [49.8397, 24.0297],
    'Одеса': [46.4825, 30.7233],
    'Дніпро': [48.4647, 35.0462],
    'Харків': [49.9935, 36.2304],
    'Івано-Франківськ': [48.9226, 24.7111],
    'Чернівці': [48.2909, 25.9348],
    'Ужгород': [48.6208, 22.2879],
    'Луцьк': [50.7472, 25.3254],
    'Тернопіль': [49.5535, 25.5948],
    'Вінниця': [49.2331, 28.4682],
    'Херсон': [46.6354, 32.6169],
    'Полтава': [49.5883, 34.5514],
    'Чернігів': [51.4982, 31.2893],
    'Запоріжжя': [47.8388, 35.1396],

    // Ukrainian cities (English)
    'Kyiv': [50.4501, 30.5234],
    'Lviv': [49.8397, 24.0297],
    'Odesa': [46.4825, 30.7233],
    'Dnipro': [48.4647, 35.0462],
    'Kharkiv': [49.9935, 36.2304],

    // International cities
    'Greenwich, Connecticut 06836, USA': [41.0262, -73.6282],
    'Greenwich, Connecticut': [41.0262, -73.6282],
    'Greenwich': [41.0262, -73.6282],
    'Connecticut': [41.6032, -73.0877],
    'Paphos': [34.7571, 32.4134],
    'Cyprus': [35.1264, 33.4299],
    'Пафос': [34.7571, 32.4134],
    'Кіпр': [35.1264, 33.4299],
    'London': [51.5074, -0.1278],
    'Лондон': [51.5074, -0.1278],
    'Berlin': [52.5200, 13.4050],
    'Берлін': [52.5200, 13.4050],
    'Paris': [48.8566, 2.3522],
    'Париж': [48.8566, 2.3522],
    'New York': [40.7128, -74.0060],
    'Нью-Йорк': [40.7128, -74.0060],
    'Warsaw': [52.2297, 21.0122],
    'Варшава': [52.2297, 21.0122],
    'Vienna': [48.2082, 16.3738],
    'Відень': [48.2082, 16.3738],
};

// Deterministic random number generator based on string seed
export const seededRandom = (seed: string) => {
    let value = 0;
    for (let i = 0; i < seed.length; i++) {
        value = (value << 5) - value + seed.charCodeAt(i);
        value |= 0; // Convert to 32bit integer
    }
    const x = Math.sin(value) * 10000;
    return x - Math.floor(x);
};
