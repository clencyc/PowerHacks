import os
import logging
from typing import Dict, Any
import hashlib
from datetime import datetime, timedelta

# Setup logging  
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class LightweightGBVDetector:
    """Lightweight GBV detector using keyword-based analysis"""
    
    def __init__(self):
        # Enhanced GBV-specific keywords and patterns
        self.gbv_keywords = {
            'harassment': [
                'harass', 'stalk', 'unwanted', 'inappropriate touch', 'groping',
                'following me', 'won\'t leave me alone', 'uncomfortable', 'creepy',
                'bothering', 'pestering', 'intimidating'
            ],
            'discrimination': [
                'because you\'re a woman', 'girls can\'t', 'men are better', 
                'gender role', 'stay in kitchen', 'not for women', 'too emotional',
                'weak woman', 'female brain', 'women driver'
            ],
            'threats': [
                'hurt you', 'teach you a lesson', 'know your place', 'regret this',
                'make you pay', 'get what you deserve', 'shut up', 'or else',
                'watch yourself', 'be sorry'
            ],
            'sexual': [
                'sexual favor', 'sleep with', 'dress code', 'inappropriate comments',
                'sexy', 'hot body', 'nice legs', 'what are you wearing',
                'send photo', 'private message', 'alone time'
            ],
            'swahili_gbv': [
                'msichana', 'mwanamke', 'haramu', 'aibu', 'kijana',
                'mrembo', 'dada', 'mama', 'binti'
            ],
            'violence_indicators': [
                'hit', 'slap', 'punch', 'kick', 'push', 'shove', 'grab',
                'force', 'violence', 'hurt', 'pain', 'bruise', 'scared'
            ]
        }
        
        # Toxic patterns
        self.toxic_patterns = [
            'stupid', 'idiot', 'bitch', 'whore', 'slut', 'fuck you',
            'shut up', 'kill yourself', 'die', 'hate you', 'worthless',
            'ugly', 'fat', 'disgusting'
        ]
        
        # Cache for rate limiting
        self.message_cache = {}
        
    def _clean_cache(self):
        """Remove old entries from message cache"""
        cutoff = datetime.now() - timedelta(minutes=30)
        self.message_cache = {
            k: v for k, v in self.message_cache.items() 
            if v['timestamp'] > cutoff
        }
        
    def _get_message_hash(self, text: str, user_id: str = None) -> str:
        """Generate hash for message deduplication"""
        content = f"{text}:{user_id}" if user_id else text
        return hashlib.sha256(content.encode()).hexdigest()[:16]
    
    def _check_gbv_keywords(self, text: str) -> Dict[str, float]:
        """Check for GBV-specific patterns"""
        text_lower = text.lower()
        scores = {}
        
        for category, keywords in self.gbv_keywords.items():
            matches = sum(1 for keyword in keywords if keyword in text_lower)
            # Score based on number of matches and keyword strength
            scores[category] = min(matches * 0.4, 1.0)
            
        return scores
    
    def _check_toxicity(self, text: str) -> float:
        """Simple toxicity check using keyword matching"""
        text_lower = text.lower()
        toxic_count = sum(1 for pattern in self.toxic_patterns if pattern in text_lower)
        return min(toxic_count * 0.5, 1.0)
    
    def analyze_text(self, text: str, user_id: str = None, channel_type: str = "public") -> Dict[str, Any]:
        """
        Lightweight GBV and toxicity analysis
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
                'violence_indicators': 0.0,
                'overall_gbv': 0.0
            },
            'categories': [],
            'severity': 'low',
            'timestamp': datetime.now(),
            'from_cache': False,
            'channel_type': channel_type,
            'detection_method': 'lightweight'
        }
        
        try:
            # Skip very short messages
            if len(text.strip()) < 3:
                self.message_cache[msg_hash] = result
                return result
            
            # Toxicity detection
            result['scores']['toxicity'] = self._check_toxicity(text)
            
            # GBV-specific keyword analysis
            gbv_scores = self._check_gbv_keywords(text)
            result['scores'].update(gbv_scores)
            
            # Calculate overall GBV score
            gbv_components = ['harassment', 'discrimination', 'threats', 'sexual', 'violence_indicators']
            gbv_scores_list = [result['scores'][component] for component in gbv_components]
            result['scores']['overall_gbv'] = max(gbv_scores_list) if gbv_scores_list else 0.0
            
            # Determine overall confidence and flagged status
            max_score = max(result['scores']['toxicity'], result['scores']['overall_gbv'])
            result['confidence'] = max_score
            
            # Flag based on thresholds
            if max_score >= 0.8:
                result['flagged'] = True
                result['severity'] = 'high'
            elif max_score >= 0.5:
                result['flagged'] = True
                result['severity'] = 'medium'
            elif max_score >= 0.3:
                result['flagged'] = True
                result['severity'] = 'low'
            
            # Identify categories
            for category, score in result['scores'].items():
                if score >= 0.3 and category not in ['overall_gbv']:
                    result['categories'].append(category)
            
            # Cache result
            self.message_cache[msg_hash] = result
            
        except Exception as e:
            logger.error(f"Error in lightweight analysis: {e}")
            result['error'] = str(e)
        
        return result

# Create global detector instance
detector = LightweightGBVDetector()
logger.info("Lightweight GBV detector initialized")
