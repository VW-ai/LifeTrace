"""
Tag generation prompts for LLM-powered activity categorization.
"""

from typing import List
from ..core.models import TagGenerationContext


class TagPrompts:
    """Centralized prompts for tag generation."""

    @staticmethod
    def get_individual_tag_system_prompt() -> str:
        """System prompt for individual activity tag generation."""
        return """You are an intelligent activity categorization system. Your job is to generate 1-3 relevant tags for activities to help with time tracking and analysis.

IMPORTANT RULES:
1. ALWAYS try to reuse existing tags when appropriate
2. Generate 1-10 tags maximum per activity  
3. Tags should be concise (1-4 words)
4. Use consistent naming (e.g., "web_development" not "Web Development")
5. Focus on the nature of the activity, not specific details

Tag examples: programming, meeting, study, exercise, meal, commute, reading, planning, design, debugging"""

    @staticmethod
    def get_individual_tag_user_prompt(context: TagGenerationContext) -> str:
        """User prompt for individual activity tag generation."""
        existing_tags_text = ", ".join(context.existing_tags[:50]) if context.existing_tags else "None"
        
        return f"""Activity: "{context.activity_text}"
Source: {context.source}
Duration: {context.duration_minutes} minutes
Time context: {context.time_context or "not specified"}

Existing tags to consider reusing: {existing_tags_text}

Generate 1-3 appropriate tags for this activity. Return only the tags separated by commas, nothing else."""

    @staticmethod
    def get_system_regeneration_system_prompt() -> str:
        """System prompt for system-wide tag regeneration."""
        return """You are analyzing a user's time tracking data to generate a consistent set of activity tags. 

GOALS:
1. Create a consolidated set of 10-20 main activity tags
2. Tags should cover all major activity categories 
3. Use consistent naming (lowercase, underscore_separated)
4. Focus on high-level categories, not specific tasks

Return only a JSON object mapping each activity to 1-3 tags from your consolidated set."""

    @staticmethod
    def get_system_regeneration_user_prompt(activity_texts: List[str]) -> str:
        """User prompt for system-wide tag regeneration."""
        activities_text = "\n".join([f"{i+1}. {text}" for i, text in enumerate(activity_texts[:100])])  # Limit for API
        
        return f"""Analyze these activities and generate consistent tags:

{activities_text}

Return a JSON object where keys are activity numbers (1, 2, 3...) and values are arrays of 1-3 tags."""