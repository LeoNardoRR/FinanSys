export type Transaction = {
  id: number;
  occurred_on: string;
  description: string;
  amount: number;
  kind: "income" | "expense";
};

export type Dashboard = {
  month: string;
  income: number;
  expenses: number;
  balance: number;
  recent_transactions: Transaction[];
  alerts: {level: string; text: string}[];
};

const API_URL = (process.env.EXPO_PUBLIC_API_URL || "http://127.0.0.1:8000").replace(/\/$/, "");
const API_TOKEN = process.env.EXPO_PUBLIC_API_TOKEN || "";

export async function api<T>(path: string, init?: RequestInit): Promise<T> {
  const response = await fetch(`${API_URL}/api/v1${path}`, {
    ...init,
    headers: {
      "Content-Type": "application/json",
      ...(API_TOKEN ? {"X-API-Token": API_TOKEN} : {}),
      ...(init?.headers || {}),
    },
  });
  if (!response.ok) throw new Error(`API respondeu ${response.status}`);
  return response.json() as Promise<T>;
}

export const formatMoney = (value: number) =>
  new Intl.NumberFormat("pt-BR", {style: "currency", currency: "BRL"}).format(value);
