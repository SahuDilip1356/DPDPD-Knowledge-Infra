import { createClient } from "@supabase/supabase-js";

// Fetch from Vite environment variables
const supabaseUrl = import.meta.env.VITE_SUPABASE_URL || "";
const supabaseAnonKey = import.meta.env.VITE_SUPABASE_ANON_KEY || "";

// Initialize Supabase Client ONLY if credentials are provided.
// This allows the app to work seamlessly in local mock-fallback mode or cloud-connected mode!
export const supabase = (supabaseUrl && supabaseAnonKey)
  ? createClient(supabaseUrl, supabaseAnonKey)
  : null;

// Helper to log state
if (supabase) {
  console.log("[Supabase] Active: Connected to cloud data gateway.");
} else {
  console.log("[Supabase] Offline Mode: Utilizing local DPDPA regulatory mockData.");
}
