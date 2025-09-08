# Hierarchical Tagging System

## Purpose
This document describes the three-layer hierarchical tagging system that extends SmartHistory's existing taxonomy-first tagging approach with enhanced granularity for better activity categorization.

## Core Logic

### Three-Layer Architecture
1. **Nature Layer (Layer 1)**: High-level activity type classification (work, study, personal, etc.)
   - Uses existing taxonomy-first tagging system
   - Leverages confidence scoring and fuzzy matching
   - Maintains compatibility with current processed activities

2. **Subject Layer (Layer 2)**: Domain-specific classification within nature categories
   - Web3 study, smartHistory development, CFA preparation
   - Travel destinations, meeting types, exercise categories
   - Maps personal shortcuts and bilingual content to subjects

3. **Project Layer (Layer 3)**: Optional specific project/context identification
   - Individual CS projects, specific work components
   - Optional because not all activities have specific project context
   - Enables granular tracking of focused work streams

### Key Components

#### hierarchical_taxonomy.json
**Purpose**: Structured taxonomy defining all three layers with keywords and relationships.
**Structure**:
```json
{
  "taxonomy": {
    "work": {
      "subjects": {
        "bytediff": {"keywords": [...], "projects": [...]},
        "smartHistory": {"keywords": [...], "projects": [...]}
      }
    }
  }
}
```

#### TagGenerator Enhancements
**New Methods**:
- `generate_hierarchical_tags_for_activity()`: Main entry point for three-layer tagging
- `_detect_subject_tag()`: Layer 2 subject detection using keyword matching
- `_detect_project_tag()`: Layer 3 project detection using content analysis
- `generate_hierarchical_tags_batch()`: Batch processing for multiple activities
- `get_hierarchical_summary()`: Statistics and coverage analysis

## System Interactions

### Integration with Existing System
- **Layer 1**: Reuses existing `generate_tags_with_confidence_for_activity()`
- **Fallback**: Maintains compatibility when hierarchical taxonomy unavailable
- **Database**: Compatible with existing schema, adds hierarchical metadata

### Calendar-as-Query Architecture Alignment
- **Personal Shortcuts**: "bytediff debug" → work/bytediff/debug hierarchy
- **Bilingual Support**: Mixed language content properly categorized at all layers
- **Context Enhancement**: Rich Notion context helps identify subjects and projects

## Implementation Benefits

### Enhanced Granularity
- **Nature**: Maintains broad categorization for overview analytics
- **Subject**: Enables domain-specific insights (time spent on Web3 vs CFA study)
- **Project**: Tracks specific work streams without overwhelming complexity

### Personal Intelligence
- **Shorthand Recognition**: Personal abbreviations mapped through all layers
- **Context Learning**: Calendar entries enhanced with subject/project context
- **Adaptive Classification**: System learns user-specific patterns

### Future-Ready Architecture
- **Scalability**: Three-layer structure supports growing complexity
- **Extensibility**: Easy to add new subjects/projects as user activities evolve
- **Analytics**: Rich hierarchy enables sophisticated time tracking insights

## Configuration and Usage

### Confidence Thresholds
- **Subject Detection**: Minimum 0.3 confidence required
- **Project Detection**: Keyword-based with length-weighted confidence
- **Fallback Behavior**: Falls back to nature-only when lower layers fail

### Batch Processing
- **Efficiency**: Process multiple activities in single operation
- **Statistics**: Generate coverage and confidence analytics
- **Integration**: Compatible with existing activity processing pipeline

## Performance Considerations
- **Memory Efficient**: Hierarchical taxonomy loaded once and cached
- **Fast Lookup**: O(1) taxonomy access with keyword matching
- **Minimal Overhead**: Builds on existing tagging infrastructure without duplication