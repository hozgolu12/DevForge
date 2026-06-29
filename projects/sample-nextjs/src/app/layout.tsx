import type { Metadata } from 'next';
import './globals.css';

export const metadata: Metadata = {
  title: 'DevForge Next.js Template',
  description: 'Production-ready App Router Next.js Template for DevForge',
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body className="bg-slate-950 text-slate-50 antialiased">{children}</body>
    </html>
  );
}
