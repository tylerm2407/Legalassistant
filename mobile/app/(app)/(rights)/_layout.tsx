import { Stack } from "expo-router";
import { colors } from "@/lib/theme";

export default function RightsLayout() {
  return (
    <Stack
      screenOptions={{
        headerStyle: { backgroundColor: colors.surface },
        headerTintColor: colors.text,
        headerTitleStyle: { fontWeight: "700" },
        contentStyle: { backgroundColor: colors.background },
      }}
    >
      <Stack.Screen name="index" options={{ headerShown: false }} />
      <Stack.Screen name="[guideId]" options={{ title: "Rights Guide" }} />
    </Stack>
  );
}
