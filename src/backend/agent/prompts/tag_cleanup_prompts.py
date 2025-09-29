"""
Tag Cleanup Prompts

Centralized prompts for AI-powered tag cleanup and merging operations.
Follows creativity-encouraging principles while maintaining quality standards.
"""

from typing import List, Dict, Any


class TagCleanupPrompts:
    """Centralized prompts for tag cleanup operations."""

    @staticmethod
    def get_tag_analysis_system_prompt() -> str:
        """System prompt for analyzing tag meaningfulness and merging opportunities."""
        return """
You are an expert at analyzing activity tracking tags for quality and consistency.

Your mission: Identify meaningless tags AND find merge opportunities for better tag organization.

CREATIVE ANALYSIS APPROACH:
• Think about what makes tags truly useful for understanding human activities
• Consider the full context - usage patterns, activity examples, and semantic relationships
• Look for natural groupings and consolidation opportunities

TAG QUALITY ASSESSMENT:

MEANINGFUL TAGS capture specific, actionable information:
→ Specific activities that describe what someone actually did
→ Tools, technologies, or methods that add context
→ Temporal, spatial, or social contexts that matter
→ Outcomes or purposes that explain why

MEANINGLESS TAGS to remove:
→ System artifacts that don't describe real activities (scheduled_activity, activities, tasks, events)
→ Generic process descriptors (effective_time_management, time_management, productivity)
→ Meta-concepts so generic they provide no insight (working, general, misc, other, stuff)
→ Broad categorizations instead of specific actions (management, planning, organization)
→ Malformed or accidental tags
→ Overly abstract terms with no practical value

MERGE OPPORTUNITIES to consolidate:
→ Singular/plural variants (meeting/meetings, writing/writings)
→ Synonymous terms (gym/exercise, coding/development if same context)
→ Typos or slight variations of the same concept
→ Different spellings or formats of identical meanings

ANALYSIS PRINCIPLES:
• Be aggressive about removing generic tags - err on the side of removal
• Ask: "Does this tag tell me what specific action someone took?"
• Frequency doesn't make meaningless tags meaningful
• Remove tags that could apply to almost any activity
• Preserve only tags that add specific, actionable context
• All output tags must be in English, lowercase_underscore_format

CONCRETE EXAMPLES TO REMOVE:
- scheduled_activity (too generic - what KIND of activity?)
- effective_time_management (process descriptor, not action)
- productivity (outcome measure, not specific activity)
- planning (too broad - planning what?)
- working (meta-concept, tells us nothing specific)

Trust your analytical judgment. Be aggressive but preserve genuinely useful specificity.
"""

    @staticmethod
    def get_tag_analysis_user_prompt(tags_data: str) -> str:
        """User prompt for tag analysis with actual tag data."""
        return f"""
Analyze these activity tracking tags and identify cleanup actions needed:

{tags_data}

For each tag, determine:
1. Should it be KEPT (meaningful and unique)
2. Should it be REMOVED (meaningless/problematic) 
3. Should it be MERGED into another tag (redundant/variant)

Respond in JSON format:
{{
  "actions": [
    {{
      "tag": "tag_name",
      "action": "keep|remove|merge", 
      "reason": "clear explanation",
      "confidence": 0.0-1.0,
      "merge_into": "target_tag_name (only for merge action)"
    }}
  ]
}}

Focus on consolidating similar tags while preserving meaningful distinctions.
"""

    @staticmethod 
    def get_merge_validation_system_prompt() -> str:
        """System prompt for validating proposed tag merges."""
        return """
You are validating proposed tag merges to ensure they preserve meaning and improve organization.

Your role: Review merge proposals and confirm they make semantic sense.

VALIDATION CRITERIA:

APPROVE MERGES when:
• Tags represent the same core concept (meeting/meetings)
• One tag is clearly a variant of another (gym/exercise in fitness context)
• Merging would reduce redundancy without losing information
• The target tag is more standard/canonical

REJECT MERGES when:
• Tags represent distinct concepts despite similarity
• Merging would lose important contextual information
• Different usage patterns suggest different meanings
• The merge would create confusion

IMPROVEMENT SUGGESTIONS:
• Propose better canonical forms if needed
• Suggest alternative merge targets
• Recommend keeping distinct if truly different

Be conservative - only approve merges you're confident about.
"""

    @staticmethod
    def get_merge_validation_user_prompt(merge_proposals: str) -> str:
        """User prompt for validating specific merge proposals."""
        return f"""
Review these proposed tag merges and validate each one:

{merge_proposals}

For each proposal, respond whether to approve, reject, or modify:

{{
  "validations": [
    {{
      "source_tag": "original_tag",
      "target_tag": "proposed_target", 
      "decision": "approve|reject|modify",
      "reason": "explanation",
      "alternative_target": "better_target (only if modify)"
    }}
  ]
}}
"""

    @staticmethod
    def format_tags_for_analysis(tags_with_context: List[Dict[str, Any]]) -> str:
        """Format tag data for AI analysis."""
        formatted_tags = []
        
        for tag_info in tags_with_context:
            tag_line = f"• '{tag_info['name']}' (used {tag_info['usage_count']} times)"
            
            if tag_info.get('sample_activities'):
                activities = [act[:40] + "..." if len(act) > 40 else act 
                            for act in tag_info['sample_activities'][:3]]
                tag_line += f"\n  Examples: {' | '.join(activities)}"
            
            formatted_tags.append(tag_line)
        
        return '\n'.join(formatted_tags)

    @staticmethod
    def format_merge_proposals(proposals: List[Dict[str, Any]]) -> str:
        """Format merge proposals for validation."""
        formatted = []
        
        for proposal in proposals:
            formatted.append(
                f"• Merge '{proposal['source']}' → '{proposal['target']}'\n"
                f"  Reason: {proposal['reason']}\n"
                f"  Confidence: {proposal['confidence']:.1%}\n"
                f"  Usage: {proposal['source_usage']} → {proposal['target_usage']} occurrences"
            )
        
        return '\n'.join(formatted)