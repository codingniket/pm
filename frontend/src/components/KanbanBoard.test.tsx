import { render, screen, within } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { vi } from "vitest";
import { KanbanBoard } from "@/components/KanbanBoard";
import { initialData } from "@/lib/kanban";

const getFirstColumn = () => screen.getAllByTestId(/column-/i)[0];

const createResponse = (payload: unknown) =>
  Promise.resolve({
    ok: true,
    json: () => Promise.resolve(payload),
  });

const mockFetch = () => {
  const fetchMock = vi.fn((input: RequestInfo, init?: RequestInit) => {
    const url = typeof input === "string" ? input : input.url;
    if (url.startsWith("/api/board")) {
      return createResponse({ boardId: "board-user", ...initialData });
    }
    if (url.startsWith("/api/cards") && init?.method === "POST") {
      return createResponse({
        id: "card-new",
        columnId: "col-backlog",
        title: "New card",
        details: "Notes",
        position: 2,
      });
    }
    return createResponse({ status: "ok" });
  });

  vi.stubGlobal("fetch", fetchMock);
  return fetchMock;
};

describe("KanbanBoard", () => {
  beforeEach(() => {
    mockFetch();
  });

  afterEach(() => {
    vi.unstubAllGlobals();
  });

  it("renders five columns", async () => {
    render(<KanbanBoard />);
    await screen.findByRole("heading", { name: /kanban studio/i });
    expect(screen.getAllByTestId(/column-/i)).toHaveLength(5);
  });

  it("renames a column", async () => {
    render(<KanbanBoard />);
    await screen.findByRole("heading", { name: /kanban studio/i });
    const column = getFirstColumn();
    const input = within(column).getByLabelText("Column title");
    await userEvent.clear(input);
    await userEvent.type(input, "New Name");
    expect(input).toHaveValue("New Name");
  });

  it("adds and removes a card", async () => {
    render(<KanbanBoard />);
    await screen.findByRole("heading", { name: /kanban studio/i });
    const column = getFirstColumn();
    const addButton = within(column).getByRole("button", {
      name: /add a card/i,
    });
    await userEvent.click(addButton);

    const titleInput = within(column).getByPlaceholderText(/card title/i);
    await userEvent.type(titleInput, "New card");
    const detailsInput = within(column).getByPlaceholderText(/details/i);
    await userEvent.type(detailsInput, "Notes");

    await userEvent.click(
      within(column).getByRole("button", { name: /add card/i }),
    );

    expect(within(column).getByText("New card")).toBeInTheDocument();

    const deleteButton = within(column).getByRole("button", {
      name: /delete new card/i,
    });
    await userEvent.click(deleteButton);

    expect(within(column).queryByText("New card")).not.toBeInTheDocument();
  });
});
