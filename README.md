# DSP Analyzer — Repositorio Monorepo

Este repositorio contiene el proyecto integrado para el analizador de procesamiento digital de señales (DSP). Está estructurado como un monorepo que incluye:
* **`core/dsp/`**: El motor matemático en Python (módulo que se entrega para el Trabajo Práctico de la universidad).
* **`apps/api/`**: El backend en FastAPI que expone las funciones matemáticas mediante endpoints HTTP.
* **`apps/desktop/`**: La interfaz gráfica interactiva de escritorio construida con Tauri y Vue 3.

---

## 🛠️ Ruta 1: Desarrollo del Motor DSP (Solo Python)
*Recomendado para los integrantes del equipo que trabajarán exclusivamente en las funciones matemáticas de `core/dsp/` y en los Jupyter Notebooks.*

Esta ruta **no** requiere instalar Node.js, Rust, Docker ni compiladores de C/C++. Solo requiere una instalación estándar de Python.

### Requisitos previos
* **Python 3.11 o superior** instalado.
  * *Nota para Windows:* Al instalar Python desde el instalador oficial, asegúrese de marcar la casilla **"Add python.exe to PATH"** en la primera pantalla.

### Configuración del Entorno de Trabajo

1. **Clonar el repositorio:**
   ```bash
   git clone <URL_DEL_REPOSITORIO>
   cd TP-DSP
   ```

2. **Crear un entorno virtual de Python:**
   ```bash
   python -m venv .venv
   ```

3. **Activar el entorno virtual:**
   * **En Windows (Símbolo del sistema - CMD):**
     ```cmd
     .venv\Scripts\activate.bat
     ```
   * **En Windows (PowerShell):**
     ```powershell
     # Si el sistema bloquea la ejecución de scripts, ejecute primero:
     Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope Process
     # Luego active el entorno:
     .venv\Scripts\Activate.ps1
     ```
   * **En Git Bash, Linux o macOS:**
     ```bash
     source .venv/bin/activate
     ```

4. **Instalar las dependencias del proyecto:**
   ```bash
   pip install --upgrade pip
   pip install -e .
   pip install pytest
   ```

### Ejecutar las Pruebas Unitarias (Tests)
Una vez activado el entorno virtual, puede validar la correcta implementación matemática de las funciones mediante las pruebas unitarias automatizadas:

* **Ejecutar todos los tests:**
  ```bash
  pytest
  ```
* **Ejecutar las pruebas de un archivo específico (ej. filtros):**
  ```bash
  pytest core/dsp/tests/test_filters.py
  ```
* **Ejecutar una prueba específica por su nombre:**
  ```bash
  pytest -k "test_dc_preservation"
  ```

---

## 🚀 Ruta 2: Desarrollo del Sistema Completo (Desktop + API)
*Recomendado para ejecutar la aplicación de escritorio de forma local y conectar la interfaz de usuario con el motor matemático.*

### Requisitos previos
* **Node.js (v20 o superior)**
* **Rust (rustup)** y herramientas de compilación de C++ (Build Tools para Visual Studio en Windows).
* **uv** (Administrador de paquetes de Python rápido, opcional).
* **Docker** (opcional, para levantar el servidor de FastAPI en un contenedor).

### Configuración Inicial

1. **Instalar dependencias de Python y Node.js:**
   ```bash
   # Si usa uv (instalación rápida de dependencias de Python):
   uv sync

   # Instalar dependencias del frontend:
   cd apps/desktop
   npm install
   cd ../..
   ```

2. **Ejecutar el backend (FastAPI):**
   * **Opción A (Sin Docker):**
     ```bash
     npm run api:dev
     ```
   * **Opción B (Con Docker):**
     ```bash
     npm run docker:up
     ```

3. **Ejecutar la aplicación de escritorio (Tauri + Vue):**
   En una nueva pestaña de la terminal, ejecute:
   ```bash
   npm run dev
   ```

---

## 📂 Estructura del Repositorio

* **`core/dsp/`**: Código fuente de procesamiento de señal en Python.
  * **`core/dsp/tests/`**: Archivos de prueba unitaria (`test_*.py`).
* **`faculty/`**: Notebooks de Jupyter e informes académicos para entrega.
* **`apps/api/`**: Servidor FastAPI (puente de red entre la app de escritorio y las funciones en Python).
* **`apps/desktop/`**: Interfaz de usuario multiplataforma (HTML/CSS/TS/Vue).

---
## Intengrantes

- Ferreyra, Florencia
- Gonzalez, Tomás
- Molina, Lara
- Scafati, Jerónimo 

## 📄 Licencia
Este proyecto se distribuye bajo la licencia PolyForm Noncommercial 1.0.0. No se permite el uso comercial sin autorización previa.