"""
Tag generation prompts for LLM-powered activity categorization with taxonomy-first approach.
"""

import json
import os
from typing import List, Dict, Any
from ..core.models import TagGenerationContext


class TagPrompts:
    """Centralized prompts for tag generation with taxonomy integration."""
    
    _taxonomy_cache = None
    _synonyms_cache = None
    
    @classmethod
    def _load_taxonomy(cls) -> Dict[str, Any]:
        """Load taxonomy from resources if not cached."""
        if cls._taxonomy_cache is None:
            resources_dir = os.path.join(os.path.dirname(__file__), '..', 'resources')
            taxonomy_path = os.path.join(resources_dir, 'tag_taxonomy.json')
            try:
                with open(taxonomy_path, 'r', encoding='utf-8') as f:
                    cls._taxonomy_cache = json.load(f)
            except FileNotFoundError:
                print("Warning: tag_taxonomy.json not found, using basic taxonomy")
                cls._taxonomy_cache = {"taxonomy": {}}
        return cls._taxonomy_cache
    
    @classmethod
    def _load_synonyms(cls) -> Dict[str, Any]:
        """Load synonyms from resources if not cached."""
        if cls._synonyms_cache is None:
            resources_dir = os.path.join(os.path.dirname(__file__), '..', 'resources')
            synonyms_path = os.path.join(resources_dir, 'synonyms.json')
            try:
                with open(synonyms_path, 'r', encoding='utf-8') as f:
                    cls._synonyms_cache = json.load(f)
            except FileNotFoundError:
                print("Warning: synonyms.json not found, using empty synonyms")
                cls._synonyms_cache = {"synonyms": {}}
        return cls._synonyms_cache

    @classmethod
    def get_individual_tag_system_prompt(cls) -> str:
        """System prompt for individual activity tag generation with taxonomy."""
        taxonomy = cls._load_taxonomy()
        taxonomy_tags = list(taxonomy.get("taxonomy", {}).keys())
        
        taxonomy_text = "\n".join([
            f"- {tag}: {info.get('description', '')}" 
            for tag, info in taxonomy.get("taxonomy", {}).items()
        ])
        
        return f"""You are an intelligent activity categorization system using a controlled taxonomy for consistent tagging.

TAXONOMY (MANDATORY - Use ONLY these tags):
{taxonomy_text}

CRITICAL RULES:
1. ONLY use tags from the taxonomy above - DO NOT create new tags
2. Generate 1-3 tags maximum per activity
3. Choose the most specific appropriate tag from the taxonomy
4. Consider bilingual content (English/Chinese mixed text is common)
5. Map personal shorthand to appropriate taxonomy tags
6. Include confidence reasoning for each tag

For each tag, provide:
- Tag name (from taxonomy only)
- Confidence score (0.0-1.0)
- Brief reasoning (why this tag fits)

PERSONAL CONTEXT AWARENESS:
- "bytediff", "bytedance" → work (coding/development context)
- "CI/CD过", "单测过" → work (testing/development)
- "接口会", "周会" → work (meetings)
- "smartHistory开发" → work (personal project)
- "厕所", "午休" → personal (rest/self-care)
- Mixed language is normal for this user"""

    @classmethod
    def get_individual_tag_user_prompt(cls, context: TagGenerationContext) -> str:
        """User prompt for individual activity tag generation with confidence scoring."""
        synonyms = cls._load_synonyms()
        
        # Find relevant synonyms for context
        activity_lower = context.activity_text.lower()
        relevant_synonyms = []
        for category, synonym_list in synonyms.get("synonyms", {}).items():
            if any(syn.lower() in activity_lower for syn in synonym_list):
                relevant_synonyms.append(f"{category}: {', '.join(synonym_list[:5])}")
        
        synonyms_text = "\n".join(relevant_synonyms[:3]) if relevant_synonyms else "None detected"
        
        return f"""ACTIVITY TO TAG:
Text: "{context.activity_text}"
Source: {context.source}
Duration: {context.duration_minutes} minutes
Time: {context.time_context or "not specified"}

DETECTED SYNONYM PATTERNS:
{synonyms_text}

RESPONSE FORMAT (JSON):
{{"tags": [{{"name": "taxonomy_tag", "confidence": 0.9, "reasoning": "why this fits"}}]}}

Analyze this activity and return 1-3 taxonomy tags with confidence scores and reasoning."""

    @classmethod
    def get_system_regeneration_system_prompt(cls) -> str:
        """System prompt for system-wide tag regeneration using taxonomy."""
        taxonomy = cls._load_taxonomy()
        taxonomy_text = "\n".join([
            f"- {tag}: {info.get('description', '')}" 
            for tag, info in taxonomy.get("taxonomy", {}).items()
        ])
        
        return f"""You are performing system-wide tag regeneration for a personal activity tracking system.

MANDATORY TAXONOMY (use ONLY these tags):
{taxonomy_text}

SYSTEM REGENERATION GOALS:
1. Re-tag all activities using ONLY the taxonomy above
2. Ensure consistent application across similar activities
3. Consider personal context patterns (bilingual, technical shorthand)
4. Optimize tag distribution for meaningful analytics
5. Apply confidence-based assignments

PERSONAL CONTEXT MAPPING:
- Technical work terms → "work"
- Personal routines → "personal" 
- Mixed language content → appropriate category
- Project-specific terms → "work" or relevant category

Return JSON with activity-to-tags mapping using taxonomy tags only."""

    @classmethod
    def get_system_regeneration_user_prompt(cls, activity_texts: List[str]) -> str:
        """User prompt for system-wide tag regeneration with taxonomy constraint."""
        activities_text = "\n".join([f"{i+1}. {text}" for i, text in enumerate(activity_texts[:50])])  # Reduced limit
        
        return f"""ACTIVITIES TO RE-TAG:
{activities_text}

RESPONSE FORMAT:
{{"activity_tags": {{"1": [{{"tag": "work", "confidence": 0.9}}], "2": [...]}}}}

Re-tag each activity using ONLY taxonomy tags with confidence scores. Consider patterns, personal context, and consistent categorization."""