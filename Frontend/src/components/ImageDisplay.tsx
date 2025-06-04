import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "./ui/card";

interface ImageDisplayProps {
  title: string;
  description: string;
  base64Image: string;
  altText: string;
}

export function ImageDisplay({ title, description, base64Image, altText }: ImageDisplayProps) {
  return (
    <Card className="w-full shadow-lg border-0 bg-white/80 backdrop-blur-sm dark:bg-gray-900/80 overflow-hidden">
      <CardHeader className="pb-4">
        <CardTitle className="text-xl font-semibold">{title}</CardTitle>
        <CardDescription className="text-base">{description}</CardDescription>
      </CardHeader>
      <CardContent className="p-0">
        <div className="relative overflow-hidden bg-gray-50 dark:bg-gray-800">
          <img
            src={`data:image/png;base64,${base64Image}`}
            alt={altText}
            className="w-full h-auto transition-transform duration-300 hover:scale-105"
          />
          <div className="absolute inset-0 bg-gradient-to-t from-black/10 to-transparent opacity-0 hover:opacity-100 transition-opacity duration-300" />
        </div>
      </CardContent>
    </Card>
  );
}
