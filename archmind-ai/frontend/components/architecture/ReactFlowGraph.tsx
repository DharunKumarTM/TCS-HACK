"use client";

import { useMemo, useState } from "react";
import ReactFlow, {
  Background,
  Controls,
  MiniMap,
  Node,
  Edge,
  MarkerType,
} from "reactflow";
import "reactflow/dist/style.css";
import { ArchitectureComponent } from "@/types";
import { Shield, Server, ArrowRight, X, Cpu } from "lucide-react";

interface ReactFlowGraphProps {
  components: ArchitectureComponent[];
}

export function ReactFlowGraph({ components }: ReactFlowGraphProps) {
  const [selectedComponent, setSelectedComponent] = useState<ArchitectureComponent | null>(null);

  // Layout components across tiers
  const { nodes, edges } = useMemo(() => {
    const layerPositions: Record<string, { x: number; y: number }> = {
      "API Gateway & Edge": { x: 50, y: 50 },
      "Security & Identity": { x: 420, y: 50 },
      "Data Caching Layer": { x: 790, y: 50 },
      "Core Business Domain": { x: 230, y: 260 },
      "Core Banking System": { x: 620, y: 260 },
      "Security & Cryptography": { x: 230, y: 470 },
      "Compliance & Audit": { x: 620, y: 470 },
    };

    let defaultY = 600;
    const computedNodes: Node[] = components.map((c, i) => {
      const pos = layerPositions[c.layer] || { x: 100 + (i % 3) * 350, y: defaultY };
      if (!layerPositions[c.layer]) defaultY += 150;

      return {
        id: c.component_code,
        position: pos,
        data: {
          component: c,
          label: (
            <div className="p-3 text-left">
              <div className="flex items-center justify-between mb-1">
                <span className="text-[10px] font-mono px-1.5 py-0.5 rounded bg-cyan-950 text-cyan-400 border border-cyan-800">
                  {c.component_code}
                </span>
                <span className="text-[10px] text-slate-400 font-sans">{c.layer}</span>
              </div>
              <div className="text-xs font-bold text-white mb-1 tracking-tight">{c.name}</div>
              <div className="text-[10px] text-slate-300 font-mono truncate max-w-[200px]">
                {c.technology_stack}
              </div>
            </div>
          ),
        },
        style: {
          background: "#0f172a",
          color: "#fff",
          border: "1px solid #334155",
          borderRadius: "10px",
          width: 240,
          boxShadow: "0 8px 20px rgba(0,0,0,0.4)",
        },
      };
    });

    const computedEdges: Edge[] = [];
    components.forEach((c) => {
      (c.dependencies || []).forEach((depCode) => {
        computedEdges.push({
          id: `e-${c.component_code}-${depCode}`,
          source: c.component_code,
          target: depCode,
          animated: true,
          style: { stroke: "#38bdf8", strokeWidth: 1.5 },
          markerEnd: {
            type: MarkerType.ArrowClosed,
            color: "#38bdf8",
          },
        });
      });
    });

    return { nodes: computedNodes, edges: computedEdges };
  }, [components]);

  const onNodeClick = (_: any, node: Node) => {
    if (node.data?.component) {
      setSelectedComponent(node.data.component);
    }
  };

  return (
    <div className="relative w-full h-[620px] bg-[#070b14] rounded-xl border border-[#1e293b] overflow-hidden">
      <ReactFlow
        nodes={nodes}
        edges={edges}
        onNodeClick={onNodeClick}
        fitView
        className="react-flow-dark"
      >
        <Background color="#1e293b" gap={20} size={1} />
        <Controls />
        <MiniMap
          nodeColor="#38bdf8"
          maskColor="rgba(10, 15, 29, 0.85)"
          className="border border-[#1e293b] rounded-lg bg-[#0a0f1d] overflow-hidden"
        />
      </ReactFlow>

      {/* Component Details Inspector Drawer */}
      {selectedComponent && (
        <div className="absolute top-4 right-4 w-96 max-h-[92%] bg-[#0f172a]/95 backdrop-blur-md border border-[#334155] rounded-xl shadow-2xl p-5 overflow-y-auto z-20 flex flex-col space-y-4">
          <div className="flex items-start justify-between border-b border-[#1e293b] pb-3">
            <div>
              <span className="text-[10px] font-mono font-bold px-2 py-0.5 rounded bg-cyan-500/20 text-cyan-400 border border-cyan-500/30">
                {selectedComponent.component_code}
              </span>
              <h3 className="text-sm font-bold text-white mt-1.5">{selectedComponent.name}</h3>
              <p className="text-xs text-slate-400 font-sans">{selectedComponent.layer}</p>
            </div>
            <button
              onClick={() => setSelectedComponent(null)}
              className="p-1 rounded-lg text-slate-400 hover:text-white hover:bg-slate-800 transition"
            >
              <X className="w-4 h-4" />
            </button>
          </div>

          <div className="space-y-3 text-xs">
            <div>
              <span className="text-[11px] font-semibold text-slate-400 uppercase tracking-wider block mb-1">
                Responsibility
              </span>
              <p className="text-slate-200 leading-relaxed bg-[#0a0f1d] p-2.5 rounded-lg border border-[#1e293b]">
                {selectedComponent.responsibility}
              </p>
            </div>

            <div>
              <span className="text-[11px] font-semibold text-slate-400 uppercase tracking-wider block mb-1">
                Technology Stack & Target
              </span>
              <div className="p-2.5 bg-[#0a0f1d] rounded-lg border border-[#1e293b] space-y-1">
                <div className="text-slate-200 font-mono text-[11px]">{selectedComponent.technology_stack}</div>
                <div className="text-slate-400 text-[11px]">Target: {selectedComponent.deployment_target}</div>
                <div className="text-slate-400 text-[11px]">Scaling: {selectedComponent.scaling_strategy}</div>
              </div>
            </div>

            <div>
              <span className="text-[11px] font-semibold text-slate-400 uppercase tracking-wider block mb-1">
                Security Controls
              </span>
              <div className="flex flex-wrap gap-1.5">
                {(selectedComponent.security_controls || []).map((sec, idx) => (
                  <span
                    key={idx}
                    className="flex items-center space-x-1 px-2 py-0.5 rounded bg-emerald-500/15 text-emerald-400 border border-emerald-500/30 text-[10px] font-mono"
                  >
                    <Shield className="w-2.5 h-2.5" />
                    <span>{sec}</span>
                  </span>
                ))}
              </div>
            </div>

            <div>
              <span className="text-[11px] font-semibold text-slate-400 uppercase tracking-wider block mb-1">
                Mapped Requirements
              </span>
              <div className="flex flex-wrap gap-1.5">
                {(selectedComponent.related_req_codes || []).map((code) => (
                  <span
                    key={code}
                    className="px-2 py-0.5 rounded bg-blue-500/15 text-blue-400 border border-blue-500/30 text-[10px] font-mono"
                  >
                    {code}
                  </span>
                ))}
              </div>
            </div>

            <div>
              <span className="text-[11px] font-semibold text-slate-400 uppercase tracking-wider block mb-1">
                Downstream Dependencies
              </span>
              <div className="flex flex-wrap gap-1.5">
                {(selectedComponent.dependencies || []).length > 0 ? (
                  selectedComponent.dependencies.map((dep) => (
                    <span
                      key={dep}
                      className="px-2 py-0.5 rounded bg-slate-800 text-slate-300 border border-slate-700 text-[10px] font-mono"
                    >
                      → {dep}
                    </span>
                  ))
                ) : (
                  <span className="text-slate-500 text-[11px] italic">None (Leaf component)</span>
                )}
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

