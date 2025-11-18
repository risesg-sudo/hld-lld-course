"use client";

import { useState, useEffect, useCallback } from "react";
import { Prism as SyntaxHighlighter } from "react-syntax-highlighter";
import { vscDarkPlus } from "react-syntax-highlighter/dist/esm/styles/prism";
import { Copy, Check, Code2 } from "lucide-react";
import { cn } from "@/lib/utils";

// Language icons (using Code2 as base with different colors)
const languageIcons = {
  python: { icon: Code2, color: "text-blue-400" },
  cpp: { icon: Code2, color: "text-purple-400" },
  java: { icon: Code2, color: "text-orange-400" },
};

type Language = "python" | "cpp" | "java";

interface MultiLanguageCodeBlockProps {
  pythonCode: string;
  cppCode: string;
  javaCode: string;
  className?: string;
}

export default function MultiLanguageCodeBlock({
  pythonCode,
  cppCode,
  javaCode,
  className,
}: MultiLanguageCodeBlockProps) {
  const [activeLanguage, setActiveLanguage] = useState<Language>("python");
  const [copied, setCopied] = useState(false);

  // Load saved language preference from localStorage
  useEffect(() => {
    const savedLanguage = localStorage.getItem("preferredLanguage");
    if (savedLanguage && ["python", "cpp", "java"].includes(savedLanguage)) {
      setActiveLanguage(savedLanguage as Language);
    }
  }, []);

  // Save language preference to localStorage
  const handleLanguageChange = useCallback((language: Language) => {
    setActiveLanguage(language);
    localStorage.setItem("preferredLanguage", language);
  }, []);

  // Get current code based on active language
  const getCurrentCode = () => {
    switch (activeLanguage) {
      case "python":
        return pythonCode;
      case "cpp":
        return cppCode;
      case "java":
        return javaCode;
      default:
        return pythonCode;
    }
  };

  // Copy code to clipboard
  const handleCopy = async () => {
    try {
      await navigator.clipboard.writeText(getCurrentCode());
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    } catch (err) {
      console.error("Failed to copy code:", err);
    }
  };

  // Keyboard navigation
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.target instanceof HTMLInputElement || e.target instanceof HTMLTextAreaElement) {
        return; // Don't handle keyboard shortcuts when typing in inputs
      }

      const languages: Language[] = ["python", "cpp", "java"];
      const currentIndex = languages.indexOf(activeLanguage);

      if (e.key === "ArrowRight") {
        e.preventDefault();
        const nextIndex = (currentIndex + 1) % languages.length;
        handleLanguageChange(languages[nextIndex]);
      } else if (e.key === "ArrowLeft") {
        e.preventDefault();
        const prevIndex = (currentIndex - 1 + languages.length) % languages.length;
        handleLanguageChange(languages[prevIndex]);
      }
    };

    window.addEventListener("keydown", handleKeyDown);
    return () => window.removeEventListener("keydown", handleKeyDown);
  }, [activeLanguage, handleLanguageChange]);

  const tabs: { key: Language; label: string }[] = [
    { key: "python", label: "Python" },
    { key: "cpp", label: "C++" },
    { key: "java", label: "Java" },
  ];

  return (
    <div className={cn("w-full rounded-lg overflow-hidden border border-border", className)}>
      {/* Tab Navigation */}
      <div className="bg-muted/50 border-b border-border">
        <div className="flex overflow-x-auto no-scrollbar">
          {tabs.map(({ key, label }) => {
            const IconComponent = languageIcons[key].icon;
            const isActive = activeLanguage === key;

            return (
              <button
                key={key}
                onClick={() => handleLanguageChange(key)}
                className={cn(
                  "flex items-center gap-2 px-4 py-3 text-sm font-medium transition-all duration-200",
                  "border-b-2 whitespace-nowrap focus:outline-none focus:ring-2 focus:ring-primary focus:ring-offset-2",
                  isActive
                    ? "border-primary text-primary bg-background"
                    : "border-transparent text-muted-foreground hover:text-foreground hover:bg-muted/70"
                )}
                role="tab"
                aria-selected={isActive}
                aria-controls={`code-panel-${key}`}
                id={`tab-${key}`}
                tabIndex={isActive ? 0 : -1}
              >
                <IconComponent className={cn("h-4 w-4", isActive && languageIcons[key].color)} />
                <span>{label}</span>
              </button>
            );
          })}
        </div>
      </div>

      {/* Code Display */}
      <div className="relative">
        {/* Copy Button */}
        <button
          onClick={handleCopy}
          className={cn(
            "absolute top-3 right-3 z-10 p-2 rounded-md transition-all duration-200",
            "bg-muted/80 hover:bg-muted backdrop-blur-sm",
            "focus:outline-none focus:ring-2 focus:ring-primary focus:ring-offset-2"
          )}
          aria-label="Copy code to clipboard"
          title={copied ? "Copied!" : "Copy code"}
        >
          {copied ? (
            <Check className="h-4 w-4 text-green-500" />
          ) : (
            <Copy className="h-4 w-4 text-muted-foreground" />
          )}
        </button>

        {/* Code Block with Syntax Highlighting */}
        {tabs.map(({ key }) => (
          <div
            key={key}
            role="tabpanel"
            id={`code-panel-${key}`}
            aria-labelledby={`tab-${key}`}
            hidden={activeLanguage !== key}
            className={cn(
              "transition-opacity duration-200",
              activeLanguage === key ? "opacity-100" : "opacity-0"
            )}
          >
            {activeLanguage === key && (
              <SyntaxHighlighter
                language={key === "cpp" ? "cpp" : key}
                style={vscDarkPlus}
                showLineNumbers
                customStyle={{
                  margin: 0,
                  padding: "1.5rem",
                  paddingTop: "3rem",
                  background: "#1e1e1e",
                  fontSize: "0.875rem",
                  lineHeight: "1.5",
                  borderRadius: "0",
                }}
                lineNumberStyle={{
                  minWidth: "2.5em",
                  paddingRight: "1em",
                  color: "#858585",
                  userSelect: "none",
                }}
                wrapLongLines={false}
              >
                {getCurrentCode()}
              </SyntaxHighlighter>
            )}
          </div>
        ))}
      </div>

      {/* Keyboard Hint (only visible on larger screens) */}
      <div className="hidden md:block bg-muted/30 px-4 py-2 text-xs text-muted-foreground border-t border-border">
        <span className="flex items-center gap-2">
          <kbd className="px-2 py-0.5 rounded bg-background border border-border">←</kbd>
          <kbd className="px-2 py-0.5 rounded bg-background border border-border">→</kbd>
          <span>Navigate between languages</span>
        </span>
      </div>
    </div>
  );
}
