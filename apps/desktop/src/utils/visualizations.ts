export const toolMeta = {
  rta: { icon: 'ti-activity', key: 'n-rta' },
  tf: { icon: 'ti-chart-line', key: 'n-tf' },
  spec: { icon: 'ti-chart-histogram', key: 'n-spec' },
  coh: { icon: 'ti-infinity', key: 'n-coh' },
  flt: { icon: 'ti-adjustments-horizontal', key: 'n-flt' },
  gen: { icon: 'ti-antenna', key: 'n-gen' }
};

export function generateBars(n: number, uniform: boolean = false): number[] {
  const result = [];
  let seed = 42;
  for (let i = 0; i < n; i++) {
    seed = (seed * 1664525 + 1013904223) & 0xffffffff;
    const r = (seed >>> 0) / 0xffffffff;
    const pct = uniform ? 62 : Math.max(4, Math.min(100,
      Math.sin(i / n * Math.PI) * 65 + 15 + r * 28 + Math.sin(i * 0.7) * 20
    ));
    result.push(pct);
  }
  return result;
}

export function generateSinePoints(): string {
  const pts = [];
  let seed = 7;
  for (let i = 0; i <= 96; i++) {
    seed = (seed * 1664525 + 1013904223) & 0xffffffff;
    const r = (seed >>> 0) / 0xffffffff;
    const y = 50 + Math.sin(i / 96 * Math.PI * 6) * 34 + (r - 0.5) * 4;
    pts.push(`${i * 5},${y.toFixed(1)}`);
  }
  return pts.join(' ');
}

export function generateSpectrogram(cols: number, rows: number): number[][] {
  const result = [];
  let seed = 99;
  for (let c = 0; c < cols; c++) {
    const colData = [];
    for (let r = 0; r < rows; r++) {
      seed = (seed * 1664525 + 1013904223) & 0xffffffff;
      const rnd = (seed >>> 0) / 0xffffffff;
      const v = Math.max(0.06, Math.min(0.9,
        Math.sin(c / cols * Math.PI) * 0.55 + Math.sin((rows - r) / rows * Math.PI * 1.8) * 0.3 + rnd * 0.25
      ));
      colData.push(v);
    }
    result.push(colData);
  }
  return result;
}
