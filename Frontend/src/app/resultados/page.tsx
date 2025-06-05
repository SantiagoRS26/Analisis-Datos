// app/(your-folder)/ResultadosPage.tsx
"use client";

import React from "react";
import {
	Card,
	CardContent,
	CardDescription,
	CardHeader,
	CardTitle,
} from "@/components/ui/card";
import { Download } from "lucide-react";
import WordBarChart, { WordEntry } from "@/components/TopWordsBarChart";
import TopicComparisonChart from "@/components/TopicComparisonChart";

import colombiaData from "@/api/wordcloud_colombia.json";
import worldData from "@/api/wordcloud_world.json";
import CreditsBoxPlot from "@/components/CreditsBoxPlot";

export default function ResultadosPage() {
	return (
		<div className="flex flex-col min-h-screen bg-gradient-to-br from-teal-500 to-blue-600 py-10">
			<section className="w-full max-w-4xl mx-auto space-y-8 px-4 md:px-0">
				<Card className="dark:bg-white text-gray-900 border-gray-200 rounded-2xl shadow">
					<CardHeader>
						<CardTitle className="text-2xl text-teal-700">
							Resultados de Nubes de Palabras
						</CardTitle>
						<CardDescription className="text-gray-600">
							Visualizaciones generadas para Colombia y el Mundo
						</CardDescription>
					</CardHeader>
				</Card>

				<div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
					<div className="space-y-4">
						<div className="bg-white rounded-lg shadow overflow-hidden">
							<img
								src="/col.png"
								alt="Nube de palabras en Colombia"
								className="w-full h-auto"
							/>
						</div>

						<a
							href="/col.png"
							download
							className="
                flex 
                items-center 
                justify-center 
                w-full 
                h-12 
                text-base 
                font-medium 
                border
                bg-green-100
                border-teal-600 
                text-teal-600 
                dark:text-teal-600 
                hover:bg-green-100 
                dark:hover:bg-green-100 
                rounded-lg 
                transition 
                duration-200
                focus:outline-none
                focus:ring-2 
                focus:ring-teal-500
              ">
							<Download className="w-4 h-4 mr-2" />
							Descargar Nube de Palabras – Colombia
						</a>
					</div>

					<div className="space-y-4">
						<div className="bg-white rounded-lg shadow overflow-hidden">
							<img
								src="/world.png"
								alt="Nube de palabras en el Mundo"
								className="w-full h-auto"
							/>
						</div>

						<a
							href="/world.png"
							download
							className="
                flex 
                items-center 
                justify-center 
                w-full 
                h-12 
                text-base 
                font-medium 
                border 
                bg-green-100
                border-teal-600 
                text-teal-600 
                dark:text-teal-600 
                hover:bg-green-100 
                dark:hover:bg-green-100 
                rounded-lg 
                transition 
                duration-200
                focus:outline-none
                focus:ring-2 
                focus:ring-teal-500
              ">
							<Download className="w-4 h-4 mr-2" />
							Descargar Nube de Palabras – Mundo
						</a>
					</div>
				</div>

				<div className="grid grid-cols-1 lg:grid-cols-2 gap-8 mt-8">
					<WordBarChart
						data={colombiaData as WordEntry[]}
						title="Top 20 Palabras más usadas – Colombia"
					/>

					<WordBarChart
						data={worldData as WordEntry[]}
						title="Top 20 Palabras más usadas – Mundo"
					/>
				</div>

				<div className="mt-8">
					<TopicComparisonChart />
				</div>
				<CreditsBoxPlot />
			</section>
		</div>
	);
}
