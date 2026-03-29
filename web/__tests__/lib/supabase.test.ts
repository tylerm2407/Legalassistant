jest.mock("@supabase/supabase-js", () => ({
  createClient: jest.fn().mockReturnValue({
    auth: {
      getSession: jest.fn(),
      signInWithPassword: jest.fn(),
      signOut: jest.fn(),
    },
    from: jest.fn().mockReturnValue({
      select: jest.fn().mockReturnThis(),
      insert: jest.fn().mockReturnThis(),
      update: jest.fn().mockReturnThis(),
      delete: jest.fn().mockReturnThis(),
      eq: jest.fn().mockReturnThis(),
    }),
  }),
}));

import { createClient } from "@supabase/supabase-js";

describe("supabase client", () => {
  it("creates client lazily when a property is accessed", () => {
    process.env.NEXT_PUBLIC_SUPABASE_URL = "https://test.supabase.co";
    process.env.NEXT_PUBLIC_SUPABASE_KEY = "test-key";

    jest.isolateModules(() => {
      const mod = require("@/lib/supabase");
      // Trigger lazy initialization by accessing a property on the proxy
      mod.supabase.auth;
    });

    expect(createClient).toHaveBeenCalled();
  });

  it("exports a supabase object", () => {
    jest.isolateModules(() => {
      const mod = require("@/lib/supabase");
      expect(mod.supabase).toBeDefined();
    });
  });
});
