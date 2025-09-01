"use client"

import { useState } from "react"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { Badge } from "@/components/ui/badge"
import {
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  PieChart,
  Pie,
  Cell,
  Area,
  AreaChart,
} from "recharts"
import { Clock, TrendingUp, Activity, Calendar, Sparkles, Zap } from "lucide-react"

// Mock data for demonstration
const timeRangeData = {
  "4weeks": [
    { date: "Week 1", "Study Economy": 25, "Play Basketball": 15, "Work Projects": 35, Reading: 10 },
    { date: "Week 2", "Study Economy": 30, "Play Basketball": 12, "Work Projects": 40, Reading: 8 },
    { date: "Week 3", "Study Economy": 28, "Play Basketball": 18, "Work Projects": 32, Reading: 12 },
    { date: "Week 4", "Study Economy": 22, "Play Basketball": 20, "Work Projects": 38, Reading: 15 },
  ],
  "1year": [
    { date: "Q1", "Study Economy": 320, "Play Basketball": 180, "Work Projects": 450, Reading: 120 },
    { date: "Q2", "Study Economy": 280, "Play Basketball": 220, "Work Projects": 480, Reading: 140 },
    { date: "Q3", "Study Economy": 350, "Play Basketball": 200, "Work Projects": 420, Reading: 160 },
    { date: "Q4", "Study Economy": 290, "Play Basketball": 240, "Work Projects": 500, Reading: 180 },
  ],
  "5years": [
    { date: "2020", "Study Economy": 1200, "Play Basketball": 800, "Work Projects": 1800, Reading: 600 },
    { date: "2021", "Study Economy": 1100, "Play Basketball": 900, "Work Projects": 1900, Reading: 650 },
    { date: "2022", "Study Economy": 1300, "Play Basketball": 850, "Work Projects": 2000, Reading: 700 },
    { date: "2023", "Study Economy": 1250, "Play Basketball": 920, "Work Projects": 1950, Reading: 720 },
    { date: "2024", "Study Economy": 1400, "Play Basketball": 1000, "Work Projects": 2100, Reading: 800 },
  ],
}

const pieData = [
  { name: "Work Projects", value: 2100, color: "hsl(var(--chart-1))" },
  { name: "Study Economy", value: 1400, color: "hsl(var(--chart-2))" },
  { name: "Play Basketball", value: 1000, color: "hsl(var(--chart-3))" },
  { name: "Reading", value: 800, color: "hsl(var(--chart-4))" },
]

const topActivities = [
  {
    name: "Work Projects",
    time: "2100hr 0mins",
    keywords: ["development", "meetings", "planning", "coding", "reviews"],
  },
  {
    name: "Study Economy",
    time: "1400hr 0mins",
    keywords: ["macroeconomics", "research", "analysis", "theory", "markets"],
  },
  {
    name: "Play Basketball",
    time: "1000hr 0mins",
    keywords: ["training", "games", "practice", "fitness", "team"],
  },
  {
    name: "Reading",
    time: "800hr 0mins",
    keywords: ["books", "articles", "learning", "fiction", "non-fiction"],
  },
  {
    name: "Social Activities",
    time: "600hr 0mins",
    keywords: ["friends", "family", "events", "dining", "entertainment"],
  },
]

export default function TimeTrackingDashboard() {
  const [selectedTimeRange, setSelectedTimeRange] = useState<"4weeks" | "1year" | "5years">("5years")

  const currentData = timeRangeData[selectedTimeRange]
  const totalHours = pieData.reduce((sum, item) => sum + item.value, 0)

  return (
    <div className="min-h-screen artistic-bg p-6">
      <div className="mx-auto max-w-7xl space-y-8">
        <div className="flex items-center justify-between">
          <div className="space-y-2">
            <div className="flex items-center gap-3">
              <div className="p-2 rounded-xl bg-gradient-to-br from-primary to-secondary">
                <Sparkles className="h-6 w-6 text-white" />
              </div>
              <h1 className="text-4xl font-bold bg-gradient-to-r from-primary via-secondary to-accent bg-clip-text text-transparent">
                Time Analytics Dashboard
              </h1>
            </div>
            <p className="text-lg text-muted-foreground ml-14">
              AI-powered insights into your creative time allocation
            </p>
          </div>
          <div className="flex items-center gap-4 card-artistic p-4 rounded-xl">
            <Calendar className="h-5 w-5 text-primary" />
            <Select
              value={selectedTimeRange}
              onValueChange={(value: "4weeks" | "1year" | "5years") => setSelectedTimeRange(value)}
            >
              <SelectTrigger className="w-40 border-primary/20 focus:border-primary">
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="4weeks">Last 4 Weeks</SelectItem>
                <SelectItem value="1year">Last Year</SelectItem>
                <SelectItem value="5years">Last 5 Years</SelectItem>
              </SelectContent>
            </Select>
          </div>
        </div>

        <div className="grid gap-6 md:grid-cols-4">
          <div className="metric-card rounded-2xl p-6 hover:animate-pulse">
            <div className="flex flex-row items-center justify-between space-y-0 pb-2">
              <h3 className="text-sm font-medium text-muted-foreground">Total Hours Tracked</h3>
              <div className="p-2 rounded-lg bg-gradient-to-br from-primary/20 to-secondary/20">
                <Clock className="h-4 w-4 text-primary" />
              </div>
            </div>
            <div className="space-y-1">
              <div className="text-3xl font-bold bg-gradient-to-r from-primary to-secondary bg-clip-text text-transparent">
                {totalHours.toLocaleString()}h
              </div>
              <p className="text-xs text-muted-foreground flex items-center gap-1">
                <TrendingUp className="h-3 w-3 text-green-500" />
                +12% from last period
              </p>
            </div>
          </div>

          <div className="metric-card rounded-2xl p-6 hover:animate-pulse">
            <div className="flex flex-row items-center justify-between space-y-0 pb-2">
              <h3 className="text-sm font-medium text-muted-foreground">Most Active Category</h3>
              <div className="p-2 rounded-lg bg-gradient-to-br from-secondary/20 to-accent/20">
                <Zap className="h-4 w-4 text-secondary" />
              </div>
            </div>
            <div className="space-y-1">
              <div className="text-2xl font-bold text-primary">Work Projects</div>
              <p className="text-xs text-muted-foreground">38% of total time</p>
            </div>
          </div>

          <div className="metric-card rounded-2xl p-6 hover:animate-pulse">
            <div className="flex flex-row items-center justify-between space-y-0 pb-2">
              <h3 className="text-sm font-medium text-muted-foreground">Activities Tracked</h3>
              <div className="p-2 rounded-lg bg-gradient-to-br from-accent/20 to-primary/20">
                <Activity className="h-4 w-4 text-accent" />
              </div>
            </div>
            <div className="space-y-1">
              <div className="text-3xl font-bold bg-gradient-to-r from-secondary to-accent bg-clip-text text-transparent">
                24
              </div>
              <p className="text-xs text-muted-foreground">Across all categories</p>
            </div>
          </div>

          <div className="metric-card rounded-2xl p-6 hover:animate-pulse">
            <div className="flex flex-row items-center justify-between space-y-0 pb-2">
              <h3 className="text-sm font-medium text-muted-foreground">Avg. Daily Hours</h3>
              <div className="p-2 rounded-lg bg-gradient-to-br from-primary/20 to-accent/20">
                <Clock className="h-4 w-4 text-primary" />
              </div>
            </div>
            <div className="space-y-1">
              <div className="text-3xl font-bold bg-gradient-to-r from-accent to-primary bg-clip-text text-transparent">
                8.2h
              </div>
              <p className="text-xs text-muted-foreground">Productive time per day</p>
            </div>
          </div>
        </div>

        <div className="grid gap-8 lg:grid-cols-2">
          {/* Enhanced Area Chart instead of Line Chart */}
          <div className="lg:col-span-2 card-artistic rounded-3xl p-8">
            <div className="mb-6">
              <h2 className="text-2xl font-bold bg-gradient-to-r from-primary to-secondary bg-clip-text text-transparent">
                Activity Trends Over Time
              </h2>
              <p className="text-muted-foreground mt-2">Flowing visualization of your time patterns</p>
            </div>
            <div className="chart-container">
              <div className="h-80">
                <ResponsiveContainer width="100%" height="100%">
                  <AreaChart data={currentData}>
                    <defs>
                      <linearGradient id="workGradient" x1="0" y1="0" x2="0" y2="1">
                        <stop offset="5%" stopColor="hsl(var(--chart-1))" stopOpacity={0.8} />
                        <stop offset="95%" stopColor="hsl(var(--chart-1))" stopOpacity={0.1} />
                      </linearGradient>
                      <linearGradient id="studyGradient" x1="0" y1="0" x2="0" y2="1">
                        <stop offset="5%" stopColor="hsl(var(--chart-2))" stopOpacity={0.8} />
                        <stop offset="95%" stopColor="hsl(var(--chart-2))" stopOpacity={0.1} />
                      </linearGradient>
                      <linearGradient id="basketballGradient" x1="0" y1="0" x2="0" y2="1">
                        <stop offset="5%" stopColor="hsl(var(--chart-3))" stopOpacity={0.8} />
                        <stop offset="95%" stopColor="hsl(var(--chart-3))" stopOpacity={0.1} />
                      </linearGradient>
                      <linearGradient id="readingGradient" x1="0" y1="0" x2="0" y2="1">
                        <stop offset="5%" stopColor="hsl(var(--chart-4))" stopOpacity={0.8} />
                        <stop offset="95%" stopColor="hsl(var(--chart-4))" stopOpacity={0.1} />
                      </linearGradient>
                    </defs>
                    <CartesianGrid strokeDasharray="3 3" stroke="hsl(var(--border))" opacity={0.3} />
                    <XAxis dataKey="date" stroke="hsl(var(--muted-foreground))" fontSize={12} />
                    <YAxis stroke="hsl(var(--muted-foreground))" fontSize={12} />
                    <Tooltip
                      contentStyle={{
                        backgroundColor: "rgba(255, 255, 255, 0.95)",
                        border: "1px solid hsl(var(--primary))",
                        borderRadius: "12px",
                        backdropFilter: "blur(10px)",
                      }}
                    />
                    <Area
                      type="monotone"
                      dataKey="Work Projects"
                      stroke="hsl(var(--chart-1))"
                      fillOpacity={1}
                      fill="url(#workGradient)"
                      strokeWidth={3}
                    />
                    <Area
                      type="monotone"
                      dataKey="Study Economy"
                      stroke="hsl(var(--chart-2))"
                      fillOpacity={1}
                      fill="url(#studyGradient)"
                      strokeWidth={3}
                    />
                    <Area
                      type="monotone"
                      dataKey="Play Basketball"
                      stroke="hsl(var(--chart-3))"
                      fillOpacity={1}
                      fill="url(#basketballGradient)"
                      strokeWidth={3}
                    />
                    <Area
                      type="monotone"
                      dataKey="Reading"
                      stroke="hsl(var(--chart-4))"
                      fillOpacity={1}
                      fill="url(#readingGradient)"
                      strokeWidth={3}
                    />
                  </AreaChart>
                </ResponsiveContainer>
              </div>
            </div>
          </div>

          {/* Enhanced Pie Chart */}
          <div className="card-artistic rounded-3xl p-8">
            <div className="mb-6">
              <h2 className="text-2xl font-bold bg-gradient-to-r from-secondary to-accent bg-clip-text text-transparent">
                Activity Composition
              </h2>
              <p className="text-muted-foreground mt-2">Your time distribution at a glance</p>
            </div>
            <div className="chart-container">
              <div className="h-80">
                <ResponsiveContainer width="100%" height="100%">
                  <PieChart>
                    <defs>
                      {pieData.map((entry, index) => (
                        <linearGradient
                          key={`gradient-${index}`}
                          id={`pieGradient-${index}`}
                          x1="0"
                          y1="0"
                          x2="1"
                          y2="1"
                        >
                          <stop offset="0%" stopColor={entry.color} />
                          <stop offset="100%" stopColor={entry.color} stopOpacity={0.7} />
                        </linearGradient>
                      ))}
                    </defs>
                    <Pie
                      data={pieData}
                      cx="50%"
                      cy="50%"
                      innerRadius={60}
                      outerRadius={120}
                      paddingAngle={4}
                      dataKey="value"
                    >
                      {pieData.map((entry, index) => (
                        <Cell
                          key={`cell-${index}`}
                          fill={`url(#pieGradient-${index})`}
                          stroke="white"
                          strokeWidth={2}
                        />
                      ))}
                    </Pie>
                    <Tooltip
                      formatter={(value: number) => [`${value}h`, "Hours"]}
                      contentStyle={{
                        backgroundColor: "rgba(255, 255, 255, 0.95)",
                        border: "1px solid hsl(var(--primary))",
                        borderRadius: "12px",
                        backdropFilter: "blur(10px)",
                      }}
                    />
                  </PieChart>
                </ResponsiveContainer>
              </div>
              <div className="mt-6 space-y-3">
                {pieData.map((item, index) => (
                  <div
                    key={index}
                    className="flex items-center justify-between p-2 rounded-lg hover:bg-muted/50 transition-colors"
                  >
                    <div className="flex items-center gap-3">
                      <div className="h-4 w-4 rounded-full shadow-lg" style={{ backgroundColor: item.color }} />
                      <span className="text-sm font-medium text-foreground">{item.name}</span>
                    </div>
                    <span className="text-sm font-bold text-primary">
                      {((item.value / totalHours) * 100).toFixed(1)}%
                    </span>
                  </div>
                ))}
              </div>
            </div>
          </div>

          {/* Enhanced Top Activities */}
          <div className="card-artistic rounded-3xl p-8">
            <div className="mb-6">
              <h2 className="text-2xl font-bold bg-gradient-to-r from-accent to-primary bg-clip-text text-transparent">
                Top 5 Activities
              </h2>
              <p className="text-muted-foreground mt-2">Your most engaging pursuits</p>
            </div>
            <div className="space-y-6">
              {topActivities.map((activity, index) => (
                <div
                  key={index}
                  className="space-y-3 p-4 rounded-xl bg-gradient-to-r from-muted/30 to-muted/10 hover:from-muted/50 hover:to-muted/20 transition-all duration-300"
                >
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-3">
                      <div className="w-8 h-8 rounded-full bg-gradient-to-br from-primary to-secondary flex items-center justify-center text-white font-bold text-sm">
                        {index + 1}
                      </div>
                      <h4 className="font-semibold text-foreground">{activity.name}</h4>
                    </div>
                    <span className="text-sm font-bold bg-gradient-to-r from-primary to-secondary bg-clip-text text-transparent">
                      {activity.time}
                    </span>
                  </div>
                  <div className="flex flex-wrap gap-2 ml-11">
                    {activity.keywords.map((keyword, keyIndex) => (
                      <Badge
                        key={keyIndex}
                        variant="secondary"
                        className="text-xs bg-gradient-to-r from-secondary/20 to-accent/20 hover:from-secondary/30 hover:to-accent/30 border-0 transition-all duration-200"
                      >
                        {keyword}
                      </Badge>
                    ))}
                  </div>
                  {index < topActivities.length - 1 && (
                    <div className="border-b border-gradient-to-r from-transparent via-border to-transparent ml-11" />
                  )}
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}
