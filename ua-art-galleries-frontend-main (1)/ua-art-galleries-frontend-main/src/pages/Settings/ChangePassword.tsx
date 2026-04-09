import { Lock, ShieldCheck, ArrowRight, CheckCircle2 } from "lucide-react";
import { useState } from "react";
import { changePassword } from "../../api/auth";

const ChangePasswordPage = () => {
  const [formData, setFormData] = useState({
    currentPassword: "",
    newPassword: "",
    confirmPassword: "",
  });

  const [errors, setErrors] = useState({
    currentPassword: "",
    newPassword: "",
    confirmPassword: "",
    general: "",
  });

  const [isLoading, setIsLoading] = useState(false);
  const [success, setSuccess] = useState(false);

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value } = e.target;
    setFormData((prev) => ({ ...prev, [name]: value }));
    // Очищаємо помилки при введенні
    setErrors((prev) => ({ ...prev, [name]: "", general: "" }));
    setSuccess(false);
  };

  const validateForm = () => {
    const newErrors = {
      currentPassword: "",
      newPassword: "",
      confirmPassword: "",
      general: "",
    };

    if (!formData.currentPassword) {
      newErrors.currentPassword = "Введіть поточний пароль";
    }

    if (!formData.newPassword) {
      newErrors.newPassword = "Введіть новий пароль";
    } else if (formData.newPassword.length < 8) {
      newErrors.newPassword = "Мінімум 8 символів";
    }

    if (!formData.confirmPassword) {
      newErrors.confirmPassword = "Підтвердіть пароль";
    } else if (formData.newPassword !== formData.confirmPassword) {
      newErrors.confirmPassword = "Паролі не співпадають";
    }

    if (formData.currentPassword === formData.newPassword && formData.currentPassword) {
      newErrors.newPassword = "Новий пароль має відрізнятися від поточного";
    }

    setErrors(newErrors);
    return !Object.values(newErrors).some((error) => error !== "");
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!validateForm()) return;

    setIsLoading(true);
    setErrors({ currentPassword: "", newPassword: "", confirmPassword: "", general: "" });

    try {
      await changePassword({
        current_password: formData.currentPassword,
        new_password: formData.newPassword,
        new_password_confirm: formData.confirmPassword,
      });

      // Успіх!
      setSuccess(true);
      setFormData({
        currentPassword: "",
        newPassword: "",
        confirmPassword: "",
      });
    } catch (error: any) {
      // Обробка помилок від сервера
      const errorMessage = error?.message || "Помилка при зміні пароля";

      if (errorMessage.includes("поточний пароль") || errorMessage.includes("невірний")) {
        setErrors((prev) => ({ ...prev, currentPassword: errorMessage }));
      } else if (errorMessage.includes("не співпадають")) {
        setErrors((prev) => ({ ...prev, confirmPassword: errorMessage }));
      } else if (errorMessage.includes("мінімум") || errorMessage.includes("символів")) {
        setErrors((prev) => ({ ...prev, newPassword: errorMessage }));
      } else {
        setErrors((prev) => ({ ...prev, general: errorMessage }));
      }
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="max-w-md animate-in fade-in duration-700">

      {/* Скляна картка у стилі Dropdown */}
      <div className="bg-white/90 backdrop-blur-2xl border border-gray-100 rounded-[32px] shadow-[0_20px_50px_rgba(0,0,0,0.05)] p-8 space-y-8">

        {/* Заголовок */}
        <section className="space-y-1">
          <p className="text-[10px] font-black uppercase tracking-[0.25em] text-zinc-500">Безпека</p>
          <h2 className="text-xl font-bold text-black">Зміна пароля</h2>
        </section>

        {/* Форма */}
        <form className="space-y-6" onSubmit={handleSubmit}>

          <div className="space-y-5">
            <PasswordInput
              label="Поточний пароль"
              placeholder="••••••••"
              name="currentPassword"
              value={formData.currentPassword}
              onChange={handleChange}
              error={errors.currentPassword}
            />

            <div className="pt-2 space-y-5 border-t border-gray-100">
              <PasswordInput
                label="Новий пароль"
                placeholder="Введіть новий пароль"
                name="newPassword"
                value={formData.newPassword}
                onChange={handleChange}
                error={errors.newPassword}
              />
              <PasswordInput
                label="Підтвердження"
                placeholder="Повторіть пароль"
                name="confirmPassword"
                value={formData.confirmPassword}
                onChange={handleChange}
                error={errors.confirmPassword}
              />
            </div>
          </div>

          {/* Загальна помилка */}
          {errors.general && (
            <div className="px-4 py-3 bg-red-50/40 rounded-2xl border border-red-100/50">
              <p className="text-[11px] text-red-800 font-semibold leading-tight">
                {errors.general}
              </p>
            </div>
          )}

          {/* Повідомлення про успіх */}
          {success && (
            <div className="flex items-center gap-3 px-4 py-3 bg-green-50/40 rounded-2xl border border-green-100/50">
              <CheckCircle2 className="text-green-600" size={16} />
              <p className="text-[11px] text-green-800 font-semibold leading-tight">
                Пароль успішно змінено!
              </p>
            </div>
          )}

          {/* Кнопка */}
          <button
            type="submit"
            disabled={isLoading}
            className="group w-full py-4 bg-black text-white rounded-2xl flex items-center justify-center gap-3 hover:bg-neutral-800 transition-all duration-300 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            <span className="text-[11px] font-black uppercase tracking-[0.2em] ml-2">
              {isLoading ? "Оновлення..." : "Оновити дані"}
            </span>
            {!isLoading && <ArrowRight size={16} className="group-hover:translate-x-1 transition-transform" />}
          </button>
        </form>

        {/* Порада */}
        <div className="flex items-center gap-3 px-4 py-3 bg-blue-50/40 rounded-2xl border border-blue-100/50">
          <ShieldCheck className="text-blue-600" size={16} />
          <p className="text-[11px] text-blue-800 font-semibold leading-tight">
            Пароль має бути надійним та унікальним.
          </p>
        </div>
      </div>
    </div>
  );
};

/* Контрастний інпут */
const PasswordInput = ({
  label,
  placeholder,
  name,
  value,
  onChange,
  error
}: {
  label: string;
  placeholder: string;
  name: string;
  value: string;
  onChange: (e: React.ChangeEvent<HTMLInputElement>) => void;
  error?: string;
}) => (
  <div className="space-y-2 group">
    <label className="text-[10px] font-bold uppercase tracking-wider text-zinc-500 group-focus-within:text-black transition-colors">
      {label}
    </label>
    <div className="relative">
      <input
        type="password"
        name={name}
        value={value}
        onChange={onChange}
        placeholder={placeholder}
        className={`w-full text-sm font-bold text-black border-b ${error ? 'border-red-400' : 'border-gray-200'
          } focus:border-black focus:outline-none bg-transparent pb-2 transition-all placeholder:text-gray-400`}
      />
      <Lock size={14} className={`absolute right-0 top-0 ${error ? 'text-red-400' : 'text-gray-300'
        } group-focus-within:text-black transition-colors`} />
    </div>
    {error && (
      <p className="text-[10px] text-red-600 font-semibold">{error}</p>
    )}
  </div>
);

export default ChangePasswordPage;