from typing import Dict, Optional

class QuickResponses:
    def __init__(self):
        self.quick_answers = {
            "what is giki": """GIKI stands for Ghulam Ishaq Khan Institute of Engineering Sciences and Technology. 
It is one of Pakistan's premier engineering universities, established in 1993 and located in Topi, Khyber Pakhtunkhwa.
The institute is named after Mr. Ghulam Ishaq Khan, former President of Pakistan.""",
            
            "giki full form": """GIKI stands for Ghulam Ishaq Khan Institute of Engineering Sciences and Technology.""",
            
            "where is giki": """GIKI is located in Topi, Khyber Pakhtunkhwa, Pakistan. The campus spans over 400 acres in the scenic region near Tarbela Dam.""",
            
            "when was giki established": """GIKI was established in 1993 as a project of the Ghulam Ishaq Khan Foundation.""",
            
            "giki ranking": """GIKI consistently ranks among the top engineering universities in Pakistan and is known for its high academic standards and research quality.""",
            
            "giki admission": """GIKI admissions are based on:
1. GIKI Entry Test (GET)
2. FSc/A-Level or equivalent results
3. Interview (for shortlisted candidates)

The admission process typically starts in June-July each year.""",
            
            "giki programs": """GIKI offers undergraduate programs in:
1. Computer Engineering
2. Electrical Engineering
3. Mechanical Engineering
4. Chemical Engineering
5. Materials Engineering
6. Industrial Engineering
7. Computer Science
8. Software Engineering
9. Engineering Sciences""",
            
            "giki facilities": """GIKI's main facilities include:
1. Modern laboratories and research centers
2. Central library
3. Student hostels (separate for male and female)
4. Sports complex
5. Medical center
6. Mosque
7. Shopping center
8. Banking facilities
9. Transport services""",
            
            "about giki": """GIKI (Ghulam Ishaq Khan Institute) is one of Pakistan's leading engineering universities. Key points:
• Established: 1993
• Location: Topi, KPK
• Campus: 400 acres
• Focus: Engineering & Technology
• Known for: High-quality education, research excellence, and industry linkages
• Facilities: Modern labs, hostels, sports complex
• Recognition: HEC recognized, PEC accredited""",
        }
        
        # Add variations of questions
        self._add_question_variations()
    
    def _add_question_variations(self):
        """Add common variations of questions to the quick answers"""
        variations = {
            "what is giki": ["what's giki", "what does giki stand for", "giki meaning", "giki full name", 
                           "tell me about giki", "explain giki", "describe giki"],
            "where is giki": ["giki location", "giki address", "where is giki located", "giki campus location"],
            "when was giki established": ["giki establishment", "when did giki start", "giki history", 
                                        "how old is giki", "establishment of giki"],
            "giki admission": ["how to get admission in giki", "giki entry test", "giki admission process", 
                             "admission requirements giki", "how to apply to giki"],
            "giki programs": ["what programs does giki offer", "giki courses", "departments in giki", 
                            "what can i study in giki", "giki degrees"],
            "about giki": ["introduction to giki", "giki overview", "giki introduction", "who is giki"]
        }
        
        # Add variations to quick answers
        for base_q, vars in variations.items():
            base_answer = self.quick_answers[base_q]
            for var in vars:
                self.quick_answers[var] = base_answer
    
    def get_quick_response(self, query: str) -> Optional[str]:
        """Get a quick response for common questions"""
        query = query.lower().strip()
        
        # Direct match
        if query in self.quick_answers:
            return self.quick_answers[query]
        
        # Partial match
        for q in self.quick_answers:
            if query in q or q in query:
                return self.quick_answers[q]
        
        return None 