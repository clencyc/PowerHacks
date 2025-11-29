import os
import logging
from typing import List, Dict, Any, Optional
import json
from datetime import datetime

# For now, we'll use a simple knowledge base. In production, use vector DB
logger = logging.getLogger(__name__)

class KenyanGBVRAGService:
    def __init__(self):
        self.gemini_api_key = os.environ.get("GEMINI_API_KEY")
        self.openai_api_key = os.environ.get("OPENAI_API_KEY")
        
        # Kenyan GBV resources and legal framework
        self.knowledge_base = {
            "legal_rights": {
                "constitution": "Kenya's Constitution (Article 27) guarantees equality and freedom from discrimination based on gender.",
                "sexual_offences_act": "The Sexual Offences Act (2006) criminalizes sexual harassment, assault, and other forms of GBV.",
                "employment_act": "Employment Act (2007) Section 6 prohibits sexual harassment in the workplace.",
                "national_policy": "Kenya has a National Policy on Prevention and Response to Gender-Based Violence (2014)."
            },
            "hotlines": {
                "gender_violence_recovery_centre": {
                    "name": "Gender Violence Recovery Centre",
                    "phone": "0709 558 000 / 0730 558 000",
                    "services": "24/7 counseling, medical care, legal support"
                },
                "childline_kenya": {
                    "name": "Childline Kenya", 
                    "phone": "116 (toll-free)",
                    "services": "Child protection and GBV support"
                },
                "police_gender_desk": {
                    "name": "Police Gender Desk",
                    "phone": "999 or local police station",
                    "services": "Report GBV incidents, get police intervention"
                },
                "fida_kenya": {
                    "name": "FIDA Kenya",
                    "phone": "0800 720 553",
                    "services": "Free legal aid for women"
                }
            },
            "workplace_rights": {
                "harassment_definition": "Sexual harassment includes unwelcome sexual advances, requests for sexual favors, verbal or physical conduct of a sexual nature.",
                "reporting_process": "You have the right to report harassment to HR, management, or external authorities without fear of retaliation.",
                "employer_obligations": "Employers must provide a safe work environment and have clear anti-harassment policies.",
                "evidence_collection": "Document incidents with dates, witnesses, and save any messages or emails as evidence."
            },
            "support_resources": {
                "counseling": "Free counseling available through LVCT Health (0701 867 868) and other NGOs.",
                "medical": "Visit any public health facility for post-GBV care. PEP (Post-Exposure Prophylaxis) available within 72 hours.",
                "legal": "Kenya Women Lawyers Association (KEWOLA) provides free legal services.",
                "shelters": "Safe houses available through Coalition on Violence Against Women (COVAW)."
            },
            "prevention_tips": {
                "bystander": "If you witness GBV: don't ignore it, document safely, support the victim, report if appropriate.",
                "workplace": "Know your company's harassment policy, report concerns to HR or management, support colleagues.",
                "personal_safety": "Trust your instincts, have a safety plan, know emergency contacts, document incidents."
            }
        }
        
        self.conversation_starters = {
            "what_is_gbv": "Gender-Based Violence (GBV) includes physical, sexual, psychological violence against someone based on their gender.",
            "workplace_harassment": "Workplace sexual harassment is illegal under Kenya's Employment Act. You have rights and recourse.",
            "how_to_report": "You can report GBV to police, your employer's HR department, or specialized organizations like FIDA Kenya.",
            "getting_help": "Immediate help is available 24/7 through the Gender Violence Recovery Centre (0709 558 000)."
        }

    def _find_relevant_content(self, query: str) -> List[Dict[str, Any]]:
        """Simple keyword-based content retrieval. In production, use embeddings."""
        query_lower = query.lower()
        relevant_content = []
        
        # Search through knowledge base
        for category, content in self.knowledge_base.items():
            if isinstance(content, dict):
                for key, value in content.items():
                    if any(word in query_lower for word in [category, key]) or \
                       any(word in str(value).lower() for word in query_lower.split()):
                        relevant_content.append({
                            'category': category,
                            'key': key,
                            'content': value,
                            'relevance': self._calculate_relevance(query_lower, str(value))
                        })
        
        # Sort by relevance
        relevant_content.sort(key=lambda x: x['relevance'], reverse=True)
        return relevant_content[:5]  # Top 5 results
    
    def _calculate_relevance(self, query: str, content: str) -> float:
        """Simple relevance scoring"""
        query_words = set(query.lower().split())
        content_words = set(content.lower().split())
        if not query_words:
            return 0.0
        return len(query_words.intersection(content_words)) / len(query_words)
    
    def _format_response(self, query: str, relevant_content: List[Dict], incident_type: str = None) -> str:
        """Format a helpful response based on retrieved content"""
        
        if not relevant_content:
            return self._get_default_response(query)
        
        response_parts = []
        
        # Add empathetic opening
        if incident_type in ['high', 'medium']:
            response_parts.append("🛡️ **I'm here to help. You're not alone.**\n")
        else:
            response_parts.append("🌟 **SafeSpace AI - Here to support you**\n")
        
        # Add relevant information
        for item in relevant_content:
            category = item['category'].replace('_', ' ').title()
            
            if isinstance(item['content'], dict):
                # Handle structured content (like hotlines)
                if 'phone' in item['content']:
                    response_parts.append(f"**{item['content'].get('name', item['key'])}**")
                    response_parts.append(f"📞 {item['content']['phone']}")
                    if 'services' in item['content']:
                        response_parts.append(f"Services: {item['content']['services']}")
                    response_parts.append("")
                else:
                    response_parts.append(f"**{category} - {item['key']}:**")
                    response_parts.append(f"{item['content']}\n")
            else:
                response_parts.append(f"**{category}:**")
                response_parts.append(f"{item['content']}\n")
        
        # Add call to action based on severity
        if incident_type == 'high':
            response_parts.append("🚨 **Immediate Action:** If you're in immediate danger, call 999 or go to the nearest police station.")
            response_parts.append("📞 **24/7 Support:** Gender Violence Recovery Centre: 0709 558 000")
        
        response_parts.append("\n💬 Type `/gbv-help [your question]` for more specific guidance.")
        response_parts.append("📋 Type `/gbv-report` to file an anonymous report.")
        
        return "\n".join(response_parts)
    
    def _get_default_response(self, query: str) -> str:
        """Default response when no specific content is found"""
        return f"""🌟 **SafeSpace AI Support**

I understand you're asking about: "{query}"

**Immediate Resources:**
📞 **Gender Violence Recovery Centre:** 0709 558 000 (24/7)
📞 **FIDA Kenya Legal Aid:** 0800 720 553
📞 **Emergency:** 999

**Your Rights:**
- You have the right to a safe workplace free from harassment
- You can report incidents without fear of retaliation  
- Legal support is available through multiple organizations

**Next Steps:**
💬 Ask me specific questions like:
  • "What is workplace harassment?"
  • "How do I report an incident?"
  • "What legal protections do I have?"
  
📋 Use `/gbv-report` to file an anonymous report
🔒 Use `/gbv-privacy` to understand how we protect your data

You're not alone. Help is available."""

    def query(self, question: str, context: Dict[str, Any] = None) -> str:
        """
        Process a question and return relevant GBV information
        
        Args:
            question: User's question or concern
            context: Additional context (incident severity, user type, etc.)
        """
        try:
            if not question or len(question.strip()) < 2:
                return self._get_default_response("general help")
            
            # Find relevant content
            relevant_content = self._find_relevant_content(question)
            
            # Determine incident type from context
            incident_type = None
            if context and 'severity' in context:
                incident_type = context['severity']
            
            # Format and return response
            return self._format_response(question, relevant_content, incident_type)
            
        except Exception as e:
            logger.error(f"Error in RAG query: {e}")
            return "I'm sorry, I'm having trouble processing your request right now. Please contact the Gender Violence Recovery Centre at 0709 558 000 for immediate assistance."
    
    def get_incident_response(self, severity: str, categories: List[str]) -> str:
        """Get appropriate response based on detected incident severity and categories"""
        
        context = {'severity': severity, 'categories': categories}
        
        if severity == 'high':
            query = "immediate help for serious incident"
        elif 'sexual' in categories:
            query = "sexual harassment workplace rights"
        elif 'harassment' in categories:
            query = "workplace harassment reporting"
        elif 'threats' in categories:
            query = "threats violence safety"
        else:
            query = "general GBV support and resources"
        
        return self.query(query, context)

# Initialize RAG service
rag_service = KenyanGBVRAGService()
