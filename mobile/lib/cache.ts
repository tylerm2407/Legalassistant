import AsyncStorage from "@react-native-async-storage/async-storage";
import type { LegalProfile, ConversationSummary } from "./types";

const PROFILE_KEY = "casemate_profile_cache";
const CONVERSATIONS_KEY = "casemate_conversations_cache";

export async function getCachedProfile(): Promise<LegalProfile | null> {
  try {
    const raw = await AsyncStorage.getItem(PROFILE_KEY);
    return raw ? JSON.parse(raw) : null;
  } catch {
    return null;
  }
}

export async function setCachedProfile(profile: LegalProfile): Promise<void> {
  try {
    await AsyncStorage.setItem(PROFILE_KEY, JSON.stringify(profile));
  } catch {
    // Fail silently — cache is best-effort
  }
}

export async function getCachedConversations(): Promise<ConversationSummary[]> {
  try {
    const raw = await AsyncStorage.getItem(CONVERSATIONS_KEY);
    return raw ? JSON.parse(raw) : [];
  } catch {
    return [];
  }
}

export async function setCachedConversations(
  conversations: ConversationSummary[]
): Promise<void> {
  try {
    await AsyncStorage.setItem(CONVERSATIONS_KEY, JSON.stringify(conversations));
  } catch {
    // Fail silently
  }
}

export async function clearCache(): Promise<void> {
  try {
    await AsyncStorage.multiRemove([PROFILE_KEY, CONVERSATIONS_KEY]);
  } catch {
    // Fail silently
  }
}
