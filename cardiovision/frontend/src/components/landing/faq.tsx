"use client";

const faqs = [
  {
    q: "Do I need an account to analyze a report?",
    a: "No. Guest users can upload, analyze, view results, and download PDFs without signing up.",
  },
  {
    q: "What file types are supported?",
    a: "PDF, JPG, JPEG, and PNG — including ECG, lipid profiles, and complete health checkups.",
  },
  {
    q: "Is this a medical diagnosis?",
    a: "No. CardioVision provides AI-generated risk assessments for informational purposes. Always consult a qualified healthcare professional.",
  },
  {
    q: "What do registered users get?",
    a: "Report history, risk trend tracking, dashboard analytics, comparison tools, and profile management.",
  },
];

export function FAQ() {
  return (
    <section id="faq" className="border-t border-white/5 px-4 py-24">
      <div className="mx-auto max-w-3xl">
        <h2 className="text-center text-3xl font-bold">FAQ</h2>
        <dl className="mt-10 space-y-6">
          {faqs.map((f) => (
            <div key={f.q} className="glass rounded-xl p-5">
              <dt className="font-semibold">{f.q}</dt>
              <dd className="mt-2 text-sm text-white/60">{f.a}</dd>
            </div>
          ))}
        </dl>
      </div>
    </section>
  );
}
