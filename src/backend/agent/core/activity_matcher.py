from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime, timedelta
from .models import RawActivity

class ActivityMatcher:
    """Handles matching Notion edits with Calendar events using time correlation."""
    
    def __init__(self, time_window_minutes: int = 120):
        """Initialize with configurable time correlation window."""
        self.time_window_minutes = time_window_minutes
        
    def match_activities(self, raw_activities: List[RawActivity]) -> List[RawActivity]:
        """Match and merge activities from different sources based on time correlation."""
        # Separate activities by source
        notion_activities = [a for a in raw_activities if a.source == "notion"]
        calendar_activities = [a for a in raw_activities if a.source == "google_calendar"]
        
        if not notion_activities or not calendar_activities:
            # If only one type, still process Notion activities for duration estimation
            if notion_activities and not calendar_activities:
                return self._process_unmatched_notion_activities(notion_activities) + calendar_activities
            return raw_activities
        
        # Find matches and merge
        matched_activities = []
        unmatched_notion = []
        unmatched_calendar = list(calendar_activities)  # Start with all calendar items
        
        for notion_activity in notion_activities:
            match_result = self._find_best_calendar_match(notion_activity, calendar_activities)
            
            if match_result:
                calendar_match, confidence = match_result
                if confidence > 0.3:  # Configurable threshold
                    # Create merged activity
                    merged = self._merge_activities(notion_activity, calendar_match)
                    matched_activities.append(merged)
                    
                    # Remove matched calendar activity from unmatched list
                    unmatched_calendar = [c for c in unmatched_calendar if c != calendar_match]
                else:
                    unmatched_notion.append(notion_activity)
            else:
                unmatched_notion.append(notion_activity)
        
        # Estimate duration for unmatched Notion activities
        processed_notion = self._process_unmatched_notion_activities(unmatched_notion)
        
        # Combine all activities
        result = matched_activities + processed_notion + unmatched_calendar
        
        print(f"Activity Matching Results:")
        print(f"  - Matched pairs: {len(matched_activities)}")
        print(f"  - Unmatched Notion: {len(processed_notion)}")
        print(f"  - Unmatched Calendar: {len(unmatched_calendar)}")
        
        return result
    
    def _find_best_calendar_match(self, notion_activity: RawActivity, 
                                calendar_activities: List[RawActivity]) -> Optional[Tuple[RawActivity, float]]:
        """Find the best calendar match for a Notion activity based on time and content similarity."""
        if not notion_activity.date:
            return None
        
        candidates = []
        
        for calendar_activity in calendar_activities:
            if not calendar_activity.date or not calendar_activity.time:
                continue
            
            # Check if dates are close (within 1 day)
            if not self._dates_within_window(notion_activity.date, calendar_activity.date, days=1):
                continue
            
            # Calculate time-based confidence
            time_confidence = self._calculate_time_confidence(notion_activity, calendar_activity)
            
            # Calculate content similarity confidence
            content_confidence = self._calculate_content_similarity(notion_activity, calendar_activity)
            
            # Combined confidence score (weighted)
            combined_confidence = (time_confidence * 0.4) + (content_confidence * 0.6)
            
            candidates.append((calendar_activity, combined_confidence))
        
        if not candidates:
            return None
        
        # Return best match
        candidates.sort(key=lambda x: x[1], reverse=True)
        return candidates[0]
    
    def _calculate_time_confidence(self, notion_activity: RawActivity, 
                                 calendar_activity: RawActivity) -> float:
        """Calculate confidence based on temporal proximity."""
        # For Notion activities without specific time, assume they happened during calendar event
        if not notion_activity.time:
            # If calendar event exists on same date, moderate confidence
            if notion_activity.date == calendar_activity.date:
                return 0.5
            return 0.0
        
        # Both have times - calculate exact time difference
        try:
            notion_dt = datetime.strptime(f"{notion_activity.date} {notion_activity.time}", "%Y-%m-%d %H:%M")
            calendar_dt = datetime.strptime(f"{calendar_activity.date} {calendar_activity.time}", "%Y-%m-%d %H:%M")
            
            time_diff_minutes = abs((notion_dt - calendar_dt).total_seconds() / 60)
            
            if time_diff_minutes <= 15:
                return 1.0
            elif time_diff_minutes <= 60:
                return 0.8
            elif time_diff_minutes <= 90:
                return 0.6
            elif time_diff_minutes <= self.time_window_minutes:
                return 0.4
            else:
                return 0.1
                
        except ValueError:
            return 0.0
    
    def _calculate_content_similarity(self, notion_activity: RawActivity, 
                                    calendar_activity: RawActivity) -> float:
        """Calculate content similarity confidence using keyword overlap."""
        notion_text = notion_activity.details.lower()
        calendar_text = calendar_activity.details.lower()
        
        if not notion_text or not calendar_text:
            return 0.3  # Neutral confidence when no content
        
        # Extract keywords (simple approach)
        notion_words = set(word for word in notion_text.split() if len(word) > 3)
        calendar_words = set(word for word in calendar_text.split() if len(word) > 3)
        
        if not notion_words or not calendar_words:
            return 0.3
        
        # Calculate Jaccard similarity
        intersection = notion_words & calendar_words
        union = notion_words | calendar_words
        
        similarity = len(intersection) / len(union) if union else 0
        
        # Also check for partial matches
        partial_matches = 0
        for n_word in notion_words:
            for c_word in calendar_words:
                if n_word in c_word or c_word in n_word:
                    partial_matches += 1
                    break
        
        partial_score = partial_matches / max(len(notion_words), len(calendar_words))
        
        # Combine exact and partial matches
        final_score = max(similarity, partial_score * 0.7)
        
        return min(final_score, 1.0)
    
    def _merge_activities(self, notion_activity: RawActivity, 
                         calendar_activity: RawActivity) -> RawActivity:
        """Merge a Notion and Calendar activity into a single enhanced activity."""
        # Use calendar timing as authoritative
        merged_date = calendar_activity.date
        merged_time = calendar_activity.time
        merged_duration = calendar_activity.duration_minutes
        
        # Combine details with hierarchy from Notion
        combined_details = calendar_activity.details
        if notion_activity.details and notion_activity.details != calendar_activity.details:
            combined_details += f" | {notion_activity.details}"
        
        # Merge raw_data from both sources
        merged_raw_data = {
            **calendar_activity.raw_data,
            'notion_data': notion_activity.raw_data,
            'merged_from': ['notion', 'google_calendar'],
            'match_confidence': self._calculate_combined_confidence(notion_activity, calendar_activity)
        }
        
        return RawActivity(
            date=merged_date,
            time=merged_time,
            duration_minutes=merged_duration,
            details=combined_details,
            source="merged",
            orig_link=calendar_activity.orig_link,
            raw_data=merged_raw_data
        )
    
    def _calculate_combined_confidence(self, notion_activity: RawActivity, 
                                     calendar_activity: RawActivity) -> float:
        """Calculate the overall confidence score for the merge."""
        time_conf = self._calculate_time_confidence(notion_activity, calendar_activity)
        content_conf = self._calculate_content_similarity(notion_activity, calendar_activity)
        return (time_conf * 0.4) + (content_conf * 0.6)
    
    def _process_unmatched_notion_activities(self, notion_activities: List[RawActivity]) -> List[RawActivity]:
        """Process unmatched Notion activities by estimating durations and enhancing details."""
        processed = []
        
        for activity in notion_activities:
            # Estimate duration based on content length and type
            estimated_duration = self._estimate_duration(activity)
            
            # Create enhanced activity
            enhanced_activity = RawActivity(
                date=activity.date,
                time=activity.time,
                duration_minutes=estimated_duration,
                details=activity.details,
                source=activity.source,
                orig_link=activity.orig_link,
                raw_data={
                    **activity.raw_data,
                    'duration_estimated': True,
                    'estimation_method': 'content_analysis'
                }
            )
            
            processed.append(enhanced_activity)
        
        return processed
    
    def _estimate_duration(self, activity: RawActivity) -> int:
        """Estimate duration for Notion activity based on content analysis."""
        content = activity.details.lower()
        word_count = len(content.split())
        
        # Basic heuristics for duration estimation
        if word_count < 10:
            return 15  # Short note/task
        elif word_count < 50:
            return 30  # Medium task
        elif word_count < 100:
            return 60  # Longer task
        else:
            return 90  # Complex task/session
        
        # Could be enhanced with keyword-based rules:
        # - "meeting" -> 60 minutes
        # - "call" -> 30 minutes
        # - "coding"/"programming" -> 90 minutes
        # - "quick"/"brief" -> 15 minutes
    
    def _dates_within_window(self, date1: str, date2: str, days: int = 1) -> bool:
        """Check if two dates are within the specified window."""
        try:
            dt1 = datetime.strptime(date1, "%Y-%m-%d")
            dt2 = datetime.strptime(date2, "%Y-%m-%d")
            diff = abs((dt1 - dt2).days)
            return diff <= days
        except ValueError:
            return False
    
    def get_matching_statistics(self, activities: List[RawActivity]) -> Dict[str, Any]:
        """Generate statistics about activity matching results."""
        total_activities = len(activities)
        merged_count = len([a for a in activities if a.source == "merged"])
        notion_only = len([a for a in activities if a.source == "notion"])
        calendar_only = len([a for a in activities if a.source == "google_calendar"])
        
        return {
            'total_activities': total_activities,
            'merged_activities': merged_count,
            'notion_only': notion_only,
            'calendar_only': calendar_only,
            'merge_rate': round(merged_count / total_activities * 100, 1) if total_activities > 0 else 0
        }