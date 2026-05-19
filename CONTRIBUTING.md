# Guía de Contribución y Flujo de Trabajo (Git Flow)

Para mantener el código ordenado y asegurar la correcta integración de las distintas partes del proyecto, utilizaremos un flujo de trabajo basado en Git Flow y desarrollo guiado por Issues.

## 1. Estructura de Ramas

El repositorio está organizado en las siguientes ramas principales:

* **`main`**: Contiene el código estable e implementado. No se realizan commits directamente sobre esta rama.
* **`dev`**: Es la rama principal de desarrollo e integración. Todo el código nuevo se fusiona aquí mediante Pull Requests para ser evaluado en conjunto.
* **Ramas de trabajo**: Son ramas temporales creadas para resolver tareas específicas. Deben seguir una nomenclatura basada en el tipo de tarea.

### Nomenclatura de Ramas (Ejemplos)

El nombre de la rama debe indicar el tipo de trabajo y una breve descripción, utilizando guiones para separar palabras:

* `feat/filtro-media-movil` (Para nuevas funcionalidades)
* `fix/calculo-densidad-espectral` (Para corrección de errores)
* `dsp/coherencia-cuadratica` (Para algoritmos específicos de procesamiento de señales)
* `docs/analisis-sistemas` (Para actualizaciones en los notebooks o documentación)

## 2. Flujo de Trabajo

Cada tarea del proyecto estará documentada como un Issue. El ciclo de vida de una contribución debe seguir estos pasos:

### Paso 1: Asignación del Issue

Seleccionar la tarea a realizar en la pestaña de Issues y asignarse a uno mismo (Assignees). Tomar nota del número del Issue (por ejemplo, `#12`).

### Paso 2: Sincronización del repositorio local

Asegurarse de partir siempre desde la versión más reciente de la rama de integración:

```bash
git switch dev
git pull origin dev

```

### Paso 3: Creación de la rama de trabajo

Crear una nueva rama a partir de `dev` utilizando la nomenclatura detallada en la sección anterior:

```bash
git switch -c feat/implementar-convolucion

```

### Paso 4: Desarrollo

Implementar el código necesario para resolver el Issue. Se debe asegurar que las funciones pasen las pruebas correspondientes y cumplan con los requerimientos documentados en la tarea.

### Paso 5: Registro de cambios (Commits)

Los mensajes de los commits deben seguir la convención de **Conventional Commits**. Esto facilita la lectura del historial y la automatización de las versiones.

La estructura es: `tipo: descripción breve en minúsculas`

**Ejemplos de commits:**

* `feat: agrega funcion para calcular la transformada de fourier`
* `fix: corrige el indice de ventana en el suavizado de octavas`
* `docs: actualiza el notebook con el analisis del sistema no lineal`
* `test: añade pruebas para el filtro peine`
* `refactor: optimiza el loop de lectura de archivos de audio`

Para registrar los cambios en la terminal:

```bash
git add .
git commit -m "feat: agrega funcion para calcular la transformada de fourier"

```

### Paso 6: Subida de la rama a GitHub

Al publicar la rama por primera vez en el repositorio remoto, es necesario establecer el *upstream* para vincular la rama local con la de origen:

```bash
git push -u origin feat/implementar-convolucion

```

En commits posteriores sobre la misma rama, bastará con ejecutar `git push`.

### Paso 7: Creación del Pull Request (PR)

1. En GitHub, utilizar el botón "Compare & pull request".
2. Verificar que la rama base (*base*) sea `dev` y la rama de origen (*compare*) sea la rama de trabajo recién subida.
3. En la descripción del PR, enlazar el Issue correspondiente utilizando palabras clave como `Closes` o `Fixes` seguido del número de Issue.
*Ejemplo: "Implementa la lógica del filtro FIR. Closes #12".*
4. Crear el Pull Request.

## 3. Consideraciones Finales

* **Un Issue equivale a un Pull Request:** Mantener los cambios enfocados en resolver una única tarea para facilitar la revisión del código.
* **Revisión de pares:** Una vez abierto el PR, otro miembro del equipo deberá revisar el código. Si los tests automáticos pasan y el código es aprobado, se procederá a realizar el "Merge" hacia la rama `dev`.