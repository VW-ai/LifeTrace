import os
import json
import difflib
from typing import List, Dict, Any, Optional, Tuple
from openai import OpenAI
from ..core.models import TagGenerationContext, RawActivity
from ..prompts.tag_prompts import TagPrompts
from ..prompts.taxonomy_prompts import TaxonomyPrompts

class TagGenerator:
    """Handles intelligent tag generation using taxonomy-first LLM integration."""
    
    def __init__(self, api_key: Optional[str] = None, model: str = "gpt-3.5-turbo"):
        """Initialize with OpenAI API configuration and load taxonomy."""
        self.api_key = api_key or os.getenv('OPENAI_API_KEY')
        self.model = model
        self.client = OpenAI(api_key=self.api_key) if self.api_key else None
        
        # Load taxonomy and synonyms
        self.taxonomy = self._load_taxonomy()
        self.hierarchical_taxonomy = self._load_hierarchical_taxonomy()
        self.synonyms = self._load_synonyms()
        self.taxonomy_tags = list(self.taxonomy.get("taxonomy", {}).keys())
        
        # Tag management
        self.existing_tags = self.taxonomy_tags  # Initialize with taxonomy tags
        self.tag_event_ratio_threshold = 0.3  # Configurable threshold
        
    def _load_taxonomy(self) -> Dict[str, Any]:
        """Load tag taxonomy from resources."""
        resources_dir = os.path.join(os.path.dirname(__file__), '..', 'resources')
        taxonomy_path = os.path.join(resources_dir, 'tag_taxonomy.json')
        try:
            with open(taxonomy_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            print("Warning: tag_taxonomy.json not found, using basic taxonomy")
            return {
                "taxonomy": {
                    "work": {"description": "Work-related activities"},
                    "personal": {"description": "Personal activities"},
                    "study": {"description": "Learning activities"}
                }
            }
    
    def _load_hierarchical_taxonomy(self) -> Dict[str, Any]:
        """Load hierarchical taxonomy from resources."""
        resources_dir = os.path.join(os.path.dirname(__file__), '..', 'resources')
        hierarchy_path = os.path.join(resources_dir, 'hierarchical_taxonomy.json')
        try:
            with open(hierarchy_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            print("Warning: hierarchical_taxonomy.json not found, using basic hierarchy")
            return {"taxonomy": {}}
    
    def _load_synonyms(self) -> Dict[str, Any]:
        """Load synonyms from resources."""
        resources_dir = os.path.join(os.path.dirname(__file__), '..', 'resources')
        synonyms_path = os.path.join(resources_dir, 'synonyms.json')
        try:
            with open(synonyms_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            print("Warning: synonyms.json not found, using empty synonyms")
            return {"synonyms": {}}
    
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
    
    def fuzzy_map_to_taxonomy(self, freeform_tag: str, threshold: float = 0.8) -> Optional[Tuple[str, float]]:
        """Map a freeform tag to taxonomy using fuzzy string matching.
        
        Uses difflib.get_close_matches to find the closest taxonomy tag for
        a given freeform tag string. Supports case-insensitive matching.
        
        Args:
            freeform_tag: The tag string to map to taxonomy.
            threshold: Minimum similarity ratio required (0.0-1.0).
            
        Returns:
            Tuple of (taxonomy_tag, confidence_score) if match found, else None.
            Confidence score represents similarity ratio.
            
        Example:
            >>> tag_gen.fuzzy_map_to_taxonomy("worke", 0.8)
            ("work", 0.9)
        """
        if freeform_tag.lower() in [tag.lower() for tag in self.taxonomy_tags]:
            return freeform_tag.lower(), 1.0
        
        # Use difflib for fuzzy string matching
        matches = difflib.get_close_matches(
            freeform_tag.lower(), 
            [tag.lower() for tag in self.taxonomy_tags], 
            n=1, 
            cutoff=threshold
        )
        
        if matches:
            # Find the original case taxonomy tag
            for tax_tag in self.taxonomy_tags:
                if tax_tag.lower() == matches[0]:
                    confidence = difflib.SequenceMatcher(None, freeform_tag.lower(), matches[0]).ratio()
                    return tax_tag, confidence
        
        return None
    
    def map_synonyms_to_taxonomy(self, activity_text: str) -> List[Tuple[str, float]]:
        """Map activity text to taxonomy tags using synonyms."""
        activity_lower = activity_text.lower()
        synonym_matches = []
        
        synonyms_dict = self.synonyms.get("synonyms", {})
        personal_shortcuts = self.synonyms.get("personal_shortcuts", {})
        
        # Check personal shortcuts first (higher priority)
        for shortcut, categories in personal_shortcuts.items():
            if shortcut.lower() in activity_lower:
                for category in categories:
                    if category in self.taxonomy_tags:
                        synonym_matches.append((category, 0.95))  # High confidence for personal shortcuts
        
        # Check general synonyms
        for tax_tag, synonym_list in synonyms_dict.items():
            if tax_tag in self.taxonomy_tags:
                for synonym in synonym_list:
                    if synonym.lower() in activity_lower:
                        confidence = min(0.9, len(synonym) / 20.0)  # Longer matches = higher confidence
                        synonym_matches.append((tax_tag, confidence))
        
        # Remove duplicates and sort by confidence
        unique_matches = {}
        for tag, conf in synonym_matches:
            if tag not in unique_matches or unique_matches[tag] < conf:
                unique_matches[tag] = conf
                
        return [(tag, conf) for tag, conf in sorted(unique_matches.items(), key=lambda x: x[1], reverse=True)]
    
    def find_matching_taxonomy_tags(self, activity_text: str) -> List[Tuple[str, float]]:
        """Find taxonomy tags that match the activity using multiple methods."""
        # Method 1: Direct synonym mapping
        synonym_matches = self.map_synonyms_to_taxonomy(activity_text)
        
        # Method 2: Keyword matching against taxonomy descriptions
        activity_lower = activity_text.lower()
        keyword_matches = []
        
        for tag, info in self.taxonomy.get("taxonomy", {}).items():
            keywords = info.get("keywords", [])
            matches = sum(1 for keyword in keywords if keyword.lower() in activity_lower)
            if matches > 0:
                confidence = min(0.8, matches / len(keywords) * 2)  # Scale confidence by match ratio
                keyword_matches.append((tag, confidence))
        
        # Combine and deduplicate results
        all_matches = synonym_matches + keyword_matches
        unique_matches = {}
        for tag, conf in all_matches:
            if tag not in unique_matches or unique_matches[tag] < conf:
                unique_matches[tag] = conf
        
        return [(tag, conf) for tag, conf in sorted(unique_matches.items(), key=lambda x: x[1], reverse=True)]
    
    def generate_tags_with_llm(self, context: TagGenerationContext) -> List[Tuple[str, float]]:
        """Generate tags using LLM with taxonomy constraint and confidence scores."""
        if not self.client:
            print("Warning: No OpenAI API key provided, using fallback tag generation")
            return self._generate_fallback_tags_with_confidence(context)
        
        system_prompt = TagPrompts.get_individual_tag_system_prompt()
        user_prompt = TagPrompts.get_individual_tag_user_prompt(context)

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.2,  # Lower temperature for more consistent responses
                max_tokens=300   # Increased for JSON response with reasoning
            )
            
            response_text = response.choices[0].message.content.strip()
            
            # Parse JSON response
            try:
                result = json.loads(response_text)
                tags_with_confidence = []
                
                for tag_info in result.get("tags", []):
                    tag_name = tag_info.get("name", "").lower()
                    confidence = float(tag_info.get("confidence", 0.5))
                    
                    # Validate tag is in taxonomy
                    if tag_name in [t.lower() for t in self.taxonomy_tags]:
                        # Find the proper case version
                        proper_tag = next(t for t in self.taxonomy_tags if t.lower() == tag_name)
                        tags_with_confidence.append((proper_tag, confidence))
                
                return tags_with_confidence[:3]  # Limit to 3 tags
                
            except json.JSONDecodeError:
                # Fallback to simple comma-separated parsing
                tags = [tag.strip().lower() for tag in response_text.split(',') if tag.strip()]
                validated_tags = []
                for tag in tags:
                    # Try to map to taxonomy
                    mapping = self.fuzzy_map_to_taxonomy(tag)
                    if mapping:
                        validated_tags.append(mapping)
                return validated_tags[:3]
            
        except Exception as e:
            print(f"Error calling OpenAI API: {e}")
            return self._generate_fallback_tags_with_confidence(context)
    
    def _generate_fallback_tags_with_confidence(self, context: TagGenerationContext) -> List[Tuple[str, float]]:
        """Fallback tag generation using taxonomy-based matching with confidence scores."""
        # First try synonym-based matching
        synonym_matches = self.find_matching_taxonomy_tags(context.activity_text)
        
        if synonym_matches:
            return synonym_matches[:3]
        
        # If no synonym matches, use simple heuristics based on source and content
        activity_lower = context.activity_text.lower()
        fallback_tags = []
        
        # Content-based heuristics using taxonomy
        if any(word in activity_lower for word in ['meeting', '会议', 'call', 'conference']):
            fallback_tags.append(('work', 0.7))
        elif any(word in activity_lower for word in ['eat', 'meal', '吃', '用餐']):
            fallback_tags.append(('meals', 0.8))
        elif any(word in activity_lower for word in ['rest', 'sleep', '休息', '睡觉']):
            fallback_tags.append(('personal', 0.8))
        elif any(word in activity_lower for word in ['study', 'learn', '学习', 'read']):
            fallback_tags.append(('study', 0.7))
        elif any(word in activity_lower for word in ['exercise', 'gym', '健身', '运动']):
            fallback_tags.append(('exercise', 0.8))
        
        # Source-based heuristics
        if context.source == 'google_calendar':
            if not fallback_tags:
                fallback_tags.append(('work', 0.5))  # Calendar events often work-related
        elif context.source == 'notion':
            if not fallback_tags:
                fallback_tags.append(('personal', 0.5))  # Notion entries often personal reflection
        
        # Absolute fallback
        if not fallback_tags:
            fallback_tags.append(('personal', 0.3))  # Very low confidence generic tag
        
        return fallback_tags[:3]
    
    def _generate_fallback_tags(self, context: TagGenerationContext) -> List[str]:
        """Legacy fallback method for backward compatibility."""
        tags_with_conf = self._generate_fallback_tags_with_confidence(context)
        return [tag for tag, conf in tags_with_conf]
    
    def generate_tags_for_activity(self, activity: RawActivity) -> List[str]:
        """Generate tags for a single activity using taxonomy-first approach."""
        tags_with_conf = self.generate_tags_with_confidence_for_activity(activity)
        return [tag for tag, conf in tags_with_conf]
    
    def generate_tags_with_confidence_for_activity(self, activity: RawActivity) -> List[Tuple[str, float]]:
        """Generate tags with confidence scores for a single activity."""
        # Create context for tag generation
        context = TagGenerationContext(
            existing_tags=self.taxonomy_tags,  # Use taxonomy tags instead of arbitrary existing tags
            activity_text=activity.details,
            source=activity.source,
            duration_minutes=activity.duration_minutes,
            time_context=activity.time
        )
        
        # First, try direct taxonomy matching using synonyms and keywords
        matching_tags_with_conf = self.find_matching_taxonomy_tags(activity.details)
        if matching_tags_with_conf and matching_tags_with_conf[0][1] > 0.7:  # High confidence threshold
            print(f"Found high-confidence taxonomy matches: {matching_tags_with_conf}")
            return matching_tags_with_conf[:3]
        
        # If no high-confidence matches, use LLM with taxonomy constraint
        llm_tags_with_conf = self.generate_tags_with_llm(context)
        
        # Log confidence scores for monitoring
        for tag, conf in llm_tags_with_conf:
            print(f"Generated tag '{tag}' with confidence {conf:.2f}")
        
        return llm_tags_with_conf
    
    def assess_tag_confidence(self, activity_text: str, tag: str) -> float:
        """Assess confidence of a tag assignment using multiple factors."""
        confidence_factors = []
        
        # Factor 1: Direct synonym match
        synonym_matches = self.map_synonyms_to_taxonomy(activity_text)
        synonym_conf = 0.0
        for matched_tag, conf in synonym_matches:
            if matched_tag.lower() == tag.lower():
                synonym_conf = conf
                break
        confidence_factors.append(synonym_conf)
        
        # Factor 2: Keyword overlap with taxonomy
        taxonomy_info = self.taxonomy.get("taxonomy", {}).get(tag.lower(), {})
        keywords = taxonomy_info.get("keywords", [])
        if keywords:
            activity_lower = activity_text.lower()
            matches = sum(1 for keyword in keywords if keyword.lower() in activity_lower)
            keyword_conf = min(1.0, matches / len(keywords) * 2)
            confidence_factors.append(keyword_conf)
        
        # Factor 3: Activity length and detail level (longer = more confidence in complex tags)
        detail_factor = min(1.0, len(activity_text) / 100.0)  # Normalize by 100 characters
        confidence_factors.append(detail_factor * 0.3)  # Lower weight for this factor
        
        # Combine factors using weighted average
        if confidence_factors:
            weights = [0.6, 0.3, 0.1] if len(confidence_factors) >= 3 else [0.7, 0.3]
            final_confidence = sum(factor * weight for factor, weight in zip(confidence_factors, weights))
            return min(1.0, final_confidence)
        
        return 0.3  # Default low confidence
    
    def get_low_confidence_threshold(self) -> float:
        """Get threshold for flagging activities for review."""
        return 0.5  # Activities with confidence < 0.5 should be reviewed
    
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
    
    def generate_personalized_taxonomy(self, all_activities: List[RawActivity], max_categories: int = 20) -> Dict[str, Any]:
        """Use AI to analyze user data and generate personalized taxonomy."""
        if not self.client:
            print("Warning: No OpenAI API key, cannot generate personalized taxonomy")
            return self.taxonomy
        
        # Sample activities for analysis (limit for API)
        sample_activities = all_activities[:100] if len(all_activities) > 100 else all_activities
        activity_texts = [activity.details for activity in sample_activities]
        
        system_prompt = TaxonomyPrompts.get_personalized_taxonomy_system_prompt(max_categories)
        user_prompt = TaxonomyPrompts.get_personalized_taxonomy_user_prompt(activity_texts)

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.3,
                max_tokens=2000
            )
            
            result_text = response.choices[0].message.content.strip()
            personalized_taxonomy = json.loads(result_text)
            
            print(f"Generated personalized taxonomy with {len(personalized_taxonomy.get('taxonomy', {}))} categories")
            return personalized_taxonomy
            
        except Exception as e:
            print(f"Error generating personalized taxonomy: {e}")
            return self.taxonomy
    
    def generate_personalized_synonyms(self, all_activities: List[RawActivity]) -> Dict[str, Any]:
        """Use AI to analyze user data and generate personalized synonyms mapping."""
        if not self.client:
            print("Warning: No OpenAI API key, cannot generate personalized synonyms")
            return self.synonyms
        
        # Extract unique terms and patterns from user data
        sample_activities = all_activities[:150] if len(all_activities) > 150 else all_activities
        activity_texts = [activity.details for activity in sample_activities]
        
        system_prompt = TaxonomyPrompts.get_personalized_synonyms_system_prompt()
        user_prompt = TaxonomyPrompts.get_personalized_synonyms_user_prompt(activity_texts)

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.2,
                max_tokens=1500
            )
            
            result_text = response.choices[0].message.content.strip()
            personalized_synonyms = json.loads(result_text)
            
            print(f"Generated personalized synonyms with {len(personalized_synonyms.get('synonyms', {}))} categories")
            return personalized_synonyms
            
        except Exception as e:
            print(f"Error generating personalized synonyms: {e}")
            return self.synonyms
    
    def update_taxonomy_from_data(self, all_activities: List[RawActivity]) -> None:
        """Update taxonomy and synonyms based on user's actual data."""
        print("Analyzing user data to generate personalized taxonomy and synonyms...")
        
        # Generate personalized resources
        new_taxonomy = self.generate_personalized_taxonomy(all_activities)
        new_synonyms = self.generate_personalized_synonyms(all_activities)
        
        # Update internal state
        self.taxonomy = new_taxonomy
        self.synonyms = new_synonyms
        self.taxonomy_tags = list(new_taxonomy.get("taxonomy", {}).keys())
        self.existing_tags = self.taxonomy_tags
        
        # Save to files with timestamp
        resources_dir = os.path.join(os.path.dirname(__file__), '..', 'resources')
        timestamp = json.dumps({"generated_at": "auto-generated from user data", "last_updated": "2025-09-07"})
        
        # Save personalized taxonomy
        personalized_taxonomy = {**new_taxonomy, **json.loads(timestamp)}
        taxonomy_path = os.path.join(resources_dir, 'tag_taxonomy_personalized.json')
        with open(taxonomy_path, 'w', encoding='utf-8') as f:
            json.dump(personalized_taxonomy, f, ensure_ascii=False, indent=2)
        
        # Save personalized synonyms  
        personalized_synonyms = {**new_synonyms, **json.loads(timestamp)}
        synonyms_path = os.path.join(resources_dir, 'synonyms_personalized.json')
        with open(synonyms_path, 'w', encoding='utf-8') as f:
            json.dump(personalized_synonyms, f, ensure_ascii=False, indent=2)
        
        print(f"Generated personalized taxonomy with {len(self.taxonomy_tags)} categories")
        print(f"Updated synonym mappings for improved personal context understanding")
    
    # Hierarchical Tagging Methods (Three-Layer System)
    
    def generate_hierarchical_tags_for_activity(self, raw_activity: RawActivity) -> Dict[str, Any]:
        """Generate hierarchical tags with three layers: nature, subject, project."""
        hierarchical_result = {
            "nature": None,
            "subject": None,
            "project": None,
            "confidence_scores": {
                "nature": 0.0,
                "subject": 0.0,
                "project": 0.0
            },
            "fallback_used": False
        }
        
        activity_text = raw_activity.details.lower()
        
        # Layer 1: Nature tags (high-level type) - use existing system
        nature_tags = self.generate_tags_with_confidence_for_activity(raw_activity)
        if nature_tags:
            best_nature = max(nature_tags, key=lambda x: x[1])
            hierarchical_result["nature"] = best_nature[0]
            hierarchical_result["confidence_scores"]["nature"] = best_nature[1]
        
        # Layer 2: Subject detection
        if hierarchical_result["nature"]:
            subject, subject_confidence = self._detect_subject_tag(activity_text, hierarchical_result["nature"])
            hierarchical_result["subject"] = subject
            hierarchical_result["confidence_scores"]["subject"] = subject_confidence
            
            # Layer 3: Project detection (optional)
            if subject:
                project, project_confidence = self._detect_project_tag(activity_text, hierarchical_result["nature"], subject)
                hierarchical_result["project"] = project
                hierarchical_result["confidence_scores"]["project"] = project_confidence
        
        return hierarchical_result
    
    def _detect_subject_tag(self, activity_text: str, nature_tag: str) -> Tuple[Optional[str], float]:
        """Detect subject-level tag based on nature and activity content."""
        hierarchy = self.hierarchical_taxonomy.get("taxonomy", {})
        nature_config = hierarchy.get(nature_tag, {})
        subjects = nature_config.get("subjects", {})
        
        best_subject = None
        best_confidence = 0.0
        
        for subject_name, subject_config in subjects.items():
            confidence = self._calculate_subject_confidence(activity_text, subject_config)
            if confidence > best_confidence and confidence > 0.3:  # Minimum threshold
                best_subject = subject_name
                best_confidence = confidence
        
        return best_subject, best_confidence
    
    def _detect_project_tag(self, activity_text: str, nature_tag: str, subject_tag: str) -> Tuple[Optional[str], float]:
        """Detect project-level tag based on nature, subject and activity content."""
        hierarchy = self.hierarchical_taxonomy.get("taxonomy", {})
        subject_config = hierarchy.get(nature_tag, {}).get("subjects", {}).get(subject_tag, {})
        projects = subject_config.get("projects", [])
        
        best_project = None
        best_confidence = 0.0
        
        for project_name in projects:
            # Simple keyword matching for project detection
            if project_name.lower().replace("-", " ").replace("_", " ") in activity_text:
                confidence = min(0.9, len(project_name) / 15.0)  # Length-based confidence
                if confidence > best_confidence:
                    best_project = project_name
                    best_confidence = confidence
        
        return best_project, best_confidence
    
    def _calculate_subject_confidence(self, activity_text: str, subject_config: Dict[str, Any]) -> float:
        """Calculate confidence for subject match based on keywords and personal shortcuts."""
        keywords = subject_config.get("keywords", [])
        confidence_factors = []
        
        # Keyword matching
        for keyword in keywords:
            if keyword.lower() in activity_text:
                # Weight longer keywords more heavily
                confidence_factors.append(min(0.8, len(keyword) / 20.0))
        
        # Personal shortcuts from synonyms
        personal_shortcuts = self.synonyms.get("personal_shortcuts", {})
        for shortcut, categories in personal_shortcuts.items():
            if shortcut.lower() in activity_text:
                subject_name = subject_config.get("description", "").split()[0].lower()
                if any(subject_name in cat.lower() for cat in categories):
                    confidence_factors.append(0.9)  # High confidence for personal shortcuts
        
        # Return weighted average of confidence factors
        return sum(confidence_factors) / len(confidence_factors) if confidence_factors else 0.0
    
    def generate_hierarchical_tags_batch(self, raw_activities: List[RawActivity]) -> List[Dict[str, Any]]:
        """Generate hierarchical tags for a batch of activities."""
        results = []
        for activity in raw_activities:
            hierarchical_tags = self.generate_hierarchical_tags_for_activity(activity)
            results.append({
                "activity_id": getattr(activity, 'id', None),
                "activity_text": activity.details,
                "hierarchical_tags": hierarchical_tags,
                "source": activity.source,
                "date": activity.date
            })
        return results
    
    def get_hierarchical_summary(self, hierarchical_results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Generate summary statistics for hierarchical tagging results."""
        summary = {
            "total_activities": len(hierarchical_results),
            "nature_distribution": {},
            "subject_distribution": {},
            "project_distribution": {},
            "coverage_stats": {
                "nature_coverage": 0,
                "subject_coverage": 0, 
                "project_coverage": 0
            },
            "confidence_stats": {
                "avg_nature_confidence": 0.0,
                "avg_subject_confidence": 0.0,
                "avg_project_confidence": 0.0
            }
        }
        
        nature_confidences = []
        subject_confidences = []
        project_confidences = []
        
        for result in hierarchical_results:
            tags = result["hierarchical_tags"]
            
            # Count distributions
            if tags["nature"]:
                summary["coverage_stats"]["nature_coverage"] += 1
                nature_tag = tags["nature"]
                summary["nature_distribution"][nature_tag] = summary["nature_distribution"].get(nature_tag, 0) + 1
                nature_confidences.append(tags["confidence_scores"]["nature"])
                
            if tags["subject"]:
                summary["coverage_stats"]["subject_coverage"] += 1
                subject_tag = tags["subject"]
                summary["subject_distribution"][subject_tag] = summary["subject_distribution"].get(subject_tag, 0) + 1
                subject_confidences.append(tags["confidence_scores"]["subject"])
                
            if tags["project"]:
                summary["coverage_stats"]["project_coverage"] += 1
                project_tag = tags["project"]
                summary["project_distribution"][project_tag] = summary["project_distribution"].get(project_tag, 0) + 1
                project_confidences.append(tags["confidence_scores"]["project"])
        
        # Calculate averages
        if nature_confidences:
            summary["confidence_stats"]["avg_nature_confidence"] = sum(nature_confidences) / len(nature_confidences)
        if subject_confidences:
            summary["confidence_stats"]["avg_subject_confidence"] = sum(subject_confidences) / len(subject_confidences)
        if project_confidences:
            summary["confidence_stats"]["avg_project_confidence"] = sum(project_confidences) / len(project_confidences)
        
        # Convert coverage to percentages
        total = summary["total_activities"]
        if total > 0:
            summary["coverage_stats"]["nature_coverage"] = summary["coverage_stats"]["nature_coverage"] / total * 100
            summary["coverage_stats"]["subject_coverage"] = summary["coverage_stats"]["subject_coverage"] / total * 100
            summary["coverage_stats"]["project_coverage"] = summary["coverage_stats"]["project_coverage"] / total * 100
        
        return summary