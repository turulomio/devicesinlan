# Reglas e Instrucciones para Agentes (AGENTS.md)

Este documento describe la estructura del proyecto, las normas de desarrollo y las directrices para agentes de IA que trabajen en este repositorio.

---

## ⚠️ Reglas Importantes de Ejecución

1. **NO ejecutar tareas de compilación/distribución (`poe dist_linux`, `poe dist_windows`)**:
   * Las tareas de empaquetado con Nuitka consumen muchos recursos de CPU y tiempo.
   * El agente debe configurar, modificar o arreglar los scripts y luego **pedir al usuario que ejecute los comandos de compilación**.
2. **Tareas permitidas**:
   * El agente puede ejecutar `poetry run pytest`, `poe compile`, `git status`, `git diff`, formateos o comprobaciones rápidas que no bloqueen la terminal.

---

## 🛠️ Entorno y Herramientas

* **Gestor de paquetes:** [Poetry](https://python-poetry.org/)
* **Ejecutor de tareas:** [Poe the Poet](https://github.com/nat-n/poethepoet) (`poetry run poe <tarea>`)
* **Librerías principales:**
  * `PyQt6` (Interfaz gráfica y componentes Qt)
  * `scapy` (Escaneo de red ARP y sondas de red)
  * `pydicts`, `colorama`, `tqdm`
* **Compilación a binarios:** `Nuitka` (modo `--onefile` y `--standalone`)

---

## 📂 Estructura del Repositorio

* `devicesinlan/`:
  * `devicesinlan.py`: Puntos de entrada para consola (`main_console`) y GUI (`main_gui`).
  * `libdevicesinlan.py`: Lógica de red, clases base y manejo de dispositivos.
  * `libdevicesinlan_gui.py`: Lógica y controladores de la interfaz gráfica.
  * `poethepoet.py`: Scripts y tareas de automatización para Poe the Poet.
  * `ui/`: Archivos `.ui` de Qt Designer y módulos generados `Ui_*.py`.
  * `images/`: Iconos, recursos `.qrc` y `devicesinlan_rc.py`.
  * `i18n/`: Archivos de traducción Qt (`.ts`, `.qm`).
  * `data/`: Documentación integrada y ficheros de datos (`ieee-oui.txt`).
* `dist/`: Carpeta de salida para paquetes Python y ejecutables generados.

---

## 📋 Tareas de Poe the Poet (`poe`)

| Tarea | Descripción |
| :--- | :--- |
| `poetry run poe compile` | Compila archivos `.ui` a Python (`pyuic6`) y recursos `.qrc` (`rcc`). |
| `poetry run poe translate` | Genera y actualiza archivos de traducción y páginas de manual. |
| `poetry run poe tests` | Ejecuta las pruebas unitarias con `pytest`. |
| `poetry run poe dist_linux` | *(Ejecutar por el usuario)* Genera binarios independientes para Linux (`64bits`/`32bits`). |
| `poetry run poe dist_windows` | *(Ejecutar por el usuario)* Genera binarios independientes `.exe` para Windows (`64bits`/`32bits`). |
| `poetry run poe reusing` | Actualiza módulos compartidos del repositorio `reusingcode`. |
| `poetry run poe release` | Muestra el checklist para crear una nueva versión y release. |
