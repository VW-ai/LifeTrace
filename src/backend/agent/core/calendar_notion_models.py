"""
Calendar-as-Query + Notion-as-Context data models.

Implements the paradigm shift from treating Calendar and Notion as equivalent events
to using Calendar entries as queries to find context in Notion knowledge base.
Following REGULATION.md atomic principles.
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Optional, Dict, Any, Set
import json


@dataclass
class CalendarEntry:
    """
    Calendar entry as query - compressed personal notation with temporal data.
    
    Calendar entries are treated as search queries to find relevant Notion context,
    not as standalone events to be merged with Notion blocks.
    """
    id: Optional[str] = None
    date: str = ""  # YYYY-MM-DD format
    time: Optional[str] = None  # HH:MM format
    duration_minutes: int = 30
    title: str = ""  # Original calendar title (compressed notation)
    description: str = ""  # Calendar description if available
    location: str = ""  # Meeting location/context
    attendees: List[str] = field(default_factory=list)  # Meeting attendees
    recurrence_info: Dict[str, Any] = field(default_factory=dict)  # Recurrence metadata
    
    # Enhanced context for query expansion
    expanded_query: str = ""  # AI-expanded version of compressed title
    personal_shortcuts: List[str] = field(default_factory=list)  # Detected shortcuts
    hierarchical_tags: Dict[str, Any] = field(default_factory=dict)  # Nature/subject/project
    
    # Raw calendar data
    raw_data: Dict[str, Any] = field(default_factory=dict)
    orig_link: str = ""
    created_at: Optional[datetime] = None
    
    def get_query_terms(self) -> List[str]:
        """Extract query terms for Notion context retrieval."""
        terms = []
        
        # Original title terms
        terms.extend(self.title.lower().split())
        
        # Expanded query terms
        if self.expanded_query:
            terms.extend(self.expanded_query.lower().split())
            
        # Personal shortcuts
        terms.extend(self.personal_shortcuts)
        
        # Hierarchical context
        if self.hierarchical_tags:
            if self.hierarchical_tags.get("subject"):
                terms.append(self.hierarchical_tags["subject"])
            if self.hierarchical_tags.get("project"):
                terms.append(self.hierarchical_tags["project"])
        
        return list(set(terms))  # Remove duplicates
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            'id': self.id,
            'date': self.date,
            'time': self.time,
            'duration_minutes': self.duration_minutes,
            'title': self.title,
            'description': self.description,
            'location': self.location,
            'attendees': self.attendees,
            'recurrence_info': self.recurrence_info,
            'expanded_query': self.expanded_query,
            'personal_shortcuts': self.personal_shortcuts,
            'hierarchical_tags': self.hierarchical_tags,
            'raw_data': self.raw_data,
            'orig_link': self.orig_link,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }


@dataclass
class NotionBlock:
    """
    Notion block as context - detailed reflections with tree structure.
    
    Notion blocks serve as knowledge base context to enrich Calendar queries,
    maintaining parent-child relationships for semantic hierarchy.
    """
    id: str = ""  # Notion block ID
    db_id: Optional[int] = None  # Database record ID
    parent_id: Optional[str] = None  # Parent block ID
    page_id: str = ""  # Page containing this block
    block_type: str = ""  # paragraph, heading_1, etc.
    content: str = ""  # Block text content
    
    # Tree structure preservation
    child_blocks: List[str] = field(default_factory=list)  # Child block IDs
    breadcrumb: List[str] = field(default_factory=list)  # Path from root to this block
    depth_level: int = 0  # Nesting depth in page hierarchy
    
    # Context metadata
    page_title: str = ""  # Title of containing page
    database_properties: Dict[str, Any] = field(default_factory=dict)  # Database row properties
    relations: List[str] = field(default_factory=list)  # Related pages/blocks
    
    # Temporal information
    created_time: Optional[datetime] = None
    last_edited_time: Optional[datetime] = None
    
    # Generated context
    abstract: str = ""  # AI-generated 30-100 word summary
    embedding: Optional[List[float]] = None  # Vector embedding for retrieval
    
    # Edit tracking for efficient processing
    recently_updated: bool = False  # Updated in last 24hr
    update_propagated: bool = False  # Parent notified of update
    
    # Raw Notion data
    raw_data: Dict[str, Any] = field(default_factory=dict)
    
    def get_full_context(self) -> str:
        """Get full hierarchical context including breadcrumb."""
        context_parts = []
        
        # Page context
        if self.page_title:
            context_parts.append(f"Page: {self.page_title}")
        
        # Breadcrumb context
        if self.breadcrumb:
            context_parts.append(f"Path: {' → '.join(self.breadcrumb)}")
        
        # Block content
        context_parts.append(self.content)
        
        # Abstract if available
        if self.abstract:
            context_parts.append(f"Summary: {self.abstract}")
        
        return "\n".join(context_parts)
    
    def is_leaf_block(self) -> bool:
        """Check if this is a leaf block (no children)."""
        return len(self.child_blocks) == 0
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            'id': self.id,
            'db_id': self.db_id,
            'parent_id': self.parent_id,
            'page_id': self.page_id,
            'block_type': self.block_type,
            'content': self.content,
            'child_blocks': self.child_blocks,
            'breadcrumb': self.breadcrumb,
            'depth_level': self.depth_level,
            'page_title': self.page_title,
            'database_properties': self.database_properties,
            'relations': self.relations,
            'created_time': self.created_time.isoformat() if self.created_time else None,
            'last_edited_time': self.last_edited_time.isoformat() if self.last_edited_time else None,
            'abstract': self.abstract,
            'embedding': self.embedding,
            'recently_updated': self.recently_updated,
            'update_propagated': self.update_propagated,
            'raw_data': self.raw_data
        }


@dataclass
class CalendarNotionMatch:
    """
    Represents a matched Calendar entry with its relevant Notion context.
    
    This is the core data structure for the Calendar-as-Query system,
    linking compressed calendar notation with rich Notion context.
    """
    calendar_entry: CalendarEntry
    notion_contexts: List[NotionBlock] = field(default_factory=list)
    
    # Matching metadata
    match_confidence: float = 0.0
    match_method: str = ""  # "time_window", "content_similarity", "embedding"
    match_reasoning: str = ""  # AI explanation of match
    
    # Generated output
    unified_activity: Optional[Dict[str, Any]] = None  # Combined activity representation
    generated_abstract: str = ""  # AI-generated activity summary
    
    # Processing flags
    needs_review: bool = False
    review_reason: str = ""
    processed_at: Optional[datetime] = None
    
    def get_confidence_factors(self) -> Dict[str, float]:
        """Get breakdown of confidence scoring factors."""
        return {
            "time_proximity": self._calculate_time_proximity(),
            "content_similarity": self._calculate_content_similarity(),
            "personal_shortcuts": self._calculate_shortcut_match(),
            "hierarchical_context": self._calculate_hierarchical_match()
        }
    
    def _calculate_time_proximity(self) -> float:
        """Calculate confidence based on temporal proximity."""
        if not self.notion_contexts:
            return 0.0
        
        # Simplified - would implement actual time window calculation
        return 0.5  # Placeholder
    
    def _calculate_content_similarity(self) -> float:
        """Calculate confidence based on content similarity."""
        if not self.notion_contexts:
            return 0.0
        
        # Simplified - would implement TF-IDF or embedding similarity
        return 0.3  # Placeholder
    
    def _calculate_shortcut_match(self) -> float:
        """Calculate confidence based on personal shortcut recognition."""
        if not self.calendar_entry.personal_shortcuts:
            return 0.0
        
        # Check if shortcuts appear in Notion context
        shortcuts = set(self.calendar_entry.personal_shortcuts)
        notion_content = " ".join([block.content for block in self.notion_contexts])
        
        matches = sum(1 for shortcut in shortcuts if shortcut.lower() in notion_content.lower())
        return matches / len(shortcuts) if shortcuts else 0.0
    
    def _calculate_hierarchical_match(self) -> float:
        """Calculate confidence based on hierarchical tag consistency."""
        if not self.calendar_entry.hierarchical_tags:
            return 0.0
        
        # Simplified - would check tag consistency across contexts
        return 0.2  # Placeholder
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            'calendar_entry': self.calendar_entry.to_dict(),
            'notion_contexts': [block.to_dict() for block in self.notion_contexts],
            'match_confidence': self.match_confidence,
            'match_method': self.match_method,
            'match_reasoning': self.match_reasoning,
            'unified_activity': self.unified_activity,
            'generated_abstract': self.generated_abstract,
            'needs_review': self.needs_review,
            'review_reason': self.review_reason,
            'processed_at': self.processed_at.isoformat() if self.processed_at else None
        }


@dataclass
class EditTrackingTree:
    """
    Daily tree structure for tracking recently updated Notion blocks.
    
    Enables efficient processing by focusing only on recently changed content
    rather than scanning entire Notion database.
    """
    date: str = ""  # YYYY-MM-DD for this tree
    root_pages: List[str] = field(default_factory=list)  # Page IDs with updates
    updated_blocks: Dict[str, NotionBlock] = field(default_factory=dict)  # block_id -> NotionBlock
    parent_child_map: Dict[str, List[str]] = field(default_factory=dict)  # parent_id -> [child_ids]
    
    # Propagation tracking
    propagation_complete: bool = False
    last_updated: Optional[datetime] = None
    
    def add_updated_block(self, block: NotionBlock) -> None:
        """Add a recently updated block to the tree."""
        self.updated_blocks[block.id] = block
        
        # Update parent-child relationships
        if block.parent_id:
            if block.parent_id not in self.parent_child_map:
                self.parent_child_map[block.parent_id] = []
            if block.id not in self.parent_child_map[block.parent_id]:
                self.parent_child_map[block.parent_id].append(block.id)
    
    def propagate_updates_to_parents(self) -> None:
        """Propagate update notifications up the tree hierarchy."""
        # Implementation would traverse tree and mark parents as needing update
        pass
    
    def get_blocks_for_processing(self) -> List[NotionBlock]:
        """Get all blocks that need processing today."""
        return list(self.updated_blocks.values())
    
    def clear_previous_day(self) -> None:
        """Clear previous day's update tracking."""
        self.updated_blocks.clear()
        self.parent_child_map.clear()
        self.propagation_complete = False
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            'date': self.date,
            'root_pages': self.root_pages,
            'updated_blocks': {k: v.to_dict() for k, v in self.updated_blocks.items()},
            'parent_child_map': self.parent_child_map,
            'propagation_complete': self.propagation_complete,
            'last_updated': self.last_updated.isoformat() if self.last_updated else None
        }