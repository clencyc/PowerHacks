from fastapi import APIRouter, HTTPException, BackgroundTasks
from typing import Dict, Any
import logging
import sys
import os

# Add slack app to Python path to import detection module  
sys.path.append(os.path.join(os.path.dirname(__file__), '../../../slack'))

from models import DetectionRequest, DetectionResponse

logger = logging.getLogger(__name__)
router = APIRouter()

try:
    from detection import detector
except ImportError:
    logger.warning("Could not import detection module. Detection endpoint will be mocked.")
    detector = None

@router.post("/detect", response_model=DetectionResponse)
def detect_gbv_content(
    request: DetectionRequest,
    background_tasks: BackgroundTasks
):
    """
    Analyze text for GBV content and toxicity
    
    This endpoint can be used by:
    - Slack bot for real-time detection
    - Web applications for content moderation  
    - Other services that need GBV detection
    """
    try:
        if not detector:
            # Mock response if detector not available
            return DetectionResponse(
                flagged=False,
                confidence=0.0,
                scores={"toxicity": 0.0, "harassment": 0.0},
                categories=[],
                severity="low", 
                recommendations=["Detection service not available"]
            )
        
        # Run detection
        result = detector.analyze_text(
            text=request.text,
            user_id=request.user_id,
            channel_type=request.channel_type
        )
        
        # Generate recommendations based on results
        recommendations = generate_recommendations(result)
        
        # Log high-severity detections for monitoring
        if result.get("severity") in ["high", "critical"]:
            background_tasks.add_task(
                log_high_severity_detection, 
                request.text[:100], 
                result,
                request.user_id
            )
        
        return DetectionResponse(
            flagged=result["flagged"],
            confidence=result["confidence"], 
            scores=result["scores"],
            categories=result["categories"],
            severity=result["severity"],
            recommendations=recommendations
        )
        
    except Exception as e:
        logger.error(f"Error in GBV detection: {e}")
        raise HTTPException(
            status_code=500, 
            detail="Detection service temporarily unavailable"
        )

@router.get("/detect/health")
def detection_health_check():
    """Health check for detection service"""
    try:
        if not detector:
            return {"status": "degraded", "message": "Detection module not loaded"}
        
        # Test with a simple phrase
        test_result = detector.analyze_text("Hello world", "test_user", "public")
        
        return {
            "status": "healthy",
            "detector_loaded": True,
            "test_passed": isinstance(test_result, dict)
        }
    except Exception as e:
        logger.error(f"Detection health check failed: {e}")
        return {"status": "unhealthy", "error": str(e)}

def generate_recommendations(detection_result: Dict[str, Any]) -> list:
    """Generate contextual recommendations based on detection results"""
    recommendations = []
    
    severity = detection_result.get("severity", "low")
    categories = detection_result.get("categories", [])
    flagged = detection_result.get("flagged", False)
    
    if not flagged:
        return ["Message appears appropriate for workplace communication"]
    
    if severity == "high":
        recommendations.extend([
            "🚨 Immediate intervention may be required",
            "📞 Consider contacting Gender Violence Recovery Centre: 0709 558 000",
            "🔄 Escalate to HR or management immediately",
            "📋 Document this incident for formal reporting"
        ])
    elif severity == "medium":
        recommendations.extend([
            "⚠️ Message requires attention and possible intervention", 
            "💬 Consider reaching out privately to check on involved parties",
            "📚 Provide educational resources about workplace conduct",
            "📋 Consider filing a report if pattern continues"
        ])
    else:  # low severity
        recommendations.extend([
            "💡 Gentle reminder about respectful workplace communication",
            "📚 Share resources about inclusive language",
            "👀 Monitor for patterns of concerning behavior"
        ])
    
    # Category-specific recommendations
    if "sexual" in categories:
        recommendations.append("🔍 Sexual harassment policies should be reviewed with involved parties")
    if "harassment" in categories:
        recommendations.append("📖 Anti-harassment training may be beneficial")
    if "threats" in categories:
        recommendations.append("🛡️ Safety assessment and immediate intervention required")
    if "discrimination" in categories:
        recommendations.append("🤝 Diversity and inclusion resources should be provided")
    
    return recommendations

def log_high_severity_detection(text_preview: str, result: Dict[str, Any], user_id: str = None):
    """Background task to log high-severity detections for monitoring"""
    try:
        logger.warning(
            f"High-severity GBV detection: "
            f"severity={result.get('severity')}, "
            f"confidence={result.get('confidence')}, "
            f"categories={result.get('categories')}, "
            f"user={user_id or 'anonymous'}"
        )
        
        # In production, you might want to:
        # - Send alerts to administrators
        # - Update monitoring dashboards  
        # - Trigger automated responses
        # - Store in separate high-priority queue
        
    except Exception as e:
        logger.error(f"Error logging high-severity detection: {e}")
