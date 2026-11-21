import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "Student Performance Data Warehouse | DWDM PBL",
  description: "University-grade DWDM PBL system with Star Schema ETL, OLAP Cubes, Multi-Level Apriori, Decision Trees, and AI Early-Warning Triage.",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body className="min-h-screen bg-[#FAF8F5] text-stone-900 antialiased">
        {children}
      </body>
    </html>
  );
}
