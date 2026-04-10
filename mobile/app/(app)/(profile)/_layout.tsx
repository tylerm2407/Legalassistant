import { Stack } from "expo-router";
import { colors, fonts } from "@/lib/theme";

export default function ProfileLayout() {
  return (
    <Stack
      screenOptions={{
        headerStyle: { backgroundColor: colors.surface },
        headerTintColor: colors.text,
        headerTitleStyle: { fontFamily: fonts.serif, fontWeight: "500", fontSize: 18, color: colors.text },
        headerShadowVisible: false,
        contentStyle: { backgroundColor: colors.background },
      }}
    >
      <Stack.Screen name="index" options={{ headerShown: false }} />
      <Stack.Screen name="cases" options={{ title: "Your Cases" }} />
    </Stack>
  );
}
