import type { Metadata } from "next";
import "./globals.css";
import { Sidebar } from "@/components/shared/Sidebar";

export const metadata: Metadata = {
  title: "ArchMind AI – Evidence-Driven Agentic Software Architect",
  description: "TCS AI Hackathon Challenge 02: Transforming fragmented, incomplete and contradictory software requirements into explainable, validated and traceable software architecture.",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en" className="dark">
      <body className="bg-[#080c14] text-slate-100 flex min-h-screen antialiased selection:bg-cyan-500 selection:text-black">
        <Sidebar />
        <div className="flex-1 pl-64 flex flex-col min-h-screen">
          {children}
        </div>
      </body>
    </html>
  );
}

