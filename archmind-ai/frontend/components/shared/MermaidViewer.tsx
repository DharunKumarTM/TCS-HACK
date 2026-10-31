"use client";

import { useEffect, useRef, useState } from "react";
import mermaid from "mermaid";
import { Copy, Check, ZoomIn, ZoomOut, Maximize2, Minimize2, Code2 } from "lucide-react";

interface MermaidViewerProps {
  chart: string;
  title?: string;
}

export function MermaidViewer({ chart, title }: MermaidViewerProps) {
  const containerRef = useRef<HTMLDivElement>(null);
  const [svgContent, setSvgContent] = useState<string>("");
  const [zoom, setZoom] = useState<number>(1);
  const [isFullscreen, setIsFullscreen] = useState<boolean>(false);
  const [copied, setCopied] = useState<boolean>(false);
  const [showSource, setShowSource] = useState<boolean>(false);

  useEffect(() => {
    mermaid.initialize({
      startOnLoad: false,
      theme: "dark",
      themeVariables: {
        darkMode: true,
        background: "#0b1329",
        primaryColor: "#1d4ed8",
        primaryTextColor: "#f8fafc",
        primaryBorderColor: "#38bdf8",
        lineColor: "#38bdf8",
        secondaryColor: "#0284c7",
        tertiaryColor: "#0f172a",
        fontFamily: "Inter, sans-serif",
        fontSize: "12px",
      },
      securityLevel: "loose",
    });

    let isMounted = true;
    const renderDiagram = async () => {
      if (!chart) return;
      try {
        const id = `mermaid-${Math.random().toString(36).substr(2, 9)}`;
        const { svg } = await mermaid.render(id, chart);
        if (isMounted) {
          setSvgContent(svg);
        }
      } catch (err) {
        console.error("Mermaid rendering error:", err);
      }
    };

    renderDiagram();
    return () => {
      isMounted = false;
    };
  }, [chart]);

  const handleCopy = () => {
    navigator.clipboard.writeText(chart);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  return (
    <div
      className={`border border-[#1e293b] rounded-xl bg-[#0a0f1d] overflow-hidden flex flex-col transition-all ${
        isFullscreen ? "fixed inset-4 z-50 shadow-2xl bg-[#070b14]" : "h-full min-h-[460px]"
      }`}
    >
      {/* Top Controls Bar */}
      <div className="flex items-center justify-between px-4 py-2.5 bg-[#0f172a] border-b border-[#1e293b]">
        <div className="flex items-center space-x-2">
          <span className="w-2 h-2 rounded-full bg-cyan-400"></span>
          <span className="text-xs font-semibold text-slate-200">{title || "Architecture Diagram"}</span>
        </div>

        <div className="flex items-center space-x-1.5">
          <button
            onClick={() => setZoom((z) => Math.min(z + 0.15, 2.5))}
            className="p-1.5 rounded-lg bg-[#1e293b] text-slate-300 hover:text-white hover:bg-slate-700 transition"
            title="Zoom In"
          >
            <ZoomIn className="w-3.5 h-3.5" />
          </button>
          <button
            onClick={() => setZoom((z) => Math.max(z - 0.15, 0.4))}
            className="p-1.5 rounded-lg bg-[#1e293b] text-slate-300 hover:text-white hover:bg-slate-700 transition"
            title="Zoom Out"
          >
            <ZoomOut className="w-3.5 h-3.5" />
          </button>
          <button
            onClick={() => setZoom(1)}
            className="px-2 py-1 text-[10px] font-mono rounded-lg bg-[#1e293b] text-slate-300 hover:text-white hover:bg-slate-700 transition"
            title="Reset Zoom"
          >
            {Math.round(zoom * 100)}%
          </button>
          <div className="w-px h-4 bg-slate-700 mx-1"></div>
          <button
            onClick={() => setShowSource(!showSource)}
            className={`p-1.5 rounded-lg text-slate-300 hover:text-white transition ${
              showSource ? "bg-cyan-600 text-white" : "bg-[#1e293b] hover:bg-slate-700"
            }`}
            title="Toggle Source Code"
          >
            <Code2 className="w-3.5 h-3.5" />
          </button>
          <button
            onClick={handleCopy}
            className="p-1.5 rounded-lg bg-[#1e293b] text-slate-300 hover:text-white hover:bg-slate-700 transition"
            title="Copy Mermaid Code"
          >
            {copied ? <Check className="w-3.5 h-3.5 text-emerald-400" /> : <Copy className="w-3.5 h-3.5" />}
          </button>
          <button
            onClick={() => setIsFullscreen(!isFullscreen)}
            className="p-1.5 rounded-lg bg-[#1e293b] text-slate-300 hover:text-white hover:bg-slate-700 transition"
            title={isFullscreen ? "Exit Fullscreen" : "Fullscreen"}
          >
            {isFullscreen ? <Minimize2 className="w-3.5 h-3.5" /> : <Maximize2 className="w-3.5 h-3.5" />}
          </button>
        </div>
      </div>

      {/* Main Diagram Area */}
      <div className="flex-1 relative overflow-auto p-4 flex items-center justify-center bg-[#070b14]/70">
        {showSource ? (
          <div className="w-full h-full p-4 overflow-auto font-mono text-xs text-cyan-300 bg-[#060a12] rounded-lg border border-[#1e293b] whitespace-pre">
            {chart}
          </div>
        ) : (
          <div
            ref={containerRef}
            style={{ transform: `scale(${zoom})`, transformOrigin: "center center", transition: "transform 0.15s ease-out" }}
            dangerouslySetInnerHTML={{ __html: svgContent }}
            className="w-full h-full flex items-center justify-center [&>svg]:max-w-full [&>svg]:max-h-full select-none"
          />
        )}
      </div>
    </div>
  );
}

