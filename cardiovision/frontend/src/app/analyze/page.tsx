"use client";

import { useCallback, useState } from "react";
import { useRouter } from "next/navigation";
import { motion } from "framer-motion";
import { Camera, FileUp, Loader2 } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Progress } from "@/components/ui/progress";
import { uploadAndAnalyze } from "@/services/api";

const STEPS = [
  "Uploading...",
  "OCR Processing...",
  "Extracting Parameters...",
  "Running AI Model...",
  "Generating Report...",
];

export default function AnalyzePage() {
  const router = useRouter();
  const [file, setFile] = useState<File | null>(null);
  const [preview, setPreview] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  const [step, setStep] = useState(0);
  const [error, setError] = useState<string | null>(null);

  const onFile = useCallback((f: File) => {
    setFile(f);
    setError(null);
    if (f.type.startsWith("image/")) {
      setPreview(URL.createObjectURL(f));
    } else {
      setPreview(null);
    }
  }, []);

  const runAnalysis = async () => {
    if (!file) return;
    setLoading(true);
    setError(null);
    let i = 0;
    const timer = setInterval(() => {
      setStep((s) => Math.min(s + 1, STEPS.length - 1));
      i += 1;
    }, 1800);

    try {
      const result = await uploadAndAnalyze(file);
      clearInterval(timer);
      router.push(`/results/${result.report_id}`);
    } catch (e) {
      clearInterval(timer);
      const msg = e instanceof Error ? e.message : "Analysis failed";
      setError(
        msg.includes("fetch") || msg.includes("Failed")
          ? "Cannot reach the API. Ensure the backend is running (port 8000). First analysis may take 2–3 minutes while OCR models load."
          : msg
      );
      setLoading(false);
      setStep(0);
    }
  };

  return (
    <div className="mx-auto max-w-3xl px-4 py-12">
      <h1 className="text-3xl font-bold">Analyze your report</h1>
      <p className="mt-2 text-white/60">No signup required. Results in seconds.</p>

      <motion.div
        initial={{ opacity: 0, y: 12 }}
        animate={{ opacity: 1, y: 0 }}
        className="glass mt-8 rounded-3xl p-8"
      >
        <div
          onDragOver={(e) => e.preventDefault()}
          onDrop={(e) => {
            e.preventDefault();
            const f = e.dataTransfer.files[0];
            if (f) onFile(f);
          }}
          className="flex flex-col items-center rounded-2xl border-2 border-dashed border-white/20 bg-white/5 p-12 text-center"
        >
          {preview ? (
            // eslint-disable-next-line @next/next/no-img-element
            <img src={preview} alt="Preview" className="mb-4 max-h-48 rounded-lg object-contain" />
          ) : (
            <FileUp className="mb-4 h-12 w-12 text-primary" />
          )}
          <p className="font-medium">Drag & drop your report</p>
          <p className="mt-1 text-sm text-white/50">PDF, JPG, PNG, JPEG</p>
          <div className="mt-6 flex flex-wrap justify-center gap-3">
            <label>
              <input
                type="file"
                className="hidden"
                accept=".pdf,.jpg,.jpeg,.png"
                onChange={(e) => e.target.files?.[0] && onFile(e.target.files[0])}
              />
              <Button asChild variant="secondary">
                <span>Choose file</span>
              </Button>
            </label>
            <label>
              <input
                type="file"
                className="hidden"
                accept="image/*"
                capture="environment"
                onChange={(e) => e.target.files?.[0] && onFile(e.target.files[0])}
              />
              <Button variant="ghost" asChild>
                <span>
                  <Camera className="h-4 w-4" />
                  Camera
                </span>
              </Button>
            </label>
          </div>
          {file && (
            <p className="mt-4 text-sm text-secondary">Selected: {file.name}</p>
          )}
        </div>

        {loading && (
          <div className="mt-8 space-y-3">
            <p className="text-sm text-white/70">{STEPS[step]}</p>
            <Progress value={((step + 1) / STEPS.length) * 100} />
          </div>
        )}

        {error && <p className="mt-4 text-sm text-danger">{error}</p>}

        <Button
          className="mt-8 w-full"
          size="lg"
          disabled={!file || loading}
          onClick={runAnalysis}
        >
          {loading ? (
            <>
              <Loader2 className="h-4 w-4 animate-spin" />
              Processing...
            </>
          ) : (
            "Start Analysis"
          )}
        </Button>
      </motion.div>
    </div>
  );
}
