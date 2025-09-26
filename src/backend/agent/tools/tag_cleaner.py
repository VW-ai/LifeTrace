"""
Tag Cleaner Tool

AI-powered tool to analyze all tags in the database and identify/remove meaningless ones.
Runs as a post-processing step after tag generation to ensure clean, meaningful tags.
"""

import os
import json
from typing import List, Dict, Any, Optional, Set
from dataclasses import dataclass

try:
    from openai import OpenAI  # type: ignore
except Exception:
    OpenAI = None  # type: ignore

from .tagging_logger import get_logger
from ..prompts.tag_cleanup_prompts import TagCleanupPrompts


@dataclass
class TagAnalysis:
    """Result of tag meaningfulness analysis."""
    tag_name: str
    action: str  # 'keep', 'remove', or 'merge'
    reason: str
    confidence: float
    merge_target: Optional[str] = None


@dataclass 
class MergeProposal:
    """Proposed tag merge operation."""
    source_tag: str
    target_tag: str
    reason: str
    confidence: float
    source_usage: int
    target_usage: int


class TagCleaner:
    """AI-powered tag cleanup service to remove meaningless tags."""
    
    def __init__(self, api_key: Optional[str] = None, model: str = None):
        """Initialize with OpenAI API configuration."""
        self.api_key = api_key or os.getenv('OPENAI_API_KEY')
        self.model = model or os.getenv('OPENAI_MODEL', 'gpt-3.5-turbo')
        self.client = OpenAI(api_key=self.api_key) if (self.api_key and OpenAI) else None
        import logging
        self.logger = logging.getLogger(__name__)
        logging.basicConfig(level=logging.INFO)
        
        # Known meaningless patterns (fallback if AI unavailable)
        self.meaningless_patterns = {
            'system_artifacts': ['scheduled_activity', 'activities', 'tasks', 'events'],
            'redundant_plurals': ['meetings', 'writings', 'codings'],
            'meta_tags': ['working', 'things', 'stuff', 'general', 'misc', 'other'],
            'empty_concepts': ['activity', 'item', 'entry']
        }
    
    def analyze_tags(self, tags_with_context: List[Dict[str, Any]]) -> List[TagAnalysis]:
        """
        Analyze all tags to identify meaningless ones.
        
        Args:
            tags_with_context: List of dicts with 'name', 'usage_count', 'sample_activities'
        
        Returns:
            List of TagAnalysis objects
        """
        if not self.client:
            return self._fallback_analysis(tags_with_context)
        
        try:
            return self._ai_analysis(tags_with_context)
        except Exception as e:
            self.logger.warning(f"AI analysis failed, using fallback: {e}")
            return self._fallback_analysis(tags_with_context)
    
    def _ai_analysis(self, tags_with_context: List[Dict[str, Any]]) -> List[TagAnalysis]:
        """Use AI to analyze tag meaningfulness and identify merge opportunities."""
        
        # Format tags for analysis using centralized prompts
        tags_text = TagCleanupPrompts.format_tags_for_analysis(tags_with_context)
        
        system_prompt = TagCleanupPrompts.get_tag_analysis_system_prompt()
        user_prompt = TagCleanupPrompts.get_tag_analysis_user_prompt(tags_text)
        
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.3,
            timeout=30  # 30 second timeout
        )
        
        response_text = response.choices[0].message.content
        return self._parse_ai_response(response_text, tags_with_context)
    
    def _fallback_analysis(self, tags_with_context: List[Dict[str, Any]]) -> List[TagAnalysis]:
        """Fallback analysis using pattern matching when AI unavailable."""
        analyses = []
        tag_lookup = {tag['name']: tag for tag in tags_with_context}
        
        for tag_info in tags_with_context:
            tag_name = tag_info['name']
            tag_lower = tag_name.lower()
            action = "keep"
            reason = "Appears meaningful"
            confidence = 0.7
            merge_target = None
            
            # Check for meaningless patterns
            for category, patterns in self.meaningless_patterns.items():
                if any(pattern in tag_lower for pattern in patterns):
                    action = "remove"
                    reason = f"Matches {category} pattern"
                    confidence = 0.9
                    break
            
            # Check for merge opportunities (plural/singular)
            if action == "keep":
                merge_target = self._find_merge_target(tag_name, tag_lookup)
                if merge_target:
                    action = "merge"
                    reason = f"Redundant variant of '{merge_target}'"
                    confidence = 0.8
            
            # Additional heuristics
            if len(tag_lower) < 3:
                action = "remove"
                reason = "Too short to be meaningful"
                confidence = 0.8
            elif tag_lower.count('_') > 2:
                confidence = 0.5
            
            analyses.append(TagAnalysis(
                tag_name=tag_name,
                action=action,
                reason=reason,
                confidence=confidence,
                merge_target=merge_target
            ))
        
        return analyses
    
    def _find_merge_target(self, tag_name: str, tag_lookup: Dict[str, Any]) -> Optional[str]:
        """Find potential merge target for a tag using simple heuristics."""
        tag_lower = tag_name.lower()
        
        # Check for plural/singular variants
        if tag_lower.endswith('s') and len(tag_lower) > 3:
            singular = tag_lower[:-1]
            for other_tag in tag_lookup:
                if other_tag.lower() == singular and other_tag != tag_name:
                    # Prefer the one with higher usage
                    if tag_lookup[other_tag]['usage_count'] >= tag_lookup[tag_name]['usage_count']:
                        return other_tag
        
        # Check if this is singular of a plural
        plural = tag_lower + 's'
        for other_tag in tag_lookup:
            if other_tag.lower() == plural and other_tag != tag_name:
                if tag_lookup[other_tag]['usage_count'] > tag_lookup[tag_name]['usage_count']:
                    return other_tag
        
        return None
    
    
    def _parse_ai_response(self, response_text: str, original_tags: List[Dict[str, Any]]) -> List[TagAnalysis]:
        """Parse AI response into TagAnalysis objects with merge support."""
        try:
            response_data = json.loads(response_text)
            analyses = []
            
            # Create lookup for original tags
            tag_lookup = {tag['name']: tag for tag in original_tags}
            
            for action_item in response_data.get('actions', []):
                tag_name = action_item.get('tag')
                if tag_name and tag_name in tag_lookup:
                    analyses.append(TagAnalysis(
                        tag_name=tag_name,
                        action=action_item.get('action', 'keep'),
                        reason=action_item.get('reason', 'No reason provided'),
                        confidence=action_item.get('confidence', 0.5),
                        merge_target=action_item.get('merge_into')
                    ))
            
            return analyses
            
        except Exception as e:
            self.logger.error(f"Failed to parse AI response: {e}")
            # Fallback to pattern matching
            return self._fallback_analysis(original_tags)
    
    def clean_meaningless_tags(
        self, 
        db_manager, 
        dry_run: bool = True,
        confidence_threshold: float = 0.7
    ) -> Dict[str, Any]:
        """
        Main cleanup function - analyze and remove meaningless tags.
        
        Args:
            db_manager: Database manager instance
            dry_run: If True, only analyze without removing
            confidence_threshold: Minimum confidence to remove a tag
        
        Returns:
            Dict with cleanup results
        """
        self.logger.info("Starting tag cleanup analysis...")
        self.logger.info(f"OpenAI client available: {self.client is not None}")
        if self.client:
            self.logger.info(f"Using model: {self.model}")
        
        # Get all tags with context
        tags_with_context = self._fetch_tags_with_context(db_manager)
        
        if not tags_with_context:
            return {"status": "no_tags", "message": "No tags found to analyze"}
        
        # Analyze tags
        analyses = self.analyze_tags(tags_with_context)
        
        # Categorize actions
        tags_to_remove = []
        tags_to_merge = []
        tags_to_keep = []
        
        for analysis in analyses:
            if analysis.confidence >= confidence_threshold:
                if analysis.action == "remove":
                    tags_to_remove.append(analysis)
                elif analysis.action == "merge" and analysis.merge_target:
                    tags_to_merge.append(analysis)
                else:
                    tags_to_keep.append(analysis)
            else:
                tags_to_keep.append(analysis)
        
        self.logger.info(f"Analysis complete: {len(tags_to_remove)} to remove, {len(tags_to_merge)} to merge")
        
        # Execute changes if not dry run
        removed_count = 0
        merged_count = 0
        
        if not dry_run:
            if tags_to_remove:
                removed_count = self._remove_tags(db_manager, [t.tag_name for t in tags_to_remove])
            if tags_to_merge:
                merged_count = self._merge_tags(db_manager, tags_to_merge)
        
        return {
            "status": "success",
            "total_analyzed": len(analyses),
            "marked_for_removal": len(tags_to_remove),
            "marked_for_merge": len(tags_to_merge),
            "removed": removed_count,
            "merged": merged_count,
            "dry_run": dry_run,
            "tags_to_remove": [
                {
                    "name": t.tag_name,
                    "reason": t.reason,
                    "confidence": t.confidence
                }
                for t in tags_to_remove
            ],
            "tags_to_merge": [
                {
                    "source": t.tag_name,
                    "target": t.merge_target,
                    "reason": t.reason,
                    "confidence": t.confidence
                }
                for t in tags_to_merge
            ]
        }
    
    def _fetch_tags_with_context(self, db_manager) -> List[Dict[str, Any]]:
        """Fetch all tags with usage context from database."""
        query = """
        SELECT 
            t.name,
            t.usage_count,
            GROUP_CONCAT(pa.combined_details, ' | ') as sample_activities
        FROM tags t
        LEFT JOIN activity_tags at ON t.id = at.tag_id
        LEFT JOIN processed_activities pa ON at.processed_activity_id = pa.id
        WHERE t.usage_count > 0
        GROUP BY t.id, t.name, t.usage_count
        ORDER BY t.usage_count DESC
        """
        
        rows = db_manager.execute_query(query)
        
        result = []
        for row in rows:
            # Parse sample activities and take first few as examples
            activities_text = row['sample_activities'] or ""
            sample_activities = [
                act.strip()[:50] + "..." if len(act.strip()) > 50 else act.strip()
                for act in activities_text.split(' | ')[:5]
                if act.strip()
            ]
            
            result.append({
                'name': row['name'],
                'usage_count': row['usage_count'],
                'sample_activities': sample_activities
            })
        
        return result
    
    def _remove_tags(self, db_manager, tag_names: List[str]) -> int:
        """Remove specified tags from database."""
        if not tag_names:
            return 0
        
        removed_count = 0
        
        for tag_name in tag_names:
            try:
                # Get tag ID
                tag_query = "SELECT id FROM tags WHERE name = ?"
                tag_result = db_manager.execute_query(tag_query, [tag_name])
                
                if not tag_result:
                    continue
                
                tag_id = tag_result[0]['id']
                
                # Remove associated activity_tags first
                db_manager.execute_query(
                    "DELETE FROM activity_tags WHERE tag_id = ?", 
                    [tag_id]
                )
                
                # Remove the tag
                db_manager.execute_query(
                    "DELETE FROM tags WHERE id = ?", 
                    [tag_id]
                )
                
                self.logger.info(f"Removed meaningless tag: {tag_name}")
                removed_count += 1
                
            except Exception as e:
                self.logger.error(f"Failed to remove tag {tag_name}: {e}")
        
        return removed_count
    
    def _merge_tags(self, db_manager, tags_to_merge: List[TagAnalysis]) -> int:
        """Merge specified tags into their targets."""
        if not tags_to_merge:
            return 0
        
        merged_count = 0
        
        for merge_analysis in tags_to_merge:
            source_tag = merge_analysis.tag_name
            target_tag = merge_analysis.merge_target
            
            if not target_tag:
                continue
                
            try:
                # Get source and target tag IDs
                source_query = "SELECT id FROM tags WHERE name = ?"
                source_result = db_manager.execute_query(source_query, [source_tag])
                
                target_query = "SELECT id FROM tags WHERE name = ?"
                target_result = db_manager.execute_query(target_query, [target_tag])
                
                if not source_result or not target_result:
                    self.logger.warning(f"Cannot merge {source_tag} → {target_tag}: tag not found")
                    continue
                
                source_id = source_result[0]['id']
                target_id = target_result[0]['id']
                
                # Move all activity_tags from source to target
                update_query = """
                UPDATE activity_tags 
                SET tag_id = ? 
                WHERE tag_id = ? 
                AND NOT EXISTS (
                    SELECT 1 FROM activity_tags 
                    WHERE processed_activity_id = activity_tags.processed_activity_id 
                    AND tag_id = ?
                )
                """
                db_manager.execute_query(update_query, [target_id, source_id, target_id])
                
                # Remove duplicate activity_tags (same activity with both source and target)
                cleanup_query = "DELETE FROM activity_tags WHERE tag_id = ?"
                db_manager.execute_query(cleanup_query, [source_id])
                
                # Update target tag usage count
                count_query = "SELECT COUNT(*) as count FROM activity_tags WHERE tag_id = ?"
                count_result = db_manager.execute_query(count_query, [target_id])
                new_usage = count_result[0]['count'] if count_result else 0
                
                update_usage_query = "UPDATE tags SET usage_count = ? WHERE id = ?"
                db_manager.execute_query(update_usage_query, [new_usage, target_id])
                
                # Delete the source tag
                db_manager.execute_query("DELETE FROM tags WHERE id = ?", [source_id])
                
                self.logger.info(f"Merged '{source_tag}' → '{target_tag}'")
                merged_count += 1
                
            except Exception as e:
                self.logger.error(f"Failed to merge {source_tag} → {target_tag}: {e}")
        
        return merged_count