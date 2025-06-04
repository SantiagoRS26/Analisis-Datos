import { useState } from 'react';

interface AnalysisParams {
  url: string;
  university?: string;
  program?: string;
  force?: boolean;
}

interface AnalysisResult {
  status: string;
  bar_png: string;
  cloud_png: string;
  rows: number;
}

interface AnalysisError {
  detail: string;
}

export const useAnalyzeUrl = () => {
  const [isLoading, setIsLoading] = useState(false);
  const [result, setResult] = useState<AnalysisResult | null>(null);
  const [error, setError] = useState<string | null>(null);

  const analyzeUrl = async (params: AnalysisParams) => {
    setIsLoading(true);
    setError(null);
    setResult(null);

    try {
      const response = await fetch('http://localhost:8000/analyze_url', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          url: params.url,
          university: params.university || 'N/A',
          program: params.program || 'N/A',
          force: params.force || false,
        }),
      });

      if (!response.ok) {
        const errorData: AnalysisError = await response.json();
        throw new Error(errorData.detail || `HTTP error! status: ${response.status}`);
      }

      const data: AnalysisResult = await response.json();
      setResult(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'An unexpected error occurred');
    } finally {
      setIsLoading(false);
    }
  };

  return {
    analyzeUrl,
    isLoading,
    result,
    error,
    reset: () => {
      setResult(null);
      setError(null);
    }
  };
};
