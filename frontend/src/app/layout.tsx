import type { Metadata } from "next";
import "./globals.css";
import { Sidebar } from "@/components/sidebar";

export const metadata: Metadata = {
  title: "CAMera",
  description: "Cognitive Autonomous Multi-Agent Engineering Reasoning Assistant",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en" className="h-full">
      <body className="h-full flex">
        <Sidebar />
        <main className="flex-1 overflow-auto p-8 ml-60">{children}</main>
      </body>
    </html>
  );
}
