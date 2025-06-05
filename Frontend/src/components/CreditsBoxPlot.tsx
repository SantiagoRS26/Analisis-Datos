"use client";

import React, { useMemo } from "react";
import { ResponsiveBoxPlot } from "@nivo/boxplot";
import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/card";

import rawCredits from "@/api/credits_by_region.json";

interface RegionRaw {
	region: string;
	credits: number[];
}

interface CreditRow {
	group: string;
	subgroup: string;
	value: number;
	[extra: string]: string | number;
}
// ---------------------------------------

const CreditsBoxPlot: React.FC = () => {
	const rows: CreditRow[] = useMemo(() => {
		const data = rawCredits as RegionRaw[];
		return data.flatMap((r) =>
			r.credits.map<CreditRow>((v) => ({
				group: r.region,
				subgroup: "credits",
				value: v,
			}))
		);
	}, []);

	const maxValueReal = useMemo(
		() => Math.max(...rows.map((d) => d.value)),
		[rows]
	);
	const minValueReal = useMemo(
		() => Math.min(...rows.map((d) => d.value)),
		[rows]
	);

	const nivoTheme = {
		axis: {
			ticks: {
				line: { stroke: "#cbd5e0", strokeWidth: 1 },
				text: { fill: "#4b5563", fontSize: 12 },
			},
		},
		grid: {
			line: { stroke: "#e5e7eb", strokeWidth: 1, strokeDasharray: "3 3" },
		},
		tooltip: {
			container: {
				background: "#f9fafb",
				color: "#1f2937",
				fontSize: 12,
				borderRadius: 4,
				boxShadow: "0 2px 4px rgba(0,0,0,0.1)",
			},
		},
	} as const;

	return (
		<Card className="bg-white dark:bg-white border-gray-200 dark:border-gray-200 rounded-xl shadow-lg">
			<CardHeader className="px-6 pt-6 pb-2">
				<CardTitle className="text-xl text-teal-600 dark:text-teal-600 font-semibold">
					Comparación de Créditos por Región&nbsp;(Box Plot)
				</CardTitle>
			</CardHeader>

			<CardContent className="px-6 pb-6">
				<div className="w-full h-80">
					<ResponsiveBoxPlot
						data={rows}
						groupBy="group"
						subGroupBy="subgroup"
						margin={{ top: 20, right: 20, bottom: 60, left: 80 }}
						minValue={minValueReal}
						maxValue={maxValueReal}
						colors={["#14b8a6", "#60a5fa"]}
						padding={0.6}
						axisLeft={{
							tickSize: 5,
							tickPadding: 5,
							legend: "Región",
							legendPosition: "middle",
							legendOffset: -60,
						}}
						axisBottom={{
							tickSize: 5,
							tickPadding: 5,
							legend: "Créditos",
							legendPosition: "middle",
							legendOffset: 40,
						}}
						valueFormat=">-.2~f"
						theme={nivoTheme as any}
						motionConfig="gentle"
					/>
				</div>
			</CardContent>
		</Card>
	);
};

export default CreditsBoxPlot;
