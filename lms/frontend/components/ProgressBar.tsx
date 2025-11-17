"use client";

import { Progress } from "@/components/ui/progress";
import { cn } from "@/lib/utils";

interface ProgressBarProps {
  value: number;
  className?: string;
  showLabel?: boolean;
  label?: string;
}

export default function ProgressBar({
  value,
  className,
  showLabel = false,
  label
}: ProgressBarProps) {
  const percentage = Math.round(value);

  return (
    <div className={cn("space-y-1", className)}>
      {showLabel && (
        <div className="flex items-center justify-between text-sm">
          <span className="text-muted-foreground">{label || "Progress"}</span>
          <span className="font-medium">{percentage}%</span>
        </div>
      )}
      <Progress value={percentage} className="h-2" />
    </div>
  );
}
