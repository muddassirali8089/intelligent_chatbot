from typing import Dict, List, Optional
import json
from pathlib import Path

class GIKIKnowledgeBase:
    def __init__(self):
        self.load_dataset()
        self.setup_faq_patterns()
    
    def load_dataset(self):
        """Load the GIKI dataset from JSON file"""
        try:
            with open('giki_dataset.json', 'r') as f:
                self.dataset = json.load(f)
        except Exception as e:
            raise Exception(f"Failed to load dataset: {e}")
    
    def setup_faq_patterns(self):
        """Setup FAQ patterns and their corresponding response functions"""
        self.faq_patterns = {
            "department": self._get_department_info,
            "faculty": self._get_department_info,
            "program": self._get_programs_info,
            "research": self._get_research_info,
            "admission": self._get_admission_info,
            "hostel": self._get_hostel_info,
            "facility": self._get_facilities_info,
            "societ": self._get_societies_info,
            "lab": self._get_labs_info,
            "how many": self._get_count_info
        }
    
    def _get_department_info(self, query: str) -> str:
        """Get information about departments"""
        if "how many" in query.lower():
            return f"GIKI has {len(self.dataset['departments'])} main departments/faculties:\n\n" + \
                   "\n".join(f"- {dept['name']}" for dept in self.dataset['departments'].values())
        
        # Check for specific department
        for code, dept in self.dataset['departments'].items():
            if code.lower() in query.lower() or dept['name'].lower() in query.lower():
                return f"""Department: {dept['name']} ({code})
                \nEstablished: {dept['established']}
                \nFaculty Count: {dept['faculty_count']}
                \nPrograms: {', '.join(dept['programs'])}
                \nResearch Areas: {', '.join(dept['research_areas'])}
                \nLabs: {', '.join(dept['labs'])}"""
        
        return "Please specify which department you'd like to know about. Available departments are: " + \
               ", ".join(f"{code} ({dept['name']})" for code, dept in self.dataset['departments'].items())
    
    def _get_programs_info(self, query: str) -> str:
        """Get information about academic programs"""
        all_programs = []
        for dept in self.dataset['departments'].values():
            all_programs.extend(dept['programs'])
        
        return f"GIKI offers the following programs:\n\n" + \
               "\n".join(f"- {program}" for program in sorted(all_programs))
    
    def _get_research_info(self, query: str) -> str:
        """Get information about research centers and areas"""
        centers = self.dataset['research_centers']
        response = "GIKI Research Centers:\n\n"
        
        for center in centers:
            response += f"📚 {center['name']}\nFocus Areas:\n"
            response += "\n".join(f"- {area}" for area in center['focus_areas'])
            response += "\n\n"
        
        return response
    
    def _get_admission_info(self, query: str) -> str:
        """Get admission-related information"""
        adm = self.dataset['admissions']
        return f"""Admission Requirements at GIKI:

1. Academic: {adm['requirements']['academic']}
2. Entry Test: {adm['requirements']['test']}
3. Interview: {adm['requirements']['interview']}

Entry Test Details:
- Subjects: {', '.join(adm['entry_test']['subjects'])}
- Total Marks: {adm['entry_test']['total_marks']}
- Passing Criteria: {adm['entry_test']['passing_criteria']}

Annual Intake:
- Undergraduate: {adm['annual_intake']['undergraduate']} students
- Graduate: {adm['annual_intake']['graduate']} students"""
    
    def _get_hostel_info(self, query: str) -> str:
        """Get information about hostels"""
        hostels = self.dataset['student_life']['facilities']['hostels']
        response = "GIKI Hostel Facilities:\n\n"
        
        for hostel in hostels:
            response += f"🏢 {hostel['name']}\n"
            response += f"Type: {hostel['type']}\n"
            response += f"Capacity: {hostel['capacity']} students\n\n"
        
        return response
    
    def _get_facilities_info(self, query: str) -> str:
        """Get information about campus facilities"""
        facilities = self.dataset['student_life']['facilities']
        response = "GIKI Campus Facilities:\n\n"
        
        response += "🏠 Hostels:\n"
        response += "\n".join(f"- {h['name']} ({h['type']})" for h in facilities['hostels'])
        
        response += "\n\n🍽️ Cafeterias:\n"
        response += "\n".join(f"- {cafe}" for cafe in facilities['cafeterias'])
        
        return response
    
    def _get_societies_info(self, query: str) -> str:
        """Get information about student societies"""
        societies = self.dataset['student_life']['societies']
        response = "GIKI Student Societies:\n\n"
        
        for society in societies:
            response += f"📌 {society['name']}\n"
            response += f"Type: {society['type']}\n"
            response += f"Activities: {', '.join(society['activities'])}\n\n"
        
        return response
    
    def _get_labs_info(self, query: str) -> str:
        """Get information about laboratories"""
        all_labs = []
        for dept in self.dataset['departments'].values():
            response = f"Labs in {dept['name']}:\n"
            response += "\n".join(f"- {lab}" for lab in dept['labs'])
            all_labs.append(response)
        
        return "\n\n".join(all_labs)
    
    def _get_count_info(self, query: str) -> str:
        """Handle 'how many' type questions"""
        query = query.lower()
        
        if "department" in query or "facult" in query:
            return self._get_department_info(query)
        elif "program" in query:
            all_programs = []
            for dept in self.dataset['departments'].values():
                all_programs.extend(dept['programs'])
            return f"GIKI offers {len(all_programs)} different academic programs."
        elif "hostel" in query:
            hostels = self.dataset['student_life']['facilities']['hostels']
            return f"GIKI has {len(hostels)} hostels ({sum(1 for h in hostels if h['type']=='Male')} male, {sum(1 for h in hostels if h['type']=='Female')} female)."
        elif "societ" in query:
            return f"GIKI has {len(self.dataset['student_life']['societies'])} major student societies."
        
        return self._get_default_response()
    
    def _get_default_response(self) -> str:
        """Default response when no specific pattern matches"""
        return """I can help you with information about:
        
1. Departments and Faculties
2. Academic Programs
3. Research Centers
4. Admission Requirements
5. Hostel Facilities
6. Student Societies
7. Laboratories
8. Campus Facilities

Please ask about any of these topics!"""
    
    def get_response(self, query: str) -> str:
        """Generate a response based on the query using the knowledge base"""
        query = query.lower()
        
        # Check for patterns in FAQ
        for pattern, response_func in self.faq_patterns.items():
            if pattern in query:
                return response_func(query)
        
        return self._get_default_response() 