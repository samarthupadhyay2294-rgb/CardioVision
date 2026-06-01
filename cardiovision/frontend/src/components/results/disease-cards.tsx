"use client";

import { motion } from "framer-motion";
import { Progress } from "@/components/ui/progress";

export function DiseaseCards({ risks }: { risks: Record<string, number> }) {
  return (
    <div className="grid gap-4 sm:grid-cols-2">
      {Object.entries(risks).map(([name, pct], i) => (
        <motion.div
          key={name}
          initial={{ opacity: 0, x: -8 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ delay: i * 0.06 }}
          className="glass rounded-2xl p-5"
        >
          <div className="flex justify-between text-sm">
            <span className="font-medium">{name}</span>
            <span className="text-secondary">{pct}%</span>
          </div>
          <Progress value={pct} className="mt-3" />
        </motion.div>
      ))}
    </div>
  );
}
