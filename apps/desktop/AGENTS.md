# Tauri Desktop Application

Native desktop app shell (Rust/Tauri) + web UI (Vue 3/TypeScript).
This module owns the user interface. It contains no DSP logic.

---

## Two layers, two responsibilities

```
src-tauri/    Rust — native OS access, app lifecycle, IPC bridge, audio I/O
src/          TypeScript/Vue — user interface, state, visualization
```

**`src/` knows nothing about Rust internals.
`src-tauri/` knows nothing about Vue component structure.**
They communicate exclusively through Tauri's command/event system.

---

## src/ structure

```
src/
  components/
    plots/          WaveformPlot.vue, SpectrumPlot.vue, CoherencePlot.vue
    controls/       FilterControls.vue, SignalControls.vue
    layout/         AppSidebar.vue, TopBar.vue
  views/
    tools/          RTAView.vue, TransferFunctionView.vue, SpectrogramView.vue
                    CoherenceView.vue, FilterDesignerView.vue, SignalGeneratorView.vue
  stores/
    useSignalStore.ts
    useFilterStore.ts
    useAudioStore.ts
  router/
    index.ts
  main.ts
```

---

## Rules

### ✅ DO
- Use `<script setup lang="ts">` syntax in all components
- Keep components **dumb**: they receive props and emit events — no business logic
- Put all state in Pinia stores — components read from stores, never manage their own data
- Use `@tabler/icons-vue` for icons — import individually, never the full pack
- Communicate with the API via a dedicated service layer (`src/services/api.ts`), not directly in components or stores
- Use `invoke()` for Tauri commands (native features) and `fetch()` for API calls
- Handle loading and error states explicitly in every async operation
- Use Vue Router named routes — never hardcode paths as strings in `<RouterLink>`

### ❌ DON'T
- Import `numpy`, `scipy`, or any Python-specific library — use the API
- Compute DSP operations in TypeScript — all computation happens in `core/dsp` via the API
- Use `localStorage` or `sessionStorage` for persistent state — Tauri has its own store
- Write inline styles — use CSS classes or Tailwind utilities
- Use `any` type in TypeScript — define proper interfaces in `src/types/`
- Call the API directly from a component — go through a store action
- Put route-level logic inside components — use the router guards

---

## Communication patterns

### Vue → API (offline analysis)
```typescript
// src/services/api.ts
const API_BASE = import.meta.env.VITE_API_URL ?? 'http://localhost:8000'

export async function computeFFT(samples: number[], fs: number) {
  const res = await fetch(`${API_BASE}/analysis/fft`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ samples, fs }),
  })
  if (!res.ok) throw new Error(`API error ${res.status}`)
  return res.json() as Promise<FFTOutput>
}
```

### Vue → Tauri (native / real-time)
```typescript
import { invoke } from '@tauri-apps/api/core'

// Call a Rust command defined in src-tauri/src/commands/
const result = await invoke<number[]>('process_audio_block', { block: samples })
```

**Use API for:** batch analysis, filter design, coherence, file loading
**Use Tauri commands for:** real-time audio stream, file system access, OS dialogs

---

## Pinia store pattern

```typescript
// stores/useSignalStore.ts
import { defineStore } from 'pinia'
import { computeFFT } from '../services/api'

export const useSignalStore = defineStore('signal', () => {
  const samples = ref<number[]>([])
  const frequencies = ref<number[]>([])
  const magnitudes = ref<number[]>([])
  const isLoading = ref(false)
  const error = ref<string | null>(null)

  async function runFFT(fs: number) {
    isLoading.value = true
    error.value = null
    try {
      const result = await computeFFT(samples.value, fs)
      frequencies.value = result.frequencies
      magnitudes.value = result.magnitudes
    } catch (e) {
      error.value = (e as Error).message
    } finally {
      isLoading.value = false
    }
  }

  return { samples, frequencies, magnitudes, isLoading, error, runFFT }
})
```

---

## src-tauri/ rules

- All Tauri commands live in `src-tauri/src/commands/` — one file per domain
- Register commands in `src-tauri/src/lib.rs` via `.invoke_handler(tauri::generate_handler![...])`
- Audio I/O (real-time) will use `cpal` — isolate it in `src-tauri/src/audio/`
- Heavy DSP in Tauri commands delegates to `core/dsp_rs` — never reimplement math here
- Capabilities (file system, network, shell) are declared in `src-tauri/capabilities/` — request minimum permissions

---

## Types

Define shared TypeScript interfaces in `src/types/`:

```typescript
// src/types/dsp.ts
export interface FFTOutput {
  frequencies: number[]
  magnitudes: number[]
}

export interface FrequencyResponseOutput {
  frequencies: number[]
  magnitude_db: number[]
  phase_rad: number[]
}
```

No `any`. If the API returns something untyped, define the interface and cast.

---

## Commands

```bash
# Development (from repo root)
npm run dev               # Tauri + Vue with hot reload

# From apps/desktop/
npm run dev               # Vite dev server only (no Tauri)
npm run tauri:dev         # Full Tauri dev mode
npm run build             # Production build
npm run lint              # ESLint + Prettier
npx vitest run            # Unit tests
npx playwright test       # E2E tests
```
