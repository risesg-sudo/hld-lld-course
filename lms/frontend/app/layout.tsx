import type { Metadata } from "next";
import { Inter } from "next/font/google";
import "./globals.css";
import Sidebar from "@/components/Sidebar";
import { Book, Moon, Sun } from "lucide-react";
import { Button } from "@/components/ui/button";

const inter = Inter({ subsets: ["latin"] });

export const metadata: Metadata = {
  title: "LMS - HLD & LLD Course",
  description: "Learning Management System for High-Level Design and Low-Level Design courses",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en" suppressHydrationWarning>
      <body className={inter.className}>
        <div className="flex h-screen overflow-hidden">
          {/* Sidebar */}
          <aside className="w-80 border-r bg-card hidden lg:block overflow-y-auto">
            <Sidebar />
          </aside>

          {/* Main content */}
          <div className="flex-1 flex flex-col overflow-hidden">
            {/* Header */}
            <header className="h-16 border-b bg-card px-6 flex items-center justify-between shrink-0">
              <div className="flex items-center gap-3">
                <Book className="h-6 w-6 text-primary" />
                <h1 className="text-xl font-bold">HLD & LLD Course</h1>
              </div>

              <div className="flex items-center gap-4">
                <ThemeToggle />
              </div>
            </header>

            {/* Main content area */}
            <main className="flex-1 overflow-y-auto">
              {children}
            </main>
          </div>
        </div>
      </body>
    </html>
  );
}

function ThemeToggle() {
  return (
    <Button
      variant="ghost"
      size="icon"
      onClick={() => {
        const html = document.documentElement;
        html.classList.toggle("dark");
        localStorage.setItem(
          "theme",
          html.classList.contains("dark") ? "dark" : "light"
        );
      }}
      className="h-9 w-9"
    >
      <Sun className="h-4 w-4 rotate-0 scale-100 transition-all dark:-rotate-90 dark:scale-0" />
      <Moon className="absolute h-4 w-4 rotate-90 scale-0 transition-all dark:rotate-0 dark:scale-100" />
      <span className="sr-only">Toggle theme</span>
    </Button>
  );
}
