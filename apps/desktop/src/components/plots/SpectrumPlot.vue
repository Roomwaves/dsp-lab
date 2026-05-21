<script setup lang="ts">
import { ref, onMounted, watch, onUnmounted } from 'vue';

interface Props {
  frequencies: number[]
  magnitudes: number[]
  label?: string
  dbScale?: boolean       
  logFrequency?: boolean  
  height?: number
}

const props = withDefaults(defineProps<Props>(), {
  dbScale: false,
  logFrequency: true,
  height: 200
});

const canvasRef = ref<HTMLCanvasElement | null>(null);
const containerRef = ref<HTMLDivElement | null>(null);

function draw() {
  const canvas = canvasRef.value;
  if (!canvas) return;
  const ctx = canvas.getContext('2d');
  if (!ctx) return;

  const width = canvas.width / (window.devicePixelRatio || 1);
  const height = canvas.height / (window.devicePixelRatio || 1);
  ctx.clearRect(0, 0, width, height);

  if (!props.frequencies || props.frequencies.length === 0) return;

  const fMin = 20;
  const fMax = props.frequencies[props.frequencies.length - 1];
  
  let maxMag = 0;
  let currentMaxDb = -200;
  for (const m of props.magnitudes) {
    if (m > maxMag) maxMag = m;
    const db = 20 * Math.log10(m + 1e-12);
    if (db > currentMaxDb) currentMaxDb = db;
  }

  const maxDb = Math.max(0, Math.ceil(currentMaxDb / 10) * 10);
  const minDb = maxDb - 100;
  if (maxMag === 0) maxMag = 1;

  const toX = (f: number) => {
    if (props.logFrequency) {
      const logMin = Math.log10(fMin);
      const logMax = Math.log10(fMax);
      return ((Math.log10(Math.max(f, fMin)) - logMin) / (logMax - logMin)) * width;
    } else {
      return (f / fMax) * width;
    }
  };

  const toY = (mag: number) => {
    if (props.dbScale) {
      const db = 20 * Math.log10(mag + 1e-12);
      return height - ((db - minDb) / (maxDb - minDb)) * height;
    } else {
      return height - (mag / maxMag) * height;
    }
  };

  // Draw 0 dB reference line
  if (props.dbScale) {
    ctx.strokeStyle = 'rgba(255, 255, 255, 0.1)';
    ctx.setLineDash([5, 5]);
    ctx.lineWidth = 1;
    const y0 = toY(1);
    ctx.beginPath();
    ctx.moveTo(0, y0);
    ctx.lineTo(width, y0);
    ctx.stroke();
    ctx.setLineDash([]);
  }

  // Draw spectrum
  ctx.beginPath();
  ctx.strokeStyle = '#00D97E';
  ctx.lineWidth = 1.5;

  for (let i = 0; i < props.frequencies.length; i++) {
    const f = props.frequencies[i];
    const x = toX(f);
    const y = toY(props.magnitudes[i]);
    
    if (i === 0) {
      ctx.moveTo(x, y);
    } else {
      ctx.lineTo(x, y);
    }
  }
  ctx.stroke();
}

function resize() {
  if (containerRef.value && canvasRef.value) {
    const dpr = window.devicePixelRatio || 1;
    const rect = containerRef.value.getBoundingClientRect();
    canvasRef.value.width = rect.width * dpr;
    canvasRef.value.height = props.height * dpr;
    canvasRef.value.style.width = `${rect.width}px`;
    canvasRef.value.style.height = `${props.height}px`;
    const ctx = canvasRef.value.getContext('2d');
    if (ctx) ctx.scale(dpr, dpr);
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

watch([() => props.frequencies, () => props.magnitudes, () => props.dbScale, () => props.logFrequency], () => {
  requestAnimationFrame(draw);
});
</script>

<template>
  <div ref="containerRef" class="spectrum-container" :style="{ height: height + 'px' }">
    <div v-if="label" class="plot-label">{{ label }}</div>
    <canvas ref="canvasRef"></canvas>
  </div>
</template>

<style scoped>
.spectrum-container {
  width: 100%;
  position: relative;
  background: var(--color-bg-secondary);
  border-radius: var(--border-radius-md);
  border: 1px solid var(--color-border);
  overflow: hidden;
}

.plot-label {
  position: absolute;
  top: 8px;
  left: 12px;
  font-size: 11px;
  font-weight: 600;
  color: var(--color-text-secondary);
  background: var(--color-bg-elevated);
  padding: 2px 6px;
  border-radius: 4px;
  pointer-events: none;
  z-index: 2;
}

canvas {
  display: block;
}
</style>
