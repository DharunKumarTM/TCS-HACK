"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import {
  LayoutDashboard,
  FileSearch,
  CheckSquare,
  AlertTriangle,
  HelpCircle,
  Network,
  BookOpen,
  GitBranch,
  ShieldAlert,
  Zap,
  FileText,
  Layers,
  Cpu,
  FileUp,
  PlusCircle
} from "lucide-react";
import { cn } from "@/lib/utils";

interface NavItem {
  title: string;
  href: string;
  icon: any;
  badge?: string;
  badgeColor?: string;
}

const navItems: NavItem[] = [
  { title: "Input Studio (Upload/Text)", href: "/input", icon: PlusCircle, badge: "START", badgeColor: "bg-cyan-500/20 text-cyan-400 border border-cyan-500/30" },
  { title: "Overview", href: "/dashboard", icon: LayoutDashboard },
  { title: "Evidence Workspace", href: "/evidence", icon: FileSearch },
  { title: "Requirements Intel", href: "/requirements", icon: CheckSquare },
  { title: "Conflict Detective", href: "/conflicts", icon: AlertTriangle, badge: "3", badgeColor: "bg-amber-500/20 text-amber-400 border border-amber-500/30" },
  { title: "Clarification Room", href: "/clarification", icon: HelpCircle, badge: "HITL", badgeColor: "bg-cyan-500/20 text-cyan-400 border border-cyan-500/30" },
  { title: "Architecture Studio", href: "/architecture", icon: Network },
  { title: "ADR Management", href: "/decisions", icon: BookOpen },
  { title: "Traceability Matrix", href: "/traceability", icon: GitBranch },
  { title: "Risk & Validation", href: "/validation", icon: ShieldAlert },
  { title: "Change Impact", href: "/impact-analysis", icon: Zap },
];

export function Sidebar() {
  const pathname = usePathname();

  return (
    <aside className="w-64 bg-[#0a0f1d] border-r border-[#1e293b] flex flex-col h-screen fixed left-0 top-0 z-30 select-none">
      {/* Brand Header */}
      <div className="p-5 border-b border-[#1e293b] flex items-center justify-between">
        <div className="flex items-center space-x-3">
          <div className="w-9 h-9 rounded-lg bg-gradient-to-tr from-blue-600 via-cyan-500 to-teal-400 flex items-center justify-center shadow-lg shadow-cyan-500/20">
            <Cpu className="w-5 h-5 text-white" />
          </div>
          <div>
            <h1 className="text-base font-bold tracking-tight text-white flex items-center">
              ArchMind <span className="text-cyan-400 ml-1">AI</span>
            </h1>
            <p className="text-[10px] text-slate-400 uppercase tracking-widest font-mono">Agentic Architect</p>
          </div>
        </div>
      </div>

      {/* Nav Items */}
      <div className="flex-1 overflow-y-auto py-4 px-3 space-y-1">
        <div className="px-3 mb-2 text-[10px] font-semibold text-slate-400 uppercase tracking-wider">
          Architecture Pipeline
        </div>
        {navItems.map((item) => {
          const isActive = pathname === item.href || (item.href !== "/dashboard" && pathname.startsWith(item.href));
          const Icon = item.icon;
          return (
            <Link
              key={item.href}
              href={item.href}
              className={cn(
                "flex items-center justify-between px-3 py-2.5 rounded-lg text-xs font-medium transition-all group",
                isActive
                  ? "bg-blue-600/15 text-cyan-300 border border-cyan-500/30 shadow-sm"
                  : "text-slate-400 hover:text-slate-200 hover:bg-[#131d33]"
              )}
            >
              <div className="flex items-center space-x-3">
                <Icon
                  className={cn(
                    "w-4 h-4 transition-colors",
                    isActive ? "text-cyan-400" : "text-slate-400 group-hover:text-slate-300"
                  )}
                />
                <span>{item.title}</span>
              </div>
              {item.badge && (
                <span className={cn("text-[9px] font-mono px-1.5 py-0.5 rounded-full font-bold", item.badgeColor)}>
                  {item.badge}
                </span>
              )}
            </Link>
          );
        })}
      </div>

      {/* Agent Pipeline Status Footer */}
      <div className="p-4 border-t border-[#1e293b] bg-[#0c1326]/60">
        <div className="flex items-center justify-between mb-2">
          <span className="text-[11px] font-medium text-slate-300">LangGraph Status</span>
          <span className="inline-flex items-center px-1.5 py-0.5 rounded-full text-[10px] font-medium bg-emerald-500/15 text-emerald-400 border border-emerald-500/30">
            <span className="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-pulse mr-1.5"></span>
            Orchestrated
          </span>
        </div>
        <div className="text-[10px] text-slate-400 font-mono">
          8 Agents Coordinated
        </div>
      </div>
    </aside>
  );
}

