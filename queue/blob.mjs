// Private Vercel Blob store: clips and stills live here so they outlast EngineX's 24-48 h expiry and the web UI can show them.
import './lib.mjs'; // loads ../.env into process.env
import fs from 'node:fs'; import { put, list } from '@vercel/blob';
export const toBlob = async (file, key) => { if (!process.env.BLOB_READ_WRITE_TOKEN) return; await put(key, fs.readFileSync(file), { access: 'private', allowOverwrite: true, addRandomSuffix: false }); };
export async function blobSet(prefix) { const s = new Set(); let cursor; do { const r = await list({ prefix, cursor, limit: 1000 }); r.blobs.forEach(b => s.add(b.pathname)); cursor = r.hasMore ? r.cursor : undefined; } while (cursor); return s; }
