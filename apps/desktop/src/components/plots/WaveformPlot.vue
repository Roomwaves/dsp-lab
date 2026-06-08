<script setup lang="ts">
import { ref, computed, onMounted, watch, onUnmounted } from 'vue';

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

// Zoom State
const zoomTimeMin = ref<number | null>(null);
const zoomTimeMax = ref<number | null>(null);

const activeTimeMin = computed(() => zoomTimeMin.value ?? 0);
const activeTimeMax = computed(() => {
  const dataMax = props.samples && props.samples.length > 0 
    ? props.samples.length / (props.fs || 44100) 
    : (props.traces && props.traces.length > 0 
       ? props.traces[0].samples.length / (props.traces[0].fs || 44100) 
       : 1);
  return zoomTimeMax.value ?? dataMax;
});

// Drag and Hover State
const isDragging = ref(false);
const dragStartX = ref(0);
const dragEndX = ref(0);
const hoverX = ref<number | null>(null);
const hoverY = ref<number | null>(null);

interface TooltipItem {
  label: string
  value: string
  color: string
}

const tooltip = ref({
  show: false,
  x: 0,
  y: 0,
  xValFormatted: '',
  items: [] as TooltipItem[]
});

// Dimensions Helper
function getPlotDimensions() {
  const canvas = canvasRef.value;
  if (!canvas) return { width: 0, height: 0, padL: 45, padR: 15, padT: 15, padB: 20, plotW: 0, plotH: 0 };
  const dpr = window.devicePixelRatio || 1;
  const width = canvas.width / dpr;
  const height = canvas.height / dpr;
  const padL = 45;
  const padR = 15;
  const padT = 15;
  const padB = 20;
  return {
    width,
    height,
    padL,
    padR,
    padT,
    padB,
    plotW: width - padL - padR,
    plotH: height - padT - padB
  };
}

function toX(t: number) {
  const { padL, plotW } = getPlotDimensions();
  const tMin = activeTimeMin.value;
  const tMax = activeTimeMax.value;
  if (tMax === tMin) return padL;
  return padL + ((t - tMin) / (tMax - tMin)) * plotW;
}

function fromX(x: number) {
  const { padL, plotW } = getPlotDimensions();
  const tMin = activeTimeMin.value;
  const tMax = activeTimeMax.value;
  const relativeX = x - padL;
  const ratio = Math.max(0, Math.min(1, relativeX / plotW));
  return tMin + ratio * (tMax - tMin);
}

// Draw Function
function draw() {
  const canvas = canvasRef.value;
  if (!canvas) return;
  const ctx = canvas.getContext('2d');
  if (!ctx) return;

  const { width, height, padL, padT, plotW, plotH } = getPlotDimensions();
  ctx.clearRect(0, 0, width, height);

  const hasMainData = props.samples && props.samples.length > 0;
  const hasTracesData = props.traces && props.traces.length > 0;
  if (!hasMainData && !hasTracesData) return;

  let globalMin = -0.01;
  let globalMax = 0.01;

  // Find Min/Max in the visible zoomed X-range for vertical auto-scaling
  const findMinMax = (arr: number[], fs: number) => {
    if (!arr || arr.length === 0) return;
    const startIndex = Math.max(0, Math.floor(activeTimeMin.value * fs));
    const endIndex = Math.min(arr.length, Math.ceil(activeTimeMax.value * fs));
    for (let i = startIndex; i < endIndex; i++) {
      const val = arr[i];
      if (val < globalMin) globalMin = val;
      if (val > globalMax) globalMax = val;
    }
  };

  if (props.samples) {
    findMinMax(props.samples, props.fs || 44100);
  }
  for (const t of props.traces) {
    findMinMax(t.samples, t.fs || 44100);
  }

  // Margin of 10%
  const maxAbs = Math.max(Math.abs(globalMin), Math.abs(globalMax), 0.001);
  const range = maxAbs * 2.2;
  const offset = -maxAbs * 1.1;

  const toY = (val: number) => padT + plotH - ((val - offset) / range) * plotH;

  // Draw Grid & Border
  ctx.save();
  ctx.strokeStyle = 'rgba(255, 255, 255, 0.08)';
  ctx.fillStyle = 'rgba(255, 255, 255, 0.45)';
  ctx.font = '9px monospace';

  // Border
  ctx.strokeRect(padL, padT, plotW, plotH);

  // Horizontal lines (Amplitude)
  const ampSteps = [maxAbs, maxAbs / 2, 0, -maxAbs / 2, -maxAbs];
  for (const amp of ampSteps) {
    const y = toY(amp);
    if (y >= padT && y <= padT + plotH) {
      ctx.strokeStyle = amp === 0 ? 'rgba(255, 255, 255, 0.2)' : 'rgba(255, 255, 255, 0.08)';
      ctx.setLineDash(amp === 0 ? [] : [3, 3]);
      ctx.beginPath();
      ctx.moveTo(padL, y);
      ctx.lineTo(padL + plotW, y);
      ctx.stroke();

      ctx.textAlign = 'right';
      ctx.fillText(amp.toFixed(2), padL - 6, y + 3);
    }
  }

  // Vertical lines (Time steps: e.g. 5 steps in the visible range)
  const numSteps = 5;
  ctx.setLineDash([3, 3]);
  ctx.strokeStyle = 'rgba(255, 255, 255, 0.08)';
  const tMin = activeTimeMin.value;
  const tMax = activeTimeMax.value;
  const tRange = tMax - tMin;

  for (let s = 0; s <= numSteps; s++) {
    const time = tMin + (s / numSteps) * tRange;
    const x = padL + (s / numSteps) * plotW;
    ctx.beginPath();
    ctx.moveTo(x, padT);
    ctx.lineTo(x, padT + plotH);
    ctx.stroke();

    ctx.textAlign = 'center';
    ctx.fillText(`${time.toFixed(3)}s`, x, height - 5);
  }
  ctx.restore();

  // Draw Signal (smart envelope + point connect if zoomed close)
  const drawSignalEnvelope = (data: number[], fs: number, color: string) => {
    ctx.save();
    ctx.strokeStyle = color;
    ctx.lineWidth = 1.0;

    const startIndex = Math.max(0, Math.floor(tMin * fs));
    const endIndex = Math.min(data.length, Math.ceil(tMax * fs));
    const visibleLength = endIndex - startIndex;

    if (visibleLength <= 0) {
      ctx.restore();
      return;
    }

    const numPixels = Math.floor(plotW);

    if (visibleLength <= numPixels) {
      // Direct sample drawing for high detail
      ctx.beginPath();
      let first = true;
      for (let i = 0; i < visibleLength; i++) {
        const idx = startIndex + i;
        const xVal = toX(idx / fs);
        const yVal = toY(data[idx]);
        if (first) {
          ctx.moveTo(xVal, yVal);
          first = false;
        } else {
          ctx.lineTo(xVal, yVal);
        }
      }
      ctx.stroke();

      // Show dots for individual samples if very close
      if (visibleLength < 100) {
        for (let i = 0; i < visibleLength; i++) {
          const idx = startIndex + i;
          const xVal = toX(idx / fs);
          const yVal = toY(data[idx]);
          ctx.beginPath();
          ctx.arc(xVal, yVal, 2, 0, 2 * Math.PI);
          ctx.fillStyle = color;
          ctx.fill();
        }
      }
    } else {
      // Large signal envelope
      const blockSize = Math.ceil(visibleLength / numPixels);

      for (let x = 0; x < numPixels; x++) {
        const start = startIndex + x * blockSize;
        const end = Math.min(start + blockSize, endIndex);
        if (start >= endIndex) break;

        let min = data[start];
        let max = data[start];
        for (let i = start + 1; i < end; i++) {
          const val = data[i];
          if (val < min) min = val;
          if (val > max) max = val;
        }

        const yMin = toY(min);
        const yMax = toY(max);
        const canvasX = padL + x;

        ctx.beginPath();
        ctx.moveTo(canvasX, yMin);
        ctx.lineTo(canvasX, yMax);
        ctx.stroke();
      }
    }
    ctx.restore();
  };

  // Draw traces
  for (const t of props.traces) {
    drawSignalEnvelope(t.samples, t.fs, t.color);
  }

  // Draw main signal
  if (props.samples && props.samples.length > 0) {
    drawSignalEnvelope(props.samples, props.fs || 44100, props.color);
  }

  // Draw drag selection rect for zoom
  if (isDragging.value) {
    ctx.save();
    ctx.fillStyle = 'rgba(0, 217, 126, 0.12)';
    ctx.strokeStyle = 'rgba(0, 217, 126, 0.5)';
    ctx.lineWidth = 1.5;
    const xMin = Math.min(dragStartX.value, dragEndX.value);
    const xMax = Math.max(dragStartX.value, dragEndX.value);
    ctx.fillRect(xMin, padT, xMax - xMin, plotH);
    ctx.strokeRect(xMin, padT, xMax - xMin, plotH);
    ctx.restore();
  }

  // Draw vertical cursor and intersection dots
  if (hoverX.value !== null && !isDragging.value) {
    ctx.save();
    ctx.strokeStyle = 'rgba(255, 255, 255, 0.25)';
    ctx.lineWidth = 1;
    ctx.setLineDash([2, 2]);
    ctx.beginPath();
    ctx.moveTo(hoverX.value, padT);
    ctx.lineTo(hoverX.value, padT + plotH);
    ctx.stroke();
    ctx.restore();

    const t = fromX(hoverX.value);

    // Main signal dot
    if (props.samples && props.samples.length > 0) {
      const fs = props.fs || 44100;
      const idx = Math.floor(t * fs);
      if (idx >= 0 && idx < props.samples.length) {
        const yVal = toY(props.samples[idx]);
        if (yVal >= padT && yVal <= padT + plotH) {
          drawIntersectionDot(ctx, hoverX.value, yVal, props.color);
        }
      }
    }

    // Traces dots
    for (const trace of props.traces) {
      const fs = trace.fs || 44100;
      const idx = Math.floor(t * fs);
      if (idx >= 0 && idx < trace.samples.length) {
        const yVal = toY(trace.samples[idx]);
        if (yVal >= padT && yVal <= padT + plotH) {
          drawIntersectionDot(ctx, hoverX.value, yVal, trace.color);
        }
      }
    }
  }
}

function drawIntersectionDot(ctx: CanvasRenderingContext2D, x: number, y: number, color: string) {
  ctx.save();
  ctx.beginPath();
  ctx.arc(x, y, 4.5, 0, 2 * Math.PI);
  ctx.fillStyle = color;
  ctx.fill();
  ctx.strokeStyle = '#FFFFFF';
  ctx.lineWidth = 1.5;
  ctx.stroke();
  ctx.restore();
}

// Mouse Event Handlers
function handleMouseDown(e: MouseEvent) {
  if (e.button !== 0) return; // Left click only
  const canvas = canvasRef.value;
  if (!canvas) return;
  const rect = canvas.getBoundingClientRect();
  const x = e.clientX - rect.left;
  const { padL, plotW } = getPlotDimensions();

  if (x >= padL && x <= padL + plotW) {
    isDragging.value = true;
    dragStartX.value = x;
    dragEndX.value = x;
  }
}

function handleMouseMove(e: MouseEvent) {
  const canvas = canvasRef.value;
  if (!canvas) return;
  const rect = canvas.getBoundingClientRect();
  const x = e.clientX - rect.left;
  const y = e.clientY - rect.top;
  const { padL, plotW, padT, plotH } = getPlotDimensions();

  if (isDragging.value) {
    dragEndX.value = Math.max(padL, Math.min(padL + plotW, x));
    requestAnimationFrame(draw);
  } else {
    if (x >= padL && x <= padL + plotW && y >= padT && y <= padT + plotH) {
      hoverX.value = x;
      hoverY.value = y;
      updateTooltip(x);
      requestAnimationFrame(draw);
    } else {
      if (hoverX.value !== null) {
        hoverX.value = null;
        hoverY.value = null;
        tooltip.value.show = false;
        requestAnimationFrame(draw);
      }
    }
  }
}

function handleMouseUp() {
  if (!isDragging.value) return;
  isDragging.value = false;

  const dx = Math.abs(dragEndX.value - dragStartX.value);
  if (dx > 5) {
    const tStart = fromX(dragStartX.value);
    const tEnd = fromX(dragEndX.value);
    zoomTimeMin.value = Math.min(tStart, tEnd);
    zoomTimeMax.value = Math.max(tStart, tEnd);
  }
  requestAnimationFrame(draw);
}

function handleMouseLeave() {
  isDragging.value = false;
  hoverX.value = null;
  hoverY.value = null;
  tooltip.value.show = false;
  requestAnimationFrame(draw);
}

// Tooltip Updates
function updateTooltip(mouseX: number) {
  const t = fromX(mouseX);
  const items: TooltipItem[] = [];

  if (props.samples && props.samples.length > 0) {
    const fs = props.fs || 44100;
    const idx = Math.floor(t * fs);
    if (idx >= 0 && idx < props.samples.length) {
      items.push({
        label: props.label || 'Referencia X',
        value: props.samples[idx].toFixed(4),
        color: props.color || '#00D97E'
      });
    }
  }

  for (const trace of props.traces) {
    const fs = trace.fs || 44100;
    const idx = Math.floor(t * fs);
    if (idx >= 0 && idx < trace.samples.length) {
      items.push({
        label: trace.label,
        value: trace.samples[idx].toFixed(4),
        color: trace.color
      });
    }
  }

  tooltip.value = {
    show: items.length > 0,
    x: mouseX,
    y: hoverY.value ?? 100,
    xValFormatted: `${t.toFixed(4)} s`,
    items
  };
}

// Zoom helpers
function resetZoom() {
  zoomTimeMin.value = null;
  zoomTimeMax.value = null;
  requestAnimationFrame(draw);
}

function zoomIn() {
  const currentMin = activeTimeMin.value;
  const currentMax = activeTimeMax.value;
  const range = currentMax - currentMin;
  zoomTimeMin.value = currentMin + range * 0.15;
  zoomTimeMax.value = currentMax - range * 0.15;
  requestAnimationFrame(draw);
}

function zoomOut() {
  const currentMin = activeTimeMin.value;
  const currentMax = activeTimeMax.value;
  const range = currentMax - currentMin;
  
  const dataMax = props.samples && props.samples.length > 0 
    ? props.samples.length / (props.fs || 44100) 
    : (props.traces && props.traces.length > 0 
       ? props.traces[0].samples.length / (props.traces[0].fs || 44100) 
       : 1);
       
  zoomTimeMin.value = Math.max(0, currentMin - range * 0.2);
  zoomTimeMax.value = Math.min(dataMax, currentMax + range * 0.2);
  requestAnimationFrame(draw);
}

// Mouse Wheel Zoom
function handleWheel(e: WheelEvent) {
  const canvas = canvasRef.value;
  if (!canvas) return;
  const rect = canvas.getBoundingClientRect();
  const mouseX = e.clientX - rect.left;
  const { padL, plotW } = getPlotDimensions();

  if (mouseX < padL || mouseX > padL + plotW) return;

  const mouseVal = fromX(mouseX);
  const currentMin = activeTimeMin.value;
  const currentMax = activeTimeMax.value;
  const zoomFactor = e.deltaY > 0 ? 1.15 : 0.85;

  const nextMin = mouseVal - (mouseVal - currentMin) * zoomFactor;
  const nextMax = mouseVal + (currentMax - mouseVal) * zoomFactor;

  const dataMax = props.samples && props.samples.length > 0 
    ? props.samples.length / (props.fs || 44100) 
    : (props.traces && props.traces.length > 0 
       ? props.traces[0].samples.length / (props.traces[0].fs || 44100) 
       : 1);

  zoomTimeMin.value = Math.max(0, nextMin);
  zoomTimeMax.value = Math.min(dataMax, nextMax);
  requestAnimationFrame(draw);
}

const tooltipStyle = computed(() => {
  if (!canvasRef.value) return {};
  const width = canvasRef.value.clientWidth;
  const x = Math.max(80, Math.min(width - 80, tooltip.value.x));
  return {
    left: `${x}px`,
    top: `${tooltip.value.y}px`
  };
});

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
    <div class="plot-header-overlay">
      <div v-if="label" class="plot-label">{{ label }}</div>
      <div class="plot-toolbar">
        <span class="plot-instruction">💡 Arrastrá/Rueda para zoom X | Doble click para restaurar</span>
        <div class="plot-actions">
          <button class="action-btn" @click="zoomIn" title="Acercar">🔍+</button>
          <button class="action-btn" @click="zoomOut" title="Alejar">🔍-</button>
          <button class="action-btn" @click="resetZoom" title="Restaurar">🔄</button>
        </div>
      </div>
    </div>
    
    <canvas 
      ref="canvasRef" 
      @mousedown="handleMouseDown" 
      @mousemove="handleMouseMove" 
      @mouseup="handleMouseUp" 
      @mouseleave="handleMouseLeave"
      @dblclick="resetZoom"
      @wheel.prevent="handleWheel"
    ></canvas>
    
    <!-- Floating Tooltip -->
    <div v-if="tooltip.show" class="plot-tooltip" :style="tooltipStyle">
      <div class="tooltip-header">{{ tooltip.xValFormatted }}</div>
      <div class="tooltip-body">
        <div v-for="item in tooltip.items" :key="item.label" class="tooltip-row">
          <span class="tooltip-dot" :style="{ backgroundColor: item.color }"></span>
          <span class="tooltip-label">{{ item.label }}:</span>
          <span class="tooltip-value">{{ item.value }}</span>
        </div>
      </div>
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

.plot-header-overlay {
  position: absolute;
  top: 6px;
  left: 0;
  right: 0;
  display: flex;
  justify-content: space-between;
  padding: 0 10px;
  pointer-events: none;
  z-index: 2;
}

.plot-label {
  font-size: 10px;
  font-weight: 600;
  color: var(--color-text-secondary);
  background: var(--color-bg-elevated);
  padding: 2px 6px;
  border-radius: 4px;
  border: 1px solid var(--color-border);
}

.plot-toolbar {
  display: flex;
  align-items: center;
  gap: 8px;
  pointer-events: auto;
}

.plot-instruction {
  font-size: 9px;
  color: var(--color-text-secondary);
  opacity: 0.8;
  background: var(--color-bg-elevated);
  padding: 2px 6px;
  border-radius: 4px;
  border: 1px solid var(--color-border);
}

.plot-actions {
  display: flex;
  gap: 2px;
  background: var(--color-bg-elevated);
  border: 1px solid var(--color-border);
  border-radius: 4px;
  padding: 1px;
}

.action-btn {
  background: transparent;
  border: none;
  color: var(--color-text-secondary);
  font-size: 9px;
  font-weight: bold;
  padding: 2px 5px;
  cursor: pointer;
  border-radius: 3px;
  transition: all 0.15s ease;
}

.action-btn:hover {
  background: var(--color-border);
  color: var(--color-text-primary);
}

canvas {
  display: block;
}

/* Tooltip Styling */
.plot-tooltip {
  position: absolute;
  background: rgba(15, 18, 25, 0.95);
  backdrop-filter: blur(4px);
  border: 1px solid var(--color-border);
  border-radius: 6px;
  padding: 8px 12px;
  font-size: 11px;
  color: var(--color-text-primary);
  pointer-events: none;
  z-index: 100;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.5);
  transform: translate(-50%, -100%);
  margin-top: -10px;
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.tooltip-header {
  font-weight: 700;
  color: var(--color-text-primary);
  font-family: var(--font-mono);
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
  padding-bottom: 4px;
  margin-bottom: 2px;
}

.tooltip-row {
  display: flex;
  align-items: center;
  gap: 6px;
  line-height: 1.4;
}

.tooltip-dot {
  width: 7px;
  height: 7px;
  border-radius: 50%;
}

.tooltip-label {
  color: var(--color-text-secondary);
}

.tooltip-value {
  font-weight: 600;
  font-family: var(--font-mono);
  margin-left: auto;
}
</style>
