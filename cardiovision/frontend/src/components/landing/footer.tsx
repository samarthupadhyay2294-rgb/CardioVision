import Link from "next/link";

export function Footer() {
  return (
    <footer className="border-t border-white/5 px-4 py-12 text-sm text-white/50">
      <div className="mx-auto flex max-w-6xl flex-col items-center justify-between gap-4 md:flex-row">
        <p>© {new Date().getFullYear()} CardioVision. All rights reserved.</p>
        <div className="flex gap-6">
          <Link href="/analyze" className="hover:text-foreground">
            Analyze
          </Link>
          <Link href="/auth" className="hover:text-foreground">
            Sign in
          </Link>
          <Link href="/dashboard" className="hover:text-foreground">
            Dashboard
          </Link>
        </div>
      </div>
    </footer>
  );
}
