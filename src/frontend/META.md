# Frontend META Documentation

## Purpose
The frontend layer of SmartHistory provides a **Dadaism-inspired** user interface for activity tracking and productivity visualization. It consumes the REST API backend to present user data through unconventional, artistic, and playfully disruptive design elements that challenge traditional dashboard aesthetics.

## Dadaism Design Philosophy
Our frontend embraces Dadaism principles:
- **Anti-rational layouts**: Asymmetrical compositions that break conventional grid systems
- **Collage aesthetics**: Mixing typography, imagery, and data visualizations in unexpected ways  
- **Playful disruption**: Interactive elements that surprise and delight users
- **Found object integration**: Using everyday UI elements in unexpected contexts
- **Spontaneous composition**: Dynamic layouts that change based on data patterns

## Architecture Overview

### Core Components (`/components/`)
- **Atomic UI elements** following REGULATION.md single-purpose principle
- Each component handles one visual or functional responsibility
- Dadaist styling with unconventional color schemes and typography

### Layout System (`/layouts/`)  
- **Anti-grid layouts** that break traditional dashboard patterns
- **Collage-style** compositions mixing charts, text, and imagery
- **Asymmetrical balance** creating visual tension and interest

### Data Visualization (`/visualizations/`)
- **Deconstructed charts** that present data in artistic ways
- **Typography as data** where text size/style represents metrics
- **Color chaos** using unexpected palettes for different data categories

### API Integration (`/api/`)
- **Clean REST client** for backend communication following atomic principles
- **Error handling** with Dadaist error messages and recovery flows
- **Real-time updates** with playful loading states and transitions

### Styling System (`/styles/`)
- **Dadaist color palettes** with bold, contrasting combinations
- **Typography mixing** multiple fonts and sizes unconventionally
- **Chaos-ordered layouts** that appear random but follow design logic

## Technology Stack
- **Framework**: Modern JavaScript framework (React/Vue/Svelte TBD)
- **Styling**: CSS-in-JS or Tailwind with custom Dadaist extensions  
- **Charts**: Custom visualization library or heavily customized Chart.js
- **API Client**: Axios or Fetch with comprehensive error handling
- **Testing**: Component testing following atomic testing principles

## File Organization Principles
Following REGULATION.md:
- **Atomic file structure**: Each file serves a single, well-defined purpose
- **Co-located documentation**: Each major component has accompanying `*_META.md`
- **Proper folder hierarchy**: Components organized by functionality, not file type
- **Google Style**: Clean, documented code with proper commenting

## Integration Points
- **Backend API**: Consumes all 20+ REST endpoints from SmartHistory API
- **Authentication**: API key management and secure session handling  
- **Real-time Processing**: Live updates for data processing status
- **Data Export**: User-friendly interfaces for data download/export

## Development Goals
1. **Artistic Data Presentation**: Make productivity data beautiful and engaging
2. **Unconventional UX**: Challenge users' expectations in delightful ways  
3. **Functional Art**: Ensure Dadaist elements enhance rather than hinder usability
4. **Responsive Design**: Dadaist principles adapted for all screen sizes
5. **Performance**: Fast, smooth interactions despite complex visual elements