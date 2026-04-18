"use client";

import { useMemo, useState } from "react";
import type { BoardData } from "@/lib/kanban";
import { aiQuery, type AiChatMessage } from "@/lib/api";

type LocalMessage = AiChatMessage & { applied?: boolean };

type AiSidebarProps = {
  username: string;
  onBoardUpdate: (board: BoardData) => void;
};

const suggestions = [
  "Move card-1 to Review",
  "Rename Backlog to Ideas",
  "Add a card in Done for release notes",
];

export const AiSidebar = ({ username, onBoardUpdate }: AiSidebarProps) => {
  const [messages, setMessages] = useState<LocalMessage[]>([]);
  const [input, setInput] = useState("");
  const [isSending, setIsSending] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const canSend = useMemo(
    () => input.trim().length > 0 && !isSending,
    [input, isSending],
  );

  const handleSend = async (question: string) => {
    const trimmed = question.trim();
    if (!trimmed || isSending) {
      return;
    }

    setIsSending(true);
    setError(null);
    setInput("");

    const nextHistory: LocalMessage[] = [
      ...messages,
      { role: "user", content: trimmed },
    ];
    setMessages(nextHistory);

    try {
      const response = await aiQuery(
        username,
        trimmed,
        nextHistory.map(({ role, content }) => ({ role, content })),
      );
      setMessages((prev) => [
        ...prev,
        {
          role: "assistant",
          content: response.reply,
          applied: response.applied,
        },
      ]);
      onBoardUpdate(response.board);
    } catch (err) {
      setError("Unable to reach the AI assistant.");
      setMessages((prev) => [
        ...prev,
        {
          role: "assistant",
          content: "Sorry, I could not process that request right now.",
        },
      ]);
    } finally {
      setIsSending(false);
    }
  };

  return (
    <aside className="flex w-full flex-col gap-4 rounded-[28px] border border-[var(--stroke)] bg-white/90 p-6 shadow-[var(--shadow)] backdrop-blur">
      <div>
        <p className="text-xs font-semibold uppercase tracking-[0.35em] text-[var(--gray-text)]">
          AI Assistant
        </p>
        <h2 className="mt-3 font-display text-2xl font-semibold text-[var(--navy-dark)]">
          Ask for updates
        </h2>
        <p className="mt-2 text-sm leading-6 text-[var(--gray-text)]">
          Describe a change and the assistant will update the board for you.
        </p>
      </div>

      <div className="flex flex-wrap gap-2">
        {suggestions.map((suggestion) => (
          <button
            key={suggestion}
            type="button"
            onClick={() => handleSend(suggestion)}
            className="rounded-full border border-[var(--stroke)] px-3 py-1 text-[10px] font-semibold uppercase tracking-[0.2em] text-[var(--primary-blue)] transition hover:border-[var(--primary-blue)]"
          >
            {suggestion}
          </button>
        ))}
      </div>

      <div className="flex min-h-[220px] flex-1 flex-col gap-3 overflow-y-auto rounded-2xl border border-[var(--stroke)] bg-[var(--surface)] p-4">
        {messages.length === 0 ? (
          <p className="text-xs font-semibold uppercase tracking-[0.2em] text-[var(--gray-text)]">
            No messages yet
          </p>
        ) : (
          messages.map((message, index) => (
            <div
              key={`${message.role}-${index}`}
              className={
                message.role === "user"
                  ? "self-end rounded-2xl bg-[var(--primary-blue)] px-3 py-2 text-xs font-semibold text-white"
                  : "self-start rounded-2xl border border-[var(--stroke)] bg-white px-3 py-2 text-xs text-[var(--navy-dark)]"
              }
            >
              <p>{message.content}</p>
              {message.role === "assistant" && message.applied ? (
                <p className="mt-2 text-[10px] font-semibold uppercase tracking-[0.2em] text-[var(--primary-blue)]">
                  Board updated
                </p>
              ) : null}
            </div>
          ))
        )}
      </div>

      {error ? (
        <p className="rounded-2xl border border-[var(--stroke)] bg-white px-4 py-2 text-xs font-semibold text-[var(--secondary-purple)]">
          {error}
        </p>
      ) : null}

      <form
        onSubmit={(event) => {
          event.preventDefault();
          void handleSend(input);
        }}
        className="space-y-3"
      >
        <textarea
          value={input}
          onChange={(event) => setInput(event.target.value)}
          rows={3}
          placeholder="Ask the assistant to move, add, or edit cards"
          className="w-full resize-none rounded-2xl border border-[var(--stroke)] bg-white px-3 py-2 text-sm text-[var(--navy-dark)] outline-none transition focus:border-[var(--primary-blue)]"
        />
        <button
          type="submit"
          disabled={!canSend}
          className="w-full rounded-full bg-[var(--secondary-purple)] px-4 py-3 text-xs font-semibold uppercase tracking-[0.25em] text-white transition enabled:hover:brightness-110 disabled:cursor-not-allowed disabled:opacity-60"
        >
          {isSending ? "Sending" : "Send"}
        </button>
      </form>
    </aside>
  );
};
