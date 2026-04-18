import { useSortable } from "@dnd-kit/sortable";
import { CSS } from "@dnd-kit/utilities";
import clsx from "clsx";
import type { Card } from "@/lib/kanban";

type KanbanCardProps = {
  card: Card;
  onDelete: (cardId: string) => void;
};

export const KanbanCard = ({ card, onDelete }: KanbanCardProps) => {
  const {
    attributes,
    listeners,
    setNodeRef,
    transform,
    transition,
    isDragging,
  } = useSortable({ id: card.id });

  const style = {
    transform: CSS.Transform.toString(transform),
    transition,
  };

  return (
    <article
      ref={setNodeRef}
      style={style}
      className={clsx(
        "rounded-2xl border border-transparent bg-white px-4 py-4 shadow-[0_12px_24px_rgba(3,33,71,0.08)]",
        "transition-all duration-150",
        isDragging && "opacity-60 shadow-[0_18px_32px_rgba(3,33,71,0.16)]",
      )}
      {...attributes}
      {...listeners}
      data-testid={`card-${card.id}`}
    >
      <div className="flex items-start justify-between gap-3">
        <h4 className="min-w-0 font-display text-base font-semibold text-[var(--navy-dark)]">
          {card.title}
        </h4>
        <button
          type="button"
          onClick={() => onDelete(card.id)}
          className="shrink-0 rounded-full border border-[var(--stroke)] bg-white px-2.5 py-1 text-[11px] font-semibold uppercase tracking-[0.16em] text-[var(--gray-text)] transition hover:border-[var(--primary-blue)] hover:text-[var(--navy-dark)]"
          aria-label={`Delete ${card.title}`}
        >
          Remove
        </button>
      </div>
      <p className="mt-3 text-sm leading-6 text-[var(--gray-text)]">
        {card.details}
      </p>
    </article>
  );
};
