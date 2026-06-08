<script setup lang="ts">
import { ref, computed, onMounted, watch, onUnmounted } from 'vue';

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
  height: 200,
  mode: 'both',
  traces: () => []
});

const magCanvasRef = ref<HTMLCanvasElement | null>(null);
const phaseCanvasRef = ref<HTMLCanvasElement | null>(null);
const containerRef = ref<HTMLDivElement | null>(null);

// Zoom state (shared between mag and phase)
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
const hoveredCanvas = ref<'mag' | 'phase' | null>(null);

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

const padL = 45;
const padR = 15;
const padT = 15;
const padB = 20;

// Helper to get active canvas for dimensions
function getActiveCanvas() {
  return magCanvasRef.value || phaseCanvasRef.value;
}

function getPlotDimensions() {
  const canvas = getActiveCanvas();
  if (!canvas) return { width: 0, height: 0, plotW: 0, plotH: 0 };
  const dpr = window.devicePixelRatio || 1;
  const width = canvas.width / dpr;
  const height = canvas.height / dpr;
  return {
    width,
    height,
    plotW: width - padL - padR,
    plotH: height - padT - padB
  };
}

function toX(f: number) {
  const { plotW } = getPlotDimensions();
  const fMin = activeFMin.value;
  const fMax = activeFMax.value;
  const logMin = Math.log10(fMin);
  const logMax = Math.log10(fMax);
  return padL + ((Math.log10(Math.max(f, fMin)) - logMin) / (logMax - logMin)) * plotW;
}

function fromX(x: number) {
  const { plotW } = getPlotDimensions();
  const fMin = activeFMin.value;
  const fMax = activeFMax.value;
  const relativeX = x - padL;
  const ratio = Math.max(0, Math.min(1, relativeX / plotW));
  const logMin = Math.log10(fMin);
  const logMax = Math.log10(fMax);
  return Math.pow(10, logMin + ratio * (logMax - logMin));
}

function findClosestIndex(arr: number[], target: number): number {
  if (!arr || arr.length === 0) return -1;
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

// Draw Functions
function draw() {
  drawMag();
  drawPhase();
}

function drawMag() {
  const canvas = magCanvasRef.value;
  if (!canvas || props.mode === 'phase') return;
  const ctx = canvas.getContext('2d');
  if (!ctx) return;

  const dpr = window.devicePixelRatio || 1;
  const w = canvas.width / dpr;
  const h = canvas.height / dpr;
  ctx.clearRect(0, 0, w, h);

  const plotW = w - padL - padR;
  const plotH = h - padT - padB;

  if (!props.frequencies || props.frequencies.length === 0) return;

  // Find maxDb in visible frequency range for auto-ranging
  let maxDb = -200;
  const checkMaxMag = (freqs: number[], mags: number[]) => {
    if (!freqs || !mags) return;
    const fMin = activeFMin.value;
    const fMax = activeFMax.value;
    for (let i = 0; i < freqs.length; i++) {
      const f = freqs[i];
      if (f >= fMin && f <= fMax) {
        if (mags[i] > maxDb) maxDb = mags[i];
      }
    }
  };

  checkMaxMag(props.frequencies, props.magnitudDb);
  for (const t of props.traces) {
    if (t.magnitudeDb) {
      checkMaxMag(t.frequencies, t.magnitudeDb);
    }
  }

  const topDb = Math.max(12, Math.ceil(maxDb / 6) * 6);
  const botDb = topDb - 60; // 60 dB range

  const toY = (db: number) => padT + plotH - ((db - botDb) / (topDb - botDb)) * plotH;

  // Draw Grid & Border
  ctx.save();
  ctx.strokeStyle = 'rgba(255, 255, 255, 0.08)';
  ctx.fillStyle = 'rgba(255, 255, 255, 0.45)';
  ctx.font = '9px monospace';

  // Border
  ctx.strokeRect(padL, padT, plotW, plotH);

  // Horizontal lines (Magnitude: step 12 dB)
  const dbSteps = [topDb, topDb - 12, topDb - 24, topDb - 36, topDb - 48, topDb - 60];
  for (const db of dbSteps) {
    const y = toY(db);
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
      ctx.fillText(lbl, x, h - 5);
    }
  }
  ctx.restore();

  // Draw traces (snapshots)
  for (const t of props.traces) {
    if (t.magnitudeDb && t.frequencies && t.frequencies.length > 0) {
      ctx.save();
      ctx.beginPath();
      ctx.strokeStyle = t.color;
      ctx.lineWidth = 1.2;
      let first = true;
      for (let i = 0; i < t.frequencies.length; i++) {
        const f = t.frequencies[i];
        if (f < activeFMin.value || f > activeFMax.value) continue;
        const x = toX(f);
        const y = toY(t.magnitudeDb[i]);
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

  // Draw main trace
  ctx.save();
  ctx.beginPath();
  ctx.strokeStyle = '#00D97E';
  ctx.lineWidth = 2.0;
  let first = true;
  for (let i = 0; i < props.frequencies.length; i++) {
    const f = props.frequencies[i];
    if (f < activeFMin.value || f > activeFMax.value) continue;
    const x = toX(f);
    const y = toY(props.magnitudDb[i]);
    if (x >= padL && x <= padL + plotW && y >= padT && y <= padT + plotH) {
      if (first) {
        ctx.moveTo(x, y);
        first = false;
      } else ctx.lineTo(x, y);
    }
  }
  ctx.stroke();
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

  // Draw synchronized cursor line and dot
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

    // Main dot
    const idx = findClosestIndex(props.frequencies, f);
    if (idx !== -1 && props.magnitudDb[idx] !== undefined) {
      const yVal = toY(props.magnitudDb[idx]);
      if (yVal >= padT && yVal <= padT + plotH) {
        drawIntersectionDot(ctx, hoverX.value, yVal, '#00D97E');
      }
    }

    // Traces dots
    for (const t of props.traces) {
      if (t.magnitudeDb && t.frequencies) {
        const tIdx = findClosestIndex(t.frequencies, f);
        if (tIdx !== -1 && t.magnitudeDb[tIdx] !== undefined) {
          const yVal = toY(t.magnitudeDb[tIdx]);
          if (yVal >= padT && yVal <= padT + plotH) {
            drawIntersectionDot(ctx, hoverX.value, yVal, t.color);
          }
        }
      }
    }
  }
}

function drawPhase() {
  const canvas = phaseCanvasRef.value;
  if (!canvas || props.mode === 'magnitude') return;
  const ctx = canvas.getContext('2d');
  if (!ctx) return;

  const dpr = window.devicePixelRatio || 1;
  const w = canvas.width / dpr;
  const h = canvas.height / dpr;
  ctx.clearRect(0, 0, w, h);

  const plotW = w - padL - padR;
  const plotH = h - padT - padB;

  if (!props.frequencies || props.frequencies.length === 0) return;

  const topPh = Math.PI;
  const botPh = -Math.PI;
  const toY = (p: number) => padT + plotH - ((p - botPh) / (topPh - botPh)) * plotH;

  // Draw Grid & Border
  ctx.save();
  ctx.strokeStyle = 'rgba(255, 255, 255, 0.08)';
  ctx.fillStyle = 'rgba(255, 255, 255, 0.45)';
  ctx.font = '9px monospace';

  // Border
  ctx.strokeRect(padL, padT, plotW, plotH);

  // Horizontal lines (Phase: -pi, -pi/2, 0, pi/2, pi)
  const phaseSteps = [
    { val: Math.PI, label: 'π' },
    { val: Math.PI / 2, label: 'π/2' },
    { val: 0, label: '0' },
    { val: -Math.PI / 2, label: '-π/2' },
    { val: -Math.PI, label: '-π' }
  ];
  for (const ph of phaseSteps) {
    const y = toY(ph.val);
    if (y >= padT && y <= padT + plotH) {
      ctx.strokeStyle = ph.val === 0 ? 'rgba(255, 255, 255, 0.2)' : 'rgba(255, 255, 255, 0.08)';
      ctx.setLineDash(ph.val === 0 ? [] : [3, 3]);
      ctx.beginPath();
      ctx.moveTo(padL, y);
      ctx.lineTo(padL + plotW, y);
      ctx.stroke();
      
      ctx.textAlign = 'right';
      ctx.fillText(ph.label, padL - 6, y + 3);
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
      ctx.fillText(lbl, x, h - 5);
    }
  }
  ctx.restore();

  // Draw traces
  for (const t of props.traces) {
    if (t.phaseRad && t.frequencies && t.frequencies.length > 0) {
      ctx.save();
      ctx.beginPath();
      ctx.strokeStyle = t.color;
      ctx.lineWidth = 1.2;
      let first = true;
      for (let i = 0; i < t.frequencies.length; i++) {
        const f = t.frequencies[i];
        if (f < activeFMin.value || f > activeFMax.value) continue;
        const x = toX(f);
        const y = toY(t.phaseRad[i]);
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

  // Draw main trace
  ctx.save();
  ctx.beginPath();
  ctx.strokeStyle = '#3B82F6'; 
  ctx.lineWidth = 2.0;
  let first = true;
  for (let i = 0; i < props.frequencies.length; i++) {
    const f = props.frequencies[i];
    if (f < activeFMin.value || f > activeFMax.value) continue;
    const x = toX(f);
    const y = toY(props.phaseRad[i]);
    if (x >= padL && x <= padL + plotW && y >= padT && y <= padT + plotH) {
      if (first) {
        ctx.moveTo(x, y);
        first = false;
      } else ctx.lineTo(x, y);
    }
  }
  ctx.stroke();
  ctx.restore();

  // Draw selection rect for zoom if phase is hovered/dragged
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

  // Draw synchronized cursor line and dot
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

    // Main dot
    const idx = findClosestIndex(props.frequencies, f);
    if (idx !== -1 && props.phaseRad[idx] !== undefined) {
      const yVal = toY(props.phaseRad[idx]);
      if (yVal >= padT && yVal <= padT + plotH) {
        drawIntersectionDot(ctx, hoverX.value, yVal, '#3B82F6');
      }
    }

    // Traces dots
    for (const t of props.traces) {
      if (t.phaseRad && t.frequencies) {
        const tIdx = findClosestIndex(t.frequencies, f);
        if (tIdx !== -1 && t.phaseRad[tIdx] !== undefined) {
          const yVal = toY(t.phaseRad[tIdx]);
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

// Mouse Event Handlers (shared)
function handleMouseDown(e: MouseEvent, type: 'mag' | 'phase') {
  if (e.button !== 0) return; // Left click only
  const canvas = type === 'mag' ? magCanvasRef.value : phaseCanvasRef.value;
  if (!canvas) return;
  const rect = canvas.getBoundingClientRect();
  const x = e.clientX - rect.left;
  const { plotW } = getPlotDimensions();

  if (x >= padL && x <= padL + plotW) {
    isDragging.value = true;
    dragStartX.value = x;
    dragEndX.value = x;
  }
}

function handleMouseMove(e: MouseEvent, type: 'mag' | 'phase') {
  const canvas = type === 'mag' ? magCanvasRef.value : phaseCanvasRef.value;
  if (!canvas) return;
  const rect = canvas.getBoundingClientRect();
  const x = e.clientX - rect.left;
  const y = e.clientY - rect.top;
  const { plotW, plotH } = getPlotDimensions();

  if (isDragging.value) {
    dragEndX.value = Math.max(padL, Math.min(padL + plotW, x));
    requestAnimationFrame(draw);
  } else {
    if (x >= padL && x <= padL + plotW && y >= padT && y <= padT + plotH) {
      hoverX.value = x;
      hoverY.value = y;
      hoveredCanvas.value = type;
      updateTooltip(x);
      requestAnimationFrame(draw);
    } else {
      if (hoverX.value !== null) {
        hoverX.value = null;
        hoverY.value = null;
        hoveredCanvas.value = null;
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
  hoveredCanvas.value = null;
  tooltip.value.show = false;
  requestAnimationFrame(draw);
}

function updateTooltip(mouseX: number) {
  const f = fromX(mouseX);
  const items: TooltipItem[] = [];

  const addPointData = (labelPrefix: string, magnitudeDb?: number, phaseRad?: number, color?: string) => {
    if (props.mode !== 'phase' && magnitudeDb !== undefined) {
      items.push({
        label: `${labelPrefix} (Mag)`,
        value: `${magnitudeDb.toFixed(2)} dB`,
        color: color || '#00D97E'
      });
    }
    if (props.mode !== 'magnitude' && phaseRad !== undefined) {
      const deg = (phaseRad * 180 / Math.PI).toFixed(1);
      items.push({
        label: `${labelPrefix} (Fase)`,
        value: `${phaseRad.toFixed(3)} rad (${deg}°)`,
        color: color || '#3B82F6'
      });
    }
  };

  // Main trace data
  const idx = findClosestIndex(props.frequencies, f);
  if (idx !== -1) {
    const mag = props.magnitudDb[idx];
    const ph = props.phaseRad[idx];
    addPointData('Activa', mag, ph);
  }

  // Snapshots data
  for (const t of props.traces) {
    if (t.frequencies) {
      const tIdx = findClosestIndex(t.frequencies, f);
      if (tIdx !== -1) {
        const tMag = t.magnitudeDb ? t.magnitudeDb[tIdx] : undefined;
        const tPh = t.phaseRad ? t.phaseRad[tIdx] : undefined;
        addPointData(t.label, tMag, tPh, t.color);
      }
    }
  }

  tooltip.value = {
    show: items.length > 0,
    x: mouseX,
    // Position tooltip appropriately
    y: hoveredCanvas.value === 'phase' && props.mode === 'both' ? props.height + 40 : 40,
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

function handleWheel(e: WheelEvent) {
  const canvas = getActiveCanvas();
  if (!canvas) return;
  const rect = canvas.getBoundingClientRect();
  const mouseX = e.clientX - rect.left;
  const { plotW } = getPlotDimensions();

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
  const canvas = getActiveCanvas();
  if (!canvas) return {};
  const width = canvas.clientWidth;
  const x = Math.max(80, Math.min(width - 80, tooltip.value.x));
  return {
    left: `${x}px`,
    top: `${tooltip.value.y}px`
  };
});

function resize() {
  if (containerRef.value) {
    const dpr = window.devicePixelRatio || 1;
    const rect = containerRef.value.getBoundingClientRect();
    
    if (props.mode !== 'phase' && magCanvasRef.value) {
      magCanvasRef.value.width = rect.width * dpr;
      magCanvasRef.value.height = props.height * dpr;
      magCanvasRef.value.style.width = `${rect.width}px`;
      magCanvasRef.value.style.height = `${props.height}px`;
      const ctx = magCanvasRef.value.getContext('2d');
      if (ctx) {
        ctx.resetTransform();
        ctx.scale(dpr, dpr);
      }
    }
    
    if (props.mode !== 'magnitude' && phaseCanvasRef.value) {
      phaseCanvasRef.value.width = rect.width * dpr;
      phaseCanvasRef.value.height = props.height * dpr;
      phaseCanvasRef.value.style.width = `${rect.width}px`;
      phaseCanvasRef.value.style.height = `${props.height}px`;
      const ctx = phaseCanvasRef.value.getContext('2d');
      if (ctx) {
        ctx.resetTransform();
        ctx.scale(dpr, dpr);
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

watch([
  () => props.frequencies, 
  () => props.magnitudDb, 
  () => props.phaseRad, 
  () => props.traces, 
  () => props.mode, 
  () => props.height,
  zoomFMin,
  zoomFMax
], () => {
  requestAnimationFrame(draw);
});
</script>

<template>
  <div ref="containerRef" class="fr-container" :style="{ height: (mode === 'both' ? height * 2 + 16 : height) + 'px' }">
    <div class="plot-header-overlay global-overlay">
      <div class="plot-toolbar">
        <span class="plot-instruction">💡 Arrastrá/Rueda para zoom X | Doble click para restaurar</span>
        <div class="plot-actions">
          <button class="action-btn" @click="zoomIn" title="Acercar">🔍+</button>
          <button class="action-btn" @click="zoomOut" title="Alejar">🔍-</button>
          <button class="action-btn" @click="resetZoom" title="Restaurar">🔄</button>
        </div>
      </div>
    </div>

    <!-- Magnitude Subplot -->
    <div v-if="mode !== 'phase'" class="subplot" :style="{ height: height + 'px' }">
      <div class="subplot-label">Magnitud H(ω) (dB)</div>
      <canvas 
        ref="magCanvasRef"
        @mousedown="handleMouseDown($event, 'mag')"
        @mousemove="handleMouseMove($event, 'mag')"
        @mouseup="handleMouseUp"
        @mouseleave="handleMouseLeave"
        @dblclick="resetZoom"
        @wheel.prevent="handleWheel"
      ></canvas>
    </div>

    <!-- Phase Subplot -->
    <div v-if="mode !== 'magnitude'" class="subplot" :style="{ height: height + 'px' }">
      <div class="subplot-label">Fase (rad)</div>
      <canvas 
        ref="phaseCanvasRef"
        @mousedown="handleMouseDown($event, 'phase')"
        @mousemove="handleMouseMove($event, 'phase')"
        @mouseup="handleMouseUp"
        @mouseleave="handleMouseLeave"
        @dblclick="resetZoom"
        @wheel.prevent="handleWheel"
      ></canvas>
    </div>

    <!-- Floating Tooltip (renders globally relative to the container) -->
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
.fr-container {
  width: 100%;
  display: flex;
  flex-direction: column;
  gap: 16px;
  position: relative;
}

.subplot {
  position: relative;
  background: var(--color-bg-secondary);
  border-radius: var(--border-radius-md);
  border: 1px solid var(--color-border);
  overflow: hidden;
}

.plot-header-overlay.global-overlay {
  position: absolute;
  top: 6px;
  right: 10px;
  display: flex;
  justify-content: flex-end;
  pointer-events: none;
  z-index: 10;
}

.subplot-label {
  position: absolute;
  top: 6px;
  left: 10px;
  font-size: 10px;
  font-weight: 600;
  color: var(--color-text-secondary);
  background: var(--color-bg-elevated);
  padding: 2px 6px;
  border-radius: 4px;
  border: 1px solid var(--color-border);
  z-index: 2;
  pointer-events: none;
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
