<script setup lang="ts">
import { ref, computed, onMounted, watch, onUnmounted } from 'vue';

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

// Zoom state
const zoomFMin = ref<number | null>(null);
const zoomFMax = ref<number | null>(null);

const activeFMin = computed(() => zoomFMin.value ?? 20);
const activeFMax = computed(() => {
  const dataMax = props.frequencies && props.frequencies.length > 0 
    ? props.frequencies[props.frequencies.length - 1] 
    : 20000;
  return zoomFMax.value ?? Math.max(20000, dataMax);
});

// Drag and Hover states
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

function toX(f: number) {
  const { padL, plotW } = getPlotDimensions();
  const fMin = activeFMin.value;
  const fMax = activeFMax.value;
  const logMin = Math.log10(fMin);
  const logMax = Math.log10(fMax);
  return padL + ((Math.log10(Math.max(f, fMin)) - logMin) / (logMax - logMin)) * plotW;
}

function fromX(x: number) {
  const { padL, plotW } = getPlotDimensions();
  const fMin = activeFMin.value;
  const fMax = activeFMax.value;
  const relativeX = x - padL;
  const ratio = Math.max(0, Math.min(1, relativeX / plotW));
  const logMin = Math.log10(fMin);
  const logMax = Math.log10(fMax);
  return Math.pow(10, logMin + ratio * (logMax - logMin));
}

function findClosestIndex(arr: number[], target: number): number {
  if (arr.length === 0) return -1;
  let low = 0;
  let high = arr.length - 1;
  while (low < high) {
    const mid = Math.floor((low + high) / 2);
    if (arr[mid] < target) {
      low = mid + 1;
    } else {
      high = mid;
    }
  }
  if (low > 0 && Math.abs(arr[low - 1] - target) < Math.abs(arr[low] - target)) {
    return low - 1;
  }
  return low;
}

// Draw Function
function draw() {
  const canvas = canvasRef.value;
  if (!canvas) return;
  const ctx = canvas.getContext('2d');
  if (!ctx) return;

  const { width, height, padL, padT, plotW, plotH } = getPlotDimensions();
  ctx.clearRect(0, 0, width, height);

  // Y axis in [0, 1]
  const yMin = 0;
  const yMax = 1;
  const toY = (v: number) => padT + plotH - ((v - yMin) / (yMax - yMin)) * plotH;

  // Background zone for high coherence (>0.9)
  const yThreshold = toY(HIGH_COHERENCE_THRESHOLD);
  ctx.fillStyle = 'rgba(34, 197, 94, 0.04)';
  ctx.fillRect(padL, padT, plotW, yThreshold - padT);

  // Reference line for coherence = 0.9 (dotted)
  ctx.save();
  ctx.strokeStyle = 'rgba(34, 197, 94, 0.35)';
  ctx.setLineDash([5, 3]);
  ctx.lineWidth = 1;
  ctx.beginPath();
  ctx.moveTo(padL, yThreshold);
  ctx.lineTo(padL + plotW, yThreshold);
  ctx.stroke();
  ctx.restore();

  // Label for reference line
  ctx.font = '8px monospace';
  ctx.fillStyle = 'rgba(34, 197, 94, 0.7)';
  ctx.fillText('γ²=0.9', padL + plotW - 45, yThreshold - 4);

  // Draw Grid & Border
  ctx.save();
  ctx.strokeStyle = 'rgba(255, 255, 255, 0.08)';
  ctx.fillStyle = 'rgba(255, 255, 255, 0.45)';
  ctx.font = '9px monospace';

  // Border
  ctx.strokeRect(padL, padT, plotW, plotH);

  // Horizontal lines (Coherence values: 0.0, 0.2, 0.4, 0.6, 0.8, 1.0)
  const cohSteps = [0.0, 0.2, 0.4, 0.6, 0.8, 1.0];
  for (const c of cohSteps) {
    const y = toY(c);
    if (y >= padT && y <= padT + plotH) {
      ctx.strokeStyle = 'rgba(255, 255, 255, 0.08)';
      ctx.setLineDash([3, 3]);
      ctx.beginPath();
      ctx.moveTo(padL, y);
      ctx.lineTo(padL + plotW, y);
      ctx.stroke();
      
      ctx.textAlign = 'right';
      ctx.fillText(c.toFixed(1), padL - 6, y + 3);
    }
  }

  // Vertical lines (Log Frequencies)
  const freqsGrid = [20, 50, 100, 200, 500, 1000, 2000, 5000, 10000, 20000];
  ctx.setLineDash([3, 3]);
  for (const f of freqsGrid) {
    const x = toX(f);
    if (x >= padL && x <= padL + plotW) {
      ctx.strokeStyle = 'rgba(255, 255, 255, 0.08)';
      ctx.beginPath();
      ctx.moveTo(x, padT);
      ctx.lineTo(x, padT + plotH);
      ctx.stroke();

      ctx.textAlign = 'center';
      const lbl = f >= 1000 ? `${f / 1000}k` : `${f}`;
      ctx.fillText(lbl, x, height - 5);
    }
  }
  ctx.restore();

  if (!props.frequencies || props.frequencies.length === 0) return;

  // 1. Draw snapshots (traces)
  for (const trace of props.traces) {
    if (trace.frequencies && trace.frequencies.length > 0 && trace.coherence) {
      ctx.save();
      ctx.beginPath();
      ctx.strokeStyle = trace.color;
      ctx.lineWidth = 1.2;
      let first = true;
      for (let i = 0; i < trace.frequencies.length; i++) {
        const f = trace.frequencies[i];
        if (f < activeFMin.value || f > activeFMax.value) continue;
        const x = toX(f);
        const y = toY(trace.coherence[i]);
        if (x >= padL && x <= padL + plotW && y >= padT && y <= padT + plotH) {
          if (first) {
            ctx.moveTo(x, y);
            first = false;
          } else ctx.lineTo(x, y);
        }
      }
      ctx.stroke();
      ctx.restore();
    }
  }

  // 2. Draw main coherence trace (colored above/below 0.9 threshold)
  ctx.save();
  let i = 0;
  while (i < props.frequencies.length) {
    const fStart = props.frequencies[i];
    if (fStart < activeFMin.value) {
      i++;
      continue;
    }
    if (fStart > activeFMax.value) break;

    const aboveThreshold = props.coherence[i] > HIGH_COHERENCE_THRESHOLD;
    ctx.beginPath();
    ctx.strokeStyle = aboveThreshold ? '#22C55E' : '#F97316';
    ctx.lineWidth = 2.0;

    const startX = toX(fStart);
    const startY = toY(props.coherence[i]);
    ctx.moveTo(startX, startY);

    let j = i + 1;
    while (j < props.frequencies.length) {
      const fNext = props.frequencies[j];
      if (fNext > activeFMax.value) break;

      const nextAbove = props.coherence[j] > HIGH_COHERENCE_THRESHOLD;
      if (nextAbove !== aboveThreshold) {
        // Interpolate crossing point for visual continuity
        const xCross = toX((props.frequencies[j - 1] + fNext) / 2);
        const yCross = toY(HIGH_COHERENCE_THRESHOLD);
        ctx.lineTo(xCross, yCross);
        break;
      }
      const xVal = toX(fNext);
      const yVal = toY(props.coherence[j]);
      if (xVal >= padL && xVal <= padL + plotW && yVal >= padT && yVal <= padT + plotH) {
        ctx.lineTo(xVal, yVal);
      }
      j++;
    }
    ctx.stroke();
    i = j;
  }
  ctx.restore();

  // Draw selection rect for zoom
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

    const f = fromX(hoverX.value);

    // Main coherence dot
    if (props.frequencies && props.frequencies.length > 0 && props.coherence) {
      const idx = findClosestIndex(props.frequencies, f);
      if (idx !== -1) {
        const yVal = toY(props.coherence[idx]);
        if (yVal >= padT && yVal <= padT + plotH) {
          const aboveThreshold = props.coherence[idx] > HIGH_COHERENCE_THRESHOLD;
          drawIntersectionDot(ctx, hoverX.value, yVal, aboveThreshold ? '#22C55E' : '#F97316');
        }
      }
    }

    // Traces dots
    for (const t of props.traces) {
      if (t.frequencies && t.frequencies.length > 0 && t.coherence) {
        const idx = findClosestIndex(t.frequencies, f);
        if (idx !== -1) {
          const yVal = toY(t.coherence[idx]);
          if (yVal >= padT && yVal <= padT + plotH) {
            drawIntersectionDot(ctx, hoverX.value, yVal, t.color);
          }
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
    const fStart = fromX(dragStartX.value);
    const fEnd = fromX(dragEndX.value);
    zoomFMin.value = Math.min(fStart, fEnd);
    zoomFMax.value = Math.max(fStart, fEnd);
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

function updateTooltip(mouseX: number) {
  const f = fromX(mouseX);
  const items: TooltipItem[] = [];

  if (props.frequencies && props.frequencies.length > 0 && props.coherence) {
    const idx = findClosestIndex(props.frequencies, f);
    if (idx !== -1) {
      const val = props.coherence[idx];
      items.push({
        label: 'Medición Activa',
        value: `${val.toFixed(3)} (${(val * 100).toFixed(0)}%)`,
        color: val > HIGH_COHERENCE_THRESHOLD ? '#22C55E' : '#F97316'
      });
    }
  }

  for (const t of props.traces) {
    if (t.frequencies && t.frequencies.length > 0 && t.coherence) {
      const idx = findClosestIndex(t.frequencies, f);
      if (idx !== -1) {
        const val = t.coherence[idx];
        items.push({
          label: t.label,
          value: `${val.toFixed(3)} (${(val * 100).toFixed(0)}%)`,
          color: t.color
        });
      }
    }
  }

  tooltip.value = {
    show: items.length > 0,
    x: mouseX,
    y: hoverY.value ?? 100,
    xValFormatted: f < 1000 ? `${f.toFixed(1)} Hz` : `${(f / 1000).toFixed(3)} kHz`,
    items
  };
}

// Zoom operations
function resetZoom() {
  zoomFMin.value = null;
  zoomFMax.value = null;
  requestAnimationFrame(draw);
}

function zoomIn() {
  const currentMin = activeFMin.value;
  const currentMax = activeFMax.value;
  const logMin = Math.log10(currentMin);
  const logMax = Math.log10(currentMax);
  const logRange = logMax - logMin;
  
  zoomFMin.value = Math.pow(10, logMin + logRange * 0.15);
  zoomFMax.value = Math.pow(10, logMax - logRange * 0.15);
  requestAnimationFrame(draw);
}

function zoomOut() {
  const currentMin = activeFMin.value;
  const currentMax = activeFMax.value;
  const logMin = Math.log10(currentMin);
  const logMax = Math.log10(currentMax);
  const logRange = logMax - logMin;

  const defaultMin = 20;
  const defaultMax = props.frequencies && props.frequencies.length > 0 
    ? props.frequencies[props.frequencies.length - 1] 
    : 20000;

  zoomFMin.value = Math.max(defaultMin, Math.pow(10, logMin - logRange * 0.2));
  zoomFMax.value = Math.min(defaultMax, Math.pow(10, logMax + logRange * 0.2));
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
  const currentMin = activeFMin.value;
  const currentMax = activeFMax.value;
  const zoomFactor = e.deltaY > 0 ? 1.15 : 0.85;

  const defaultMin = 20;
  const defaultMax = props.frequencies && props.frequencies.length > 0 
    ? props.frequencies[props.frequencies.length - 1] 
    : 20000;

  const logMouse = Math.log10(mouseVal);
  const logMin = Math.log10(currentMin);
  const logMax = Math.log10(currentMax);

  const nextLogMin = logMouse - (logMouse - logMin) * zoomFactor;
  const nextLogMax = logMouse + (logMax - logMouse) * zoomFactor;

  zoomFMin.value = Math.max(defaultMin, Math.pow(10, nextLogMin));
  zoomFMax.value = Math.min(defaultMax, Math.pow(10, nextLogMax));
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

watch([() => props.frequencies, () => props.coherence, () => props.traces, () => props.height], () => {
  requestAnimationFrame(draw);
});
</script>

<template>
  <div ref="containerRef" class="coherence-container" :style="{ height: height + 'px' }">
    <div class="plot-header-overlay">
      <div class="plot-label">Coherencia γ²(ω)</div>
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
.coherence-container {
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