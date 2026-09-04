import { getInitData } from "./telegram";

const API = import.meta.env.VITE_API_URL || "";

export function mediaUrl(path) {
  if (!path) return null;
  if (path.startsWith("http")) return path;
  return `${API}${path}`;
}

export async function api(path, { method = "GET", json, form } = {}) {
  const headers = { Authorization: `tma ${getInitData()}` };
  let body;
  if (form) {
    body = form;
  } else if (json !== undefined) {
    headers["Content-Type"] = "application/json";
    body = JSON.stringify(json);
  }

  const res = await fetch(`${API}${path}`, { method, headers, body });
  if (res.status === 204) return null;

  const data = await res.json().catch(() => ({}));
  if (!res.ok) {
    const detail = data.detail;
    const message = typeof detail === "string" ? detail : res.statusText;
    throw new Error(message || "Ошибка запроса");
  }
  return data;
}