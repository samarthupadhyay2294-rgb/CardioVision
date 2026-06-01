"use client";

import { motion } from "framer-motion";
import { ArrowDown, Brain, FileUp, ScanLine } from "lucide-react";

const steps = [
  { icon: FileUp, label: "Upload", desc: "PDF or image of your cardiac report" },
  { icon: ScanLine, label: "OCR", desc: "Extract parameters automatically" },
  { icon: Brain, label: "AI Analysis", desc: "ML risk scoring + SHAP explainability" },
  { icon: FileUp, label: "Results", desc: "Dashboard view + downloadable PDF" },
];

export function HowItWorks() {
  return (
    <section id="how-it-works" className="border-t border-white/5 px-4 py-24">
      <div className="mx-auto max-w-4xl text-center">
        <h2 className="text-3xl font-bold">How it works</h2>
        <div className="mt-12 flex flex-col items-center gap-4">
          {steps.map((step, i) => (
            <motion.div
              key={step.label}
              initial={{ opacity: 0 }}
              whileInView={{ opacity: 1 }}
              viewport={{ once: true }}
              className="w-full max-w-md"
            >
              <div className="glass flex items-center gap-4 rounded-2xl p-5 text-left">
                <div className="flex h-12 w-12 shrink-0 items-center justify-center rounded-xl bg-primary/20 text-primary">
                  <step.icon className="h-6 w-6" />
                </div>
                <div>
                  <h3 className="font-semibold">{step.label}</h3>
                  <p className="text-sm text-white/60">{step.desc}</p>
                </div>
              </div>
              {i < steps.length - 1 && (
                <ArrowDown className="mx-auto my-2 h-5 w-5 text-white/30" />
              )}
            </motion.div>
          ))}
        </div>
      </div>
    </section>
  );
}
