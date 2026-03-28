import React, { useState, useEffect } from "react";
import { View, Text, TouchableOpacity, FlatList, StyleSheet, ActivityIndicator } from "react-native";
import { useRouter } from "expo-router";
import { getRightsDomains, getRightsGuides } from "@/lib/api";
import type { RightsDomain, RightsGuide } from "@/lib/types";

export default function RightsScreen() {
  const router = useRouter();
  const [domains, setDomains] = useState<RightsDomain[]>([]);
  const [guides, setGuides] = useState<RightsGuide[]>([]);
  const [selectedDomain, setSelectedDomain] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadDomains();
  }, []);

  const loadDomains = async () => {
    try {
      const data = await getRightsDomains();
      setDomains(data.domains);
    } catch { /* ignore */ }
    finally { setLoading(false); }
  };

  const loadGuides = async (domain: string) => {
    setSelectedDomain(domain);
    setLoading(true);
    try {
      const data = await getRightsGuides(domain);
      setGuides(data.guides);
    } catch { /* ignore */ }
    finally { setLoading(false); }
  };

  if (loading) {
    return <View style={styles.center}><ActivityIndicator size="large" color="#1e40af" /></View>;
  }

  if (selectedDomain) {
    return (
      <View style={styles.container}>
        <TouchableOpacity onPress={() => { setSelectedDomain(null); setGuides([]); }} style={styles.backBtn}>
          <Text style={styles.backBtnText}>← Back to domains</Text>
        </TouchableOpacity>
        <FlatList
          data={guides}
          keyExtractor={(item) => item.id}
          contentContainerStyle={styles.list}
          renderItem={({ item }) => (
            <TouchableOpacity
              style={styles.guideCard}
              onPress={() => router.push({ pathname: "/(app)/rights-guide", params: { guideId: item.id } } as any)}
            >
              <Text style={styles.guideTitle}>{item.title}</Text>
              <Text style={styles.guideDesc}>{item.summary || item.description || ""}</Text>
            </TouchableOpacity>
          )}
          ListEmptyComponent={<Text style={styles.emptyText}>No guides available for this domain.</Text>}
        />
      </View>
    );
  }

  return (
    <FlatList
      data={domains}
      keyExtractor={(item) => item.id}
      contentContainerStyle={styles.list}
      style={styles.container}
      renderItem={({ item }) => (
        <TouchableOpacity style={styles.domainCard} onPress={() => loadGuides(item.id)}>
          <Text style={styles.domainTitle}>{item.name}</Text>
          <Text style={styles.domainCount}>{item.guide_count} guides</Text>
        </TouchableOpacity>
      )}
    />
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: "#f8fafc" },
  center: { flex: 1, justifyContent: "center", alignItems: "center" },
  list: { padding: 16, gap: 12 },
  backBtn: { padding: 16, paddingBottom: 0 },
  backBtnText: { color: "#1e40af", fontSize: 15, fontWeight: "600" },
  domainCard: {
    backgroundColor: "#ffffff", borderRadius: 12, padding: 18,
    borderWidth: 1, borderColor: "#e2e8f0",
  },
  domainTitle: { fontSize: 17, fontWeight: "700", color: "#0f172a" },
  domainCount: { fontSize: 13, color: "#64748b", marginTop: 4 },
  guideCard: {
    backgroundColor: "#ffffff", borderRadius: 12, padding: 16,
    borderWidth: 1, borderColor: "#e2e8f0",
  },
  guideTitle: { fontSize: 16, fontWeight: "700", color: "#0f172a", marginBottom: 4 },
  guideDesc: { fontSize: 13, color: "#64748b", lineHeight: 18 },
  emptyText: { color: "#94a3b8", fontSize: 14, textAlign: "center", padding: 40 },
});
