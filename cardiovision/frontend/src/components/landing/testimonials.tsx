"use client";

import { motion } from "framer-motion";

const items = [
  {
    quote:
      "CardioVision turned my lipid panel into a clear risk breakdown in under a minute. The SHAP explanations helped me discuss results with my doctor.",
    name: "Dr. Priya Sharma",
    role: "Cardiologist, Mumbai",
  },
  {
    quote:
      "We use it for patient education — guests can upload without friction, and registered users get trend tracking.",
    name: "James Chen",
    role: "Digital Health Founder",
  },
  {
    quote:
      "The PDF reports are presentation-ready. Perfect for our preventive health clinic workflow.",
    name: "Sarah Okonkwo",
    role: "Clinical Operations Lead",
  },
];

export function Testimonials() {
  return (
    <section className="px-4 py-24">
      <div className="mx-auto max-w-6xl">
        <h2 className="text-center text-3xl font-bold">Trusted by clinicians & patients</h2>
        <div className="mt-12 grid gap-6 md:grid-cols-3">
          {items.map((t, i) => (
            <motion.blockquote
              key={t.name}
              initial={{ opacity: 0, y: 12 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              transition={{ delay: i * 0.1 }}
              className="glass rounded-2xl p-6"
            >
              <p className="text-sm text-white/80">&ldquo;{t.quote}&rdquo;</p>
              <footer className="mt-4 text-sm">
                <strong>{t.name}</strong>
                <span className="block text-white/50">{t.role}</span>
              </footer>
            </motion.blockquote>
          ))}
        </div>
      </div>
    </section>
  );
}
