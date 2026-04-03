import { useEffect, useState } from "react";
import { useRouter } from "expo-router";
import { Tabs } from "expo-router";
import { Text, StyleSheet, ActivityIndicator, View } from "react-native";
import { supabase } from "@/lib/supabase";
import { colors } from "@/lib/theme";

function TabIcon({ icon, focused }: { icon: string; focused: boolean }) {
  return (
    <Text style={[styles.tabIcon, focused && styles.tabIconFocused]}>
      {icon}
    </Text>
  );
}

export default function AppLayout() {
  const router = useRouter();
  const [checking, setChecking] = useState(true);

  useEffect(() => {
    supabase.auth.getSession().then(({ data: { session } }) => {
      if (!session) {
        router.replace("/(auth)/login");
      }
      setChecking(false);
    });

    const { data: { subscription } } = supabase.auth.onAuthStateChange(
      (_event, session) => {
        if (!session) {
          router.replace("/(auth)/login");
        }
      }
    );

    return () => subscription.unsubscribe();
  }, [router]);

  if (checking) {
    return (
      <View style={{ flex: 1, justifyContent: "center", alignItems: "center", backgroundColor: colors.background }}>
        <ActivityIndicator size="large" color={colors.primary} />
      </View>
    );
  }

  return (
    <Tabs
      screenOptions={{
        tabBarActiveTintColor: colors.primary,
        tabBarInactiveTintColor: colors.textMuted,
        tabBarStyle: {
          backgroundColor: colors.surface,
          borderTopColor: colors.border,
          borderTopWidth: 1,
          paddingBottom: 4,
          paddingTop: 4,
          height: 60,
        },
        tabBarLabelStyle: {
          fontSize: 11,
          fontWeight: "600",
        },
        headerStyle: {
          backgroundColor: colors.surface,
        },
        headerTintColor: colors.text,
        headerTitleStyle: {
          fontWeight: "700",
          fontSize: 18,
        },
      }}
    >
      <Tabs.Screen
        name="(chat)"
        options={{
          title: "Chat",
          headerTitle: "CaseMate",
          tabBarIcon: ({ focused }) => <TabIcon icon="💬" focused={focused} />,
        }}
      />
      <Tabs.Screen
        name="(profile)"
        options={{
          title: "Profile",
          headerTitle: "Your Profile",
          tabBarIcon: ({ focused }) => <TabIcon icon="👤" focused={focused} />,
        }}
      />
      <Tabs.Screen
        name="(rights)"
        options={{
          title: "Rights",
          headerTitle: "Know Your Rights",
          tabBarIcon: ({ focused }) => <TabIcon icon="⚖️" focused={focused} />,
        }}
      />
      <Tabs.Screen
        name="(tools)"
        options={{
          title: "Tools",
          headerTitle: "Legal Tools",
          tabBarIcon: ({ focused }) => <TabIcon icon="🛠️" focused={focused} />,
        }}
      />
      <Tabs.Screen
        name="(more)"
        options={{
          title: "More",
          headerTitle: "More",
          tabBarIcon: ({ focused }) => <TabIcon icon="☰" focused={focused} />,
        }}
      />
    </Tabs>
  );
}

const styles = StyleSheet.create({
  tabIcon: {
    fontSize: 22,
    opacity: 0.5,
  },
  tabIconFocused: {
    opacity: 1,
  },
});
