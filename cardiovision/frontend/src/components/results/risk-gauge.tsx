"use client";

import { motion } from "framer-motion";

export function RiskGauge({ value, category }: { value: number; category: string }) {
  const color =
    value >= 75 ? "#EF4444" : value >= 55 ? "#EF4444" : value >= 35 ? "#F59E0B" : "#10B981";

  return (
    <div className="glass flex flex-col items-center rounded-3xl p-8">
      <motion.div
        initial={{ scale: 0.8, opacity: 0 }}
        animate={{ scale: 1, opacity: 1 }}
        className="relative flex h-40 w-40 items-center justify-center rounded-full"
        style={{
          background: `conic-gradient(${color} ${value * 3.6}deg, rgba(255,255,255,0.08) 0deg)`,
        }}
      >
        <div className="flex h-32 w-32 flex-col items-center justify-center rounded-full bg-card">
          <span className="text-4xl font-bold" style={{ color }}>
            {value}%
          </span>
          <span className="text-xs text-white/50">Overall Risk</span>
        </div>
      </motion.div>
      <p className="mt-4 text-lg font-semibold" style={{ color }}>
        {category}
      </p>
    </div>
  );
}
