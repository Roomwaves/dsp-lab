<script setup lang="ts">
import { ref, onMounted, watch, onUnmounted } from 'vue';

export interface Trace {
  frequencies: number[]
  magnitudeDb?: number[]
  phaseRad?: number[]
  color: string
  label: string
}

interface Props {
  frequencies: number[]
  magnitudDb: number[]
  phaseRad: number[]
  height?: number
  mode?: 'both' | 'magnitude' | 'phase'
  traces?: Trace[]
}

const props = withDefaults(defineProps<Props>(), {
  height: 300,
  mode: 'both',
  traces: () => []
});

const magCanvasRef = ref<HTMLCanvasElement | null>(null);
const phaseCanvasRef = ref<HTMLCanvasElement | null>(null);
const containerRef = ref<HTMLDivElement | null>(null);

function draw() {
  const magCanvas = magCanvasRef.value;
  const phaseCanvas = phaseCanvasRef.value;
  
  const showMag = props.mode !== 'phase' && magCanvas;
  const showPhase = props.mode !== 'magnitude' && phaseCanvas;
  
  if (!showMag && !showPhase) return;

  const mCtx = showMag ? magCanvas.getContext('2d') : null;
  const pCtx = showPhase ? phaseCanvas.getContext('2d') : null;

  if (mCtx && magCanvas) {
    const w = magCanvas.width / (window.devicePixelRatio || 1);
    const h = magCanvas.height / (window.devicePixelRatio || 1);
    mCtx.clearRect(0, 0, w, h);

    if (props.frequencies && props.frequencies.length > 0) {
      const fMin = 20;
      const fMax = props.frequencies[props.frequencies.length - 1] || 20000;
      
      const toX = (f: number) => {
        const logMin = Math.log10(fMin);
        const logMax = Math.log10(fMax);
        return ((Math.log10(Math.max(f, fMin)) - logMin) / (logMax - logMin)) * w;
      };

      let maxDb = -200;
      for (let i = 0; i < props.magnitudDb.length; i++) {
        if (props.magnitudDb[i] > maxDb) maxDb = props.magnitudDb[i];
      }
      for (const t of props.traces) {
        if (t.magnitudeDb) {
          for (let i = 0; i < t.magnitudeDb.length; i++) {
            if (t.magnitudeDb[i] > maxDb) maxDb = t.magnitudeDb[i];
          }
        }
      }
      const topDb = Math.max(0, Math.ceil(maxDb / 10) * 10);
      const botDb = topDb - 80;

      const toY = (db: number) => h - ((db - botDb) / (topDb - botDb)) * h;

      // Draw 0 dB reference
      const y0 = toY(0);
      if (y0 >= 0 && y0 <= h) {
        mCtx.save();
        mCtx.strokeStyle = 'rgba(255, 255, 255, 0.12)';
        mCtx.setLineDash([5, 5]);
        mCtx.beginPath();
        mCtx.moveTo(0, y0);
        mCtx.lineTo(w, y0);
        mCtx.stroke();
        mCtx.restore();
      }

      // Draw traces
      for (const t of props.traces) {
        if (t.magnitudeDb && t.frequencies && t.frequencies.length > 0) {
          mCtx.beginPath();
          mCtx.strokeStyle = t.color;
          mCtx.lineWidth = 1.2;
          for (let i = 0; i < t.frequencies.length; i++) {
            const x = toX(t.frequencies[i]);
            const y = toY(t.magnitudeDb[i]);
            if (i === 0) mCtx.moveTo(x, y);
            else mCtx.lineTo(x, y);
          }
          mCtx.stroke();
        }
      }

      // Draw main trace
      mCtx.beginPath();
      mCtx.strokeStyle = '#00D97E';
      mCtx.lineWidth = 2;
      for (let i = 0; i < props.frequencies.length; i++) {
        const x = toX(props.frequencies[i]);
        const y = h - ((props.magnitudDb[i] - botDb) / (topDb - botDb)) * h;
        if (i === 0) mCtx.moveTo(x, y);
        else mCtx.lineTo(x, y);
      }
      mCtx.stroke();
    }
  }

  if (pCtx && phaseCanvas) {
    const w = phaseCanvas.width / (window.devicePixelRatio || 1);
    const h = phaseCanvas.height / (window.devicePixelRatio || 1);
    pCtx.clearRect(0, 0, w, h);

    if (props.frequencies && props.frequencies.length > 0) {
      const fMin = 20;
      const fMax = props.frequencies[props.frequencies.length - 1] || 20000;
      
      const toX = (f: number) => {
        const logMin = Math.log10(fMin);
        const logMax = Math.log10(fMax);
        return ((Math.log10(Math.max(f, fMin)) - logMin) / (logMax - logMin)) * w;
      };

      const topPh = Math.PI;
      const botPh = -Math.PI;
      const toY = (p: number) => h - ((p - botPh) / (topPh - botPh)) * h;

      // Draw 0 rad reference
      const y0 = toY(0);
      pCtx.save();
      pCtx.strokeStyle = 'rgba(255, 255, 255, 0.08)';
      pCtx.setLineDash([5, 5]);
      pCtx.beginPath();
      pCtx.moveTo(0, y0);
      pCtx.lineTo(w, y0);
      pCtx.stroke();
      pCtx.restore();

      // Draw traces
      for (const t of props.traces) {
        if (t.phaseRad && t.frequencies && t.frequencies.length > 0) {
          pCtx.beginPath();
          pCtx.strokeStyle = t.color;
          pCtx.lineWidth = 1.2;
          for (let i = 0; i < t.frequencies.length; i++) {
            const x = toX(t.frequencies[i]);
            const y = toY(t.phaseRad[i]);
            if (i === 0) pCtx.moveTo(x, y);
            else pCtx.lineTo(x, y);
          }
          pCtx.stroke();
        }
      }

      // Draw main trace
      pCtx.beginPath();
      pCtx.strokeStyle = '#3B82F6'; 
      pCtx.lineWidth = 2;
      for (let i = 0; i < props.frequencies.length; i++) {
        const x = toX(props.frequencies[i]);
        const y = h - ((props.phaseRad[i] - botPh) / (topPh - botPh)) * h;
        if (i === 0) pCtx.moveTo(x, y);
        else pCtx.lineTo(x, y);
      }
      pCtx.stroke();
    }
  }
}

function resize() {
  if (containerRef.value) {
    const dpr = window.devicePixelRatio || 1;
    const rect = containerRef.value.getBoundingClientRect();
    
    if (props.mode !== 'phase' && magCanvasRef.value) {
      const parent = magCanvasRef.value.parentElement;
      if (parent) {
        const parentRect = parent.getBoundingClientRect();
        magCanvasRef.value.width = rect.width * dpr;
        magCanvasRef.value.height = parentRect.height * dpr;
        magCanvasRef.value.style.width = `${rect.width}px`;
        magCanvasRef.value.style.height = `${parentRect.height}px`;
        const ctx = magCanvasRef.value.getContext('2d');
        if (ctx) {
          ctx.resetTransform();
          ctx.scale(dpr, dpr);
        }
      }
    }
    
    if (props.mode !== 'magnitude' && phaseCanvasRef.value) {
      const parent = phaseCanvasRef.value.parentElement;
      if (parent) {
        const parentRect = parent.getBoundingClientRect();
        phaseCanvasRef.value.width = rect.width * dpr;
        phaseCanvasRef.value.height = parentRect.height * dpr;
        phaseCanvasRef.value.style.width = `${rect.width}px`;
        phaseCanvasRef.value.style.height = `${parentRect.height}px`;
        const ctx = phaseCanvasRef.value.getContext('2d');
        if (ctx) {
          ctx.resetTransform();
          ctx.scale(dpr, dpr);
        }
      }
    }
    draw();
  }
}

onMounted(() => {
  resize();
  window.addEventListener('resize', resize);
});

onUnmounted(() => {
  window.removeEventListener('resize', resize);
});

watch([() => props.frequencies, () => props.magnitudDb, () => props.phaseRad, () => props.traces, () => props.mode, () => props.height], () => {
  requestAnimationFrame(draw);
});
</script>

<template>
  <div ref="containerRef" class="fr-container" :style="{ height: height + 'px' }">
    <div v-if="mode !== 'phase'" class="subplot">
      <div class="subplot-label">Magnitude (dB)</div>
      <canvas ref="magCanvasRef"></canvas>
    </div>
    <div v-if="mode !== 'magnitude'" class="subplot">
      <div class="subplot-label">Phase (rad)</div>
      <canvas ref="phaseCanvasRef"></canvas>
    </div>
  </div>
</template>

<style scoped>
.fr-container {
  width: 100%;
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.subplot {
  flex: 1;
  position: relative;
  background: var(--color-bg-secondary);
  border-radius: var(--border-radius-md);
  border: 1px solid var(--color-border);
  overflow: hidden;
}

.subplot-label {
  position: absolute;
  top: 6px;
  left: 10px;
  font-size: 10px;
  font-weight: 600;
  color: var(--color-text-secondary);
  background: var(--color-bg-elevated);
  padding: 1px 5px;
  border-radius: 3px;
  z-index: 2;
  pointer-events: none;
}

canvas {
  display: block;
}
</style>
