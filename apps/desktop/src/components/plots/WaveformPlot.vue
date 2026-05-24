<script setup lang="ts">
import { ref, onMounted, watch, onUnmounted } from 'vue';

export interface WaveformTrace {
  samples: number[]
  fs: number
  color: string
  label: string
}

interface Props {
  samples?: number[]
  fs?: number
  label?: string          
  color?: string          
  height?: number         
  traces?: WaveformTrace[]
}

const props = withDefaults(defineProps<Props>(), {
  color: '#00D97E', 
  height: 200,
  traces: () => []
});

const canvasRef = ref<HTMLCanvasElement | null>(null);
const containerRef = ref<HTMLDivElement | null>(null);
const tooltip = ref({ show: false, x: 0, y: 0, time: 0, value: 0 });

function downsample(data: number[], target: number): number[] {
  if (data.length <= target) return data;
  const ratio = Math.ceil(data.length / target);
  const result = [];
  for (let i = 0; i < data.length; i += ratio) {
    result.push(data[i]);
  }
  return result;
}

function draw() {
  const canvas = canvasRef.value;
  if (!canvas) return;
  const ctx = canvas.getContext('2d');
  if (!ctx) return;

  const width = canvas.width / (window.devicePixelRatio || 1);
  const height = canvas.height / (window.devicePixelRatio || 1);
  ctx.clearRect(0, 0, width, height);

  const hasMainData = props.samples && props.samples.length > 0;
  const hasTracesData = props.traces && props.traces.length > 0;
  if (!hasMainData && !hasTracesData) return;

  let globalMin = 0;
  let globalMax = 0;

  const findMinMax = (arr: number[]) => {
    if (!arr || arr.length === 0) return;
    for (const val of arr) {
      if (val < globalMin) globalMin = val;
      if (val > globalMax) globalMax = val;
    }
  };

  if (props.samples) {
    findMinMax(props.samples);
  }
  for (const t of props.traces) {
    findMinMax(t.samples);
  }

  const range = (globalMax - globalMin) || 2;
  const offset = globalMin;

  const drawSignal = (data: number[], color: string) => {
    const displayData = data.length > 10000 
      ? downsample(data, 2000) 
      : data;

    ctx.beginPath();
    ctx.strokeStyle = color; 
    ctx.lineWidth = 1.5;

    for (let i = 0; i < displayData.length; i++) {
      const x = (i / (displayData.length - 1)) * width;
      const y = height - ((displayData[i] - offset) / range) * height;
      
      if (i === 0) ctx.moveTo(x, y);
      else ctx.lineTo(x, y);
    }
    ctx.stroke();
  };

  // Draw traces
  for (const t of props.traces) {
    drawSignal(t.samples, t.color);
  }

  // Draw main signal
  if (props.samples && props.samples.length > 0) {
    drawSignal(props.samples, props.color);
  }
}

function handleMouseMove(e: MouseEvent) {
  const currentSamples = props.samples && props.samples.length > 0
    ? props.samples
    : (props.traces && props.traces.length > 0 ? props.traces[0].samples : null);
    
  const currentFs = props.fs || (props.traces && props.traces.length > 0 ? props.traces[0].fs : 44100);

  if (!canvasRef.value || !currentSamples || currentSamples.length === 0) return;
  const rect = canvasRef.value.getBoundingClientRect();
  const x = e.clientX - rect.left;
  const ratio = Math.max(0, Math.min(1, x / rect.width));
  const index = Math.floor(ratio * (currentSamples.length - 1));
  
  if (index >= 0 && index < currentSamples.length) {
    tooltip.value = {
      show: true,
      x: x,
      y: e.clientY - rect.top,
      time: index / currentFs,
      value: currentSamples[index]
    };
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

watch([() => props.samples, () => props.traces, () => props.height], () => {
  requestAnimationFrame(draw);
});
</script>

<template>
  <div ref="containerRef" class="waveform-container" :style="{ height: height + 'px' }">
    <div v-if="label" class="plot-label">{{ label }}</div>
    <canvas 
      ref="canvasRef" 
      @mousemove="handleMouseMove" 
      @mouseleave="tooltip.show = false"
    ></canvas>
    <div v-if="tooltip.show" class="tooltip" :style="{ left: tooltip.x + 'px', top: (tooltip.y - 40) + 'px' }">
      t = {{ tooltip.time.toFixed(4) }} s, amp = {{ tooltip.value.toFixed(4) }}
    </div>
  </div>
</template>

<style scoped>
.waveform-container {
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

.tooltip {
  position: absolute;
  background: rgba(0, 0, 0, 0.9);
  color: white;
  padding: 4px 8px;
  border-radius: 4px;
  font-size: 10px;
  pointer-events: none;
  white-space: nowrap;
  z-index: 5;
  transform: translateX(-50%);
  border: 0.5px solid var(--color-border);
}
</style>
