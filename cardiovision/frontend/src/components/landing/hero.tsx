"use client";

import { motion } from "framer-motion";
import { ArrowRight, Heart, Upload } from "lucide-react";
import Link from "next/link";
import { Button } from "@/components/ui/button";

export function Hero() {
  return (
    <section className="relative overflow-hidden px-4 pb-24 pt-20">
      <div className="pointer-events-none absolute inset-0 bg-hero-glow" />
      <div className="mx-auto grid max-w-6xl items-center gap-12 lg:grid-cols-2">
        <motion.div
          initial={{ opacity: 0, y: 24 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6 }}
        >
          <p className="mb-4 inline-flex rounded-full border border-primary/30 bg-primary/10 px-4 py-1 text-sm text-secondary">
            Heart Report Analysis & Cardiovascular Risk Assessment
          </p>
          <h1 className="text-4xl font-bold tracking-tight md:text-5xl lg:text-6xl">
            Understand Your <span className="gradient-text">Heart Health</span> in Seconds
          </h1>
          <p className="mt-6 max-w-xl text-lg text-white/60">
            Upload your medical reports and receive AI-powered cardiovascular risk assessments,
            explanations, and recommendations instantly. No account required.
          </p>
          <div className="mt-8 flex flex-wrap gap-4">
            <Link href="/analyze">
              <Button size="lg">
                Analyze Report
                <ArrowRight className="h-4 w-4" />
              </Button>
            </Link>
            <Link href="/analyze?demo=1">
              <Button variant="secondary" size="lg">
                View Demo
              </Button>
            </Link>
          </div>
        </motion.div>

        <motion.div
          initial={{ opacity: 0, scale: 0.95 }}
          animate={{ opacity: 1, scale: 1 }}
          transition={{ duration: 0.7, delay: 0.2 }}
          className="relative"
        >
          <div className="glass relative rounded-3xl p-8">
            <div className="absolute -right-8 -top-8 h-32 w-32 rounded-full bg-primary/20 blur-3xl" />
            <div className="flex flex-col items-center gap-6">
              <div className="heart-pulse flex h-28 w-28 items-center justify-center rounded-full bg-gradient-to-br from-primary to-secondary shadow-lg shadow-primary/40">
                <Heart className="h-14 w-14 fill-white text-white" />
              </div>
              <div className="w-full rounded-2xl border border-dashed border-white/20 bg-white/5 p-6 text-center">
                <Upload className="mx-auto mb-3 h-8 w-8 text-secondary" />
                <p className="text-sm text-white/70">Drag & drop your lab report</p>
                <p className="mt-1 text-xs text-white/40">PDF, JPG, PNG — ECG & lipid profiles</p>
              </div>
              <div className="flex w-full gap-2 text-xs text-white/50">
                {["OCR", "AI Analysis", "SHAP", "PDF"].map((step, i) => (
                  <div key={step} className="flex-1 rounded-lg bg-white/5 py-2 text-center">
                    <span className="text-primary">{i + 1}.</span> {step}
                  </div>
                ))}
              </div>
            </div>
          </div>
        </motion.div>
      </div>
    </section>
  );
}
