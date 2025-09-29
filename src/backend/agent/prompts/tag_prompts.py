"""
Tag generation prompts for LLM-powered activity categorization.

Updated for taxonomy-first tagging with confidences (Phase 2).
Output remains backward-compatible (comma-separated tags) for the
individual tagging path used by TagGenerator.
"""

from typing import List, Dict, Optional
from ..core.models import TagGenerationContext


class TagPrompts:
    """Centralized prompts for tag generation."""

    @staticmethod
    def _format_allowed_tags(calibration: Optional[Dict]) -> str:
        if not calibration:
            return "- work, meeting, development, study, exercise, meals, planning, writing, communication, admin, social, health, maintenance, hobby"
        tax: Dict = calibration.get("taxonomy", {}) or {}
        # Flatten top-level + children as allowed canonical vocabulary
        allowed = list(tax.keys())
        for parent, children in tax.items():
            allowed.extend(children or [])
        # Deduplicate while preserving order
        seen = set()
        ordered = []
        for t in allowed:
            if t and t not in seen:
                seen.add(t)
                ordered.append(t)
        return "- " + ", ".join(ordered)

    @staticmethod
    def _format_synonyms(calibration: Optional[Dict]) -> str:
        if not calibration:
            return "(e.g., development~code/coding/debug; meals~lunch/dinner/breakfast)"
        syn: Dict = calibration.get("synonyms", {}) or {}
        # Keep it concise to avoid overly long prompts
        parts = []
        for i, (canon, words) in enumerate(syn.items()):
            if i >= 12:
                parts.append("…")
                break
            sample = ", ".join(words[:6]) if words else ""
            parts.append(f"{canon} ~ {sample}")
        return "; ".join(parts)

    @staticmethod
    def get_individual_tag_system_prompt(calibration: Optional[Dict] = None) -> str:
        """System prompt for individual activity tag generation.

        Uses principle-based prompt engineering without constraining examples.
        """
        allowed = TagPrompts._format_allowed_tags(calibration)
        synonyms_hint = TagPrompts._format_synonyms(calibration)

        return (
            "You are a creative activity analyst who generates insightful English tags that capture both the essence and context of human activities.\n\n"
            
            "CREATIVE MANDATE:\n"
            "• Think beyond surface descriptions to capture deeper meaning and context\n"
            "• Invent precise tags when existing vocabulary falls short\n"
            "• Consider multiple dimensions simultaneously: what, how, why, where, with what\n"
            "• Generate 4-8 tags that collectively tell the complete story\n\n"
            
            "DIMENSIONAL EXPLORATION (be creative in each space):\n"
            "→ Core activity type and its fundamental nature\n"
            "→ Method, medium, or approach used\n"
            "→ Subject domains, fields, or areas of knowledge involved\n"
            "→ Tools, technologies, platforms, or resources engaged\n"
            "→ Purpose, context, outcome, or situational factors\n\n"
            
            "QUALITY THROUGH CREATIVITY:\n"
            "• Prefer specific, descriptive terms over generic categories\n"
            "• Each tag should add unique dimensional value\n"
            "• Balance broad categorization with precise details\n"
            "• Consider intensity, complexity, and emotional context when relevant\n\n"
            
            "CONSTRAINTS (minimal for maximum creativity):\n"
            "• ALL tags in English (translate concepts from other languages)\n"
            "• Use lowercase_underscore_format for compound concepts\n"
            "• Avoid meaningless meta-tags that don't describe actual activities\n\n"
            
            f"VOCABULARY FOUNDATION (expand beyond these when needed):\n{allowed}\n\n"
            f"SYNONYM PATTERNS: {synonyms_hint}\n\n"
            
            "Trust your analytical creativity. Be specific. Capture the full context."
        )

    @staticmethod
    def get_individual_tag_user_prompt(context: TagGenerationContext) -> str:
        """User prompt for individual activity tag generation."""
        existing_tags_text = ", ".join(context.existing_tags[:50]) if context.existing_tags else "None"

        return (
            f"Activity: \"{context.activity_text}\"\n"
            f"Source: {context.source}\n"
            f"Duration: {context.duration_minutes} minutes\n"
            f"Time context: {context.time_context or 'not specified'}\n\n"
            f"Existing tags to consider reusing (if appropriate): {existing_tags_text}\n\n"
            "Select 1–10 tags: start with a primary high-level tag (prefer from the recommended taxonomy), then add distinct dimension tags where useful.\n"
            "Return ONLY the tags separated by commas."
        )

    @staticmethod
    def get_system_regeneration_system_prompt(calibration: Optional[Dict] = None) -> str:
        """System prompt for system-wide tag regeneration.

        Enforces taxonomy-first outputs and consistent naming.
        """
        allowed = TagPrompts._format_allowed_tags(calibration)
        return (
            "You are consolidating a user's activities into a consistent yet flexible tag set.\n\n"
            "Goals:\n"
            "1) Prefer the recommended taxonomy for the primary tag; you may introduce new tags where needed.\n"
            "2) Assign 1–10 tags per activity (lowercase, snake_case), maximizing coverage across distinct dimensions without redundancy.\n"
            "3) Provide layered meaning: primary category + specific dimension tags (type, topic, tool, context, outcome).\n\n"
            f"Recommended tags (taxonomy):\n{allowed}\n\n"
            "Output: Return a JSON object where keys are activity numbers (1-based) and values are arrays of 1–10 tags."
        )

    @staticmethod
    def get_system_regeneration_user_prompt(activity_texts: List[str]) -> str:
        """User prompt for system-wide tag regeneration."""
        activities_text = "\n".join([f"{i+1}. {text}" for i, text in enumerate(activity_texts[:100])])  # Limit for API

        return (
            "Analyze these activities and assign canonical tags from the allowed taxonomy.\n\n"
            f"{activities_text}\n\n"
            "Return a JSON object where keys are activity numbers (1, 2, 3, ...) and values are arrays of 1–3 tags."
        )

    # ============================================================================
    # TAXONOMY BUILDING PROMPTS
    # ============================================================================

    @staticmethod
    def get_taxonomy_builder_system_prompt() -> str:
        """System prompt for building taxonomy and synonyms from activity corpus."""
        return (
            "You are a creative taxonomy architect who discovers natural patterns in human activity data.\n\n"
            
            "Your mission: analyze real activity patterns to build TWO complementary systems:\n"
            "1. TAXONOMY: hierarchical organization reflecting how activities naturally cluster\n"
            "2. SYNONYMS: mapping of different ways people express the same concepts\n\n"
            
            "CREATIVE APPROACH:\n"
            "• Let the data reveal its own patterns rather than imposing predetermined categories\n"
            "• Discover unexpected connections and groupings\n"
            "• Balance broad utility with specific precision\n"
            "• Consider cultural, contextual, and personal variations in activity description\n\n"
            
            "DESIGN PRINCIPLES:\n"
            "• Taxonomy should reflect natural activity relationships and workflows\n"
            "• Synonyms should capture the rich variety of human expression\n"
            "• Optimize for both discovery (finding activities) and organization (understanding patterns)\n"
            "• All concepts in English for consistency"
        )

    @staticmethod
    def get_taxonomy_builder_user_prompt(activity_examples: List[str]) -> str:
        """User prompt for taxonomy building with activity examples."""
        examples_text = "\n".join(activity_examples)
        
        return (
            "Analyze this activity data and discover its natural organizational patterns.\n\n"
            "Create a JSON response with two fields:\n\n"
            "'taxonomy': Hierarchical organization that emerges from the data\n"
            "   → Keys: major activity domains you discover\n"
            "   → Values: specific activities within each domain\n\n"
            "'synonyms': Alternative expressions for the same concepts\n"
            "   → Keys: canonical terms from your taxonomy or common activities\n"
            "   → Values: different ways people express that same concept\n\n"
            "DISCOVERY APPROACH:\n"
            "• Look for natural clusters and relationships in the data\n"
            "• Identify recurring themes and patterns\n"
            "• Notice cultural/linguistic variations and translate concepts to English\n"
            "• Balance specificity with broad applicability\n\n"
            f"Activity Data:\n{examples_text}\n\n"
            "Return valid JSON only."
        )

    @staticmethod
    def format_activity_example(item_type: str, title: str = "", text: str = "", max_text_length: int = 180) -> str:
        """Format a single activity example for prompt inclusion."""
        cleaned_text = text.replace("\n", " ")
        
        if title:
            return f"- {item_type} | {title} :: {cleaned_text[:max_text_length]}"
        else:
            return f"- {item_type} :: {cleaned_text[:max_text_length + 20]}"
