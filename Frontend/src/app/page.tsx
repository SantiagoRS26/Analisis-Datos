'use client';

import { useState } from "react";
import Image from "next/image";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { ImageDisplay } from "@/components/ImageDisplay";
import { StatusBadge } from "@/components/StatusBadge";
import { useAnalyzeUrl } from "@/hooks/useAnalyzeUrl";
import {
  Loader2,
  BarChart3,
  Cloud,
  ExternalLink,
  Download,
  RefreshCw,
} from "lucide-react";

export default function Home() {
  const [url, setUrl] = useState("");
  const [university, setUniversity] = useState("");
  const [program, setProgram] = useState("");
  const [force, setForce] = useState(false);

  const { analyzeUrl, isLoading, result, error, reset } = useAnalyzeUrl();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!url.trim()) return;

    await analyzeUrl({
      url: url.trim(),
      university: university.trim() || undefined,
      program: program.trim() || undefined,
      force,
    });
  };

  const handleReset = () => {
    setUrl("");
    setUniversity("");
    setProgram("");
    setForce(false);
    reset();
  };

  const downloadImage = (base64Data: string, filename: string) => {
    const link = document.createElement("a");
    link.href = `data:image/png;base64,${base64Data}`;
    link.download = filename;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-indigo-50 to-purple-50 dark:from-gray-900 dark:via-blue-900/20 dark:to-purple-900/20">
      <div className="container mx-auto px-4 py-8">
        {/* Header */}
        <div className="text-center mb-12">
          <div className="inline-flex items-center justify-center w-16 h-16 bg-blue-100 rounded-full mb-4 dark:bg-blue-900/30">
            <BarChart3 className="w-8 h-8 text-blue-600 dark:text-blue-400" />
          </div>
          <h1 className="text-5xl font-bold text-gray-900 dark:text-white mb-4 bg-clip-text text-transparent bg-gradient-to-r from-blue-600 to-purple-600">
            Analizador de Datos Universitarios
          </h1>
          <p className="text-xl text-gray-600 dark:text-gray-300 max-w-2xl mx-auto">
            Analiza contenido web para extraer información universitaria y generar visualizaciones inteligentes
          </p>
        </div>

        {/* Form Card */}
        <Card className="max-w-3xl mx-auto mb-8 shadow-xl border-0 bg-white/80 backdrop-blur-sm dark:bg-gray-900/80">
          <CardHeader className="pb-6">
            <CardTitle className="flex items-center gap-3 text-2xl">
              <ExternalLink className="w-6 h-6 text-blue-600" />
              Configuración del Análisis
            </CardTitle>
            <CardDescription className="text-base">
              Ingresa la URL y la información adicional para procesar el contenido
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-6">
            <form onSubmit={handleSubmit} className="space-y-6">
              <div className="space-y-3">
                <Label htmlFor="url">URL a analizar *</Label>
                <Input
                  id="url"
                  type="url"
                  placeholder="https://ejemplo.com/pagina-universidad"
                  value={url}
                  onChange={(e) => setUrl(e.target.value)}
                  required
                  className="h-12 text-black"
                />
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div className="space-y-3">
                  <Label htmlFor="university">Universidad (opcional)</Label>
                  <Input
                    id="university"
                    placeholder="Ej: Universidad Nacional"
                    value={university}
                    onChange={(e) => setUniversity(e.target.value)}
                    className="h-12 text-black"
                  />
                </div>

                <div className="space-y-3">
                  <Label htmlFor="program">Programa (opcional)</Label>
                  <Input
                    id="program"
                    placeholder="Ej: Ingeniería de Sistemas"
                    value={program}
                    onChange={(e) => setProgram(e.target.value)}
                    className="h-12 text-black"
                  />
                </div>
              </div>

              <div className="flex items-center space-x-3 p-4 bg-gray-50 rounded-lg dark:bg-gray-800">
                <input
                  type="checkbox"
                  id="force"
                  checked={force}
                  onChange={(e) => setForce(e.target.checked)}
                  className="w-4 h-4 rounded border-gray-300 text-blue-600 focus:ring-blue-500"
                />
                <Label htmlFor="force" className="text-base">
                  Forzar re-descarga del contenido
                </Label>
              </div>

              <div className="flex gap-3 pt-4">
                <Button
                  type="submit"
                  disabled={isLoading || !url.trim()}
                  className="flex-1 h-12 text-base font-medium"
                >
                  {isLoading ? (
                    <>
                      <Loader2 className="w-5 h-5 mr-2 animate-spin" />
                      Procesando...
                    </>
                  ) : (
                    <>
                      <BarChart3 className="w-5 h-5 mr-2" />
                      Analizar URL
                    </>
                  )}
                </Button>

                {(result || error) && (
                  <Button
                    type="button"
                    variant="outline"
                    onClick={handleReset}
                    className="h-12 px-6"
                  >
                    <RefreshCw className="w-4 h-4 mr-2" />
                    Nuevo
                  </Button>
                )}
              </div>
            </form>
          </CardContent>
        </Card>

        {/* Loading */}
        {isLoading && (
          <div className="max-w-3xl mx-auto mb-8 text-center">
            <StatusBadge status="loading">
              Procesando contenido y generando visualizaciones...
            </StatusBadge>
          </div>
        )}

        {/* Error */}
        {error && (
          <Card className="max-w-3xl mx-auto mb-8 border-red-200 bg-red-50/80 backdrop-blur-sm dark:border-red-800 dark:bg-red-900/20">
            <CardHeader>
              <CardTitle className="text-red-700 dark:text-red-400 flex items-center gap-2">
                <StatusBadge status="error">Error en el procesamiento</StatusBadge>
              </CardTitle>
            </CardHeader>
            <CardContent>
              <p className="text-red-600 dark:text-red-300 text-base">{error}</p>
            </CardContent>
          </Card>
        )}

        {/* Result */}
        {result && (
          <div className="space-y-8">
            <Card className="max-w-3xl mx-auto bg-green-50/80 backdrop-blur-sm border-green-200 dark:bg-green-900/20 dark:border-green-800">
              <CardHeader>
                <CardTitle className="text-green-700 dark:text-green-400 flex items-center justify-between">
                  <StatusBadge status="success">
                    Análisis Completado Exitosamente
                  </StatusBadge>
                  <span className="text-sm font-normal">
                    {result.rows} registros procesados
                  </span>
                </CardTitle>
                <CardDescription className="text-green-600 dark:text-green-300 text-base">
                  Se han generado visualizaciones que puedes descargar.
                </CardDescription>
              </CardHeader>
            </Card>

            <div className="grid grid-cols-1 xl:grid-cols-2 gap-8">
              <div className="space-y-4">
                <ImageDisplay
                  title="Gráfico de Barras"
                  description="Visualización de frecuencias"
                  base64Image={result.bar_png}
                  altText="Gráfico de barras"
                />
                <Button
                  onClick={() => downloadImage(result.bar_png, 'grafico_barras.png')}
                  variant="outline"
                  className="w-full"
                >
                  <Download className="w-4 h-4 mr-2" />
                  Descargar Gráfico de Barras
                </Button>
              </div>

              <div className="space-y-4">
                <ImageDisplay
                  title="Nube de Palabras"
                  description="Palabras más frecuentes"
                  base64Image={result.cloud_png}
                  altText="Nube de palabras"
                />
                <Button
                  onClick={() => downloadImage(result.cloud_png, 'nube_palabras.png')}
                  variant="outline"
                  className="w-full"
                >
                  <Download className="w-4 h-4 mr-2" />
                  Descargar Nube de Palabras
                </Button>
              </div>
            </div>
          </div>
        )}

        {/* Footer */}
        <footer className="text-center mt-16 text-gray-500 dark:text-gray-400">
          <p className="text-sm">
            Proyecto Final - Computación 3 | Análisis Inteligente de Datos Universitarios
          </p>
        </footer>
      </div>
    </div>
  );
}
