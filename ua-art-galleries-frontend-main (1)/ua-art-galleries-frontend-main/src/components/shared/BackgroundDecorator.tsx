const BackgroundDecorator = () => {
  return (
    <div className="fixed inset-0 -z-10 overflow-hidden bg-[#FBFBFB] pointer-events-none">
      
      {/* 1. ГЕОМЕТРИЧНА ОСНОВА (Тінь від стіни/вікна) */}
      {/* Використовуємо Skew для створення динаміки */}
      <div className="absolute top-[-10%] left-[-5%] w-[60vw] h-[110vh] bg-zinc-200/40 -skew-x-12 blur-[100px]" />

      {/* 2. СВІТЛОВИЙ АКЦЕНТ (Промінь світла) */}
      {/* Прямокутник, що імітує сонячне світло, яке падає на підлогу */}
      <div className="absolute top-[20%] right-[10%] w-[40vw] h-[80vh] bg-white shadow-[0_0_150px_rgba(255,255,255,0.8)] rotate-12 blur-[60px]" />

      {/* 3. "МАТЕРІАЛЬНІСТЬ" (Текстура полотна) */}
      {/* Додаємо дуже слабке зерно, щоб фон не здавався "пластиковим" */}
      <div 
        className="absolute inset-0 opacity-[0.04] mix-blend-multiply" 
        style={{ 
          backgroundImage: `url('https://grainy-gradients.vercel.app/noise.svg')`,
          filter: 'contrast(120%) brightness(110%)' 
        }} 
      />

      {/* 4. ГЛИБОКА ТІНЬ ЗНИЗУ */}
      <div className="absolute -bottom-48 -right-48 w-[800px] h-[600px] bg-slate-200/30 rounded-full blur-[180px]" />

      {/* 5. АКЦЕНТНА ЛІНІЯ (The Gallery Edge) */}
      {/* Тонка, ледь помітна лінія, що розділяє простір */}
      <div className="absolute left-[20%] top-0 w-[1px] h-full bg-zinc-900/[0.03]" />
    </div>
  );
};

export default BackgroundDecorator;