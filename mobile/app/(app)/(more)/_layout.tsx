import { Stack } from "expo-router";
import { colors, fonts } from "@/lib/theme";

export default function MoreLayout() {
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
      <Stack.Screen name="attorneys" options={{ title: "Find Attorneys" }} />
      <Stack.Screen name="deadlines" options={{ title: "Deadlines" }} />
      <Stack.Screen name="documents" options={{ title: "Documents" }} />
      <Stack.Screen name="subscription" options={{ title: "Subscription" }} />
    </Stack>
  );
}
