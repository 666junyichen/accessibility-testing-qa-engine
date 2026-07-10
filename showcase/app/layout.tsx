import type { Metadata } from "next";
import type { CSSProperties, ReactNode } from "react";
import "./globals.css";

export const metadata: Metadata = {
  title: "Accessibility Testing QA Engine",
  description:
    "Polished web demo for an internal accessibility testing review platform with single-session review, tester trajectory, and cohort oversight.",
};

export default function RootLayout({ children }: { children: ReactNode }) {
  return (
    <html lang="en">
      <body
        style={
          {
            "--font-display": '"Georgia", "Times New Roman", serif',
            "--font-body": '"Segoe UI", "Helvetica Neue", Arial, sans-serif',
            "--font-mono": '"Consolas", "SFMono-Regular", "Courier New", monospace',
          } as CSSProperties
        }
      >
        {children}
      </body>
    </html>
  );
}
