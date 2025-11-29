import os
import logging
from typing import Dict, Any
from transformers import pipeline, AutoTokenizer, AutoModelForSequenceClassification
import torch
import hashlib
from datetime import datetime, timedelta

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class GBVDetector:
    def __init__(self):
        self.perspective_api_key = os.environ.get("PERSPECTIVE_API_KEY")
        self.device = 0 if torch.cuda.is_available() else -1
        
        # Initialize lightweight toxicity classifier (lazy loading)
        self.toxicity_classifier = None
        self.model_loaded = False
        logger.info("GBV Detector initialized (model will load on first use)")
        
        # GBV-specific keywords and patterns
        self.gbv_keywords = {
            'harassment': ['harass', 'stalk', 'unwanted', 'inappropriate touch', 'groping'],
            'discrimination': ['because you\'re a woman', 'girls can\'t', 'men are better', 'gender role'],
            'threats': ['hurt you', 'teach you a lesson', 'know your place'],
            'sexual': ['sexual favor', 'sleep with', 'dress code', 'inappropriate comments'],
            'swahili_gbv': ['msichana', 'mwanamke', 'haramu', 'aibu']  # Common Swahili terms
        }
        
        # Cache for rate limiting repeated messages
        self.message_cache = {}
        
    def _clean_cache(self):
        """Remove old entries from message cache"""
        cutoff = datetime.now() - timedelta(minutes=30)
        self.message_cache = {
            k: v for k, v in self.message_cache.items() 
            if v['timestamp'] > cutoff
        }
    
    def _get_message_hash(self, text: str, user_id: str = None) -> str:
        """Create hash of message for deduplication"""
        content = f"{text}:{user_id}" if user_id else text
        return hashlib.sha256(content.encode()).hexdigest()[:16]
    
    def _check_gbv_keywords(self, text: str) -> Dict[str, float]:
        """Check for GBV-specific patterns"""
        text_lower = text.lower()
        scores = {}
        
        for category, keywords in self.gbv_keywords.items():
            matches = sum(1 for keyword in keywords if keyword in text_lower)
            scores[category] = min(matches * 0.3, 1.0)  # Cap at 1.0
            
        return scores
    
    def _load_model(self):
        """Lazy load the toxicity classifier when needed"""
        if not self.model_loaded:
            try:
                from transformers import pipeline
                self.toxicity_classifier = pipeline(
                    "text-classification",
                    model="unitary/toxic-bert",
                    device=self.device,
                    truncation=True,
                    max_length=512
                )
                self.model_loaded = True
                logger.info("Loaded toxic-bert model successfully")
            except Exception as e:
                logger.warning(f"Failed to load toxic-bert: {e}. Using keyword-only detection.")
                self.toxicity_classifier = None
                self.model_loaded = True

    def analyze_text(self, text: str, user_id: str = None, channel_type: str = "public") -> Dict[str, Any]:
        """
        Comprehensive GBV and toxicity analysis
        
        Args:
            text: Message text to analyze
            user_id: Slack user ID (for rate limiting)
            channel_type: Type of channel (public, private, dm)
            
        Returns:
            Dict with analysis results
        """
        # Clean old cache entries
        self._clean_cache()
        
        # Check cache for recent duplicate
        msg_hash = self._get_message_hash(text, user_id)
        if msg_hash in self.message_cache:
            cached = self.message_cache[msg_hash]
            cached['from_cache'] = True
            return cached
        
        # Initialize result
        result = {
            'flagged': False,
            'confidence': 0.0,
            'scores': {
                'toxicity': 0.0,
                'harassment': 0.0,
                'discrimination': 0.0,
                'threats': 0.0,
                'sexual': 0.0,
                'overall_gbv': 0.0
            },
            'categories': [],
            'severity': 'low',
            'timestamp': datetime.now(),
            'from_cache': False,
            'channel_type': channel_type
        }
        
        try:
            # Skip very short messages
            if len(text.strip()) < 3:
                self.message_cache[msg_hash] = result
                return result
            
            # HuggingFace toxicity detection (lazy load)
            self._load_model()
            if self.toxicity_classifier:
                try:
                    hf_results = self.toxicity_classifier(text)
                    if isinstance(hf_results, list):
                        hf_results = hf_results[0]
                    
                    # toxic-bert returns TOXIC/NON_TOXIC labels
                    if hf_results['label'] == 'TOXIC':
                        result['scores']['toxicity'] = hf_results['score']
                    else:
                        result['scores']['toxicity'] = 1 - hf_results['score']
                        
                except Exception as e:
                    logger.warning(f"HF classifier error: {e}")
                    result['scores']['toxicity'] = 0.0
            
            # GBV-specific keyword analysis
            gbv_scores = self._check_gbv_keywords(text)
            result['scores'].update(gbv_scores)
            
            # Calculate overall GBV score
            gbv_components = ['harassment', 'discrimination', 'threats', 'sexual']
            result['scores']['overall_gbv'] = max(
                result['scores'][component] for component in gbv_components
            )
            
            # Determine if flagged (more sensitive in DMs)
            toxicity_threshold = 0.7 if channel_type == "public" else 0.5
            gbv_threshold = 0.3 if channel_type == "public" else 0.2
            
            result['flagged'] = (
                result['scores']['toxicity'] > toxicity_threshold or
                result['scores']['overall_gbv'] > gbv_threshold
            )
            
            # Set confidence and severity
            max_score = max(result['scores']['toxicity'], result['scores']['overall_gbv'])
            result['confidence'] = max_score
            
            if max_score > 0.8:
                result['severity'] = 'high'
            elif max_score > 0.5:
                result['severity'] = 'medium'
            else:
                result['severity'] = 'low'
            
            # Identify primary categories
            for category, score in result['scores'].items():
                if score > 0.3 and category != 'overall_gbv':
                    result['categories'].append(category)
            
        except Exception as e:
            logger.error(f"Error analyzing text: {e}")
            result['error'] = str(e)
        
        # Cache result
        self.message_cache[msg_hash] = result
        return result

# Initialize detector instance
detector = GBVDetector()
