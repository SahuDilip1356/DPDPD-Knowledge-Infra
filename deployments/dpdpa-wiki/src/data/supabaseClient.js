import { createClient } from "@supabase/supabase-js";
import { MOCKS_ENABLED } from "./runtimeMode";

// Fetch from Vite environment variables
const supabaseUrl = import.meta.env.VITE_SUPABASE_URL || "";
const supabaseAnonKey = import.meta.env.VITE_SUPABASE_ANON_KEY || "";

// Initialize Supabase only when both public values are configured.
export const supabase = (supabaseUrl && supabaseAnonKey)
  ? createClient(supabaseUrl, supabaseAnonKey)
  : null;

// Helper to log state
if (supabase) {
  console.log("[Supabase] Active: Connected to cloud data gateway.");
} else {
  console.log(MOCKS_ENABLED
    ? "[Supabase] Explicit local fixture mode active."
    : "[Supabase] Not configured; data-backed screens will show unavailable or empty states.");
}
