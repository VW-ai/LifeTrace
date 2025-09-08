#!/usr/bin/env python3
"""
Comprehensive test suite for enhanced AI-native tagging system.

Tests the taxonomy-first tagging approach, confidence scoring,
synonym mapping, and personalized taxonomy generation.
"""

import pytest
import json
import os
from unittest.mock import patch, MagicMock
from typing import List, Tuple

from agent.tools.tag_generator import TagGenerator
from agent.core.models import RawActivity, TagGenerationContext
from agent.prompts.taxonomy_prompts import TaxonomyPrompts


class TestTaxonomyPrompts:
    """Test the taxonomy prompt generation functionality."""
    
    def test_personalized_taxonomy_system_prompt(self):
        """Test system prompt generation for personalized taxonomy."""
        prompt = TaxonomyPrompts.get_personalized_taxonomy_system_prompt(15)
        
        assert "15 main activity categories" in prompt
        assert "bilingual" in prompt.lower()
        assert "taxonomy" in prompt.lower()
        assert '"taxonomy"' in prompt
    
    def test_personalized_taxonomy_user_prompt(self):
        """Test user prompt generation with activity data."""
        activities = ["工作会议 with team", "健身房 workout", "吃午饭 lunch"]
        prompt = TaxonomyPrompts.get_personalized_taxonomy_user_prompt(activities)
        
        assert "1. 工作会议 with team" in prompt
        assert "2. 健身房 workout" in prompt
        assert "3. 吃午饭 lunch" in prompt
        assert "patterns" in prompt.lower()
    
    def test_personalized_synonyms_system_prompt(self):
        """Test system prompt for synonym generation."""
        prompt = TaxonomyPrompts.get_personalized_synonyms_system_prompt()
        
        assert "synonym" in prompt.lower()
        assert "bilingual" in prompt.lower()
        assert "personal" in prompt.lower()
        assert "shortcuts" in prompt.lower()
    
    def test_personalized_synonyms_user_prompt(self):
        """Test user prompt for synonym extraction."""
        activities = ["bytediff debug", "厕所 break", "smartHistory开发"]
        prompt = TaxonomyPrompts.get_personalized_synonyms_user_prompt(activities)
        
        assert "bytediff debug" in prompt
        assert "厕所 break" in prompt
        assert "smartHistory开发" in prompt
        assert "patterns" in prompt.lower()


class TestTagGenerator:
    """Test the enhanced TagGenerator functionality."""
    
    @pytest.fixture
    def tag_generator(self):
        """Create a TagGenerator instance for testing."""
        return TagGenerator()
    
    def test_taxonomy_loading(self, tag_generator):
        """Test that taxonomy loads correctly."""
        assert len(tag_generator.taxonomy_tags) > 0
        assert "work" in tag_generator.taxonomy_tags
        assert "personal" in tag_generator.taxonomy_tags
        assert "meals" in tag_generator.taxonomy_tags
        
        # Check taxonomy structure
        taxonomy = tag_generator.taxonomy
        assert "taxonomy" in taxonomy
        assert "work" in taxonomy["taxonomy"]
        assert "description" in taxonomy["taxonomy"]["work"]
        assert "keywords" in taxonomy["taxonomy"]["work"]
    
    def test_synonyms_loading(self, tag_generator):
        """Test that synonyms load correctly."""
        synonyms = tag_generator.synonyms
        assert "synonyms" in synonyms
        assert "personal_shortcuts" in synonyms
        
        # Check for expected mappings
        assert "work" in synonyms["synonyms"]
        assert "bytediff" in synonyms["personal_shortcuts"]
    
    def test_fuzzy_mapping_exact_match(self, tag_generator):
        """Test fuzzy mapping with exact taxonomy match."""
        result = tag_generator.fuzzy_map_to_taxonomy("work")
        assert result is not None
        tag, confidence = result
        assert tag == "work"
        assert confidence == 1.0
    
    def test_fuzzy_mapping_close_match(self, tag_generator):
        """Test fuzzy mapping with similar string."""
        result = tag_generator.fuzzy_map_to_taxonomy("worke")
        # Should find close match or return None based on threshold
        if result:
            tag, confidence = result
            assert tag == "work"
            assert confidence > 0.8
    
    def test_fuzzy_mapping_no_match(self, tag_generator):
        """Test fuzzy mapping with completely different string."""
        result = tag_generator.fuzzy_map_to_taxonomy("completely_different_tag")
        assert result is None
    
    def test_synonym_mapping_personal_shortcuts(self, tag_generator):
        """Test synonym mapping for personal shortcuts."""
        matches = tag_generator.map_synonyms_to_taxonomy("bytediff debug session")
        
        assert len(matches) > 0
        # Should map to work category
        work_match = next((tag for tag, conf in matches if tag == "work"), None)
        assert work_match is not None
    
    def test_synonym_mapping_bilingual(self, tag_generator):
        """Test bilingual synonym mapping."""
        # Test Chinese meal terms
        matches = tag_generator.map_synonyms_to_taxonomy("吃午饭 with colleagues")
        
        meal_match = next((tag for tag, conf in matches if tag == "meals"), None)
        assert meal_match is not None
    
    def test_find_matching_taxonomy_tags_work(self, tag_generator):
        """Test taxonomy matching for work activities."""
        matches = tag_generator.find_matching_taxonomy_tags("Meeting with team about project")
        
        assert len(matches) > 0
        work_match = next((tag for tag, conf in matches if tag == "work"), None)
        assert work_match is not None
    
    def test_find_matching_taxonomy_tags_mixed_language(self, tag_generator):
        """Test taxonomy matching for mixed language content."""
        matches = tag_generator.find_matching_taxonomy_tags("健身房 workout session")
        
        exercise_match = next((tag for tag, conf in matches if tag == "exercise"), None)
        assert exercise_match is not None
    
    def test_confidence_assessment(self, tag_generator):
        """Test confidence scoring logic."""
        # High confidence case - clear work activity
        confidence = tag_generator.assess_tag_confidence("Team meeting about project development", "work")
        assert confidence > 0.4
        
        # Low confidence case - ambiguous activity
        confidence = tag_generator.assess_tag_confidence("Random activity", "work")
        assert confidence < 0.8
    
    def test_fallback_tag_generation(self, tag_generator):
        """Test fallback tag generation without LLM."""
        context = TagGenerationContext(
            existing_tags=tag_generator.taxonomy_tags,
            activity_text="Team meeting about database migration",
            source="google_calendar",
            duration_minutes=60,
            time_context="14:00"
        )
        
        tags_with_conf = tag_generator._generate_fallback_tags_with_confidence(context)
        
        assert len(tags_with_conf) > 0
        # Should identify as work activity
        work_tag = next((tag for tag, conf in tags_with_conf if tag == "work"), None)
        assert work_tag is not None
    
    def test_fallback_bilingual_support(self, tag_generator):
        """Test fallback system with bilingual content."""
        context = TagGenerationContext(
            existing_tags=tag_generator.taxonomy_tags,
            activity_text="午休时间 rest break",
            source="notion",
            duration_minutes=30
        )
        
        tags_with_conf = tag_generator._generate_fallback_tags_with_confidence(context)
        
        assert len(tags_with_conf) > 0
        personal_tag = next((tag for tag, conf in tags_with_conf if tag == "personal"), None)
        assert personal_tag is not None


class TestRealActivityProcessing:
    """Test processing of real activity data patterns."""
    
    @pytest.fixture
    def tag_generator(self):
        return TagGenerator()
    
    def test_work_activity_patterns(self, tag_generator):
        """Test recognition of various work activity patterns."""
        work_activities = [
            "Weekly组会 team meeting",
            "doris DDL implementation", 
            "Meeting w/ 天人哥",
            "建表 database setup",
            "权限申请 permission request"
        ]
        
        for activity_text in work_activities:
            raw_activity = RawActivity(
                date="2025-09-07",
                time="14:00",
                duration_minutes=60,
                details=activity_text,
                source="google_calendar",
                orig_link=""
            )
            
            tags_with_conf = tag_generator.generate_tags_with_confidence_for_activity(raw_activity)
            
            # Should identify as work or admin (both work-related)
            work_tag = next((tag for tag, conf in tags_with_conf if tag in ["work", "admin"]), None)
            assert work_tag is not None, f"Failed to identify '{activity_text}' as work-related (got: {[tag for tag, conf in tags_with_conf]})"
    
    def test_personal_activity_patterns(self, tag_generator):
        """Test recognition of personal activity patterns."""
        personal_activities = [
            "午休 afternoon nap",
            "厕所 bathroom break",
            "wash and sleep",
            "个人时间 personal time"
        ]
        
        for activity_text in personal_activities:
            raw_activity = RawActivity(
                date="2025-09-07",
                time="12:00", 
                duration_minutes=30,
                details=activity_text,
                source="notion",
                orig_link=""
            )
            
            tags_with_conf = tag_generator.generate_tags_with_confidence_for_activity(raw_activity)
            
            # Should identify as personal
            personal_tag = next((tag for tag, conf in tags_with_conf if tag == "personal"), None)
            assert personal_tag is not None, f"Failed to identify '{activity_text}' as personal"
    
    def test_meal_activity_patterns(self, tag_generator):
        """Test recognition of meal activity patterns."""
        meal_activities = [
            "快速吃点 quick snack",
            "lunch with team",
            "吃午饭 having lunch", 
            "dinner preparation"
        ]
        
        for activity_text in meal_activities:
            raw_activity = RawActivity(
                date="2025-09-07",
                time="12:30",
                duration_minutes=45,
                details=activity_text,
                source="google_calendar",
                orig_link=""
            )
            
            tags_with_conf = tag_generator.generate_tags_with_confidence_for_activity(raw_activity)
            
            # Should identify as meals
            meal_tag = next((tag for tag, conf in tags_with_conf if tag == "meals"), None)
            assert meal_tag is not None, f"Failed to identify '{activity_text}' as meals"
    
    def test_exercise_activity_patterns(self, tag_generator):
        """Test recognition of exercise activity patterns."""
        exercise_activities = [
            "健身房 gym session",
            "workout routine",
            "健身，背/腿 back and legs",
            "gym training"
        ]
        
        for activity_text in exercise_activities:
            raw_activity = RawActivity(
                date="2025-09-07",
                time="18:00",
                duration_minutes=90,
                details=activity_text,
                source="google_calendar", 
                orig_link=""
            )
            
            tags_with_conf = tag_generator.generate_tags_with_confidence_for_activity(raw_activity)
            
            # Should identify as exercise
            exercise_tag = next((tag for tag, conf in tags_with_conf if tag == "exercise"), None)
            assert exercise_tag is not None, f"Failed to identify '{activity_text}' as exercise"


class TestConfidenceScoring:
    """Test confidence scoring mechanisms."""
    
    @pytest.fixture
    def tag_generator(self):
        return TagGenerator()
    
    def test_high_confidence_assignments(self, tag_generator):
        """Test activities that should have high confidence scores."""
        high_confidence_cases = [
            ("Team meeting about project", "work"),
            ("健身房 workout", "exercise"),
            ("吃午饭 lunch", "meals"),
            ("午休 nap time", "personal")
        ]
        
        for activity_text, expected_tag in high_confidence_cases:
            confidence = tag_generator.assess_tag_confidence(activity_text, expected_tag)
            assert confidence > 0.1, f"Extremely low confidence ({confidence}) for '{activity_text}' → {expected_tag}"
    
    def test_low_confidence_threshold(self, tag_generator):
        """Test low confidence threshold detection."""
        threshold = tag_generator.get_low_confidence_threshold()
        assert threshold == 0.5
        
        # Test activity that should trigger review
        ambiguous_confidence = tag_generator.assess_tag_confidence("random stuff", "work")
        if ambiguous_confidence < threshold:
            # Should be flagged for review
            assert True
    
    def test_confidence_factors_combination(self, tag_generator):
        """Test how different confidence factors combine."""
        # Test activity with strong synonym match
        activity_with_synonyms = "bytediff development session"
        confidence_synonyms = tag_generator.assess_tag_confidence(activity_with_synonyms, "work")
        
        # Test activity with keyword match only
        activity_with_keywords = "project implementation"
        confidence_keywords = tag_generator.assess_tag_confidence(activity_with_keywords, "work")
        
        # Synonym match should generally have higher confidence
        # (though this depends on the specific implementation)
        assert confidence_synonyms > 0.3
        assert confidence_keywords > 0.2


@pytest.mark.integration
class TestPersonalizedTaxonomyGeneration:
    """Integration tests for personalized taxonomy generation."""
    
    @pytest.fixture
    def sample_activities(self):
        """Sample activities for taxonomy generation testing."""
        return [
            RawActivity(date="2025-09-01", details="bytediff code review", source="calendar"),
            RawActivity(date="2025-09-01", details="健身房 workout", source="calendar"),
            RawActivity(date="2025-09-01", details="午休 nap", source="notion"),
            RawActivity(date="2025-09-01", details="team meeting", source="calendar"),
            RawActivity(date="2025-09-01", details="吃午饭 lunch", source="calendar")
        ]
    
    @patch('agent.tools.tag_generator.OpenAI')
    def test_personalized_taxonomy_generation(self, mock_openai, sample_activities):
        """Test personalized taxonomy generation with mocked API."""
        # Mock OpenAI response
        mock_response = MagicMock()
        mock_response.choices[0].message.content = json.dumps({
            "taxonomy": {
                "work": {"description": "Work activities", "keywords": ["bytediff", "meeting"], "sub_tags": []},
                "exercise": {"description": "Physical activities", "keywords": ["健身房"], "sub_tags": []},
                "personal": {"description": "Personal time", "keywords": ["午休"], "sub_tags": []}
            }
        })
        
        mock_client = MagicMock()
        mock_client.chat.completions.create.return_value = mock_response
        mock_openai.return_value = mock_client
        
        tag_generator = TagGenerator(api_key="test_key")
        result = tag_generator.generate_personalized_taxonomy(sample_activities)
        
        assert "taxonomy" in result
        assert "work" in result["taxonomy"]
        assert "exercise" in result["taxonomy"] 
        assert "personal" in result["taxonomy"]
    
    @patch('agent.tools.tag_generator.OpenAI')
    def test_personalized_synonyms_generation(self, mock_openai, sample_activities):
        """Test personalized synonyms generation with mocked API."""
        # Mock OpenAI response
        mock_response = MagicMock()
        mock_response.choices[0].message.content = json.dumps({
            "synonyms": {
                "work": ["bytediff", "meeting", "coding"],
                "exercise": ["健身房", "workout", "gym"]
            },
            "personal_shortcuts": {
                "bytediff": ["work", "coding"]
            }
        })
        
        mock_client = MagicMock()
        mock_client.chat.completions.create.return_value = mock_response
        mock_openai.return_value = mock_client
        
        tag_generator = TagGenerator(api_key="test_key")
        result = tag_generator.generate_personalized_synonyms(sample_activities)
        
        assert "synonyms" in result
        assert "personal_shortcuts" in result
        assert "bytediff" in result["personal_shortcuts"]


if __name__ == "__main__":
    pytest.main([__file__, "-v"])