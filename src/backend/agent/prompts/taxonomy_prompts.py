"""
Prompts for AI-driven personalized taxonomy generation.
"""

from typing import List


class TaxonomyPrompts:
    """Prompts for generating personalized taxonomies from user data."""
    
    @staticmethod
    def get_personalized_taxonomy_system_prompt(max_categories: int = 20) -> str:
        """System prompt for generating personalized taxonomy from user data."""
        return f"""You are analyzing personal activity data to create a customized activity taxonomy.

TASK: Create a personalized taxonomy of {max_categories} main activity categories based on the user's actual data patterns.

REQUIREMENTS:
1. Categories should reflect the user's actual lifestyle and work patterns
2. Include both English and Chinese terms where relevant (user is bilingual)
3. Capture personal shortcuts and project names (e.g., "bytediff", "smartHistory")
4. Balance work, personal, and routine activities
5. Each category should have description, keywords, and sub_tags

ANALYSIS APPROACH:
- Identify recurring patterns in activity descriptions
- Group similar activities under meaningful categories
- Extract personal terminology and technical shortcuts
- Consider time-of-day patterns and duration hints
- Balance granularity - not too specific, not too generic

RESPONSE FORMAT:
{{"taxonomy": {{"category_name": {{"description": "Clear category description", "keywords": ["keyword1", "keyword2", ...], "sub_tags": ["sub1", "sub2", ...]}}}}}}

Focus on creating categories that will actually be useful for organizing THIS user's specific activities."""

    @staticmethod
    def get_personalized_taxonomy_user_prompt(activity_texts: List[str]) -> str:
        """User prompt with activity data for taxonomy generation."""
        activities_text = "\n".join([f"{i+1}. {text}" for i, text in enumerate(activity_texts)])
        
        return f"""ACTIVITY DATA TO ANALYZE:
{activities_text}

Generate a personalized taxonomy that best categorizes these activities. Focus on the user's actual patterns, not generic categories.

Consider:
- What are the main types of activities this person does?
- What personal/work projects appear repeatedly?
- What bilingual patterns are present?
- What routine activities need separate categories?
- How can these be grouped into 15-20 meaningful categories?"""

    @staticmethod
    def get_personalized_synonyms_system_prompt() -> str:
        """System prompt for generating personalized synonyms from user data."""
        return """You are analyzing personal activity data to create a customized synonym mapping.

TASK: Identify recurring personal terms, shortcuts, and patterns in the user's activity descriptions.

FOCUS ON:
1. Personal project names and shortcuts (e.g., "bytediff" → work-related)
2. Bilingual patterns (Chinese-English mixed usage)
3. Personal routine descriptions (e.g., "厕所" → personal care)
4. Technical abbreviations and work terms
5. Recurring activity patterns
6. Time-specific language patterns
7. Informal vs formal descriptions

ANALYSIS APPROACH:
- Extract frequently used terms and phrases
- Identify personal shortcuts and abbreviations
- Map bilingual terminology (Chinese-English)
- Group semantically similar expressions
- Identify project-specific vocabulary
- Consider context clues and co-occurrence patterns

RESPONSE FORMAT:
{
  "synonyms": {
    "category": ["synonym1", "synonym2", ...]
  },
  "personal_shortcuts": {
    "shortcut": ["category1", "category2"]
  },
  "technical_abbreviations": {
    "abbrev": ["full_term1", "full_term2"]
  },
  "bilingual_patterns": {
    "chinese_term": "english_equivalent"
  }
}

Create mappings that help accurately categorize this specific user's personal language patterns."""

    @staticmethod
    def get_personalized_synonyms_user_prompt(activity_texts: List[str]) -> str:
        """User prompt with activity data for synonym generation."""
        activities_text = "\n".join([f"{i+1}. {text}" for i, text in enumerate(activity_texts)])
        
        return f"""ACTIVITY DATA TO ANALYZE:
{activities_text}

Extract personal language patterns, shortcuts, and synonyms from this user's activity descriptions.

Look for:
- Repeated terms that mean the same thing
- Personal abbreviations and shortcuts
- Chinese-English mixed usage patterns
- Project-specific terminology
- Work vs personal language differences
- Informal expressions and personal notation

Create comprehensive mappings that will improve activity categorization accuracy."""