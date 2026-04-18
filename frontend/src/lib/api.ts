import type { BoardData } from "@/lib/kanban";

type BoardResponse = BoardData & { boardId: string };

type ApiOptions = RequestInit & { headers?: Record<string, string> };

export type AiChatMessage = {
  role: "user" | "assistant";
  content: string;
};

const request = async <T>(
  url: string,
  options: ApiOptions = {},
): Promise<T> => {
  const response = await fetch(url, {
    ...options,
    headers: {
      "Content-Type": "application/json",
      ...(options.headers ?? {}),
    },
  });

  if (!response.ok) {
    throw new Error(`Request failed: ${response.status}`);
  }

  return (await response.json()) as T;
};

export const fetchBoard = async (username: string): Promise<BoardData> => {
  const data = await request<BoardResponse>(`/api/board?username=${username}`);
  return { columns: data.columns, cards: data.cards };
};

export const updateColumn = async (columnId: string, title: string) => {
  return request<{ status: string }>(`/api/columns/${columnId}`, {
    method: "PATCH",
    body: JSON.stringify({ title }),
  });
};

export const createCard = async (
  username: string,
  columnId: string,
  title: string,
  details: string,
) => {
  return request<{
    id: string;
    columnId: string;
    title: string;
    details: string;
    position: number;
  }>("/api/cards", {
    method: "POST",
    body: JSON.stringify({
      username,
      column_id: columnId,
      title,
      details,
    }),
  });
};

export const updateCard = async (
  cardId: string,
  payload: {
    title?: string;
    details?: string;
    column_id?: string;
    position?: number;
  },
) => {
  return request<{ status: string }>(`/api/cards/${cardId}`, {
    method: "PATCH",
    body: JSON.stringify(payload),
  });
};

export const deleteCard = async (cardId: string) => {
  return request<{ status: string }>(`/api/cards/${cardId}`, {
    method: "DELETE",
  });
};

export const aiQuery = async (
  username: string,
  question: string,
  history: AiChatMessage[],
) => {
  return request<{
    reply: string;
    applied: boolean;
    board: BoardData;
  }>("/api/ai/query", {
    method: "POST",
    body: JSON.stringify({ username, question, history }),
  });
};
