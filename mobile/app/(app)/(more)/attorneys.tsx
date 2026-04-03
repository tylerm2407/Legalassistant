import React, { useState } from "react";
import { View, Text, TextInput, TouchableOpacity, FlatList, StyleSheet, ActivityIndicator } from "react-native";
import { findAttorneys } from "@/lib/api";
import { colors } from "@/lib/theme";
import type { ReferralSuggestion } from "@/lib/types";

export default function AttorneysScreen() {
  const [state, setState] = useState("");
  const [legalArea, setLegalArea] = useState("");
  const [results, setResults] = useState<ReferralSuggestion[]>([]);
  const [loading, setLoading] = useState(false);
  const [searched, setSearched] = useState(false);

  const handleSearch = async () => {
    if (!state.trim()) return;
    setLoading(true);
    setSearched(true);
    try {
      const data = await findAttorneys(state.toUpperCase(), legalArea || undefined);
      setResults(data.suggestions);
    } catch { setResults([]); }
    finally { setLoading(false); }
  };

  return (
    <View style={styles.container}>
      <View style={styles.searchBar}>
        <TextInput style={styles.input} placeholder="State (e.g. CA)" value={state} onChangeText={setState} autoCapitalize="characters" maxLength={2} placeholderTextColor={colors.textMuted} />
        <TextInput style={[styles.input, { flex: 2 }]} placeholder="Legal area (optional)" value={legalArea} onChangeText={setLegalArea} placeholderTextColor={colors.textMuted} />
        <TouchableOpacity style={styles.searchBtn} onPress={handleSearch} disabled={loading}>
          <Text style={styles.searchBtnText}>Search</Text>
        </TouchableOpacity>
      </View>

      {loading ? (
        <View style={styles.center}><ActivityIndicator size="large" color={colors.primary} /></View>
      ) : (
        <FlatList
          data={results}
          keyExtractor={(_, i) => i.toString()}
          contentContainerStyle={styles.list}
          renderItem={({ item }) => (
            <View style={styles.card}>
              <Text style={styles.cardName}>{item.attorney?.name || "Attorney"}</Text>
              <Text style={styles.cardDetail}>{item.attorney?.state} • {item.attorney?.specializations?.join(", ") || "General Practice"}</Text>
              <Text style={styles.cardReason}>{item.match_reason}</Text>
              {item.attorney?.phone && <Text style={styles.cardContact}>{item.attorney.phone}</Text>}
              {item.attorney?.email && <Text style={styles.cardContact}>{item.attorney.email}</Text>}
            </View>
          )}
          ListEmptyComponent={searched ? <Text style={styles.emptyText}>No attorneys found for this search.</Text> : null}
        />
      )}
    </View>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: colors.background },
  center: { flex: 1, justifyContent: "center", alignItems: "center" },
  searchBar: { flexDirection: "row", padding: 16, gap: 8 },
  input: {
    flex: 1, backgroundColor: colors.inputBg, borderRadius: 10, paddingHorizontal: 12,
    paddingVertical: 10, fontSize: 14, color: colors.text, borderWidth: 1, borderColor: colors.border,
  },
  searchBtn: { backgroundColor: colors.primary, paddingHorizontal: 16, borderRadius: 10, justifyContent: "center" },
  searchBtnText: { color: "#ffffff", fontWeight: "700", fontSize: 14 },
  list: { paddingHorizontal: 16, gap: 12, paddingBottom: 16 },
  card: {
    backgroundColor: colors.surface, borderRadius: 12, padding: 16,
    borderWidth: 1, borderColor: colors.border,
  },
  cardName: { fontSize: 16, fontWeight: "700", color: colors.text, marginBottom: 4 },
  cardDetail: { fontSize: 13, color: colors.textSecondary, marginBottom: 4 },
  cardReason: { fontSize: 12, color: colors.primary, fontWeight: "500" },
  cardContact: { fontSize: 13, color: colors.textSecondary, marginTop: 4 },
  emptyText: { color: colors.textSecondary, fontSize: 14, textAlign: "center", padding: 40 },
});
