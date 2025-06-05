"use client";

import { useState } from "react";
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
	ExternalLink,
	Download,
	RefreshCw,
} from "lucide-react";

export default function Home() {
	// Estado para mostrar/ocultar la tarjeta con animación
	const [showCard, setShowCard] = useState(false); // <<<

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

	const scrollToForm = () => {
		const el = document.getElementById("form-card");
		if (el) {
			el.scrollIntoView({ behavior: "smooth", block: "start" });
		}
	};

	const handleStartClick = () => {
		setShowCard(true);
		setTimeout(scrollToForm, 50);
	};

	return (
		<div className="flex flex-col min-h-screen bg-gradient-to-br from-teal-500 to-blue-600">
			{/* ==================== HERO SECTION ==================== */}
			<header className="flex flex-col items-center justify-center text-center px-4 py-20 lg:py-32">
				<div className="w-20 h-20 flex items-center justify-center bg-white/20 backdrop-blur-lg rounded-full mb-6">
					<BarChart3 className="w-10 h-10 text-white opacity-90" />
				</div>

				<h1 className="text-5xl md:text-6xl font-extrabold text-white mb-4 drop-shadow-md">
					Analizador de Datos Universitarios
				</h1>
				<p className="max-w-2xl text-lg md:text-xl text-white/90 mb-8">
					Extrae información de sitios web universitarios y genera
					visualizaciones inteligentes
				</p>

				<Button
					size="lg"
					onClick={handleStartClick}
					className="bg-white text-teal-600 hover:bg-white/90 shadow-lg transition duration-300">
					Comenzar Análisis
				</Button>
			</header>

			<section
				id="form-card"
				className={`w-full flex justify-center px-4 -mt-4 pb-12
          transition-all duration-500 ease-in-out
          ${
						showCard
							? "opacity-100 translate-y-0"
							: "opacity-0 -translate-y-4 pointer-events-none"
					}`}>
				<Card
					className="
          w-full max-w-3xl
          bg-white dark:bg-white
          text-gray-900 dark:text-gray-900
          border-gray-200 dark:border-gray-200
          rounded-2xl shadow-2xl
        ">
					<CardHeader className="pt-6 pb-4 px-6">
						<CardTitle className="flex items-center gap-3 text-2xl text-teal-700">
							<ExternalLink className="w-6 h-6 text-teal-600" />
							Configuración del Análisis
						</CardTitle>
						<CardDescription className="text-gray-600">
							Ingresa la URL y la información adicional para procesar el
							contenido
						</CardDescription>
					</CardHeader>

					<CardContent className="px-6 pb-6">
						<form
							onSubmit={handleSubmit}
							className="space-y-6">
							<div className="space-y-2">
								<Label
									htmlFor="url"
									className="text-sm font-medium text-gray-800">
									URL a analizar <span className="text-red-500">*</span>
								</Label>
								<Input
									id="url"
									type="url"
									placeholder="https://ejemplo.com/pagina-universidad"
									value={url}
									onChange={(e) => setUrl(e.target.value)}
									required
									className="h-12 text-gray-900 placeholder-gray-400 focus:border-teal-500 focus:ring-teal-200"
								/>
							</div>

							<div className="grid grid-cols-1 md:grid-cols-2 gap-6">
								<div className="space-y-2">
									<Label
										htmlFor="university"
										className="text-sm font-medium text-gray-800">
										Universidad (opcional)
									</Label>
									<Input
										id="university"
										placeholder="Ej: Universidad Nacional"
										value={university}
										onChange={(e) => setUniversity(e.target.value)}
										className="h-12 text-gray-900 placeholder-gray-400 focus:border-teal-500 focus:ring-teal-200"
									/>
								</div>

								<div className="space-y-2">
									<Label
										htmlFor="program"
										className="text-sm font-medium text-gray-800">
										Programa (opcional)
									</Label>
									<Input
										id="program"
										placeholder="Ej: Ingeniería de Sistemas"
										value={program}
										onChange={(e) => setProgram(e.target.value)}
										className="h-12 text-gray-900 placeholder-gray-400 focus:border-teal-500 focus:ring-teal-200"
									/>
								</div>
							</div>

							<div className="flex items-center gap-3 px-4 py-3 bg-gray-100 rounded-lg">
								<input
									type="checkbox"
									id="force"
									checked={force}
									onChange={(e) => setForce(e.target.checked)}
									className="w-4 h-4 text-teal-600 border-gray-300 rounded focus:ring-teal-500"
								/>
								<Label
									htmlFor="force"
									className="text-sm text-gray-700">
									Forzar re-descarga del contenido
								</Label>
							</div>

							<div className="flex flex-col md:flex-row items-center gap-4 pt-4">
								<Button
									type="submit"
									disabled={isLoading || !url.trim()}
									className="flex-1 h-12 text-base font-semibold bg-teal-600 hover:bg-teal-700 text-white shadow transition duration-300">
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
										className="flex-1 h-12 text-base font-medium border-teal-600 text-teal-600 hover:bg-teal-50 transition duration-300">
										<RefreshCw className="w-4 h-4 mr-2" />
										Nuevo
									</Button>
								)}
							</div>
						</form>
					</CardContent>
				</Card>
			</section>

			{isLoading && (
				<div className="w-full max-w-3xl mx-auto mt-8 text-center">
					<StatusBadge status="loading">
						Procesando contenido y generando visualizaciones...
					</StatusBadge>
				</div>
			)}

			{error && (
				<Card
					className="
          w-full max-w-3xl mx-auto mt-6
          bg-red-50 dark:bg-red-50
          text-red-700 dark:text-red-700
          border-red-300 dark:border-red-300
          rounded-lg shadow
        ">
					<CardHeader>
						<CardTitle className="flex items-center gap-2 text-red-700">
							<StatusBadge status="error">
								Error en el procesamiento
							</StatusBadge>
						</CardTitle>
					</CardHeader>
					<CardContent className="pb-6">
						<p className="text-red-600 text-base">{error}</p>
					</CardContent>
				</Card>
			)}

			{result && (
				<section className="w-full max-w-4xl mx-auto mt-10 space-y-8 px-4 md:px-0">
					<Card
						className="
            bg-green-50 dark:bg-green-50
            text-green-700 dark:text-green-700
            border-green-200 dark:border-green-200
            rounded-lg shadow
          ">
						<CardHeader>
							<CardTitle className="flex items-center justify-between">
								<StatusBadge status="success">
									Análisis Completado Exitosamente
								</StatusBadge>
								<span className="text-sm font-normal">
									{result.rows} registros procesados
								</span>
							</CardTitle>
							<CardDescription className="text-green-600">
								Se han generado visualizaciones que puedes descargar.
							</CardDescription>
						</CardHeader>
					</Card>

					<div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
						<div className="space-y-4">
							<ImageDisplay
								title="Gráfico de Barras"
								description="Visualización de frecuencias"
								base64Image={result.bar_png}
								altText="Gráfico de barras"
							/>
							<Button
								onClick={() =>
									downloadImage(result.bar_png, "grafico_barras.png")
								}
								variant="outline"
								className="w-full hover:bg-green-100 transition duration-200">
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
								onClick={() =>
									downloadImage(result.cloud_png, "nube_palabras.png")
								}
								variant="outline"
								className="w-full hover:bg-green-100 transition duration-200">
								<Download className="w-4 h-4 mr-2" />
								Descargar Nube de Palabras
							</Button>
						</div>
					</div>
				</section>
			)}
		</div>
	);
}
