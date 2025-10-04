export function formatDate(date: string | Date): string {
  const d = typeof date === "string" ? new Date(date) : date
  return d.toLocaleDateString("en-US", {
    year: "numeric",
    month: "short",
    day: "numeric",
  })
}

export function formatTime(time: string): string {
  const [hours, minutes] = time.split(":")
  const hour = Number.parseInt(hours)
  const ampm = hour >= 12 ? "PM" : "AM"
  const displayHour = hour % 12 || 12
  return `${displayHour}:${minutes} ${ampm}`
}

export function formatDuration(minutes: number): string {
  if (minutes < 60) {
    return `${minutes}m`
  }

  const hours = Math.floor(minutes / 60)
  const remainingMinutes = minutes % 60

  if (remainingMinutes === 0) {
    return `${hours}h`
  }

  return `${hours}h ${remainingMinutes}m`
}

export function getDateRange(period: "1w" | "1m" | "3m" | "1y" | "all"): {
  start: string
  end: string
} {
  const end = new Date()
  const start = new Date()

  switch (period) {
    case "1w":
      start.setDate(end.getDate() - 7)
      break
    case "1m":
      start.setMonth(end.getMonth() - 1)
      break
    case "3m":
      start.setMonth(end.getMonth() - 3)
      break
    case "1y":
      start.setFullYear(end.getFullYear() - 1)
      break
    case "all":
      start.setFullYear(2020) // Reasonable start date
      break
  }

  return {
    start: start.toISOString().split("T")[0],
    end: end.toISOString().split("T")[0],
  }
}

export function isDateInRange(date: string, range: { start: string; end: string }): boolean {
  const d = new Date(date)
  const start = new Date(range.start)
  const end = new Date(range.end)

  return d >= start && d <= end
}
