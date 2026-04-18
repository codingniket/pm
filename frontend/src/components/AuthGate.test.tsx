import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { AuthGate } from "@/components/AuthGate";

const renderAuthGate = () => render(<AuthGate />);

describe("AuthGate", () => {
  beforeEach(() => {
    window.localStorage.clear();
  });

  it("shows login form by default", async () => {
    renderAuthGate();
    expect(
      await screen.findByRole("heading", { name: /sign in/i }),
    ).toBeVisible();
  });

  it("logs in with correct credentials", async () => {
    renderAuthGate();
    await screen.findByRole("heading", { name: /sign in/i });

    await userEvent.type(screen.getByLabelText(/username/i), "user");
    await userEvent.type(screen.getByLabelText(/password/i), "password");
    await userEvent.click(screen.getByRole("button", { name: /sign in/i }));

    expect(
      await screen.findByRole("button", { name: /log out/i }),
    ).toBeVisible();
    expect(window.localStorage.getItem("pm-authenticated")).toBe("true");
  });

  it("rejects invalid credentials", async () => {
    renderAuthGate();
    await screen.findByRole("heading", { name: /sign in/i });

    await userEvent.type(screen.getByLabelText(/username/i), "wrong");
    await userEvent.type(screen.getByLabelText(/password/i), "credentials");
    await userEvent.click(screen.getByRole("button", { name: /sign in/i }));

    expect(await screen.findByText(/invalid credentials/i)).toBeVisible();
  });

  it("logs out and returns to login", async () => {
    window.localStorage.setItem("pm-authenticated", "true");
    renderAuthGate();

    const logoutButton = await screen.findByRole("button", {
      name: /log out/i,
    });
    await userEvent.click(logoutButton);

    expect(
      await screen.findByRole("heading", { name: /sign in/i }),
    ).toBeVisible();
  });
});
