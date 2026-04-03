export const colors = {
  background: "#0F0D23",
  surface: "#1A1833",
  elevated: "#242042",
  primary: "#8B5CF6",
  primaryMuted: "#7C3AED",
  text: "#F8FAFC",
  textSecondary: "#94A3B8",
  textMuted: "#64748B",
  border: "#2D2A4A",
  inputBg: "#1E1B38",
  success: "#22C55E",
  warning: "#EAB308",
  error: "#EF4444",
  errorMuted: "#991B1B",
  info: "#3B82F6",
} as const;

export const card = {
  backgroundColor: colors.surface,
  borderRadius: 14,
  borderWidth: 1,
  borderColor: colors.border,
} as const;

export const input = {
  backgroundColor: colors.inputBg,
  borderWidth: 1,
  borderColor: colors.border,
  borderRadius: 12,
  paddingHorizontal: 16,
  paddingVertical: 14,
  fontSize: 16,
  color: colors.text,
} as const;

export const buttonPrimary = {
  backgroundColor: colors.primary,
  paddingVertical: 14,
  borderRadius: 12,
  alignItems: "center" as const,
} as const;

export const buttonSecondary = {
  backgroundColor: "transparent",
  paddingVertical: 14,
  borderRadius: 12,
  alignItems: "center" as const,
  borderWidth: 1,
  borderColor: colors.primary,
} as const;

export const headerStyle = {
  backgroundColor: colors.surface,
} as const;

export const headerTintColor = colors.text;

export const tabBarStyle = {
  backgroundColor: colors.surface,
  borderTopColor: colors.border,
  borderTopWidth: 1,
  paddingBottom: 4,
  paddingTop: 4,
  height: 60,
} as const;
