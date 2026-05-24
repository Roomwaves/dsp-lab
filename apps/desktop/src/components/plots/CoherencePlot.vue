<script setup lang="ts">
import { ref, onMounted, watch, onUnmounted } from 'vue';

export interface CoherenceTrace {
  frequencies: number[]
  coherence: number[]
  color: string
  label: string
}

interface Props {
  frequencies: number[]
  coherence: number[]   // valores en [0, 1]
  height?: number
  traces?: CoherenceTrace[]
}

const props = withDefaults(defineProps<Props>(), {
  height: 200,
  traces: () => []
});

const canvasRef = ref<HTMLCanvasElement | null>(null);
const containerRef = ref<HTMLDivElement | null>(null);

const HIGH_COHERENCE_THRESHOLD = 0.9;

function draw() {
  const canvas = canvasRef.value;
  if (!canvas) return;
  const ctx = canvas.getContext('2d');
  if (!ctx) return;

  const dpr = window.devicePixelRatio || 1;
  const width = canvas.width / dpr;
  const height = canvas.height / dpr;

  ctx.clearRect(0, 0, width, height);

  // Y fijo en [0, 1]
  const yMin = 0;
  const yMax = 1;

  const toY = (v: number) => height - ((v - yMin) / (yMax - yMin)) * height;

  // Fondo tenue de zona "alta coherencia" (encima del umbral 0.9)
  const yThreshold = toY(HIGH_COHERENCE_THRESHOLD);
  ctx.fillStyle = 'rgba(34, 197, 94, 0.05)';
  ctx.fillRect(0, 0, width, yThreshold);

  // Línea de referencia γ² = 0.9 (punteada)
  ctx.save();
  ctx.strokeStyle = 'rgba(34, 197, 94, 0.55)';
  ctx.setLineDash([6, 4]);
  ctx.lineWidth = 1;
  ctx.beginPath();
  ctx.moveTo(0, yThreshold);
  ctx.lineTo(width, yThreshold);
  ctx.stroke();
  ctx.restore();

  // Etiqueta de la línea de referencia
  ctx.font = '10px monospace';
  ctx.fillStyle = 'rgba(34, 197, 94, 0.7)';
  ctx.fillText('γ² = 0.9', width - 54, yThreshold - 4);

  if (!props.frequencies || props.frequencies.length === 0) return;

  const fMin = Math.max(props.frequencies[0] || 1, 1);
  const fMax = props.frequencies[props.frequencies.length - 1] || 20000;

  const toX = (f: number) => {
    const logMin = Math.log10(fMin);
    const logMax = Math.log10(fMax);
    return ((Math.log10(Math.max(f, fMin)) - logMin) / (logMax - logMin)) * width;
  };

  // 1. Draw traces (snapshots)
  for (const trace of props.traces) {
    if (trace.frequencies && trace.frequencies.length > 0 && trace.coherence) {
      ctx.beginPath();
      ctx.strokeStyle = trace.color;
      ctx.lineWidth = 1.2;
      for (let i = 0; i < trace.frequencies.length; i++) {
        const x = toX(trace.frequencies[i]);
        const y = toY(trace.coherence[i]);
        if (i === 0) ctx.moveTo(x, y);
        else ctx.lineTo(x, y);
      }
      ctx.stroke();
    }
  }

  // 2. Dibujar la curva de coherencia segmentada por color (main trace)
  let i = 0;
  while (i < props.frequencies.length) {
    const aboveThreshold = props.coherence[i] > HIGH_COHERENCE_THRESHOLD;
    ctx.beginPath();
    ctx.strokeStyle = aboveThreshold ? '#22C55E' : '#F97316';
    ctx.lineWidth = 2.0;

    const startX = toX(props.frequencies[i]);
    const startY = toY(props.coherence[i]);
    ctx.moveTo(startX, startY);

    let j = i + 1;
    while (j < props.frequencies.length) {
      const nextAbove = props.coherence[j] > HIGH_COHERENCE_THRESHOLD;
      if (nextAbove !== aboveThreshold) {
        // Interpolamos el punto de cruce para continuidad visual
        const xCross = toX((props.frequencies[j - 1] + props.frequencies[j]) / 2);
        const yCross = toY(HIGH_COHERENCE_THRESHOLD);
        ctx.lineTo(xCross, yCross);
        break;
      }
      ctx.lineTo(toX(props.frequencies[j]), toY(props.coherence[j]));
      j++;
    }
    ctx.stroke();
    i = j;
  }
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
    if (ctx) {
      ctx.resetTransform();
      ctx.scale(dpr, dpr);
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

watch([() => props.frequencies, () => props.coherence, () => props.traces, () => props.height], () => {
  requestAnimationFrame(draw);
});
</script>

<template>
  <div ref="containerRef" class="coherence-container" :style="{ height: height + 'px' }">
    <div class="plot-label">Coherence γ²</div>
    <canvas ref="canvasRef"></canvas>
  </div>
</template>

<style scoped>
.coherence-container {
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