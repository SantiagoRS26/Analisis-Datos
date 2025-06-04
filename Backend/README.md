# ProyectoAnaliticaDatos

Este repositorio contiene un pipeline en Python para extraer y procesar datos de programas de posgrado en universidades. A continuación encontrarás las instrucciones para clonar el proyecto, configurar el entorno, instalar dependencias y ejecutar las tareas de descarga y extracción.

---

## 1. Clonar el repositorio

Abre tu terminal (PowerShell, Git Bash o Mac OS) y ejecuta:

```bash
git clone https://github.com/SantiagoRS26/Analisis-Datos.git
cd ProyectoAnaliticaDatos
```

---

## 2. Crear y activar un entorno virtual

Para asegurar que las dependencias no interfieran con otros proyectos, crea y activa un entorno virtual. A continuación encontrarás los comandos específicos para cada entorno:

### 2.1 En Windows (PowerShell)

1. **Crear el entorno:**

   ```powershell
   python -m venv venv
   ```

2. **Activar el entorno:**

   ```powershell
   .\venv\Scripts\Activate.ps1
   ```

   Si tu sistema impide la ejecución de scripts, ejecuta primero en PowerShell (como Administrador):

   ```powershell
   Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
   ```

   Luego vuelve a:

   ```powershell
   .\venv\Scripts\Activate.ps1
   ```

### 2.2 En Windows (Git Bash)

1. **Crear el entorno:**

   ```bash
   python -m venv venv
   ```

2. **Activar el entorno:**

   ```bash
   source venv/Scripts/activate
   ```

### 2.3 En macOS o Linux

1. **Crear el entorno (nota: en macOS suele invocarse `python3`):**

   ```bash
   python3 -m venv venv
   ```

2. **Activar el entorno:**

   ```bash
   source venv/bin/activate
   ```

> Al activar el entorno virtual, tu prompt cambiará para reflejar que estás dentro de `venv`.
> Para desactivarlo en cualquier momento:
>
> ```bash
> deactivate
> ```

---

## 3. Instalar dependencias

Con el entorno virtual activado, instala todas las librerías necesarias usando el archivo `requirements.txt`:

```bash
pip install -r requirements.txt
```

> En algunos sistemas puede ser `pip3 install -r requirements.txt`, pero si tu entorno virtual está activo, `pip` ya apunta a la versión correcta.

---

## 4. Estructura de carpetas del proyecto

Para referencia rápida, esta es la estructura principal del repositorio:

```
ProyectoAnaliticaDatos/
├── .gitignore
├── README.md
├── LICENSE
├── requirements.txt
├── data/
│   ├── raw/
│   │   ├── html/        ← Archivos HTML descargados
│   │   └── pdf/         ← Archivos PDF descargados
│   ├── output/          ← Resultados generados (se ignora en Git)
│   │   ├── courses.csv
│   │   └── download_log.json
│   └── universidades.csv← Lista de universidades y enlaces a procesar
│
├── src/                 ← Código fuente en Python
│   ├── __init__.py
│   ├── downloader.py    ← Funciones para descargar páginas
│   ├── extractor.py     ← Funciones para extraer cursos de HTML/PDF
│   ├── utils.py         ← Funciones auxiliares
│   └── main.py          ← Script principal (entry point)
│
├── tests/               ← Pruebas unitarias (pytest)
│   ├── __init__.py
│   ├── test_cleaner.py
│   └── test_extractor.py
│
└── uso.txt              ← Documentación adicional de uso (opcional)
```

* **`data/universidades.csv`**: Debe contener al menos dos columnas:

  * `Universidad` (nombre)
  * `Carrera` (nombre del programa)
  * `Enlace` (URL o URLs separados por comas, de donde se extraerán datos)
* **`data/output/`**: Carpeta donde se generan los archivos de salida (`download_log.json` y `courses.csv`). Esta carpeta está en `.gitignore` porque se recrea cada vez que corres el pipeline.

---

## 5. Ejecutar el pipeline

El pipeline se compone de dos pasos principales: **download** (descarga/almacenamiento) y **extract** (extracción de cursos). Ambos comandos invocan a `main.py` desde el paquete `src`.

### 5.1 Paso 1: Descargar (download)

* **Uso básico (con caché):**
  Este comando revisa si ya existe el HTML/PDF correspondiente en `data/raw/`. Si no existe, lo descarga; si ya existe, lo salta. La metadata de cada descarga se guarda en `data/output/download_log.json`.

  ```bash
  python -m src.main download
  ```

* **Forzar re-descarga de todo (ignorar caché):**
  Con `--force`, se descarga de nuevo todos los enlaces, aunque ya existan localmente.

  ```bash
  python -m src.main download --force
  ```

> #### Ejecución en distintos entornos:
>
> * **PowerShell** / **Git Bash (Windows)** / **macOS**
>   Si tu entorno virtual ya está activado, basta con:
>
>   ```bash
>   python -m src.main download
>   ```
>
>   En macOS / Linux, si al activar tu venv `python` apunta a la versión correcta, no necesitas usar `python3`. De todos modos, si hay conflicto, puedes invocar:
>
>   ```bash
>   python3 -m src.main download
>   ```

### 5.2 Paso 2: Extraer (extract)

Una vez completada la descarga y generado el `download_log.json`, este comando lee ese archivo y recorre cada entrada exitosa para extraer la lista de cursos (título, descripción, etc.). El resultado final se guarda en `data/output/courses.csv`.

```bash
python -m src.main extract
```

> Al igual que en el paso anterior, si en tu sistema `python` apunta al Python 3 del entorno virtual, no necesitas `python3`.
> Si quieres volver a extraer (por ejemplo, si cambiaste la lógica del extractor), basta con ejecutar el mismo comando de nuevo.

---

## 6. Archivos de salida

* **`data/output/download_log.json`**
  Contiene un arreglo de objetos JSON, cada uno con metadatos de descarga:

  ```jsonc
  [
    {
      "url": "https://.../programa_univ_A.html",
      "path": "data/raw/html/programa_univ_A.html",
      "university": "Universidad A",
      "program": "Ingeniería X",
      "error": null
    },
    {
      "url": "...",
      "path": "...",
      "university": "...",
      "program": "...",
      "error": "404 Not Found"
    },
    ...
  ]
  ```

  * **`error`** es `null` si la descarga fue exitosa; de lo contrario, indica el motivo del fallo.

* **`data/output/courses.csv`**
  Archivo CSV con todas las filas de cursos extraídos. Columnas típicas (ejemplo):

  ```csv
  university,program,title,duration,location,extra_field_1,...
  Universidad A,Ingeniería X,Maestría en Y,2 años,Sede Central,...
  Universidad B,Ciencias Z,Doctorado en W,4 años,Campus Norte,...
  ...
  ```

---


## 7. Posibles errores y soluciones rápidas

1. **`ModuleNotFoundError: No module named 'src'`**

   * Asegúrate de que estés en la carpeta raíz del proyecto (`ProyectoAnaliticaDatos/`) y que el entorno virtual esté activado.
   * Verifica que `src/` contenga un archivo `__init__.py` (aunque no siempre es obligatorio, ayuda a Python a reconocerlo como paquete).
   * Corre el comando tal cual:

     ```bash
     python -m src.main download
     ```

2. **Problemas con permisos al activar el entorno en PowerShell**

   * Ejecuta `Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser` en una terminal de PowerShell con privilegios de administrador y luego vuelve a activar el venv:

     ```powershell
     .\venv\Scripts\Activate.ps1
     ```

3. **Errores de versión de Python**

   * Se recomienda usar **Python 3.8+**. Verifica tu versión con:

     ```bash
     python --version
     ```
   * En macOS, si `python` no apunta a Python 3, usa `python3`:

     ```bash
     python3 --version
     python3 -m venv venv
     source venv/bin/activate
     ```

---

## 8. Contribuciones

Si deseas contribuir:

1. Haz un “fork” del repositorio en GitHub.
2. Clónalo en tu máquina local.
3. Crea una rama nueva para tu feature o corrección:

   ```bash
   git checkout -b feature/nombre-descriptivo
   ```
4. Realiza tus cambios o agrega nuevas pruebas.
5. Haz tus commits y súbelos:

   ```bash
   git add .
   git commit -m "Descripción clara de lo que hiciste"
   git push origin feature/nombre-descriptivo
   ```
6. Abre un Pull Request en GitHub describiendo tus cambios.

---

## 10. Licencia

Este proyecto está licenciado bajo [MIT License](LICENSE). Si deseas usar, modificar o redistribuir este código, consulta el archivo `LICENSE` para más detalles.