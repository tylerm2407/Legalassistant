import { Platform } from "react-native";

/**
 * CaseMate editorial design tokens — mobile.
 *
 * Matches the web design system (trustworthy editorial, warm off-white, deep
 * forest green accent). Keys on `colors` preserve the legacy API surface
 * (background, surface, primary, text, etc.) so existing imports keep working;
 * values have been swapped to the editorial palette.
 *
 * New, semantic aliases (bg, ink, accent, etc.) are also exported for screens
 * written against the updated token names.
 */

// --- Editorial palette -----------------------------------------------------

const palette = {
  bg: "#FBF9F4",
  bgSubtle: "#F5F2EB",
  inkPrimary: "#1A1A1A",
  inkSecondary: "#5A5A5A",
  inkTertiary: "#8A8A8A",
  accent: "#1F4D3A",
  accentHover: "#173A2C",
  accentSubtle: "#E8EFEB",
  warning: "#B5654A",
  warningSubtle: "#F5E8E2",
  success: "#1F4D3A",
  successSubtle: "#E8EFEB",
  border: "#E5E1D8",
  borderStrong: "#C9C3B5",
  white: "#FFFFFF",
} as const;

// --- Legacy-compatible color map (still used by most screens) --------------

export const colors = {
  // Surfaces — map dark tones to warm off-white / paper tones.
  background: palette.bg,
  surface: palette.white,
  elevated: palette.bgSubtle,

  // Brand — forest green replaces the old indigo / purple.
  primary: palette.accent,
  primaryMuted: palette.accentHover,

  // Text — ink hierarchy.
  text: palette.inkPrimary,
  textSecondary: palette.inkSecondary,
  textMuted: palette.inkTertiary,

  // Lines + inputs.
  border: palette.border,
  inputBg: palette.white,

  // Status.
  success: palette.accent,
  warning: palette.warning,
  error: palette.warning,
  errorMuted: palette.warningSubtle,
  info: palette.accent,
} as const;

// --- Semantic aliases (preferred for new code) -----------------------------

export const tokens = palette;

// --- Typography ------------------------------------------------------------

export const fonts = {
  // Editorial serif for headlines. Georgia ships on iOS; Android falls back
  // to its system serif. This keeps the editorial feel without requiring
  // expo-font loading up-front.
  serif: Platform.select({ ios: "Georgia", android: "serif", default: "serif" }),
  // Body sans — defer to the platform sans (SF Pro / Roboto).
  sans: Platform.select({ ios: "System", android: "sans-serif", default: "System" }),
  // Mono for citations and case numbers.
  mono: Platform.select({ ios: "Menlo", android: "monospace", default: "monospace" }),
} as const;

// --- Reusable style fragments ---------------------------------------------

export const card = {
  backgroundColor: colors.surface,
  borderRadius: 12,
  borderWidth: 1,
  borderColor: colors.border,
} as const;

export const input = {
  backgroundColor: colors.inputBg,
  borderWidth: 1,
  borderColor: colors.border,
  borderRadius: 8,
  paddingHorizontal: 16,
  paddingVertical: 14,
  fontSize: 16,
  color: colors.text,
} as const;

export const buttonPrimary = {
  backgroundColor: colors.primary,
  paddingVertical: 14,
  borderRadius: 8,
  alignItems: "center" as const,
} as const;

export const buttonSecondary = {
  backgroundColor: colors.surface,
  paddingVertical: 14,
  borderRadius: 8,
  alignItems: "center" as const,
  borderWidth: 1,
  borderColor: colors.border,
} as const;

export const headerStyle = {
  backgroundColor: colors.background,
  borderBottomWidth: 1,
  borderBottomColor: colors.border,
} as const;

export const headerTintColor = colors.text;

export const tabBarStyle = {
  backgroundColor: colors.background,
  borderTopColor: colors.border,
  borderTopWidth: 1,
  paddingBottom: 4,
  paddingTop: 4,
  height: 60,
} as const;
