<script setup lang="ts">
import { ref, onMounted, watch, onUnmounted } from 'vue';

interface Props {
  frequencies: number[]
  magnitudDb: number[]
  phaseRad: number[]
  height?: number         
}

const props = withDefaults(defineProps<Props>(), {
  height: 400
});

const magCanvasRef = ref<HTMLCanvasElement | null>(null);
const phaseCanvasRef = ref<HTMLCanvasElement | null>(null);
const containerRef = ref<HTMLDivElement | null>(null);

function draw() {
  const magCanvas = magCanvasRef.value;
  const phaseCanvas = phaseCanvasRef.value;
  if (!magCanvas || !phaseCanvas) return;
  
  const mCtx = magCanvas.getContext('2d');
  const pCtx = phaseCanvas.getContext('2d');
  if (!mCtx || !pCtx) return;

  const width = magCanvas.width / (window.devicePixelRatio || 1);
  const h = magCanvas.height / (window.devicePixelRatio || 1);
  
  mCtx.clearRect(0, 0, width, h);
  pCtx.clearRect(0, 0, width, h);

  if (!props.frequencies || props.frequencies.length === 0) return;

  const fMin = 20;
  const fMax = props.frequencies[props.frequencies.length - 1];
  
  const toX = (f: number) => {
    const logMin = Math.log10(fMin);
    const logMax = Math.log10(fMax);
    return ((Math.log10(Math.max(f, fMin)) - logMin) / (logMax - logMin)) * width;
  };

  // Magnitude Plot (top)
  let maxDb = -200;
  for (let i = 0; i < props.magnitudDb.length; i++) {
    if (props.magnitudDb[i] > maxDb) maxDb = props.magnitudDb[i];
  }
  const topDb = Math.max(0, Math.ceil(maxDb / 10) * 10);
  const botDb = topDb - 80;

  mCtx.beginPath();
  mCtx.strokeStyle = '#00D97E';
  mCtx.lineWidth = 1.5;
  for (let i = 0; i < props.frequencies.length; i++) {
    const x = toX(props.frequencies[i]);
    const y = h - ((props.magnitudDb[i] - botDb) / (topDb - botDb)) * h;
    if (i === 0) mCtx.moveTo(x, y);
    else mCtx.lineTo(x, y);
  }
  mCtx.stroke();

  // Phase Plot (bottom)
  const topPh = Math.PI;
  const botPh = -Math.PI;

  pCtx.beginPath();
  pCtx.strokeStyle = '#3B82F6'; 
  pCtx.lineWidth = 1.5;
  for (let i = 0; i < props.frequencies.length; i++) {
    const x = toX(props.frequencies[i]);
    const y = h - ((props.phaseRad[i] - botPh) / (topPh - botPh)) * h;
    if (i === 0) pCtx.moveTo(x, y);
    else pCtx.lineTo(x, y);
  }
  pCtx.stroke();
}

function resize() {
  if (containerRef.value && magCanvasRef.value && phaseCanvasRef.value) {
    const dpr = window.devicePixelRatio || 1;
    const rect = containerRef.value.getBoundingClientRect();
    const halfH = (props.height - 8) / 2; // Subtracting gap
    
    [magCanvasRef.value, phaseCanvasRef.value].forEach(canvas => {
      canvas.width = rect.width * dpr;
      canvas.height = halfH * dpr;
      canvas.style.width = `${rect.width}px`;
      canvas.style.height = `${halfH}px`;
      const ctx = canvas.getContext('2d');
      if (ctx) ctx.scale(dpr, dpr);
    });
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

watch([() => props.frequencies, () => props.magnitudDb, () => props.phaseRad], () => {
  requestAnimationFrame(draw);
});
</script>

<template>
  <div ref="containerRef" class="fr-container" :style="{ height: height + 'px' }">
    <div class="subplot">
      <div class="subplot-label">Magnitude (dB)</div>
      <canvas ref="magCanvasRef"></canvas>
    </div>
    <div class="subplot">
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
