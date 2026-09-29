#!/usr/bin/env python3
"""
Supabase Storage Bucket Setup Script
====================================
Automates the creation of a public 'gazette-pdfs' storage bucket on your Supabase instance,
and provides the PostgreSQL SQL script to set up secure RLS policies.
"""

import os
import sys
from dotenv import load_dotenv
from supabase import create_client

load_dotenv()

# We need the service role key to manage storage buckets programmatically
url = os.getenv("SUPABASE_URL") or os.getenv("VITE_SUPABASE_URL")
service_key = os.getenv("SUPABASE_SERVICE_KEY")

SQL_POLICIES = """
-- ═══════════════════════════════════════════════════════════════════
-- SUPABASE STORAGE SECURITY POLICIES FOR GAZETTE PDF BUCKET
-- Run this script in your Supabase SQL Editor to secure document files.
-- ═══════════════════════════════════════════════════════════════════

-- 1. Create public select policy
CREATE POLICY "Allow public read access to Gazette PDFs"
ON storage.objects FOR SELECT
USING ( bucket_id = 'gazette-pdfs' );

-- 2. Create authenticated upload policy
CREATE POLICY "Allow authenticated admin upload"
ON storage.objects FOR INSERT
TO authenticated
WITH CHECK ( bucket_id = 'gazette-pdfs' );

-- 3. Create authenticated delete policy
CREATE POLICY "Allow authenticated admin delete"
ON storage.objects FOR DELETE
TO authenticated
USING ( bucket_id = 'gazette-pdfs' );
"""

def main():
    if not url or not service_key:
        print("[!] ERROR: SUPABASE_URL and SUPABASE_SERVICE_KEY must be set in your environment.")
        print("    If you don't have the service key, run the SQL script below in the Supabase SQL Editor:")
        print(SQL_POLICIES)
        sys.exit(1)

    print("[*] Connecting to Supabase client...")
    supabase_client = create_client(url, service_key)

    print("[*] Creating public storage bucket 'gazette-pdfs'...")
    try:
        # Check if bucket already exists
        buckets = supabase_client.storage.list_buckets()
        exists = any(b.name == 'gazette-pdfs' for b in buckets)
        
        if not exists:
            supabase_client.storage.create_bucket('gazette-pdfs', options={"public": True})
            print("[+] Successfully created public storage bucket 'gazette-pdfs'!")
        else:
            print("[*] Storage bucket 'gazette-pdfs' already exists. Skipping creation.")
            
        print("\n" + "═" * 70)
        print("   🔒 RUN THE FOLLOWING SQL POLICIES IN YOUR SUPABASE SQL EDITOR")
        print("═" * 70)
        print(SQL_POLICIES)
        print("═" * 70)
        
    except Exception as e:
        print(f"[!] Error creating bucket: {e}")
        print("\nIf you encounter permission issues, copy/run this in the Supabase SQL Editor:")
        print(f"INSERT INTO storage.buckets (id, name, public) VALUES ('gazette-pdfs', 'gazette-pdfs', true);")
        print(SQL_POLICIES)

if __name__ == "__main__":
    main()
