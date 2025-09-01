# Components META Documentation

## Purpose
Atomic UI components following both REGULATION.md principles and Dadaist design philosophy. Each component serves a single, well-defined purpose while embracing unconventional aesthetics.

## Structure

### `/atomic/`
**Single-responsibility UI elements** - the building blocks of our Dadaist interface:
- `Button/` - Anti-traditional buttons with playful hover states and unexpected shapes
- `Typography/` - Text components mixing fonts, sizes, and orientations unconventionally  
- `Input/` - Form elements with surprising visual treatments and interactions
- `Icon/` - Custom iconography with collage-style and deconstructed imagery
- `Loader/` - Loading states that entertain and surprise users

### `/molecules/`
**Combined atomic elements** serving specific functional purposes:
- `DataCard/` - Information display with asymmetrical layouts and bold typography
- `ChartWrapper/` - Container for visualizations with artistic framing elements
- `FilterPanel/` - Data filtering with drag-and-drop collage-style interactions
- `StatusIndicator/` - System status display with playful error messages and states
- `TagCloud/` - Activity tags presented as floating, interactive art pieces

### `/organisms/`
**Complex components** combining molecules and atoms:
- `Dashboard/` - Main interface with anti-grid layouts and dynamic composition  
- `ActivityTimeline/` - Time-based activity display as artistic timeline collage
- `InsightsPanels/` - Analytics display with deconstructed chart presentations
- `SettingsInterface/` - Configuration UI with playful, discovery-based navigation
- `ProcessingStatus/` - Real-time processing updates with artistic progress indicators

## Design Principles
Each component follows:

### **Atomic Responsibility**
- Single, clear purpose (REGULATION.md compliance)
- Minimal external dependencies
- Easy to test and maintain

### **Dadaist Aesthetics**
- **Anti-rational layouts**: Challenging traditional UI expectations
- **Typographic play**: Mixing fonts, sizes, orientations for visual interest
- **Color disruption**: Unexpected color combinations that create energy
- **Interactive surprise**: Hover states and animations that delight users
- **Collage integration**: Layered visual elements creating depth and interest

### **Functional Art**
- Visual experimentation never compromises usability
- Accessibility maintained through proper semantic HTML and ARIA labels
- Performance optimized despite complex visual treatments
- Responsive design adapting Dadaist principles to all screen sizes

## File Organization
Each component follows atomic structure:
```
ComponentName/
├── index.ts                 # Export interface
├── ComponentName.tsx        # Main component logic
├── ComponentName.styles.ts  # Styled components with Dadaist themes
├── ComponentName.test.tsx   # Comprehensive testing
├── ComponentName_META.md    # Component-specific documentation
└── types.ts                 # TypeScript interfaces
```

## Integration Requirements
- **API Integration**: Components consume backend data through `../api/` clients
- **State Management**: Uses React Context or Redux for global state  
- **Styling System**: Integrates with `../styles/` theme and utility classes
- **Type Safety**: All components fully typed with `../types/` interfaces