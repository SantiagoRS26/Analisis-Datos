// components/TopWordsBarChart.tsx
"use client";

import React from "react";
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  Tooltip,
  CartesianGrid,
  ResponsiveContainer,
} from "recharts";
import {
  Card,
  CardHeader,
  CardTitle,
  CardContent,
} from "@/components/ui/card";

export interface WordEntry {
  text: string;
  value: number;
}

interface TopWordsBarChartProps {
  data: WordEntry[];
  title: string;
}

const TopWordsBarChart: React.FC<TopWordsBarChartProps> = ({
  data,
  title,
}) => {
  // Ordenar descendente y tomar únicamente las 20 primeras entradas
  const topTwenty = [...data]
    .sort((a, b) => b.value - a.value)
    .slice(0, 20);

  return (
    <Card className="bg-white dark:bg-white border-gray-200 dark:border-gray-200 rounded-xl shadow-lg">
      <CardHeader className="px-6 pt-6 pb-2">
        <CardTitle className="text-xl text-teal-600 dark:text-teal-600 font-semibold">
          {title}
        </CardTitle>
      </CardHeader>

      <CardContent className="px-6 pb-6">
        {/* 
          Definimos todas las variables CSS con el mismo valor
          en light y dark para forzar tonos claros siempre.
        */}
        <div
          className="
            w-full h-80
            [--grid-stroke:#e5e7eb] dark:[--grid-stroke:#e5e7eb]
            [--tick-color:#4b5563] dark:[--tick-color:#4b5563]
            [--tooltip-bg:#f9fafb] dark:[--tooltip-bg:#f9fafb]
            [--item-color:#1f2937] dark:[--item-color:#1f2937]
            [--cursor-fill:rgba(20,184,166,0.1)] dark:[--cursor-fill:rgba(20,184,166,0.1)]
            [--bar-fill:#14b8a6] dark:[--bar-fill:#14b8a6]
          "
        >
          <ResponsiveContainer width="100%" height="100%">
            <BarChart
              data={topTwenty}
              margin={{ top: 10, right: 20, left: 0, bottom: 50 }}
            >
              <CartesianGrid
                strokeDasharray="3 3"
                stroke="var(--grid-stroke)"
              />
              <XAxis
                dataKey="text"
                angle={-45}
                textAnchor="end"
                interval={0}
                height={60}
                tick={{ fill: "var(--tick-color)", fontSize: 12 }}
              />
              <YAxis tick={{ fill: "var(--tick-color)", fontSize: 12 }} />
              <Tooltip
                contentStyle={{
                  backgroundColor: "var(--tooltip-bg)",
                  border: "none",
                  borderRadius: "4px",
                  boxShadow: "0 2px 4px rgba(0,0,0,0.1)",
                }}
                itemStyle={{ color: "var(--item-color)" }}
                cursor={{ fill: "var(--cursor-fill)" }}
              />
              <Bar
                dataKey="value"
                name="Frecuencia"
                fill="var(--bar-fill)"
                radius={[4, 4, 0, 0]}
              />
            </BarChart>
          </ResponsiveContainer>
        </div>
      </CardContent>
    </Card>
  );
};

export default TopWordsBarChart;
