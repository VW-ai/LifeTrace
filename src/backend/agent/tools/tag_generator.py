import os
import json
from typing import List, Dict, Any, Optional, Tuple
from openai import OpenAI
from ..core.models import TagGenerationContext, RawActivity
from ..prompts.tag_prompts import TagPrompts

class TagGenerator:
    """Handles intelligent tag generation using LLM integration."""
    
    def __init__(self, api_key: Optional[str] = None, model: str = "gpt-3.5-turbo"):
        """Initialize with OpenAI API configuration."""
        self.api_key = api_key or os.getenv('OPENAI_API_KEY')
        self.model = model
        self.client = OpenAI(api_key=self.api_key) if self.api_key else None
        
        # Tag management
        self.existing_tags = []
        self.tag_event_ratio_threshold = 0.3  # Configurable threshold

        # Calibration (Phase 2): thresholds, weights, synonyms/taxonomy, biases
        self.calibration: Dict[str, Any] = {}
        try:
            # Default resource path inside repo
            base_dir = os.path.join(os.path.dirname(__file__), '..', 'resources')
            calib_path = os.path.abspath(os.path.join(base_dir, 'tagging_calibration.json'))
            self.load_calibration(calib_path)
        except Exception as e:
            print(f"Warning: failed to load tagging calibration: {e}")
            self.calibration = {
                "threshold": 0.5,
                "max_tags": 10,
                "weights": {
                    "synonym_match": 1.0,
                    "taxonomy_match": 1.2,
                    "title_bonus": 0.3,
                    "duration_scale": 0.001
                },
                "downweight": {"work": 0.5},
                "synonyms": {},
                "taxonomy": {},
                "source_bias": {}
            }

    def load_calibration(self, path: str) -> None:
        """Load tagging calibration JSON from resources."""
        with open(path, 'r', encoding='utf-8') as f:
            self.calibration = json.load(f)
    
    def load_existing_tags(self, tags_file: str = 'existing_tags.json') -> None:
        """Load existing tags from storage."""
        try:
            with open(tags_file, 'r', encoding='utf-8') as f:
                self.existing_tags = json.load(f)
            print(f"Loaded {len(self.existing_tags)} existing tags")
        except FileNotFoundError:
            print("No existing tags file found, starting fresh")
            self.existing_tags = []
        except json.JSONDecodeError:
            print("Error loading tags file, starting fresh")
            self.existing_tags = []
    
    def save_tags(self, tags_file: str = 'existing_tags.json') -> None:
        """Save current tags to storage."""
        unique_tags = list(set(self.existing_tags))
        with open(tags_file, 'w', encoding='utf-8') as f:
            json.dump(unique_tags, f, ensure_ascii=False, indent=2)
    
    def find_matching_existing_tags(self, activity_text: str, threshold: float = 0.6) -> List[str]:
        """Find existing tags that might match the activity using simple keyword matching."""
        if not self.existing_tags:
            return []
        
        activity_lower = activity_text.lower()
        matching_tags = []
        
        for tag in self.existing_tags:
            tag_lower = tag.lower()
            # Simple keyword matching - could be enhanced with semantic similarity
            if (tag_lower in activity_lower or 
                any(word in activity_lower for word in tag_lower.split()) or
                any(word in tag_lower for word in activity_lower.split())):
                matching_tags.append(tag)
        
        return matching_tags
    
    def generate_tags_with_llm(self, context: TagGenerationContext) -> List[str]:
        """Generate tags using LLM with context about existing tags."""
        if not self.client:
            print("Warning: No OpenAI API key provided, using fallback tag generation")
            return self._generate_fallback_tags(context)
        
        system_prompt = TagPrompts.get_individual_tag_system_prompt()
        user_prompt = TagPrompts.get_individual_tag_user_prompt(context)

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.3,
                max_tokens=50
            )
            
            tags_text = response.choices[0].message.content.strip()
            tags = [tag.strip().lower() for tag in tags_text.split(',') if tag.strip()]
            
            # Limit to 3 tags maximum
            return tags[:3]
            
        except Exception as e:
            print(f"Error calling OpenAI API: {e}")
            return self._generate_fallback_tags(context)
    
    def _generate_fallback_tags(self, context: TagGenerationContext) -> List[str]:
        """Fallback tag generation using simple keyword matching."""
        activity_lower = context.activity_text.lower()
        
        # Simple keyword-based tagging as fallback
        keyword_tags = {
            'programming': ['code', 'coding', 'program', 'debug', 'develop', 'git', 'python', 'javascript'],
            'meeting': ['meeting', 'call', 'conference', '会议', '接口meeting'],
            'study': ['study', 'learn', 'read', 'research', 'education'],
            'work': ['work', 'project', 'task', 'client', '客户'],
            'planning': ['plan', 'planning', 'organize', 'schedule'],
            'writing': ['write', 'document', 'note', 'diary', '文档'],
            'communication': ['email', 'message', 'chat', 'discussion']
        }
        
        generated_tags = []
        for tag, keywords in keyword_tags.items():
            if any(keyword in activity_lower for keyword in keywords):
                generated_tags.append(tag)
        
        # If no matches, create a generic tag based on source
        if not generated_tags:
            if context.source == 'google_calendar':
                generated_tags = ['scheduled_activity']
            else:
                generated_tags = ['general_activity']
        
        return generated_tags[:3]  # Limit to 3 tags
    
    def generate_tags_for_activity(self, activity: RawActivity) -> List[str]:
        """Generate tags for a single activity with calibrated scoring and thresholds."""
        # Create context for tag generation
        context = TagGenerationContext(
            existing_tags=self.existing_tags,
            activity_text=activity.details,
            source=activity.source,
            duration_minutes=activity.duration_minutes,
            time_context=activity.time
        )
        # Build candidate scores from: existing tag matches, synonyms, taxonomy, and (optionally) LLM
        scores = self._score_candidates(activity)
        if not scores:
            # Fall back to previous mechanisms if scoring produced nothing
            matching_tags = self.find_matching_existing_tags(activity.details)
            if matching_tags:
                return matching_tags[: self.calibration.get('max_tags', 3)]
            new_tags = self.generate_tags_with_llm(context)
            for tag in new_tags:
                if tag not in self.existing_tags:
                    self.existing_tags.append(tag)
            return new_tags

        # Normalize and select above threshold
        selected = self._select_top_tags(scores)
        # Track any new tags
        for tag in selected:
            if tag not in self.existing_tags:
                self.existing_tags.append(tag)
        return selected

    def _select_top_tags(self, scores: Dict[str, float]) -> List[str]:
        """Normalize scores to [0,1], apply threshold and return top N tags."""
        if not scores:
            return []
        max_score = max(scores.values()) or 1.0
        threshold = float(self.calibration.get('threshold', 0.5))
        max_tags = int(self.calibration.get('max_tags', 3))
        # Normalize
        norm = {t: (s / max_score) for t, s in scores.items()}
        # Apply threshold and sort
        filtered = [(t, v) for t, v in norm.items() if v >= threshold]
        if not filtered:
            # Ensure at least one tag
            t, _ = max(norm.items(), key=lambda x: x[1])
            return [t]
        filtered.sort(key=lambda x: x[1], reverse=True)
        return [t for t, _ in filtered[:max_tags]]

    def _score_candidates(self, activity: RawActivity) -> Dict[str, float]:
        """Produce candidate tag scores using synonyms, taxonomy, and biases."""
        text = (activity.details or '').lower()
        words = set(text.split())
        dur = float(activity.duration_minutes or 0)
        source = activity.source or ''

        cal = self.calibration
        syn = cal.get('synonyms', {})
        tax = cal.get('taxonomy', {})
        weights = cal.get('weights', {})
        down = cal.get('downweight', {})
        bias = cal.get('source_bias', {}).get(source, {})

        scores: Dict[str, float] = {}

        # Synonym matches
        for tag, keys in syn.items():
            for k in keys:
                if k.lower() in text:
                    scores[tag] = scores.get(tag, 0.0) + float(weights.get('synonym_match', 1.0))

        # Taxonomy matches: if a subtag matched above, give parent tag some credit
        for parent, children in tax.items():
            for child in children:
                if child in scores:
                    scores[parent] = scores.get(parent, 0.0) + float(weights.get('taxonomy_match', 1.2))

        # Duration scaling (longer tasks likely more significant)
        scores = {t: s + dur * float(weights.get('duration_scale', 0.0)) for t, s in scores.items()}

        # Source bias adjustments
        for t in list(scores.keys()):
            scores[t] = scores[t] + float(bias.get(t, 0.0))

        # Title bonus (approximate: early words perceived as title keywords)
        first_tokens = set((activity.details or '').lower().split()[:6])
        for tag, keys in syn.items():
            if any(k in first_tokens for k in keys):
                scores[tag] = scores.get(tag, 0.0) + float(weights.get('title_bonus', 0.0))

        # Downweight generic tags (e.g., 'work')
        for t, factor in down.items():
            if t in scores:
                scores[t] *= float(factor)

        return scores
    
    def should_regenerate_system_tags(self, total_events: int) -> bool:
        """Check if system-wide tag regeneration is needed."""
        if not self.existing_tags or total_events == 0:
            return False
        
        ratio = len(self.existing_tags) / total_events
        return ratio > self.tag_event_ratio_threshold
    
    def regenerate_system_tags(self, all_activities: List[RawActivity]) -> Dict[str, List[str]]:
        """Regenerate tags for all activities when ratio threshold is exceeded."""
        print("Initiating system-wide tag regeneration...")
        
        # Collect all activity texts for batch processing
        activity_texts = [activity.details for activity in all_activities]
        
        if not self.client:
            print("Warning: No OpenAI API key, using fallback for system regeneration")
            return self._fallback_system_regeneration(all_activities)
        
        system_prompt = TagPrompts.get_system_regeneration_system_prompt()
        user_prompt = TagPrompts.get_system_regeneration_user_prompt(activity_texts)
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.2,
                max_tokens=2000
            )
            
            result_text = response.choices[0].message.content.strip()
            tag_mapping = json.loads(result_text)
            
            # Convert to activity-based mapping
            activity_tag_map = {}
            new_tag_set = set()
            
            for i, activity in enumerate(all_activities[:len(tag_mapping)]):
                activity_key = f"activity_{i}"
                tags = tag_mapping.get(str(i+1), ['general_activity'])
                activity_tag_map[activity_key] = tags
                new_tag_set.update(tags)
            
            # Update existing tags with consolidated set
            self.existing_tags = list(new_tag_set)
            print(f"System regeneration complete: {len(self.existing_tags)} consolidated tags")
            
            return activity_tag_map
            
        except Exception as e:
            print(f"Error in system tag regeneration: {e}")
            return self._fallback_system_regeneration(all_activities)
    
    def _fallback_system_regeneration(self, all_activities: List[RawActivity]) -> Dict[str, List[str]]:
        """Fallback system regeneration using keyword analysis."""
        # Simple approach: analyze most common keywords
        word_counts = {}
        
        for activity in all_activities:
            words = activity.details.lower().split()
            for word in words:
                if len(word) > 3:  # Skip short words
                    word_counts[word] = word_counts.get(word, 0) + 1
        
        # Get most common words as basis for tags
        common_words = sorted(word_counts.items(), key=lambda x: x[1], reverse=True)[:15]
        self.existing_tags = [word for word, count in common_words if count > 1]
        
        # Simple mapping based on keywords
        activity_tag_map = {}
        for i, activity in enumerate(all_activities):
            tags = self._generate_fallback_tags(TagGenerationContext(activity_text=activity.details))
            activity_tag_map[f"activity_{i}"] = tags
        
        return activity_tag_map
