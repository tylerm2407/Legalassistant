import { Stack } from "expo-router";
import { SafeAreaProvider } from "react-native-safe-area-context";
import { StatusBar } from "expo-status-bar";
import { colors } from "@/lib/theme";

export default function RootLayout() {
  return (
    <SafeAreaProvider>
      <StatusBar style="light" />
      <Stack
        screenOptions={{
          headerStyle: { backgroundColor: colors.surface },
          headerTintColor: "#ffffff",
          headerTitleStyle: { fontWeight: "700" },
          contentStyle: { backgroundColor: colors.background },
        }}
      >
        <Stack.Screen name="index" options={{ headerShown: false }} />
        <Stack.Screen
          name="(auth)/onboarding"
          options={{ title: "Get Started", headerShown: false }}
        />
        <Stack.Screen
          name="(auth)/login"
          options={{ title: "Sign In", headerShown: false }}
        />
        <Stack.Screen
          name="(app)"
          options={{ headerShown: false }}
        />
      </Stack>
    </SafeAreaProvider>
  );
}
