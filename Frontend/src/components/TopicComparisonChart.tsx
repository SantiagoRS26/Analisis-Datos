// components/TopicComparisonChart.tsx
"use client";

import React from "react";
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  Tooltip,
  CartesianGrid,
  Legend,
  ResponsiveContainer,
} from "recharts";
import {
  Card,
  CardHeader,
  CardTitle,
  CardContent,
} from "@/components/ui/card";
import distributionData from "@/api/topic_distribution_by_region.json";
import ldaData from "@/api/lda_topics_keywords.json";

interface RegionDist {
  region: string;
  [key: string]: number | string;
}

interface LdaTopic {
  topic: number;
  keywords: string[];
}

const TopicComparisonChart: React.FC = () => {
  const regions = distributionData as RegionDist[];
  const ldaTopics = ldaData as LdaTopic[];

  // Mapeo rápido: "0" → ["systems", "computer", …], "1" → […], etc.
  const keywordsMap: Record<string, string[]> = {};
  ldaTopics.forEach((t) => {
    keywordsMap[String(t.topic)] = t.keywords;
  });

  // Extraigo todas las claves que no sean "region" (serie de topics: "0", "1", …)
  const topicKeys = Object.keys(regions[0]).filter((key) => key !== "region");

  // Armo chartData: para cada topicKey, saco los valores de Colombia y World,
  // y agrego también el arreglo de keywords, para usarlo luego en el tooltip o listado.
  const chartData = topicKeys.map((topicKey) => {
    const colombiaVal = Number(
      regions.find((r) => r.region === "Colombia")?.[topicKey]
    );
    const worldVal = Number(
      regions.find((r) => r.region === "World")?.[topicKey]
    );
    return {
      topic: `Topic ${topicKey}`,
      Colombia: colombiaVal,
      World: worldVal,
      keywords: keywordsMap[topicKey] || [],
    };
  });

  // Renderizo el componente
  return (
    <Card className="bg-white dark:bg-white border-gray-200 dark:border-gray-200 rounded-xl shadow-lg">
      <CardHeader className="px-6 pt-6 pb-2">
        <CardTitle className="text-xl text-teal-600 dark:text-teal-600 font-semibold">
          Distribución de Temas por Región
        </CardTitle>
      </CardHeader>
      <CardContent className="px-6 pb-6 space-y-6">
        {/* Bloque del gráfico de barras */}
        <div
          className="
            w-full h-80
            [--grid-stroke:#e5e7eb] dark:[--grid-stroke:#e5e7eb]
            [--tick-color:#4b5563] dark:[--tick-color:#4b5563]
            [--tooltip-bg:#f9fafb] dark:[--tooltip-bg:#f9fafb]
            [--item-color:#1f2937] dark:[--item-color:#1f2937]
            [--cursor-fill:rgba(20,184,166,0.1)] dark:[--cursor-fill:rgba(20,184,166,0.1)]
            [--bar-colombia:#14b8a6] dark:[--bar-colombia:#14b8a6]
            [--bar-world:#60a5fa] dark:[--bar-world:#60a5fa]
          "
        >
          <ResponsiveContainer width="100%" height="100%">
            <BarChart
              data={chartData}
              margin={{ top: 10, right: 20, left: 0, bottom: 50 }}
            >
              <CartesianGrid
                strokeDasharray="3 3"
                stroke="var(--grid-stroke)"
              />
              <XAxis
                dataKey="topic"
                angle={-45}
                textAnchor="end"
                interval={0}
                height={60}
                tick={{ fill: "var(--tick-color)", fontSize: 12 }}
              />
              <YAxis tick={{ fill: "var(--tick-color)", fontSize: 12 }} />
              <Tooltip
                content={(props) => {
                  // Custom tooltip: muestro región y valor + keywords del topic
                  if (!props.active || !props.payload) return null;
                  const { payload } = props;
                  // payload es un arreglo con dos objetos (Colombia y World)
                  const entryCol = payload.find((p) => p.dataKey === "Colombia");
                  const entryWld = payload.find((p) => p.dataKey === "World");
                  // topicLabel en formato "Topic X"
                  const topicLabel = payload[0]?.payload.topic || "";
                  const topicKey = topicLabel.replace("Topic ", "");
                  const kws = keywordsMap[topicKey] || [];

                  return (
                    <div
                      style={{
                        backgroundColor: "var(--tooltip-bg)",
                        padding: "8px",
                        borderRadius: "4px",
                        boxShadow: "0 2px 4px rgba(0,0,0,0.1)",
                      }}
                    >
                      <p
                        style={{
                          margin: 0,
                          fontWeight: 600,
                          color: "var(--item-color)",
                        }}
                      >
                        {topicLabel}
                      </p>
                      {entryCol && (
                        <p style={{ margin: "4px 0", color: "var(--item-color)" }}>
                          Colombia: {entryCol.value}
                        </p>
                      )}
                      {entryWld && (
                        <p style={{ margin: "4px 0", color: "var(--item-color)" }}>
                          World: {entryWld.value}
                        </p>
                      )}
                      {kws.length > 0 && (
                        <div style={{ marginTop: "6px" }}>
                          <p
                            style={{
                              margin: 0,
                              fontSize: 12,
                              fontWeight: 500,
                              color: "var(--item-color)",
                            }}
                          >
                            Keywords:
                          </p>
                          <ul style={{ margin: "2px 0 0 12px" }}>
                            {kws.map((kw) => (
                              <li
                                key={kw}
                                style={{
                                  fontSize: 12,
                                  color: "var(--item-color)",
                                }}
                              >
                                {kw}
                              </li>
                            ))}
                          </ul>
                        </div>
                      )}
                    </div>
                  );
                }}
                wrapperStyle={{ outline: "none" }}
                cursor={{ fill: "var(--cursor-fill)" }}
              />
              <Legend wrapperStyle={{ color: "#4b5563", fontSize: 12 }} />
              <Bar
                dataKey="Colombia"
                name="Colombia"
                fill="var(--bar-colombia)"
                radius={[4, 4, 0, 0]}
              />
              <Bar
                dataKey="World"
                name="World"
                fill="var(--bar-world)"
                radius={[4, 4, 0, 0]}
              />
            </BarChart>
          </ResponsiveContainer>
        </div>

        {/* Bloque de listado de keywords por tema (para referencia rápida) */}
        <div>
          <h3 className="text-lg text-teal-600 dark:text-teal-600 font-semibold mb-2">
            Palabras clave por Tema
          </h3>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {ldaTopics.map((t) => (
              <div
                key={t.topic}
                className="bg-white dark:bg-white border border-gray-200 dark:border-gray-200 rounded-lg p-4"
              >
                <p className="text-sm font-medium text-gray-700 dark:text-gray-700 mb-1">
                  Tema {t.topic}
                </p>
                <ul className="list-disc list-inside text-sm text-gray-600 dark:text-gray-600">
                  {t.keywords.map((kw) => (
                    <li key={kw}>{kw}</li>
                  ))}
                </ul>
              </div>
            ))}
          </div>
        </div>
      </CardContent>
    </Card>
  );
};

export default TopicComparisonChart;
