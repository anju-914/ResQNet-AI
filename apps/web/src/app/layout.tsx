import type { Metadata } from "next";
import "./globals.css";
import "maplibre-gl/dist/maplibre-gl.css";
import Navbar from "@/components/Navbar";
import LeftRail from "@/components/LeftRail";

export const metadata: Metadata = {
  title: "ResQNet AI | Rescue Coordinator Dashboard",
  description: "Disaster SOS Ingestion, Verification, and Graph-based Rescue Routing Engine",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en" className="dark bg-[#0a0a0a]">
      <body className="bg-[#0a0a0a] text-white min-h-screen flex flex-col antialiased selection:bg-gold/30 selection:text-gold-hover">
        <Navbar />
        <div className="flex flex-1 overflow-hidden h-[calc(100vh-56px)]">
          <LeftRail />
          <main className="flex-1 relative overflow-auto bg-[#0a0a0a]">
            {children}
          </main>
        </div>
      </body>
    </html>
  );
}

