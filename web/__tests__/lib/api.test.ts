// Mock supabase before importing api
jest.mock("@/lib/supabase", () => ({
  supabase: {
    auth: {
      getSession: jest.fn().mockResolvedValue({
        data: { session: { access_token: "test-token" } },
      }),
    },
  },
}));

// Mock fetch
const mockFetch = jest.fn();
global.fetch = mockFetch;

import { api } from "@/lib/api";

describe("api", () => {
  beforeEach(() => {
    mockFetch.mockReset();
  });

  describe("chat", () => {
    it("sends POST request with message and auth header", async () => {
      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: () =>
          Promise.resolve({
            conversation_id: "conv-1",
            answer: "Based on your situation...",
            legal_area: "landlord_tenant",
            suggested_actions: [],
          }),
      });

      const result = await api.chat({
        userId: "user-1",
        question: "My landlord won't return my deposit",
      });

      expect(mockFetch).toHaveBeenCalledWith(
        expect.stringContaining("/chat"),
        expect.objectContaining({
          method: "POST",
          headers: expect.objectContaining({
            Authorization: "Bearer test-token",
            "Content-Type": "application/json",
          }),
        })
      );
      expect(result.answer).toBe("Based on your situation...");
    });

    it("throws on non-ok 4xx response without retrying", async () => {
      mockFetch.mockResolvedValueOnce({ ok: false, status: 400 });

      await expect(
        api.chat({ userId: "user-1", question: "test" })
      ).rejects.toThrow("Chat failed: 400");
    });
  });

  describe("getProfile", () => {
    it("returns profile on success", async () => {
      const profile = { user_id: "user-1", display_name: "Sarah" };
      mockFetch.mockResolvedValueOnce({
        ok: true,
        status: 200,
        json: () => Promise.resolve({ profile }),
      });

      const result = await api.getProfile("user-1");
      expect(result).toEqual(profile);
    });

    it("returns null on 404", async () => {
      mockFetch.mockResolvedValueOnce({ ok: false, status: 404 });

      const result = await api.getProfile("user-1");
      expect(result).toBeNull();
    });
  });

  describe("createProfile", () => {
    it("sends profile data and returns created profile", async () => {
      const profile = { display_name: "Sarah", state: "Massachusetts" };
      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: () => Promise.resolve({ profile }),
      });

      const result = await api.createProfile(profile);
      expect(result).toEqual(profile);
      expect(mockFetch).toHaveBeenCalledWith(
        expect.stringContaining("/profile"),
        expect.objectContaining({ method: "POST" })
      );
    });
  });

  describe("generateLetter", () => {
    it("returns demand letter on success", async () => {
      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: () =>
          Promise.resolve({
            letter_text: "Dear Landlord...",
            legal_citations: ["M.G.L. c.186"],
          }),
      });

      const result = await api.generateLetter("user-1");
      expect(result.letter_text).toBe("Dear Landlord...");
    });
  });

  describe("getConversations", () => {
    it("returns conversation list", async () => {
      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: () =>
          Promise.resolve({
            conversations: [{ id: "conv-1", preview: "Test" }],
          }),
      });

      const result = await api.getConversations();
      expect(result).toHaveLength(1);
      expect(result[0].id).toBe("conv-1");
    });

    it("returns empty array when conversations key is missing", async () => {
      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: () => Promise.resolve({}),
      });

      const result = await api.getConversations();
      expect(result).toEqual([]);
    });
  });

  describe("deleteConversation", () => {
    it("sends DELETE request", async () => {
      mockFetch.mockResolvedValueOnce({ ok: true });

      await api.deleteConversation("conv-1");
      expect(mockFetch).toHaveBeenCalledWith(
        expect.stringContaining("/conversations/conv-1"),
        expect.objectContaining({ method: "DELETE" })
      );
    });
  });

  describe("getDeadlines", () => {
    it("returns deadline list", async () => {
      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: () =>
          Promise.resolve({
            deadlines: [{ id: "dl-1", title: "File form" }],
          }),
      });

      const result = await api.getDeadlines();
      expect(result).toHaveLength(1);
    });
  });

  describe("findAttorneys", () => {
    it("sends state and legal area in query params", async () => {
      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: () => Promise.resolve({ suggestions: [] }),
      });

      await api.findAttorneys("Massachusetts", "landlord_tenant");
      expect(mockFetch).toHaveBeenCalledWith(
        expect.stringContaining("state=Massachusetts&legal_area=landlord_tenant"),
        expect.anything()
      );
    });
  });
});
