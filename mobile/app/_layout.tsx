import { Stack } from "expo-router";
import { SafeAreaProvider } from "react-native-safe-area-context";
import { StatusBar } from "expo-status-bar";
import { colors, fonts, headerStyle } from "@/lib/theme";

export default function RootLayout() {
  return (
    <SafeAreaProvider>
      <StatusBar style="dark" />
      <Stack
        screenOptions={{
          headerStyle,
          headerTintColor: colors.text,
          headerTitleStyle: {
            fontFamily: fonts.serif,
            fontWeight: "500",
            fontSize: 18,
            color: colors.text,
          },
          headerShadowVisible: false,
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
        <Stack.Screen name="(app)" options={{ headerShown: false }} />
      </Stack>
    </SafeAreaProvider>
  );
}
