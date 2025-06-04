# Frontend - Analizador de Datos Universitarios

Este es el frontend para tu proyecto final de Computación 3. Una aplicación web moderna construida con Next.js, React y shadcn/ui que consume tu API de FastAPI para analizar contenido universitario.

## 🚀 Características

- **Interfaz moderna y elegante** usando shadcn/ui
- **Diseño responsivo** que funciona en desktop y móvil
- **Formulario intuitivo** para configurar los parámetros de análisis
- **Visualización de resultados** con gráficos de barras y nubes de palabras
- **Manejo de errores** con mensajes claros para el usuario
- **Estados de carga** con indicadores visuales
- **Modo oscuro** automático según las preferencias del sistema

## 🛠️ Tecnologías

- **Next.js 15** - Framework de React
- **React 19** - Biblioteca de UI
- **TypeScript** - Tipado estático
- **Tailwind CSS** - Framework de estilos
- **shadcn/ui** - Componentes de UI
- **Lucide React** - Iconos

## 📋 Prerrequisitos

- Node.js 18+ 
- npm o yarn
- Tu API de FastAPI ejecutándose en `http://localhost:8000`

## 🔧 Instalación

1. **Clona el repositorio** (si no lo has hecho ya)

2. **Instala las dependencias:**
   ```bash
   npm install
   ```

3. **Inicia el servidor de desarrollo:**
   ```bash
   npm run dev
   ```

4. **Abre tu navegador** en `http://localhost:3000`

## 🎯 Uso

1. **Asegúrate de que tu API esté funcionando** en `http://localhost:8000`

2. **Completa el formulario:**
   - **URL (requerida):** La URL del contenido a analizar
   - **Universidad (opcional):** Nombre de la universidad
   - **Programa (opcional):** Nombre del programa académico
   - **Forzar re-descarga:** Checkbox para forzar la descarga del contenido

3. **Haz clic en "Analizar URL"** y espera los resultados

4. **Visualiza los resultados:**
   - Gráfico de barras con las frecuencias
   - Nube de palabras con los términos más relevantes

## 📁 Estructura del Proyecto

```
src/
├── app/
│   ├── globals.css          # Estilos globales con variables de shadcn/ui
│   ├── layout.tsx           # Layout principal
│   └── page.tsx             # Página principal con el formulario
├── components/
│   ├── ui/                  # Componentes de shadcn/ui
│   │   ├── button.tsx
│   │   ├── card.tsx
│   │   ├── input.tsx
│   │   └── label.tsx
│   └── ImageDisplay.tsx     # Componente para mostrar las imágenes
├── hooks/
│   └── useAnalyzeUrl.ts     # Hook personalizado para la API
└── lib/
    └── utils.ts             # Utilidades (cn function)
```

## 🚀 Para ejecutar

1. **Inicia tu API de FastAPI primero:**
   ```bash
   cd "../Analisis-Datos"
   uvicorn src.main:app --reload
   ```

2. **Luego inicia el frontend:**
   ```bash
   npm run dev
   ```

3. **Abre tu navegador** en `http://localhost:3000`

¡Disfruta tu proyecto final! 🎓
