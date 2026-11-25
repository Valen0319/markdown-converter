# Conversor a Markdown

Aplicación de escritorio para Windows que convierte archivos de distintos formatos a Markdown mediante [MarkItDown](https://github.com/microsoft/markitdown).

> [!WARNING]
> Este proyecto fue **vibecodeado**: desarrollado con asistencia intensiva de inteligencia artificial. Puede contener errores, comportamientos inesperados o compatibilidad limitada con determinados formatos de archivo. Revisar siempre el Markdown generado antes de utilizarlo en documentos importantes.

## Características

- Interfaz de escritorio oscura con acentos verde oliva
- Arrastrar y soltar archivos
- Selección individual o de carpetas completas
- Conversión por lotes
- Selección de carpeta de salida
- Apertura automática de la carpeta resultante
- Configuración guardada localmente
- Protección básica contra sobrescritura mediante nombres numerados
- Registro visual de conversiones y errores
- Ejecución como código fuente o como ejecutable portátil de Windows

## Formatos previstos

- PDF
- DOC y DOCX
- XLS y XLSX
- PPT y PPTX
- HTML y HTM
- TXT y Markdown
- CSV, JSON y XML
- PNG, JPG, JPEG, GIF, BMP, TIFF y WEBP

La calidad de la extracción depende del formato y del contenido original. Los documentos escaneados, PDF con imágenes y diseños complejos pueden requerir OCR o producir resultados incompletos.

## Ejecutar desde el código fuente

Requisitos: Windows y Python 3.11 o posterior.

```powershell
.\setup.ps1
.\run.ps1
```

Para ejecutar las pruebas:

```powershell
.\.venv\Scripts\python.exe -m pytest -q
```

## Crear el ejecutable portable

```powershell
.\build.ps1
```

El resultado se genera en:

```text
dist\Conversor-Markdown\Conversor-Markdown.exe
```

El ejecutable debe conservar junto a él la carpeta `_internal`. Para distribuirlo, comprime ambas partes en una única carpeta o archivo ZIP.

## Configuración portable

Los ajustes se guardan dentro de:

```text
config\settings.json
```

El programa evita depender de rutas personales predefinidas. Sin embargo, ciertos formatos pueden necesitar que sus bibliotecas externas estén disponibles en el sistema.

## Estado del proyecto

Proyecto personal y experimental. Puede cambiar con frecuencia y no está garantizado que conserve todas las características o formatos en futuras versiones.

## Uso responsable

- Conservar una copia de los archivos originales
- Revisar tablas, imágenes y encabezados convertidos
- Comprobar especialmente documentos académicos, legales o técnicos
- No considerar la salida automática como una traducción o validación perfecta

## Licencia

Añadir una licencia antes de publicar redistribuciones públicas o contribuciones externas.

## Uso directo con la versión portable

La carpeta `portable` ya contiene el ejecutable listo para usar:

```text
portable\Conversor-Markdown.exe
```

En Windows, abre esa carpeta y haz doble clic en `Conversor-Markdown.exe`. Mantén junto al ejecutable la carpeta `portable\_internal` y no ejecutes el `.exe` desde una ubicación distinta sin esa carpeta.

No necesitas tener Python, crear un entorno virtual ni ejecutar scripts de instalación para usar la versión portable.
