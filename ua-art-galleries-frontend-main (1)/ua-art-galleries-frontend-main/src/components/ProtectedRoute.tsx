import { Navigate, Outlet } from "react-router-dom";
import { useAuth } from "../hooks/useAuth";

const ProtectedRoute = () => {
  const auth = useAuth();

  if (!auth) return null;

  const { user, isLoading } = auth;

  if (isLoading) {
    return (
      <div className="flex justify-center items-center h-[60vh] text-gray-500">
        Перевірка авторизації…
      </div>
    );
  }

  if (!user) {
    return <Navigate to="/login" replace />;
  }

  return <Outlet />;
};

export default ProtectedRoute;
