<script setup lang="ts">
import { ref, computed, onMounted, watch, onUnmounted } from 'vue';

export interface SpectrumTrace {
  frequencies: number[]
  magnitudes: number[]
  color: string
  label: string
}

interface Props {
  frequencies?: number[]
  magnitudes?: number[]
  label?: string
  dbScale?: boolean       
  logFrequency?: boolean  
  height?: number
  traces?: SpectrumTrace[]
}

const props = withDefaults(defineProps<Props>(), {
  dbScale: false,
  logFrequency: true,
  height: 200,
  traces: () => []
});

const canvasRef = ref<HTMLCanvasElement | null>(null);
const containerRef = ref<HTMLDivElement | null>(null);

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

// Heurística para detectar si un arreglo de magnitudes ya está en dBFS
function isAlreadyDb(mags: number[]): boolean {
  if (!mags || mags.length === 0) return false;
  let negativeCount = 0;
  const sampleSize = Math.min(15, mags.length);
  for (let i = 0; i < sampleSize; i++) {
    if (mags[i] < 0) negativeCount++;
  }
  return negativeCount > sampleSize * 0.7; // Si más del 70% de las muestras iniciales son negativas
}

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
  if (props.logFrequency) {
    const logMin = Math.log10(fMin);
    const logMax = Math.log10(fMax);
    return padL + ((Math.log10(Math.max(f, fMin)) - logMin) / (logMax - logMin)) * plotW;
  } else {
    return padL + ((f - fMin) / (fMax - fMin)) * plotW;
  }
}

function fromX(x: number) {
  const { padL, plotW } = getPlotDimensions();
  const fMin = activeFMin.value;
  const fMax = activeFMax.value;
  const relativeX = x - padL;
  const ratio = Math.max(0, Math.min(1, relativeX / plotW));
  if (props.logFrequency) {
    const logMin = Math.log10(fMin);
    const logMax = Math.log10(fMax);
    return Math.pow(10, logMin + ratio * (logMax - logMin));
  } else {
    return fMin + ratio * (fMax - fMin);
  }
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

  const hasMainData = props.frequencies && props.magnitudes && props.frequencies.length > 0;
  const hasTracesData = props.traces && props.traces.length > 0;
  if (!hasMainData && !hasTracesData) return;

  let maxMag = 0.001;
  let currentMaxDb = -200;

  const mainIsDb = props.magnitudes ? isAlreadyDb(props.magnitudes) : false;

  // Find Min/Max Y values in visible frequency range for vertical auto-scaling
  const processDataRange = (freqs: number[], mags: number[], isDb: boolean) => {
    if (!freqs || freqs.length === 0) return;
    const fMin = activeFMin.value;
    const fMax = activeFMax.value;
    for (let i = 0; i < freqs.length; i++) {
      const f = freqs[i];
      if (f >= fMin && f <= fMax) {
        const m = mags[i];
        if (isDb) {
          if (m > currentMaxDb) currentMaxDb = m;
          const lin = Math.pow(10, m / 20);
          if (lin > maxMag) maxMag = lin;
        } else {
          if (m > maxMag) maxMag = m;
          const db = 20 * Math.log10(m + 1e-12);
          if (db > currentMaxDb) currentMaxDb = db;
        }
      }
    }
  };

  if (props.frequencies && props.magnitudes) {
    processDataRange(props.frequencies, props.magnitudes, mainIsDb);
  }
  for (const t of props.traces) {
    processDataRange(t.frequencies, t.magnitudes, isAlreadyDb(t.magnitudes));
  }

  // dB scale calculation
  const maxDb = Math.ceil(currentMaxDb / 12) * 12;
  const minDb = maxDb - 72; // Standard 72 dB range
  if (maxMag === 0) maxMag = 1;

  const toY = (mag: number, isDb: boolean) => {
    if (props.dbScale) {
      const db = isDb ? mag : 20 * Math.log10(mag + 1e-12);
      return padT + plotH - ((db - minDb) / (maxDb - minDb)) * plotH;
    } else {
      return padT + plotH - (mag / maxMag) * plotH;
    }
  };

  // Draw Grid & Border
  ctx.save();
  ctx.strokeStyle = 'rgba(255, 255, 255, 0.08)';
  ctx.fillStyle = 'rgba(255, 255, 255, 0.45)';
  ctx.font = '9px monospace';

  // Border
  ctx.strokeRect(padL, padT, plotW, plotH);

  // Horizontal lines (Y Axis)
  if (props.dbScale) {
    const dbSteps = [maxDb, maxDb - 12, maxDb - 24, maxDb - 36, maxDb - 48, maxDb - 60, maxDb - 72];
    for (const db of dbSteps) {
      const y = toY(Math.pow(10, db / 20), false);
      if (y >= padT && y <= padT + plotH) {
        ctx.strokeStyle = db === 0 ? 'rgba(255, 255, 255, 0.2)' : 'rgba(255, 255, 255, 0.08)';
        ctx.setLineDash(db === 0 ? [] : [3, 3]);
        ctx.beginPath();
        ctx.moveTo(padL, y);
        ctx.lineTo(padL + plotW, y);
        ctx.stroke();

        ctx.textAlign = 'right';
        ctx.fillText(`${db}`, padL - 6, y + 3);
      }
    }
  } else {
    const steps = [0.0, 0.2, 0.4, 0.6, 0.8, 1.0];
    for (const s of steps) {
      const y = toY(s * maxMag, false);
      if (y >= padT && y <= padT + plotH) {
        ctx.strokeStyle = 'rgba(255, 255, 255, 0.08)';
        ctx.setLineDash([3, 3]);
        ctx.beginPath();
        ctx.moveTo(padL, y);
        ctx.lineTo(padL + plotW, y);
        ctx.stroke();

        ctx.textAlign = 'right';
        ctx.fillText(s === 0 ? '0' : (s * maxMag).toFixed(3), padL - 6, y + 3);
      }
    }
  }

  // Vertical lines (X Axis - Frequencies)
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

  // Draw Traces
  for (const t of props.traces) {
    if (t.frequencies && t.frequencies.length > 0 && t.magnitudes) {
      const tIsDb = isAlreadyDb(t.magnitudes);
      ctx.save();
      ctx.beginPath();
      ctx.strokeStyle = t.color;
      ctx.lineWidth = 1.2;
      let first = true;
      for (let i = 0; i < t.frequencies.length; i++) {
        const f = t.frequencies[i];
        if (f < activeFMin.value || f > activeFMax.value) continue;
        const x = toX(f);
        const y = toY(t.magnitudes[i], tIsDb);
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

  // Draw main spectrum
  if (props.frequencies && props.magnitudes) {
    ctx.save();
    ctx.beginPath();
    ctx.strokeStyle = '#00D97E';
    ctx.lineWidth = 2.0;
    let first = true;
    for (let i = 0; i < props.frequencies.length; i++) {
      const f = props.frequencies[i];
      if (f < activeFMin.value || f > activeFMax.value) continue;
      const x = toX(f);
      const y = toY(props.magnitudes[i], mainIsDb);
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

    // Main spectrum dot
    if (props.frequencies && props.frequencies.length > 0 && props.magnitudes) {
      const idx = findClosestIndex(props.frequencies, f);
      if (idx !== -1) {
        const yVal = toY(props.magnitudes[idx], mainIsDb);
        if (yVal >= padT && yVal <= padT + plotH) {
          drawIntersectionDot(ctx, hoverX.value, yVal, '#00D97E');
        }
      }
    }

    // Traces dots
    for (const t of props.traces) {
      if (t.frequencies && t.frequencies.length > 0 && t.magnitudes) {
        const idx = findClosestIndex(t.frequencies, f);
        if (idx !== -1) {
          const tIsDb = isAlreadyDb(t.magnitudes);
          const yVal = toY(t.magnitudes[idx], tIsDb);
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

  const mainIsDb = props.magnitudes ? isAlreadyDb(props.magnitudes) : false;

  const formatMag = (val: number, isDb: boolean) => {
    if (props.dbScale) {
      const db = isDb ? val : 20 * Math.log10(val + 1e-12);
      return `${db.toFixed(1)} dB`;
    }
    const linear = isDb ? Math.pow(10, val / 20) : val;
    return linear.toFixed(4);
  };

  if (props.frequencies && props.frequencies.length > 0 && props.magnitudes) {
    const idx = findClosestIndex(props.frequencies, f);
    if (idx !== -1) {
      items.push({
        label: props.label || 'Referencia X',
        value: formatMag(props.magnitudes[idx], mainIsDb),
        color: '#00D97E'
      });
    }
  }

  for (const t of props.traces) {
    if (t.frequencies && t.frequencies.length > 0 && t.magnitudes) {
      const idx = findClosestIndex(t.frequencies, f);
      if (idx !== -1) {
        items.push({
          label: t.label,
          value: formatMag(t.magnitudes[idx], isAlreadyDb(t.magnitudes)),
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
  
  if (props.logFrequency) {
    const logMin = Math.log10(currentMin);
    const logMax = Math.log10(currentMax);
    const logRange = logMax - logMin;
    zoomFMin.value = Math.pow(10, logMin + logRange * 0.15);
    zoomFMax.value = Math.pow(10, logMax - logRange * 0.15);
  } else {
    const range = currentMax - currentMin;
    zoomFMin.value = currentMin + range * 0.15;
    zoomFMax.value = currentMax - range * 0.15;
  }
  requestAnimationFrame(draw);
}

function zoomOut() {
  const currentMin = activeFMin.value;
  const currentMax = activeFMax.value;
  
  const defaultMin = 20;
  const defaultMax = props.frequencies && props.frequencies.length > 0 
    ? props.frequencies[props.frequencies.length - 1] 
    : 20000;

  if (props.logFrequency) {
    const logMin = Math.log10(currentMin);
    const logMax = Math.log10(currentMax);
    const logRange = logMax - logMin;
    zoomFMin.value = Math.max(defaultMin, Math.pow(10, logMin - logRange * 0.2));
    zoomFMax.value = Math.min(defaultMax, Math.pow(10, logMax + logRange * 0.2));
  } else {
    const range = currentMax - currentMin;
    zoomFMin.value = Math.max(defaultMin, currentMin - range * 0.2);
    zoomFMax.value = Math.min(defaultMax, currentMax + range * 0.2);
  }
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

  if (props.logFrequency) {
    const logMouse = Math.log10(mouseVal);
    const logMin = Math.log10(currentMin);
    const logMax = Math.log10(currentMax);

    const nextLogMin = logMouse - (logMouse - logMin) * zoomFactor;
    const nextLogMax = logMouse + (logMax - logMouse) * zoomFactor;

    zoomFMin.value = Math.max(defaultMin, Math.pow(10, nextLogMin));
    zoomFMax.value = Math.min(defaultMax, Math.pow(10, nextLogMax));
  } else {
    const nextMin = mouseVal - (mouseVal - currentMin) * zoomFactor;
    const nextMax = mouseVal + (currentMax - mouseVal) * zoomFactor;

    zoomFMin.value = Math.max(defaultMin, nextMin);
    zoomFMax.value = Math.min(defaultMax, nextMax);
  }
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

watch([
  () => props.frequencies, 
  () => props.magnitudes, 
  () => props.dbScale, 
  () => props.logFrequency, 
  () => props.traces, 
  () => props.height,
  zoomFMin,
  zoomFMax
], () => {
  requestAnimationFrame(draw);
});
</script>

<template>
  <div ref="containerRef" class="spectrum-container" :style="{ height: height + 'px' }">
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
          <span class="tooltip-label">{{ item.label }}</span>
          <span class="tooltip-value">{{ item.value }}</span>
        </div>
      </div>
    </div>
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
