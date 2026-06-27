"use client";

import { useCallback, useMemo } from "react";
import {
  ReactFlow,
  Background,
  Controls,
  MiniMap,
  Node,
  Edge,
  useNodesState,
  useEdgesState,
  MarkerType,
} from "@xyflow/react";
import "@xyflow/react/dist/style.css";
import type { NetworkResponse } from "@/types";
import { Badge } from "@/components/ui/badge";

type Props = {
  data: NetworkResponse;
};

const nodeColors: Record<string, string> = {
  person: "#2563eb",
  case: "#dc2626",
  evidence: "#16a34a",
  location: "#ca8a04",
  gang: "#9333ea",
  phone: "#0891b2",
  vehicle: "#db2777",
  default: "#6b7280",
};

export function NetworkGraph({ data }: Props) {
  const initialNodes: Node[] = useMemo(
    () =>
      data.nodes.map((n, i) => ({
        id: n.id,
        position: {
          x: 150 * Math.cos((2 * Math.PI * i) / data.nodes.length) + 300,
          y: 150 * Math.sin((2 * Math.PI * i) / data.nodes.length) + 250,
        },
        data: {
          label: n.label,
          type: n.type,
        },
        style: {
          background: nodeColors[n.type] || nodeColors.default,
          color: "#fff",
          border: "none",
          borderRadius: "8px",
          padding: "8px 12px",
          fontSize: "12px",
          fontWeight: 500,
        },
      })),
    [data.nodes]
  );

  const initialEdges: Edge[] = useMemo(
    () =>
      data.edges.map((e, i) => ({
        id: `e-${i}`,
        source: e.source,
        target: e.target,
        label: e.relationship,
        style: { stroke: "#94a3b8", strokeWidth: e.weight ? Math.max(1, e.weight * 3) : 1.5 },
        markerEnd: { type: MarkerType.ArrowClosed, color: "#94a3b8" },
        labelStyle: { fontSize: 10, fill: "#64748b" },
      })),
    [data.edges]
  );

  const [nodes, , onNodesChange] = useNodesState(initialNodes);
  const [edges, , onEdgesChange] = useEdgesState(initialEdges);

  const onNodeClick = useCallback((_event: React.MouseEvent, node: Node) => {
    console.log("Node clicked:", node.id, node.data);
  }, []);

  return (
    <div className="h-[500px] w-full rounded-lg border">
      <ReactFlow
        nodes={nodes}
        edges={edges}
        onNodesChange={onNodesChange}
        onEdgesChange={onEdgesChange}
        onNodeClick={onNodeClick}
        fitView
        attributionPosition="bottom-left"
      >
        <Background />
        <Controls />
        <MiniMap
          nodeStrokeColor="#94a3b8"
          nodeColor={(n) => nodeColors[(n.data as { type: string })?.type] || nodeColors.default}
          nodeBorderRadius={8}
        />
      </ReactFlow>
    </div>
  );
}

export function NetworkStats({ data }: { data: NetworkResponse }) {
  const typeCounts = data.nodes.reduce<Record<string, number>>((acc, n) => {
    acc[n.type] = (acc[n.type] || 0) + 1;
    return acc;
  }, {});

  return (
    <div className="flex flex-wrap gap-2">
      {Object.entries(typeCounts).map(([type, count]) => (
        <Badge
          key={type}
          style={{ background: nodeColors[type] || nodeColors.default }}
          className="text-white"
        >
          {type}: {count}
        </Badge>
      ))}
      <Badge variant="outline">{data.edges.length} connections</Badge>
      {data.centrality && (
        <Badge variant="secondary">
          Top:{" "}
          {Object.entries(data.centrality)
            .sort(([, a], [, b]) => b - a)
            .slice(0, 3)
            .map(([id]) => id.slice(0, 6))
            .join(", ")}
        </Badge>
      )}
    </div>
  );
}
