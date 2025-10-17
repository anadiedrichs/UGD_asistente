# Proyecto asistente para la UGD FRM UTN

## Requisitos

* Debe ya contar con Python instalado en su sistema operativo.
* Conocimientos de Git y Python.

## Instrucciones de configuración

### 1) Clonar el repositorio

### 2) Virtual environment de Python

Crea el Entorno Virtual: Esto aísla las dependencias de tu proyecto.

En tu terminal, dentro de la carpeta del proyecto:

```
python -m venv venv
source venv/bin/activate  # En Windows: venv\Scripts\activate
```

### 3) Instalación de librerías

En tu terminal, dentro de la carpeta del proyecto:

```
pip install -r requirements.txt
```

### 4) Variables de entorno

Copia el archivo .creaTuEnv para renombrarlo a .env.

```
cp .creaTuEnv .env
```
Dentro del mismo debes agregar tus claves para cada API.

**NO agregues a Git tu archivo .env**

### 5) API keys

Para cada servicio, debes tener una API KEY , como se menciona en el archivo .env.
Completalo antes de ejecutar el proyecto

### 6) Base de datos en Notion

Debe crear una base de datos en Notion (tabla). Luego vincularla con la integracion y darle permisos de acceso.
Más detalles en el documento del proyecto.


## Instrucciones de uso

En tu terminal, dentro de la carpeta del proyecto, ejecuta la siguiente línea para correr el proyecto:

```
python -m src.main
```