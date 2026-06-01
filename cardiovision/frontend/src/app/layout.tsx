import type { Metadata } from "next";
import "@/styles/globals.css";
import { Providers } from "@/providers/query-provider";
import { Navbar } from "@/components/layout/navbar";

export const metadata: Metadata = {
  title: "CardioVision — Heart Report Analysis & Cardiovascular Risk Assessment",
  description:
    "Upload medical reports and receive AI-powered cardiovascular risk assessments, explanations, and recommendations instantly.",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en" className="dark">
      <body className="font-sans min-h-screen">
        <Providers>
          <Navbar />
          <main className="pt-16">{children}</main>
        </Providers>
      </body>
    </html>
  );
}
