<script setup lang="ts">
import { computed } from 'vue';
import {
  IconBrandUbuntu,
  IconBrandApple,
  IconBrandWindows,
  IconDownload,
  IconPackage,
  IconChevronRight,
} from '@tabler/icons-vue';

// ── Platform download descriptors ────────────────────────────────────────────
// URLs come from env vars set in .env.local (see .env.example).
// If a URL is not configured, the download button is disabled for that format.

interface DownloadFormat {
  label: string;
  ext: string;
  url: string | undefined;
  note: string;
}

interface Platform {
  id: string;
  name: string;
  accent: string;
  formats: DownloadFormat[];
}

const BASE_GITHUB_RELEASE = 'https://github.com/Roomwaves/dsp-lab/releases/latest/download';

const platforms = computed<Platform[]>(() => [
  {
    id: 'linux',
    name: 'Linux',
    accent: 'lime',
    formats: [
      {
        label: 'AppImage',
        ext: '.AppImage',
        url: import.meta.env.VITE_DOWNLOAD_URL_LINUX_APPIMAGE || `${BASE_GITHUB_RELEASE}/Roomwaves-DSP-Linux.AppImage`,
        note: 'Universal — no install required',
      },
      {
        label: 'Debian / Ubuntu',
        ext: '.deb',
        url: import.meta.env.VITE_DOWNLOAD_URL_LINUX_DEB || `${BASE_GITHUB_RELEASE}/Roomwaves-DSP-Linux.deb`,
        note: 'dpkg / apt compatible',
      },
    ],
  },
  {
    id: 'mac',
    name: 'macOS',
    accent: 'peach',
    formats: [
      {
        label: 'Disk Image',
        ext: '.dmg',
        url: import.meta.env.VITE_DOWNLOAD_URL_MAC_DMG || `${BASE_GITHUB_RELEASE}/Roomwaves-DSP-macOS.dmg`,
        note: 'Universal — Apple Silicon & Intel',
      },
    ],
  },
  {
    id: 'windows',
    name: 'Windows',
    accent: 'sky',
    formats: [
      {
        label: 'Installer',
        ext: '.exe',
        url: import.meta.env.VITE_DOWNLOAD_URL_WINDOWS_EXE || `${BASE_GITHUB_RELEASE}/Roomwaves-DSP-Setup.exe`,
        note: 'NSIS — recommended',
      },
      {
        label: 'MSI Package',
        ext: '.msi',
        url: import.meta.env.VITE_DOWNLOAD_URL_WINDOWS_MSI || `${BASE_GITHUB_RELEASE}/Roomwaves-DSP.msi`,
        note: 'For enterprise / silent installs',
      },
    ],
  },
]);

const APP_VERSION = '0.1.0';
</script>

<template>
  <div class="download-view">
    <!-- ── Header ─────────────────────────────────────────────── -->
    <div class="dv-header">
      <div class="dv-icon-wrapper">
        <IconPackage size="28" />
      </div>
      <div>
        <h1 class="dv-title">Descargar DSP-LAB</h1>
        <p class="dv-subtitle">
          Versión {{ APP_VERSION }} — Seleccioná tu plataforma
        </p>
      </div>
    </div>

    <!-- ── Platform cards ─────────────────────────────────────── -->
    <div class="dv-grid">
      <div
        v-for="platform in platforms"
        :key="platform.id"
        class="platform-card"
        :class="[`platform-card--${platform.accent}`, `platform--${platform.id}`]"
      >
        <!-- Card header -->
        <div class="pc-header">
          <div class="pc-icon">
            <IconBrandUbuntu  v-if="platform.id === 'linux'"   size="26" />
            <IconBrandApple   v-if="platform.id === 'mac'"     size="26" />
            <IconBrandWindows v-if="platform.id === 'windows'" size="26" />
          </div>
          <span class="pc-name">{{ platform.name }}</span>
        </div>

        <!-- Formats list -->
        <div class="pc-formats">
          <a
            v-for="fmt in platform.formats"
            :key="fmt.ext"
            class="fmt-row"
            :class="{ 'fmt-row--disabled': !fmt.url }"
            :href="fmt.url ?? '#'"
            :download="!!fmt.url || undefined"
            :aria-disabled="!fmt.url"
            :tabindex="fmt.url ? 0 : -1"
            :id="`download-${platform.id}-${fmt.ext.replace('.', '')}`"
          >
            <div class="fmt-info">
              <span class="fmt-label">{{ fmt.label }}</span>
              <span class="fmt-ext">{{ fmt.ext }}</span>
              <span class="fmt-note">{{ fmt.note }}</span>
            </div>
            <div class="fmt-action">
              <IconDownload v-if="fmt.url" size="15" class="fmt-dl-icon" />
              <span v-else class="fmt-soon">Pronto</span>
              <IconChevronRight size="13" class="fmt-chevron" />
            </div>
          </a>
        </div>
      </div>
    </div>

    <!-- ── Footer note ────────────────────────────────────────── -->
    <p class="dv-footer-note">
      Los archivos son distribuidos directamente desde nuestro sitio web.<br/>
      Verificá la firma del instalador antes de ejecutarlo.
    </p>
  </div>
</template>

<style scoped>
/* ── Container ───────────────────────────────────────────────── */
.download-view {
  padding: 32px 36px;
  height: 100%;
  overflow-y: auto;
  display: flex;
  flex-direction: column;
  gap: 28px;
  background-image:
    radial-gradient(ellipse 55% 35% at 50% 0%, rgba(131, 188, 169, 0.05) 0%, transparent 70%);
}

/* ── Header ──────────────────────────────────────────────────── */
.dv-header {
  display: flex;
  align-items: center;
  gap: 16px;
}

.dv-icon-wrapper {
  width: 52px;
  height: 52px;
  border-radius: var(--radius-md);
  background: var(--accent-lime-10);
  border: 1px solid var(--border-bold);
  display: flex;
  align-items: center;
  justify-content: center;
  color: var(--accent-lime);
  flex-shrink: 0;
}

.dv-title {
  font-family: var(--font-ui);
  font-size: 20px;
  font-weight: 400;
  color: var(--text-white);
  margin: 0 0 4px 0;
  letter-spacing: 0.02em;
}

.dv-subtitle {
  font-family: var(--font-mono);
  font-size: 11px;
  color: var(--text-gray);
  margin: 0;
  letter-spacing: 0.04em;
}

/* ── Grid ────────────────────────────────────────────────────── */
.dv-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 16px;
}

/* ── Platform card ───────────────────────────────────────────── */
.platform-card {
  background: rgba(0, 26, 35, 0.65);
  backdrop-filter: blur(10px);
  -webkit-backdrop-filter: blur(10px);
  border: 1px solid rgba(255, 255, 255, 0.14);
  border-radius: var(--radius-md);
  box-shadow: 4px 4px 0px 0px var(--surface-0);
  overflow: hidden;
  display: flex;
  flex-direction: column;
  transition: transform 0.15s var(--ease-material), box-shadow 0.15s var(--ease-material), border-color 0.15s var(--ease-material);
}

.platform-card--lime:hover {
  transform: translate(-3px, -3px);
  box-shadow: 4px 4px 0px 0px var(--accent-lime);
  border-color: rgba(131, 188, 169, 0.45);
}

.platform-card--peach:hover {
  transform: translate(-3px, -3px);
  box-shadow: 4px 4px 0px 0px var(--accent-peach);
  border-color: rgba(224, 159, 103, 0.45);
}

.platform-card--sky:hover {
  transform: translate(-3px, -3px);
  box-shadow: 4px 4px 0px 0px #6eb4f7;
  border-color: rgba(110, 180, 247, 0.45);
}

/* ── Card header ─────────────────────────────────────────────── */
.pc-header {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 18px 20px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.07);
}

.pc-icon {
  width: 42px;
  height: 42px;
  border-radius: var(--radius-sm);
  background: var(--surface-2);
  border: 1px solid var(--border-ghost);
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
  transition: background 0.15s var(--ease-material), border-color 0.15s var(--ease-material);
}

.platform-card--lime .pc-icon  { color: var(--accent-lime); }
.platform-card--peach .pc-icon { color: var(--accent-peach); }
.platform-card--sky .pc-icon   { color: #6eb4f7; }

.platform-card--lime:hover .pc-icon {
  background: var(--accent-lime-10);
  border-color: var(--border-bold);
}
.platform-card--peach:hover .pc-icon {
  background: rgba(224, 159, 103, 0.10);
  border-color: rgba(224, 159, 103, 0.4);
}
.platform-card--sky:hover .pc-icon {
  background: rgba(110, 180, 247, 0.08);
  border-color: rgba(110, 180, 247, 0.35);
}

.pc-name {
  font-family: var(--font-ui);
  font-size: 16px;
  font-weight: 400;
  color: var(--text-white);
  letter-spacing: 0.02em;
}

/* ── Formats ─────────────────────────────────────────────────── */
.pc-formats {
  display: flex;
  flex-direction: column;
  flex: 1;
}

.fmt-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 13px 20px;
  gap: 12px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.05);
  text-decoration: none;
  cursor: pointer;
  transition: background 0.12s var(--ease-material);
}

.fmt-row:last-child {
  border-bottom: none;
}

.fmt-row:not(.fmt-row--disabled):hover {
  background: rgba(255, 255, 255, 0.04);
}

.fmt-row--disabled {
  opacity: 0.38;
  cursor: default;
  pointer-events: none;
}

.fmt-info {
  display: flex;
  flex-direction: column;
  gap: 3px;
  min-width: 0;
}

.fmt-label {
  font-family: var(--font-ui);
  font-size: 13px;
  font-weight: 400;
  color: var(--text-white);
}

.fmt-ext {
  font-family: var(--font-mono);
  font-size: 10px;
  color: var(--text-gray);
  letter-spacing: 0.04em;
}

.fmt-note {
  font-family: var(--font-ui);
  font-size: 11px;
  color: var(--text-gray);
  font-weight: 300;
}

.fmt-action {
  display: flex;
  align-items: center;
  gap: 4px;
  flex-shrink: 0;
}

.platform-card--lime  .fmt-dl-icon { color: var(--accent-lime); }
.platform-card--peach .fmt-dl-icon { color: var(--accent-peach); }
.platform-card--sky   .fmt-dl-icon { color: #6eb4f7; }

.fmt-chevron {
  color: var(--text-gray);
}

.fmt-soon {
  font-family: var(--font-mono);
  font-size: 10px;
  color: var(--text-gray);
  letter-spacing: 0.06em;
  text-transform: uppercase;
}

/* ── Footer note ─────────────────────────────────────────────── */
.dv-footer-note {
  font-family: var(--font-ui);
  font-size: 13px;
  font-weight: 300;
  color: var(--text-gray);
  line-height: 1.6;
  text-align: center;
  margin: 0;
  padding-top: 4px;
}
</style>
