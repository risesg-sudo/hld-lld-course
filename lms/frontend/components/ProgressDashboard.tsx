"use client";

import { useEffect, useState } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Progress } from "@/lib/types";
import { getProgress } from "@/lib/api";
import { formatDuration, calculateEstimatedCompletion } from "@/lib/utils";
import ProgressBar from "@/components/ProgressBar";
import { Doughnut, Bar } from "react-chartjs-2";
import {
  Chart as ChartJS,
  ArcElement,
  CategoryScale,
  LinearScale,
  BarElement,
  Title,
  Tooltip,
  Legend,
} from "chart.js";
import { BookOpen, Clock, TrendingUp, Flame, Play } from "lucide-react";
import Link from "next/link";

// Register ChartJS components
ChartJS.register(
  ArcElement,
  CategoryScale,
  LinearScale,
  BarElement,
  Title,
  Tooltip,
  Legend
);

export default function ProgressDashboard() {
  const [progress, setProgress] = useState<Progress | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadProgress();
  }, []);

  async function loadProgress() {
    try {
      const data = await getProgress();
      setProgress(data);
    } catch (error) {
      console.error("Failed to load progress:", error);
    } finally {
      setLoading(false);
    }
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary"></div>
      </div>
    );
  }

  if (!progress) {
    return (
      <div className="text-center py-12">
        <p className="text-muted-foreground">Failed to load progress data</p>
      </div>
    );
  }

  const completedMinutes = Math.round(progress.overall.time_spent_seconds / 60);
  const estimatedRemaining = calculateEstimatedCompletion(
    progress.overall.total_estimated_minutes,
    completedMinutes
  );

  // Donut chart data
  const donutData = {
    labels: ["Completed", "Remaining"],
    datasets: [
      {
        data: [
          progress.overall.completed_lessons,
          progress.overall.total_lessons - progress.overall.completed_lessons,
        ],
        backgroundColor: ["#3b82f6", "#e5e7eb"],
        borderWidth: 0,
      },
    ],
  };

  const donutOptions = {
    responsive: true,
    maintainAspectRatio: false,
    cutout: "70%",
    plugins: {
      legend: {
        display: false,
      },
      tooltip: {
        callbacks: {
          label: (context: any) => {
            const label = context.label || "";
            const value = context.parsed;
            const total = progress.overall.total_lessons;
            const percentage = ((value / total) * 100).toFixed(1);
            return `${label}: ${value} (${percentage}%)`;
          },
        },
      },
    },
  };

  // Bar chart data for weekly progress
  const weekLabels = progress.by_week.map(
    (w) => `${w.week_type} W${w.week_num}`
  );
  const weekCompletionData = progress.by_week.map(
    (w) => w.completion_percentage
  );

  const barData = {
    labels: weekLabels,
    datasets: [
      {
        label: "Completion %",
        data: weekCompletionData,
        backgroundColor: "#3b82f6",
        borderRadius: 4,
      },
    ],
  };

  const barOptions = {
    responsive: true,
    maintainAspectRatio: false,
    scales: {
      y: {
        beginAtZero: true,
        max: 100,
        ticks: {
          callback: (value: any) => value + "%",
        },
      },
    },
    plugins: {
      legend: {
        display: false,
      },
    },
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-3xl font-bold">Dashboard</h1>
        <p className="text-muted-foreground mt-1">
          Track your learning progress
        </p>
      </div>

      {/* Stats Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <Card>
          <CardHeader className="pb-2">
            <div className="flex items-center justify-between">
              <CardTitle className="text-sm font-medium text-muted-foreground">
                Lessons Complete
              </CardTitle>
              <BookOpen className="h-4 w-4 text-muted-foreground" />
            </div>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">
              {progress.overall.completed_lessons}/{progress.overall.total_lessons}
            </div>
            <p className="text-xs text-muted-foreground mt-1">
              {progress.overall.completion_percentage.toFixed(1)}% Complete
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2">
            <div className="flex items-center justify-between">
              <CardTitle className="text-sm font-medium text-muted-foreground">
                Time Remaining
              </CardTitle>
              <Clock className="h-4 w-4 text-muted-foreground" />
            </div>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{estimatedRemaining}</div>
            <p className="text-xs text-muted-foreground mt-1">
              {formatDuration(progress.overall.time_spent_seconds)} spent
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2">
            <div className="flex items-center justify-between">
              <CardTitle className="text-sm font-medium text-muted-foreground">
                Overall Progress
              </CardTitle>
              <TrendingUp className="h-4 w-4 text-muted-foreground" />
            </div>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">
              {progress.overall.completion_percentage.toFixed(0)}%
            </div>
            <Progress
              value={progress.overall.completion_percentage}
              className="mt-2"
            />
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2">
            <div className="flex items-center justify-between">
              <CardTitle className="text-sm font-medium text-muted-foreground">
                Current Streak
              </CardTitle>
              <Flame className="h-4 w-4 text-orange-500" />
            </div>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">
              {progress.streak.current_days} days
            </div>
            <p className="text-xs text-muted-foreground mt-1">
              Best: {progress.streak.best_days} days
            </p>
          </CardContent>
        </Card>
      </div>

      {/* Charts Row */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Donut Chart */}
        <Card>
          <CardHeader>
            <CardTitle>Overall Completion</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="relative h-64">
              <Doughnut data={donutData} options={donutOptions} />
              <div className="absolute inset-0 flex items-center justify-center flex-col">
                <div className="text-4xl font-bold">
                  {progress.overall.completion_percentage.toFixed(0)}%
                </div>
                <div className="text-sm text-muted-foreground">Complete</div>
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Bar Chart */}
        <Card>
          <CardHeader>
            <CardTitle>Weekly Progress</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="h-64">
              <Bar data={barData} options={barOptions} />
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Week Breakdown */}
      <Card>
        <CardHeader>
          <CardTitle>Progress by Week</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            {progress.by_week.map((week) => (
              <div key={`${week.week_type}-${week.week_num}`}>
                <div className="flex items-center justify-between mb-2">
                  <span className="text-sm font-medium">
                    {week.week_type} Week {week.week_num}
                  </span>
                  <span className="text-sm text-muted-foreground">
                    {week.completed_lessons}/{week.total_lessons} lessons
                  </span>
                </div>
                <ProgressBar
                  value={week.completion_percentage}
                  showLabel={false}
                />
              </div>
            ))}
          </div>
        </CardContent>
      </Card>

      {/* Continue Learning CTA */}
      <Card className="bg-primary text-primary-foreground">
        <CardContent className="pt-6">
          <div className="flex items-center justify-between">
            <div>
              <h3 className="text-xl font-semibold mb-1">
                Ready to continue learning?
              </h3>
              <p className="text-primary-foreground/80">
                Pick up where you left off
              </p>
            </div>
            <Link href="/lesson/1">
              <Button size="lg" variant="secondary">
                <Play className="h-4 w-4 mr-2" />
                Continue Learning
              </Button>
            </Link>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
