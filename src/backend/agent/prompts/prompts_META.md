# AI Prompts Module

## Purpose
This module provides comprehensive AI prompts for the SmartHistory tagging system, implementing both basic tag generation and advanced personalized taxonomy creation. The prompts are designed to work with the taxonomy-first approach outlined in Milestone 2, enabling intelligent, context-aware activity categorization.

## Contents

### tag_prompts.py
**Purpose**: Core prompts for activity tag generation using taxonomy-first approach.
**Core Logic**: 
- **Individual Tag Generation**: Prompts for single activity tagging with confidence scoring
- **System-Wide Regeneration**: Prompts for batch re-tagging of historical activities
- **Taxonomy Integration**: Injects controlled vocabulary into prompts for consistent tagging
- **Bilingual Context**: Optimized for mixed Chinese-English content processing

**Key Classes**:
- `TagPrompts`: Static methods for tag generation prompts
- Enhanced with taxonomy loading and constraint enforcement
- Structured JSON response format for reliable parsing

**Prompt Types**:
- `get_individual_tag_system_prompt()`: System context with taxonomy constraints
- `get_individual_tag_user_prompt()`: Activity-specific prompts with synonym hints
- `get_system_regeneration_system_prompt()`: Batch processing context with taxonomy
- `get_system_regeneration_user_prompt()`: Multi-activity processing prompts

### taxonomy_prompts.py
**Purpose**: Advanced prompts for generating personalized taxonomies and synonym mappings from user activity data.
**Core Logic**:
- **Pattern Recognition**: Analyzes user activity patterns to create customized taxonomies
- **Personal Context Learning**: Extracts user-specific terminology and shortcuts
- **Bilingual Analysis**: Handles mixed language content and creates appropriate mappings
- **Adaptive Categorization**: Creates categories that reflect actual user behavior patterns

**Key Classes**:
- `TaxonomyPrompts`: Static methods for personalized taxonomy generation
- Designed for data-driven taxonomy creation and continuous learning
- Optimized for JSON response parsing with error handling

**Prompt Types**:
- `get_personalized_taxonomy_system_prompt()`: Context for taxonomy generation from user data
- `get_personalized_taxonomy_user_prompt()`: Formats activity data for analysis
- `get_personalized_synonyms_system_prompt()`: Context for synonym extraction
- `get_personalized_synonyms_user_prompt()`: Prepares data for synonym mapping

## System Interactions

### Integration with TagGenerator
The prompts module integrates directly with the enhanced TagGenerator:
```
TagGenerator → TagPrompts → OpenAI API → Structured Responses
                ↓
             TaxonomyPrompts → OpenAI API → Personalized Resources
```

### Dependency Chain
- `TagGenerator` loads and caches prompt classes
- `tag_prompts.py` provides real-time tagging capabilities
- `taxonomy_prompts.py` enables personalized learning and adaptation
- Both prompt types support fallback scenarios without LLM access

## Enhanced Capabilities (Milestone 2)

### Taxonomy-First Design
- **Controlled Vocabulary**: All prompts enforce taxonomy constraints to prevent tag proliferation
- **Consistency Enforcement**: Prompts include existing taxonomy context for consistent categorization
- **Validation Integration**: Structured responses enable automatic taxonomy validation

### Personalized Intelligence
- **Data-Driven Learning**: Prompts analyze actual user activity patterns
- **Personal Context Recognition**: Identifies user-specific projects, shortcuts, and terminology
- **Adaptive Categories**: Creates taxonomies that reflect individual user behavior rather than generic assumptions

### Bilingual Optimization
- **Mixed Language Support**: Prompts optimized for Chinese-English mixed content
- **Cultural Context**: Understanding of bilingual work environments and personal notation
- **Cross-Language Mapping**: Creates synonym mappings between languages and contexts

## Implementation Details

### Prompt Engineering Principles
- **Context Clarity**: Prompts provide comprehensive context and requirements
- **Response Structure**: Enforced JSON format for reliable parsing
- **Error Resilience**: Graceful degradation when API responses are malformed
- **Token Efficiency**: Optimized prompt length for API cost management

### Quality Assurance
- **Response Validation**: All prompts designed for structured, parseable responses
- **Fallback Handling**: Prompts include instructions for edge cases and ambiguity
- **Confidence Integration**: Prompts encourage confidence scoring for quality control

### Configuration Management
- **Dynamic Parameters**: Prompts accept configuration parameters (max categories, limits)
- **Resource Integration**: Prompts load and utilize existing taxonomy and synonym resources
- **Version Compatibility**: Designed for evolution with taxonomy schema changes

## Future Enhancements

### Advanced Personalization
- **Temporal Learning**: Prompts could incorporate time-based activity pattern learning
- **Context Expansion**: Enhanced understanding of project relationships and work contexts
- **Multi-User Support**: Prompts designed for potential multi-user taxonomy sharing

### Performance Optimization  
- **Caching Strategies**: Prompt results could be cached for similar activity patterns
- **Batch Processing**: Enhanced batch prompts for large-scale taxonomy updates
- **API Efficiency**: Further optimization for token usage and response times