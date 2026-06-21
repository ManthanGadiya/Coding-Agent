import Link from "next/link";

export default function NotFound() {
  return (
    <div className="flex flex-col items-center justify-center h-full gap-4">
      <div className="text-6xl font-mono font-bold text-accent">404</div>
      <p className="text-muted text-lg">This page doesn&apos;t exist.</p>
      <Link href="/" className="text-accent hover:underline text-sm font-mono">cd ~</Link>
    </div>
  );
}
