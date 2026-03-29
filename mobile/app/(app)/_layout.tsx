import { useEffect, useState } from "react";
import { useRouter } from "expo-router";
import { Tabs } from "expo-router";
import { Text, StyleSheet, ActivityIndicator, View } from "react-native";
import { supabase } from "@/lib/supabase";

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
      <View style={{ flex: 1, justifyContent: "center", alignItems: "center", backgroundColor: "#ffffff" }}>
        <ActivityIndicator size="large" color="#1e40af" />
      </View>
    );
  }

  return (
    <Tabs
      screenOptions={{
        tabBarActiveTintColor: "#1e40af",
        tabBarInactiveTintColor: "#94a3b8",
        tabBarStyle: {
          backgroundColor: "#ffffff",
          borderTopColor: "#e2e8f0",
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
          backgroundColor: "#1e40af",
        },
        headerTintColor: "#ffffff",
        headerTitleStyle: {
          fontWeight: "700",
          fontSize: 18,
        },
      }}
    >
      <Tabs.Screen
        name="chat"
        options={{
          title: "Chat",
          headerTitle: "CaseMate",
          tabBarIcon: ({ focused }) => (
            <TabIcon icon="💬" focused={focused} />
          ),
        }}
      />
      <Tabs.Screen
        name="rights"
        options={{
          title: "Rights",
          headerTitle: "Know Your Rights",
          tabBarIcon: ({ focused }) => (
            <TabIcon icon="⚖️" focused={focused} />
          ),
        }}
      />
      <Tabs.Screen
        name="tools"
        options={{
          title: "Tools",
          headerTitle: "Legal Tools",
          tabBarIcon: ({ focused }) => (
            <TabIcon icon="🛠️" focused={focused} />
          ),
        }}
      />
      <Tabs.Screen
        name="profile"
        options={{
          title: "Profile",
          headerTitle: "Your Profile",
          tabBarIcon: ({ focused }) => (
            <TabIcon icon="👤" focused={focused} />
          ),
        }}
      />
      {/* Hidden stack screens */}
      <Tabs.Screen
        name="cases"
        options={{ href: null, headerTitle: "Your Cases" }}
      />
      <Tabs.Screen
        name="deadlines"
        options={{ href: null, headerTitle: "Your Deadlines" }}
      />
      <Tabs.Screen
        name="rights-guide"
        options={{ href: null, headerTitle: "Rights Guide" }}
      />
      <Tabs.Screen
        name="workflows"
        options={{ href: null, headerTitle: "Legal Workflows" }}
      />
      <Tabs.Screen
        name="workflow-wizard"
        options={{ href: null, headerTitle: "Workflow" }}
      />
      <Tabs.Screen
        name="attorneys"
        options={{ href: null, headerTitle: "Find Attorneys" }}
      />
      <Tabs.Screen
        name="conversations"
        options={{ href: null, headerTitle: "Conversations" }}
      />
      <Tabs.Screen
        name="documents"
        options={{ href: null, headerTitle: "Documents" }}
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
