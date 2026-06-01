"use client";

import { motion } from "framer-motion";
import {
  Brain,
  FileText,
  LineChart,
  Scan,
  Shield,
  Stethoscope,
} from "lucide-react";

const features = [
  {
    icon: Scan,
    title: "OCR Report Reading",
    desc: "Extract clinical values from PDFs and images with PaddleOCR.",
  },
  {
    icon: Brain,
    title: "AI Risk Assessment",
    desc: "XGBoost ensemble trained on enhanced cardiovascular datasets.",
  },
  {
    icon: Stethoscope,
    title: "Disease Detection",
    desc: "CAD, hypertension, heart failure, arrhythmia & atherosclerosis scores.",
  },
  {
    icon: LineChart,
    title: "Explainable AI",
    desc: "SHAP feature importance and top risk driver visualizations.",
  },
  {
    icon: Shield,
    title: "Personalized Recommendations",
    desc: "Diet, exercise, lifestyle, and follow-up guidance.",
  },
  {
    icon: FileText,
    title: "PDF Reports",
    desc: "Download professional reports for your records.",
  },
];

export function Features() {
  return (
    <section id="features" className="px-4 py-24">
      <div className="mx-auto max-w-6xl">
        <h2 className="text-center text-3xl font-bold">Enterprise-grade cardiac intelligence</h2>
        <p className="mx-auto mt-3 max-w-2xl text-center text-white/60">
          From upload to actionable insights in one seamless pipeline.
        </p>
        <div className="mt-12 grid gap-6 sm:grid-cols-2 lg:grid-cols-3">
          {features.map((f, i) => (
            <motion.div
              key={f.title}
              initial={{ opacity: 0, y: 16 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              transition={{ delay: i * 0.08 }}
              className="glass rounded-2xl p-6 transition hover:border-primary/30"
            >
              <f.icon className="mb-4 h-8 w-8 text-primary" />
              <h3 className="font-semibold">{f.title}</h3>
              <p className="mt-2 text-sm text-white/60">{f.desc}</p>
            </motion.div>
          ))}
        </div>
      </div>
    </section>
  );
}
