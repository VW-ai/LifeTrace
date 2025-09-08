"""
Calendar-as-Query + Notion-as-Context processor.

Implements the paradigm shift from merging Calendar/Notion as equivalent events
to using Calendar entries as queries to retrieve relevant Notion context.
Following REGULATION.md atomic principles with focused functionality.
"""

import os
import json
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass

from .calendar_notion_models import CalendarEntry, NotionBlock, CalendarNotionMatch, EditTrackingTree
from .models import RawActivity
from ..tools.tag_generator import TagGenerator


class CalendarNotionProcessor:
    """
    Core processor implementing Calendar-as-Query + Notion-as-Context architecture.
    
    Key principle: Calendar entries are compressed personal notation that serves
    as queries to find relevant context in the Notion knowledge base.
    """
    
    def __init__(self):
        """Initialize processor with enhanced tagging capabilities."""
        self.tag_generator = TagGenerator()
        self.time_window_hours = 24  # Configurable time window for matching
        
    def convert_raw_to_calendar_entry(self, raw_activity: RawActivity) -> CalendarEntry:
        """
        Convert raw calendar activity to CalendarEntry query object.
        
        Treats calendar data as compressed personal notation requiring expansion.
        """
        calendar_entry = CalendarEntry(
            date=raw_activity.date,
            time=raw_activity.time,
            duration_minutes=raw_activity.duration_minutes,
            title=raw_activity.details,  # Original compressed notation
            raw_data=raw_activity.raw_data,
            orig_link=raw_activity.orig_link
        )
        
        # Extract enhanced metadata from raw_data if available
        if raw_activity.raw_data:
            calendar_entry.description = raw_activity.raw_data.get('description', '')
            calendar_entry.location = raw_activity.raw_data.get('location', '')
            calendar_entry.attendees = raw_activity.raw_data.get('attendees', [])
            calendar_entry.recurrence_info = raw_activity.raw_data.get('recurrence', {})
        
        # Generate hierarchical tags for query expansion
        hierarchical_tags = self.tag_generator.generate_hierarchical_tags_for_activity(raw_activity)
        calendar_entry.hierarchical_tags = hierarchical_tags
        
        # Detect personal shortcuts
        personal_shortcuts = self._detect_personal_shortcuts(calendar_entry.title)
        calendar_entry.personal_shortcuts = personal_shortcuts
        
        # Expand query using AI and hierarchical context
        expanded_query = self._expand_calendar_query(calendar_entry)
        calendar_entry.expanded_query = expanded_query
        
        return calendar_entry
    
    def convert_raw_to_notion_block(self, raw_activity: RawActivity) -> NotionBlock:
        """
        Convert raw Notion activity to NotionBlock context object.
        
        Preserves tree structure and extracts rich contextual information.
        """
        notion_block = NotionBlock(
            content=raw_activity.details,
            raw_data=raw_activity.raw_data
        )
        
        # Extract Notion-specific metadata
        if raw_activity.raw_data:
            notion_block.id = raw_activity.raw_data.get('block_id', '')
            notion_block.parent_id = raw_activity.raw_data.get('parent_id')
            notion_block.page_id = raw_activity.raw_data.get('page_id', '')
            notion_block.block_type = raw_activity.raw_data.get('type', 'paragraph')
            notion_block.page_title = raw_activity.raw_data.get('page_title', '')
            notion_block.database_properties = raw_activity.raw_data.get('properties', {})
            notion_block.breadcrumb = raw_activity.raw_data.get('breadcrumb', [])
            notion_block.depth_level = raw_activity.raw_data.get('depth', 0)
        
        # Set temporal information
        if raw_activity.raw_data.get('created_time'):
            notion_block.created_time = datetime.fromisoformat(
                raw_activity.raw_data['created_time'].replace('Z', '+00:00')
            )
        if raw_activity.raw_data.get('last_edited_time'):
            notion_block.last_edited_time = datetime.fromisoformat(
                raw_activity.raw_data['last_edited_time'].replace('Z', '+00:00')
            )
        
        return notion_block
    
    def find_notion_context_for_calendar(
        self, 
        calendar_entry: CalendarEntry, 
        notion_blocks: List[NotionBlock],
        method: str = "hybrid"
    ) -> List[NotionBlock]:
        """
        Find relevant Notion context for a Calendar query.
        
        Implements the core Calendar-as-Query retrieval logic.
        """
        if method == "time_window":
            return self._find_by_time_window(calendar_entry, notion_blocks)
        elif method == "content_similarity":
            return self._find_by_content_similarity(calendar_entry, notion_blocks)
        elif method == "hybrid":
            return self._find_by_hybrid_approach(calendar_entry, notion_blocks)
        else:
            raise ValueError(f"Unknown matching method: {method}")
    
    def create_calendar_notion_match(
        self, 
        calendar_entry: CalendarEntry, 
        notion_contexts: List[NotionBlock],
        method: str = "hybrid"
    ) -> CalendarNotionMatch:
        """
        Create matched Calendar-Notion pair with confidence scoring.
        
        This is the core output of the Calendar-as-Query system.
        """
        match = CalendarNotionMatch(
            calendar_entry=calendar_entry,
            notion_contexts=notion_contexts,
            match_method=method
        )
        
        # Calculate match confidence
        match.match_confidence = self._calculate_match_confidence(match)
        
        # Generate reasoning
        match.match_reasoning = self._generate_match_reasoning(match)
        
        # Generate unified activity summary
        match.generated_abstract = self._generate_activity_abstract(match)
        
        # Determine if review is needed
        if match.match_confidence < 0.3:
            match.needs_review = True
            match.review_reason = f"Low confidence match ({match.match_confidence:.2f})"
        
        match.processed_at = datetime.now()
        
        return match
    
    def process_daily_activities(
        self, 
        calendar_activities: List[RawActivity],
        notion_activities: List[RawActivity]
    ) -> List[CalendarNotionMatch]:
        """
        Process a day's activities using Calendar-as-Query approach.
        
        Main orchestration method for daily processing workflow.
        """
        # Convert raw activities to structured objects
        calendar_entries = [
            self.convert_raw_to_calendar_entry(activity)
            for activity in calendar_activities
        ]
        
        notion_blocks = [
            self.convert_raw_to_notion_block(activity) 
            for activity in notion_activities
        ]
        
        # Process each calendar entry as a query
        matches = []
        for calendar_entry in calendar_entries:
            # Find relevant Notion context
            relevant_contexts = self.find_notion_context_for_calendar(
                calendar_entry, notion_blocks
            )
            
            # Create match object
            match = self.create_calendar_notion_match(
                calendar_entry, relevant_contexts
            )
            
            matches.append(match)
        
        return matches
    
    # Private helper methods
    
    def _detect_personal_shortcuts(self, calendar_title: str) -> List[str]:
        """Detect personal shortcuts in calendar title."""
        shortcuts = []
        
        # Use existing synonym detection from tag_generator
        synonyms = self.tag_generator.synonyms.get("personal_shortcuts", {})
        
        title_lower = calendar_title.lower()
        for shortcut in synonyms.keys():
            if shortcut.lower() in title_lower:
                shortcuts.append(shortcut)
        
        return shortcuts
    
    def _expand_calendar_query(self, calendar_entry: CalendarEntry) -> str:
        """
        Expand compressed calendar notation into fuller query.
        
        Uses hierarchical tagging and personal shortcuts for expansion.
        """
        expansions = []
        
        # Add original title
        expansions.append(calendar_entry.title)
        
        # Add hierarchical context
        hierarchical = calendar_entry.hierarchical_tags
        if hierarchical.get("subject"):
            expansions.append(hierarchical["subject"])
        if hierarchical.get("project"):
            expansions.append(hierarchical["project"])
        
        # Add personal shortcut expansions
        for shortcut in calendar_entry.personal_shortcuts:
            # Look up shortcut meaning from synonyms
            synonyms = self.tag_generator.synonyms.get("personal_shortcuts", {})
            if shortcut in synonyms:
                expansions.extend(synonyms[shortcut])
        
        # Add location/attendee context
        if calendar_entry.location:
            expansions.append(calendar_entry.location)
        if calendar_entry.attendees:
            expansions.extend(calendar_entry.attendees)
        
        return " ".join(expansions)
    
    def _find_by_time_window(
        self, 
        calendar_entry: CalendarEntry, 
        notion_blocks: List[NotionBlock]
    ) -> List[NotionBlock]:
        """Find Notion blocks within time window of calendar entry."""
        if not calendar_entry.date or not calendar_entry.time:
            return []
        
        # Parse calendar datetime
        calendar_dt = datetime.strptime(
            f"{calendar_entry.date} {calendar_entry.time}", 
            "%Y-%m-%d %H:%M"
        )
        
        # Define time window
        window_start = calendar_dt - timedelta(hours=self.time_window_hours)
        window_end = calendar_dt + timedelta(hours=self.time_window_hours)
        
        matches = []
        for block in notion_blocks:
            if not block.last_edited_time:
                continue
                
            # Check if block was edited within time window
            if window_start <= block.last_edited_time <= window_end:
                matches.append(block)
        
        return matches
    
    def _find_by_content_similarity(
        self, 
        calendar_entry: CalendarEntry, 
        notion_blocks: List[NotionBlock]
    ) -> List[NotionBlock]:
        """Find Notion blocks with content similarity to calendar query."""
        query_terms = set(calendar_entry.get_query_terms())
        
        scored_blocks = []
        for block in notion_blocks:
            # Simple term overlap scoring (TODO: upgrade to TF-IDF)
            block_terms = set(block.content.lower().split())
            overlap = len(query_terms.intersection(block_terms))
            
            if overlap > 0:
                similarity_score = overlap / len(query_terms.union(block_terms))
                scored_blocks.append((block, similarity_score))
        
        # Sort by similarity and return top matches
        scored_blocks.sort(key=lambda x: x[1], reverse=True)
        return [block for block, score in scored_blocks[:5]]  # Top 5 matches
    
    def _find_by_hybrid_approach(
        self, 
        calendar_entry: CalendarEntry, 
        notion_blocks: List[NotionBlock]
    ) -> List[NotionBlock]:
        """Combine time window and content similarity for best results."""
        # Get candidates from both approaches
        time_matches = self._find_by_time_window(calendar_entry, notion_blocks)
        content_matches = self._find_by_content_similarity(calendar_entry, notion_blocks)
        
        # Combine and deduplicate
        all_matches = {}  # block.id -> block
        
        # Prioritize time matches
        for block in time_matches:
            all_matches[block.id] = block
        
        # Add content matches
        for block in content_matches:
            if block.id not in all_matches:
                all_matches[block.id] = block
        
        return list(all_matches.values())
    
    def _calculate_match_confidence(self, match: CalendarNotionMatch) -> float:
        """Calculate confidence score for Calendar-Notion match."""
        confidence_factors = match.get_confidence_factors()
        
        # Weighted combination of confidence factors
        weights = {
            "time_proximity": 0.3,
            "content_similarity": 0.4,
            "personal_shortcuts": 0.2,
            "hierarchical_context": 0.1
        }
        
        weighted_score = sum(
            confidence_factors.get(factor, 0.0) * weight
            for factor, weight in weights.items()
        )
        
        return min(1.0, weighted_score)
    
    def _generate_match_reasoning(self, match: CalendarNotionMatch) -> str:
        """Generate human-readable reasoning for the match."""
        reasons = []
        
        confidence_factors = match.get_confidence_factors()
        
        if confidence_factors.get("time_proximity", 0) > 0.3:
            reasons.append("temporal proximity")
        
        if confidence_factors.get("content_similarity", 0) > 0.3:
            reasons.append("content similarity")
        
        if confidence_factors.get("personal_shortcuts", 0) > 0.3:
            reasons.append("personal shortcut recognition")
        
        if confidence_factors.get("hierarchical_context", 0) > 0.3:
            reasons.append("hierarchical tag consistency")
        
        if not reasons:
            return "Low confidence match - manual review recommended"
        
        return f"Matched based on: {', '.join(reasons)}"
    
    def _generate_activity_abstract(self, match: CalendarNotionMatch) -> str:
        """
        Generate 30-100 word abstract from Calendar entry + Notion context.
        
        This is a key output of the Calendar-as-Query system.
        """
        # Combine calendar and notion information
        calendar_info = match.calendar_entry.title
        
        if match.calendar_entry.expanded_query:
            calendar_info += f" ({match.calendar_entry.expanded_query})"
        
        notion_context = ""
        if match.notion_contexts:
            # Use first context block as primary
            primary_context = match.notion_contexts[0]
            notion_context = primary_context.content[:200]  # First 200 chars
        
        # Simple combination (TODO: upgrade to AI-generated abstract)
        if notion_context:
            abstract = f"{calendar_info}. Context: {notion_context}"
        else:
            abstract = calendar_info
        
        # Truncate to reasonable length
        if len(abstract) > 500:
            abstract = abstract[:497] + "..."
        
        return abstract