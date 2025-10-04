export function generateTagColor(tagName: string): string {
  // Generate stable HSL color based on tag name hash
  let hash = 0
  for (let i = 0; i < tagName.length; i++) {
    const char = tagName.charCodeAt(i)
    hash = (hash << 5) - hash + char
    hash = hash & hash // Convert to 32-bit integer
  }

  // Use golden ratio for better distribution
  const goldenRatio = 0.618033988749
  const hue = Math.abs(hash * goldenRatio) % 360

  // Ensure good saturation and lightness for readability
  const saturation = 65 + (Math.abs(hash) % 20) // 65-85%
  const lightness = 45 + (Math.abs(hash >> 8) % 20) // 45-65%

  return `hsl(${hue}, ${saturation}%, ${lightness}%)`
}

export const getTagColor = generateTagColor

export function ensureColorContrast(colors: string[], minDistance = 30): string[] {
  // Ensure minimum hue distance between adjacent colors
  const adjustedColors = [...colors]

  for (let i = 1; i < adjustedColors.length; i++) {
    const currentHue = extractHue(adjustedColors[i])
    const prevHue = extractHue(adjustedColors[i - 1])

    const distance = Math.abs(currentHue - prevHue)
    if (distance < minDistance) {
      const newHue = (prevHue + minDistance) % 360
      adjustedColors[i] = adjustedColors[i].replace(/hsl\((\d+)/, `hsl(${newHue}`)
    }
  }

  return adjustedColors
}

function extractHue(hslColor: string): number {
  const match = hslColor.match(/hsl\((\d+)/)
  return match ? Number.parseInt(match[1]) : 0
}

export const colorblindSafePalette = [
  "#1f77b4", // blue
  "#ff7f0e", // orange
  "#2ca02c", // green
  "#d62728", // red
  "#9467bd", // purple
  "#8c564b", // brown
  "#e377c2", // pink
  "#7f7f7f", // gray
  "#bcbd22", // olive
  "#17becf", // cyan
]

export function getColorblindSafeColor(index: number): string {
  return colorblindSafePalette[index % colorblindSafePalette.length]
}
