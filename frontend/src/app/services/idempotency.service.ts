import { Injectable } from '@angular/core';

const TTL_MS = 5 * 60 * 1000;

@Injectable({ providedIn: 'root' })
export class IdempotencyService {
  private cache = new Map<string, { key: string; exp: number }>();

  async getKeyFor(action: string, payload?: unknown): Promise<string> {  // <- Promise<string>
    const hash = payload ? await this.hashPayload(payload) : this.uuid();
    const cacheKey = `${action}:${hash}`;

    const hit = this.cache.get(cacheKey);
    const now = Date.now();
    if (hit && hit.exp > now) return hit.key;

    const key = this.uuid();
    this.cache.set(cacheKey, { key, exp: now + TTL_MS });
    return key;
  }

  private async hashPayload(payload: unknown): Promise<string> {          // <- Promise<string>
    const canonical = JSON.stringify(payload, Object.keys(payload as any).sort());
    const enc = new TextEncoder().encode(canonical);
    const digest = await crypto.subtle.digest('SHA-256', enc);
    return Array.from(new Uint8Array(digest)).map(b => b.toString(16).padStart(2, '0')).join('');
  }

  private uuid(): string {
    return (crypto as any).randomUUID?.() ?? this.fallbackUuid();
  }

  private fallbackUuid(): string {
    return 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, c => {
      const r = (Math.random() * 16) | 0; const v = c === 'x' ? r : (r & 0x3) | 0x8;
      return v.toString(16);
    });
  }
}
