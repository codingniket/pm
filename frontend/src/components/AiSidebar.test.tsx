import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { vi } from "vitest";
import { AiSidebar } from "@/components/AiSidebar";

const createResponse = (payload: unknown) =>
  Promise.resolve({
    ok: true,
    json: () => Promise.resolve(payload),
  });

const mockFetch = () => {
  const fetchMock = vi.fn(() =>
    createResponse({
      reply: "Done.",
      applied: true,
      board: { columns: [], cards: {} },
    }),
  );
  vi.stubGlobal("fetch", fetchMock);
  return fetchMock;
};

describe("AiSidebar", () => {
  afterEach(() => {
    vi.unstubAllGlobals();
  });

  it("sends a message and shows the reply", async () => {
    mockFetch();
    const onBoardUpdate = vi.fn();
    render(<AiSidebar username="user" onBoardUpdate={onBoardUpdate} />);

    await userEvent.type(
      screen.getByPlaceholderText(/ask the assistant/i),
      "Move card-1 to Review",
    );
    await userEvent.click(screen.getByRole("button", { name: /send/i }));

    expect(await screen.findByText("Done.")).toBeVisible();
    expect(onBoardUpdate).toHaveBeenCalled();
  });
});
