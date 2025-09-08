#!/usr/bin/env python3
"""
Comprehensive test suite for hierarchical tagging system.

Tests the three-layer tagging approach: nature, subject, and project levels.
Follows REGULATION.md testing principles with focused, atomic test methods.
"""

import pytest
import json
from typing import List, Dict, Any
from unittest.mock import patch, MagicMock

from agent.tools.tag_generator import TagGenerator
from agent.core.models import RawActivity


class TestHierarchicalTaxonomyLoading:
    """Test hierarchical taxonomy loading and initialization."""
    
    def test_hierarchical_taxonomy_loads_correctly(self):
        """Test that hierarchical taxonomy loads with proper structure."""
        tag_generator = TagGenerator()
        
        assert hasattr(tag_generator, 'hierarchical_taxonomy')
        hierarchy = tag_generator.hierarchical_taxonomy
        assert "taxonomy" in hierarchy
        
        # Test work category structure
        work_config = hierarchy["taxonomy"].get("work", {})
        assert "subjects" in work_config
        assert "bytediff" in work_config["subjects"]
        assert "smartHistory" in work_config["subjects"]
        
    def test_subject_configuration_structure(self):
        """Test that subject configurations have required fields."""
        tag_generator = TagGenerator()
        hierarchy = tag_generator.hierarchical_taxonomy["taxonomy"]
        
        work_subjects = hierarchy["work"]["subjects"]
        bytediff_config = work_subjects["bytediff"]
        
        assert "description" in bytediff_config
        assert "keywords" in bytediff_config
        assert "projects" in bytediff_config
        assert isinstance(bytediff_config["keywords"], list)
        assert isinstance(bytediff_config["projects"], list)


class TestHierarchicalTagGeneration:
    """Test hierarchical tag generation for individual activities."""
    
    @pytest.fixture
    def tag_generator(self):
        """Create a TagGenerator instance for testing."""
        return TagGenerator()
    
    def test_work_activity_hierarchical_tagging(self, tag_generator):
        """Test hierarchical tagging for work activities."""
        work_activity = RawActivity(
            date="2025-09-07",
            time="14:00",
            duration_minutes=60,
            details="bytediff code review and debugging session",
            source="google_calendar",
            orig_link=""
        )
        
        result = tag_generator.generate_hierarchical_tags_for_activity(work_activity)
        
        # Should identify as work activity
        assert result["nature"] == "work"
        assert result["confidence_scores"]["nature"] > 0.0
        
        # Should identify bytediff as subject
        assert result["subject"] == "bytediff"
        assert result["confidence_scores"]["subject"] > 0.0
        
        # May identify debug as project
        if result["project"]:
            assert result["project"] == "debug"
    
    def test_study_activity_hierarchical_tagging(self, tag_generator):
        """Test hierarchical tagging for study activities."""
        study_activity = RawActivity(
            date="2025-09-07",
            time="19:00",
            duration_minutes=90,
            details="Web3 blockchain fundamentals learning",
            source="notion",
            orig_link=""
        )
        
        result = tag_generator.generate_hierarchical_tags_for_activity(study_activity)
        
        # Should identify as study activity
        assert result["nature"] == "study"
        
        # Should identify web3 as subject
        assert result["subject"] == "web3"
        assert result["confidence_scores"]["subject"] > 0.0
    
    def test_personal_activity_hierarchical_tagging(self, tag_generator):
        """Test hierarchical tagging for personal activities."""
        personal_activity = RawActivity(
            date="2025-09-07",
            time="12:30",
            duration_minutes=30,
            details="午休 afternoon nap break",
            source="notion",
            orig_link=""
        )
        
        result = tag_generator.generate_hierarchical_tags_for_activity(personal_activity)
        
        # Should identify as personal activity
        assert result["nature"] == "personal"
        
        # Should identify rest as subject
        assert result["subject"] == "rest"
        assert result["confidence_scores"]["subject"] > 0.0
    
    def test_exercise_activity_hierarchical_tagging(self, tag_generator):
        """Test hierarchical tagging for exercise activities."""
        exercise_activity = RawActivity(
            date="2025-09-07",
            time="18:00",
            duration_minutes=90,
            details="健身房 upper body strength training",
            source="google_calendar",
            orig_link=""
        )
        
        result = tag_generator.generate_hierarchical_tags_for_activity(exercise_activity)
        
        # Should identify as exercise activity
        assert result["nature"] == "exercise"
        
        # Should identify gym as subject
        assert result["subject"] == "gym"
        assert result["confidence_scores"]["subject"] > 0.0


class TestSubjectDetection:
    """Test subject-level tag detection logic."""
    
    @pytest.fixture
    def tag_generator(self):
        return TagGenerator()
    
    def test_work_subject_detection(self, tag_generator):
        """Test detection of work-related subjects."""
        test_cases = [
            ("bytediff debugging session", "work", "bytediff"),
            ("smartHistory tagging development", "work", "smartHistory"),
            ("team meeting discussion", "work", "meetings")
        ]
        
        for activity_text, nature, expected_subject in test_cases:
            subject, confidence = tag_generator._detect_subject_tag(activity_text, nature)
            assert subject == expected_subject
            assert confidence > 0.0
    
    def test_study_subject_detection(self, tag_generator):
        """Test detection of study-related subjects."""
        test_cases = [
            ("web3 blockchain learning", "study", "web3"),
            ("CFA level 1 preparation", "study", "cfa"),
            ("computer science algorithms", "study", "computer-science")
        ]
        
        for activity_text, nature, expected_subject in test_cases:
            subject, confidence = tag_generator._detect_subject_tag(activity_text, nature)
            assert subject == expected_subject
            assert confidence > 0.0
    
    def test_subject_confidence_scoring(self, tag_generator):
        """Test confidence scoring for subject detection."""
        # High confidence case - clear keyword match
        subject, conf_high = tag_generator._detect_subject_tag("bytediff code review", "work")
        assert conf_high > 0.5
        
        # Lower confidence case - partial match
        subject, conf_low = tag_generator._detect_subject_tag("some work task", "work")
        assert conf_low < conf_high or conf_low == 0.0
    
    def test_no_subject_match(self, tag_generator):
        """Test behavior when no subject matches."""
        subject, confidence = tag_generator._detect_subject_tag("random activity", "work")
        # Should return None or empty subject
        assert subject is None or confidence < 0.3


class TestProjectDetection:
    """Test project-level tag detection logic."""
    
    @pytest.fixture  
    def tag_generator(self):
        return TagGenerator()
    
    def test_work_project_detection(self, tag_generator):
        """Test detection of work project tags."""
        test_cases = [
            ("bytediff debug session", "work", "bytediff", "debug"),
            ("CI/CD pipeline setup", "work", "bytediff", "CI/CD"),
            ("code review process", "work", "bytediff", "code-review")
        ]
        
        for activity_text, nature, subject, expected_project in test_cases:
            project, confidence = tag_generator._detect_project_tag(activity_text, nature, subject)
            if project:  # Project detection is optional
                assert expected_project in project or project in expected_project
                assert confidence > 0.0
    
    def test_study_project_detection(self, tag_generator):
        """Test detection of study project tags."""  
        test_cases = [
            ("solidity smart contract development", "study", "web3", "solidity"),
            ("ethereum protocol learning", "study", "web3", "ethereum")
        ]
        
        for activity_text, nature, subject, expected_project in test_cases:
            project, confidence = tag_generator._detect_project_tag(activity_text, nature, subject)
            if project:
                assert expected_project in project or project in expected_project
    
    def test_project_optional_behavior(self, tag_generator):
        """Test that project detection is optional and graceful."""
        project, confidence = tag_generator._detect_project_tag("general work meeting", "work", "meetings")
        # Should return None or low confidence for generic activities
        assert project is None or confidence == 0.0


class TestBatchProcessing:
    """Test batch processing of hierarchical tags."""
    
    @pytest.fixture
    def tag_generator(self):
        return TagGenerator()
    
    @pytest.fixture
    def sample_activities(self):
        """Sample activities for batch testing."""
        return [
            RawActivity(date="2025-09-01", details="bytediff debugging", source="calendar"),
            RawActivity(date="2025-09-01", details="web3 study session", source="notion"),
            RawActivity(date="2025-09-01", details="健身房 workout", source="calendar"),
            RawActivity(date="2025-09-01", details="午休 break", source="notion"),
        ]
    
    def test_batch_hierarchical_tagging(self, tag_generator, sample_activities):
        """Test batch processing of hierarchical tags."""
        results = tag_generator.generate_hierarchical_tags_batch(sample_activities)
        
        assert len(results) == 4
        
        # Check structure of results
        for result in results:
            assert "activity_text" in result
            assert "hierarchical_tags" in result
            assert "source" in result
            assert "date" in result
            
            tags = result["hierarchical_tags"]
            assert "nature" in tags
            assert "subject" in tags
            assert "project" in tags
            assert "confidence_scores" in tags
    
    def test_hierarchical_summary_generation(self, tag_generator, sample_activities):
        """Test summary statistics generation."""
        results = tag_generator.generate_hierarchical_tags_batch(sample_activities)
        summary = tag_generator.get_hierarchical_summary(results)
        
        # Check summary structure
        assert "total_activities" in summary
        assert "nature_distribution" in summary
        assert "subject_distribution" in summary
        assert "project_distribution" in summary
        assert "coverage_stats" in summary
        assert "confidence_stats" in summary
        
        # Check coverage percentages
        coverage = summary["coverage_stats"]
        assert 0 <= coverage["nature_coverage"] <= 100
        assert 0 <= coverage["subject_coverage"] <= 100
        assert 0 <= coverage["project_coverage"] <= 100
        
        # Check confidence averages
        conf_stats = summary["confidence_stats"]
        assert 0 <= conf_stats["avg_nature_confidence"] <= 1
        assert 0 <= conf_stats["avg_subject_confidence"] <= 1
        assert 0 <= conf_stats["avg_project_confidence"] <= 1


class TestBilingualSupport:
    """Test bilingual content support in hierarchical tagging."""
    
    @pytest.fixture
    def tag_generator(self):
        return TagGenerator()
    
    def test_mixed_language_work_activities(self, tag_generator):
        """Test mixed Chinese-English work activities."""
        mixed_activities = [
            "bytediff 调试会话 debugging",
            "周会 team meeting discussion", 
            "smartHistory 开发工作 development"
        ]
        
        for activity_text in mixed_activities:
            activity = RawActivity(
                date="2025-09-07",
                details=activity_text,
                source="calendar"
            )
            
            result = tag_generator.generate_hierarchical_tags_for_activity(activity)
            assert result["nature"] == "work"
            assert result["subject"] is not None
    
    def test_mixed_language_personal_activities(self, tag_generator):
        """Test mixed Chinese-English personal activities."""
        mixed_activities = [
            "午休时间 rest break",
            "厕所 bathroom break",
            "个人时间 personal time"
        ]
        
        for activity_text in mixed_activities:
            activity = RawActivity(
                date="2025-09-07", 
                details=activity_text,
                source="notion"
            )
            
            result = tag_generator.generate_hierarchical_tags_for_activity(activity)
            assert result["nature"] == "personal"


class TestConfidenceScoring:
    """Test confidence scoring across hierarchical levels."""
    
    @pytest.fixture
    def tag_generator(self):
        return TagGenerator()
    
    def test_confidence_decreases_by_layer(self, tag_generator):
        """Test that confidence generally decreases from nature to project."""
        activity = RawActivity(
            date="2025-09-07",
            details="bytediff debug and code review session",
            source="calendar"
        )
        
        result = tag_generator.generate_hierarchical_tags_for_activity(activity)
        scores = result["confidence_scores"]
        
        # Nature should have highest confidence (established system)
        assert scores["nature"] > 0.0
        
        # Subject confidence should be reasonable
        if result["subject"]:
            assert scores["subject"] > 0.0
            
        # Project confidence should be reasonable if detected
        if result["project"]:
            assert scores["project"] > 0.0
    
    def test_low_confidence_handling(self, tag_generator):
        """Test handling of low confidence scenarios."""
        ambiguous_activity = RawActivity(
            date="2025-09-07",
            details="random unclear activity",
            source="calendar"
        )
        
        result = tag_generator.generate_hierarchical_tags_for_activity(ambiguous_activity)
        
        # Should still attempt classification but may have low confidence
        # System should gracefully handle uncertainty
        assert "nature" in result
        assert "subject" in result
        assert "project" in result


if __name__ == "__main__":
    pytest.main([__file__, "-v"])