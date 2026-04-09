import { http } from "./http";

export type UserDTO = {
  id: number;
  username: string;
  email: string;
  first_name: string;
  last_name: string;
  is_active: boolean;
};

// --- Утиліти для роботи з токеном ---

export function getToken() {
  return localStorage.getItem("authToken");
}

export function setToken(token: string) {
  localStorage.setItem("authToken", token);
}

export function clearToken() {
  localStorage.removeItem("authToken");
}

// --- Функції запитів до API ---

export async function login(payload: {
  username: string;
  password: string;
}) {
  // POST /api/auth/login/
  const data = await http<{ key: string }>("/api/auth/login/", {
    method: "POST",
    body: payload,
  });
  return data.key;
}

export async function register(payload: {
  username: string;
  email?: string;
  password: string;
  password2?: string;
  first_name?: string;
  last_name?: string;
}) {
  // POST /api/auth/register/
  const data = await http<{ key: string }>("/api/auth/register/", {
    method: "POST",
    body: payload,
  });
  return data.key;
}

export function fetchMe() {
  // GET /api/auth/user/
  // Токен додається автоматично завдяки auth: true
  return http<UserDTO>("/api/auth/user/", {
    auth: true,
  });
}

export async function changePassword(payload: {
  current_password: string;
  new_password: string;
  new_password_confirm: string;
}) {
  // POST /api/auth/change-password/
  const data = await http<{ detail: string }>("/api/auth/change-password/", {
    method: "POST",
    auth: true,
    body: payload,
  });
  return data;
}
