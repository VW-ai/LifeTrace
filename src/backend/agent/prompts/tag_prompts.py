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

        Adds taxonomy and synonym guidance; requires tags to be from the
        allowed vocabulary. Output is still comma-separated tags to keep
        compatibility with current TagGenerator parsing.
        """
        allowed = TagPrompts._format_allowed_tags(calibration)
        synonyms_hint = TagPrompts._format_synonyms(calibration)

        return (
            "You are an activity tagging assistant that assigns 1–10 high-quality tags for time-tracking and analysis.\n\n"
            "Rules:\n"
            "- Prefer the recommended taxonomy below for the PRIMARY tag (make it the first tag).\n"
            "- You MAY introduce new tags if they better capture specific dimensions; keep them lowercase, snake_case, concise, and non-redundant.\n"
            "- Aim for layered meaning and diversity across dimensions (avoid near-duplicates):\n"
            "  • category: work, personal, health, social, admin\n"
            "  • activity_type/mode: meeting, development, writing, study, exercise\n"
            "  • domain/topic: auth, ci_cd, frontend, hiring, database\n"
            "  • tool/tech: python, react, vscode, github_actions, notion\n"
            "  • context: commute, meals, remote, office, deep_work, quick_task\n"
            "  • outcome/goal: planning, review, delivery, bugfix, refactor\n"
            "- Prefer specific canonical tags over vague ones (e.g., development over work) unless no better fit exists.\n"
            "- Consider synonym cues when mapping to canonical tags.\n\n"
            f"Recommended tags (taxonomy):\n{allowed}\n\n"
            f"Synonym cues: {synonyms_hint}\n\n"
            "Think carefully about distinct dimensions; do not output reasoning.\n"
            "Output: return ONLY the selected tags (1–10), comma-separated (no JSON, no extra text)."
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
            "You are an expert in building practical tagging systems for personal activity logs.\n"
            "Your task: create TWO DISTINCT outputs:\n"
            "1. TAXONOMY: hierarchical categories (parent → children) representing activity types\n"
            "2. SYNONYMS: alternative words/phrases that should map to the same concept\n\n"
            "TAXONOMY should be hierarchical organization (e.g., 'work' → ['meetings', 'coding', 'planning'])\n"
            "SYNONYMS should be alternative terms (e.g., 'meetings' → ['calls', 'video_chat', 'standup', 'sync'])\n\n"
            "Guidelines:\n"
            "- Be concrete and specific (prefer 'standup' over 'communication')\n"
            "- Taxonomy: organize activities by type/domain\n"
            "- Synonyms: find alternative ways people describe the same activity\n"
            "- Keep categories under 10, subcategories under 8 per parent\n"
            "- Total unique tags should be under 80"
        )

    @staticmethod
    def get_taxonomy_builder_user_prompt(activity_examples: List[str]) -> str:
        """User prompt for taxonomy building with activity examples."""
        examples_text = "\n".join(activity_examples)
        
        return (
            "Analyze these activity examples and create a JSON with two DISTINCT fields:\n\n"
            "1) 'taxonomy': Hierarchical organization of activity types\n"
            "   - Keys: broad activity domains (e.g., 'work', 'health', 'personal')\n"
            "   - Values: specific activity types within that domain\n"
            "   - Example: {'work': ['meetings', 'coding', 'planning'], 'health': ['exercise', 'meals', 'sleep']}\n\n"
            "2) 'synonyms': Alternative terms for the SAME activity\n"
            "   - Keys: canonical activity names (from taxonomy or common terms)\n"
            "   - Values: alternative words/phrases people use for that activity\n"
            "   - Example: {'meetings': ['calls', 'standup', 'sync', 'conference'], 'exercise': ['gym', 'workout', 'training']}\n\n"
            "Requirements:\n"
            "- Base categories on actual data patterns below\n"
            "- Taxonomy: organize by WHAT TYPE of activity\n"
            "- Synonyms: capture HOW PEOPLE SAY the same thing\n"
            "- Be specific and practical (avoid generic terms)\n"
            "- Return ONLY valid JSON\n\n"
            f"Activity Examples:\n{examples_text}"
        )

    @staticmethod
    def format_activity_example(item_type: str, title: str = "", text: str = "", max_text_length: int = 180) -> str:
        """Format a single activity example for prompt inclusion."""
        cleaned_text = text.replace("\n", " ")
        
        if title:
            return f"- {item_type} | {title} :: {cleaned_text[:max_text_length]}"
        else:
            return f"- {item_type} :: {cleaned_text[:max_text_length + 20]}"
