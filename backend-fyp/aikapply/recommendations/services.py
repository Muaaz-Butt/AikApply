"""
Service for generating university recommendations using Gemini API
"""
import os
import google.generativeai as genai
from django.conf import settings
import json


class GeminiRecommendationService:
    """Service to generate recommendations using Gemini API"""
    
    def __init__(self):
        api_key = settings.GEMINI_API_KEY
        if not api_key:
            raise ValueError("GEMINI_API_KEY not found in environment variables")
        genai.configure(api_key=api_key)
        # 'gemini-pro' was retired (404), which silently forced every request onto the fallback list
        self.model = genai.GenerativeModel('gemini-2.5-flash')
    
    def generate_recommendations(self, user_profile):
        """
        Generate university recommendations for a user profile using Gemini
        
        Args:
            user_profile: UserProfile instance
            
        Returns:
            List of recommendation dictionaries
        """
        # Build comprehensive prompt
        prompt = self._build_prompt(user_profile)
        
        try:
            # Generate response from Gemini
            response = self.model.generate_content(prompt)
            recommendations_text = response.text
            
            # Parse the response to extract recommendations
            recommendations = self._parse_recommendations(recommendations_text, user_profile)
            
            return recommendations
            
        except Exception as e:
            print(f"Error generating recommendations: {str(e)}")
            # Return fallback recommendations
            return self._get_fallback_recommendations(user_profile)
    
    def _build_prompt(self, user_profile):
        """Build a comprehensive prompt for Gemini"""
        # The degree is decided by the chosen fields; hobbies only stand in when no field was chosen
        study_field = user_profile.preferred_field_of_study or ', '.join(user_profile.interests)
        hobbies = ', '.join(user_profile.interests) or 'None'
        
        # Build strict location constraints
        if user_profile.can_move_to_other_cities:
            if user_profile.preferred_cities:
                allowed_cities = ', '.join(user_profile.preferred_cities)
                # Include both current city AND preferred cities
                all_cities = [user_profile.current_city] + user_profile.preferred_cities
                all_cities_str = ', '.join(all_cities)
                location_constraint = f"""CRITICAL LOCATION RULE - YOU MUST FOLLOW THIS EXACTLY:
The student is currently living in: {user_profile.current_city}
The student is willing to move to: {allowed_cities}

YOU MUST RECOMMEND UNIVERSITIES FROM BOTH CITIES:
1. Include universities from CURRENT CITY: {user_profile.current_city} (e.g., if Lahore: UET Lahore, Punjab University, COMSATS Lahore, FAST Lahore, LUMS, GCU Lahore, etc.)
2. Include universities from PREFERRED CITIES: {allowed_cities} (e.g., if Islamabad: NUST, QAU, FAST Islamabad, Bahria University, Air University, etc.)

DISTRIBUTION REQUIREMENT:
- Recommend approximately 50% from current city ({user_profile.current_city}) and 50% from preferred cities ({allowed_cities})
- If recommending 8 universities: include 4 from {user_profile.current_city} and 4 from {allowed_cities}
- DO NOT recommend only from preferred cities - you MUST include universities from the current city as well
- DO NOT recommend only from current city - you MUST include universities from preferred cities as well

VALID CITIES FOR RECOMMENDATIONS: {all_cities_str}
DO NOT recommend universities from any other cities outside this list."""
            else:
                location_constraint = f"The student is currently in {user_profile.current_city} and can move to any city in Pakistan. You can recommend universities from {user_profile.current_city} (current city) and any other city in Pakistan."
        else:
            location_constraint = f"CRITICAL: The student CANNOT move to other cities. You MUST ONLY recommend universities in or very near {user_profile.current_city}, {user_profile.current_province}. DO NOT recommend universities from other cities like Islamabad, Karachi, etc. if the student is in Lahore."
        
        # Build fee constraint
        fee_mapping = {
            'low': 'Under 50,000 PKR per semester',
            'medium': '50,000 to 150,000 PKR per semester',
            'high': '150,000 to 300,000 PKR per semester',
            'very_high': 'Above 300,000 PKR per semester'
        }
        fee_constraint = fee_mapping.get(user_profile.fee_affordability, 'Not specified')
        
        # Build university type constraint
        if user_profile.university_type == 'public':
            type_constraint = "CRITICAL: The student wants ONLY PUBLIC universities (universities owned and operated by the government). DO NOT recommend ANY private universities (universities owned by private individuals or organizations). If you recommend a private university, the recommendation is WRONG."
        elif user_profile.university_type == 'private':
            type_constraint = "CRITICAL: The student wants ONLY PRIVATE universities (universities owned by private individuals or private organizations, NOT government-owned). DO NOT recommend ANY public universities (government-owned universities like UET, COMSATS, Punjab University, NUST, QAU, etc.). If you recommend a public university, the recommendation is WRONG. Examples of private universities: LUMS, FAST, IBA, SZABIST, BNU, UMT, Bahria, Riphah, etc."
        else:
            type_constraint = "The student is open to both public (government-owned) and private (privately-owned) universities."
        
        prompt = f"""You are an expert educational consultant specializing in Pakistani universities. 
You MUST provide personalized recommendations that STRICTLY match each student's specific requirements.

STUDENT PROFILE:
- Name: {user_profile.name}
- Academic Level: Intermediate/FSC (All students are intermediate level)
- Current Location: {user_profile.current_city}, {user_profile.current_province}
- Can Move to Other Cities: {'YES' if user_profile.can_move_to_other_cities else 'NO'}
- Preferred Cities (if can move): {', '.join(user_profile.preferred_cities) if user_profile.preferred_cities else 'Any city'}
- Preferred Field of Study (CAREER GOAL - decides the degree): {study_field or 'Not specified'}
- Hobbies & Personal Interests (NOT career goals - do NOT use to pick the field): {hobbies}
- Intermediate Percentage: {user_profile.intermediate_percentage or 'Not provided'}%
- Fee Affordability: {user_profile.get_fee_affordability_display()} ({fee_constraint})
- Scholarship Required: {'YES - prioritize universities with scholarship programs' if user_profile.scholarship_required else 'NO'}
- University Type Preference: {user_profile.get_university_type_display()}
- Language Preference: {user_profile.get_language_preference_display()}
- Required Campus Facilities: {', '.join(user_profile.campus_facilities) if user_profile.campus_facilities else 'Not specified'}
- Additional Requirements: {user_profile.additional_requirements or 'None'}

CRITICAL RULES - YOU MUST FOLLOW THESE STRICTLY:

1. LOCATION CONSTRAINT (MOST IMPORTANT - READ CAREFULLY):
{location_constraint}

ADDITIONAL LOCATION RULES:
   - If student is willing to move and has preferred cities, you MUST recommend universities from BOTH current city AND preferred cities
   - Example: If student is in Lahore but willing to move to Islamabad, you MUST include:
     * Universities from Lahore (current city): UET Lahore, Punjab University, COMSATS Lahore, FAST Lahore, LUMS, etc.
     * Universities from Islamabad (preferred city): NUST, QAU, FAST Islamabad, Bahria University, Air University, etc.
   - DO NOT skip the current city - always include it when student can move
   - If student cannot move, recommend ONLY from current city
   - If student can move but has no specific preferred cities, you can recommend from current city and any other city

2. FEE CONSTRAINT:
   - The student's fee affordability is: {fee_constraint}
   - ONLY recommend universities whose fees fall within this range
   - If student has 'low' affordability, DO NOT recommend expensive universities
   - If student has 'high' affordability, you can recommend premium universities

3. UNIVERSITY TYPE CONSTRAINT:
   {type_constraint}
   - PUBLIC universities = Government-owned and operated (e.g., UET, NUST, COMSATS, Punjab University, QAU, NED, Karachi University)
   - PRIVATE universities = Privately-owned by individuals/organizations (e.g., LUMS, FAST, IBA, SZABIST, BNU, UMT, Bahria, Riphah)
   - If student selects "Private only", recommend ONLY private universities - NO government universities
   - If student selects "Public only", recommend ONLY public universities - NO private universities

4. FIELD OF STUDY MATCHING (CRITICAL - MUST BE ACCURATE):
   - The student wants to study: {study_field}
   - Student's hobbies (personal only): {hobbies}
   - CRITICAL: The field of study above is the ONLY basis for choosing universities. Hobbies are things the
     student enjoys in free time, NOT what they want to study. NEVER recommend a university because of a hobby.
     Example: a student whose field is Software Engineering with an "Art & Design" hobby must get CS/SE
     universities - NOT art/design universities such as NCA, BNU (Beaconhouse) or Indus Valley.
   - Hobbies may only be mentioned as a small bonus (e.g. a good art society on campus), never as a reason to recommend
   - CRITICAL: ONLY recommend universities that are ACTUALLY KNOWN FOR and SPECIALIZE IN this field
   - DO NOT recommend engineering universities (like UET, COMSATS, NUST) if the student wants Arts, Design, Architecture, Business, etc.
   - DO NOT recommend arts universities (like NCA, BNU) if the student wants Engineering
   - Research which universities are ACTUALLY famous for the student's field
   - Examples of correct matching:
     * Arts/Design/Architecture → NCA (Lahore), BNU (Lahore), Indus Valley School (Karachi), etc. (NOT UET, COMSATS, NUST)
     * Engineering → UET, NUST, COMSATS, NED, etc. (NOT NCA, BNU)
     * Business → LUMS, IBA, SZABIST, etc. (NOT UET, COMSATS)
     * Medical → KEMU, Aga Khan, King Edward, etc.
   - If student wants "Design and Architecture" or "Arts", recommend universities LIKE NCA, BNU - NOT engineering universities
   - Verify that the university's PRIMARY focus matches the student's field of interest

5. ADMISSION REQUIREMENTS / AGGREGATE MATCHING (CRITICAL):
   - Student's Intermediate Percentage: {user_profile.intermediate_percentage or 'Not provided'}%
   - CRITICAL: You MUST verify each university's admission requirements/aggregate percentage
   - ONLY recommend universities where the student's percentage MEETS or EXCEEDS the university's admission requirements
   - DO NOT recommend universities with higher aggregate requirements than the student's percentage
   - If student has 70%, do NOT recommend universities requiring 80%+ aggregate
   - If student has 85%+, you can recommend competitive universities with high requirements
   - If student has lower percentage (60-70%), recommend universities with lower/moderate admission requirements (60-75%)
   - If student has moderate percentage (70-80%), recommend universities with moderate requirements (70-85%)
   - Research actual admission requirements for each university before recommending
   - Examples:
     * Student with 65% → Recommend universities with requirements of 60-70% (NOT universities requiring 80%+)
     * Student with 75% → Recommend universities with requirements of 70-85% (can include some competitive ones)
     * Student with 90% → Can recommend top universities with high requirements (85%+)

6. SCHOLARSHIP REQUIREMENT:
   {'- Student needs scholarship - Prioritize universities with good scholarship programs' if user_profile.scholarship_required else '- Student does not need scholarship'}

TASK:
1. Search and analyze Pakistani universities that STRICTLY match ALL of the above criteria
2. Provide 6-10 DIVERSE university recommendations that are SPECIFIC to this student's profile
3. LOCATION DISTRIBUTION - CRITICAL:
   - If student can move and has preferred cities, you MUST split recommendations between current city and preferred cities
   - Example: For 8 recommendations with student in Lahore willing to move to Islamabad:
     * 4 universities from Lahore (current city): UET Lahore, Punjab University, COMSATS Lahore, FAST Lahore
     * 4 universities from Islamabad (preferred city): NUST, QAU, FAST Islamabad, Bahria University
   - DO NOT recommend all universities from only one city when student can move
4. DIVERSITY REQUIREMENT - CRITICAL:
   - DO NOT repeat the same universities (e.g., don't only recommend LUMS and UET for Lahore)
   - Research and recommend a VARIETY of universities in the specified city(s)
   - Include different types: some top-tier, some mid-tier, some accessible options (all within fee range)
   - Each university should be UNIQUE and offer something different
   - If recommending for Lahore, include: LUMS, UET Lahore, Punjab University, COMSATS Lahore, GCU Lahore, FC College, UMT, LSE, etc. (not just LUMS and UET)
   - If recommending for Islamabad, include: NUST, QAU, FAST Islamabad, Bahria University, Air University, Riphah, etc. (not just NUST)
   - If recommending for Karachi, include: IBA, Karachi University, NED, FAST Karachi, Szabist, Habib University, etc. (not just IBA)
   - Match at least 3-4 universities specifically strong in the student's field of interest
   - Provide variety in fee ranges (within the student's affordability: some at lower end, some at higher end)

4. FEE STRUCTURE ANALYSIS - MUST BE PRECISE:
   - The student's affordability is: {fee_constraint}
   - For each university, provide EXACT fee information
   - Categorize recommendations:
     * If fee range is "medium" (50,000-150,000 PKR), include:
       - Some universities around 50,000-80,000 PKR (lower end)
       - Some universities around 80,000-120,000 PKR (mid range)
       - Some universities around 120,000-150,000 PKR (higher end)
   - DO NOT recommend universities that exceed the student's affordability range
   - Verify actual current fees for each university before recommending

5. FIELD OF STUDY MATCHING - DEEP ANALYSIS:
   - Student wants to study: {study_field}
   - Research universities specifically known for excellence in THIS field
   - Recommend at least 3-4 universities that are TOP choices for this specific field
   - Include universities with strong industry connections in this field
   - Consider specialization programs, research opportunities, and faculty expertise

6. Each recommendation must STRICTLY match ALL criteria:
   - Be in the correct city (as per location constraint) - CRITICAL
   - Match university type preference EXACTLY (if private requested, ONLY private; if public requested, ONLY public) - CRITICAL
   - Be ACTUALLY KNOWN FOR and SPECIALIZE IN the student's field of interest (Arts/Design → NCA/BNU, NOT UET/COMSATS) - CRITICAL
   - Have fees that MATCH the affordability range (verify exact fees)
   - Have admission requirements/aggregate that the student's percentage CAN MEET (CRITICAL - verify before recommending)
   - Consider scholarship needs if required
   - Be UNIQUE (not duplicate of other recommendations)
   - Match additional requirements: {user_profile.additional_requirements or 'None'}

7. For each university, provide:
   - Full university name (exact official name)
   - City and Province (must match location constraint)
   - Why it's a good match (explain how it matches EACH criterion including admission requirements)
   - Match score (0-100) - be honest, lower score significantly if student's percentage doesn't meet requirements
   - Admission requirements/aggregate percentage (verify this matches student's {user_profile.intermediate_percentage or 'N/A'}%)
   - Notable achievements and rankings
   - Fee structure information (must match affordability)
   - Relevant programs available (must match the field of study)
   - Pros (list of advantages specific to this student)
   - Cons (list of disadvantages)
   - Detailed analysis explaining why THIS university fits THIS specific student (mention how admission requirements align)

EXAMPLES OF DIVERSE RECOMMENDATIONS:

Example 1: Student in Lahore, wants Computer Science, medium fee (50,000-150,000 PKR):
  → Recommend DIVERSE options:
    1. UET Lahore (Public, ~50,000-70,000 PKR, excellent CS program)
    2. COMSATS Lahore (Public, ~60,000-90,000 PKR, strong IT programs)
    3. Punjab University (Public, ~30,000-50,000 PKR, affordable, good CS)
    4. FAST Lahore (Private, ~80,000-120,000 PKR, top CS program)
    5. GCU Lahore (Public, ~40,000-60,000 PKR, good CS department)
    6. University of Management and Technology (UMT) (Private, ~100,000-140,000 PKR, good CS)
  → DO NOT just recommend LUMS and UET - provide variety!

Example 2: Student in Islamabad, wants Business, high fee (150,000-300,000 PKR), has 82% aggregate:
  → Recommend DIVERSE options (all requiring 82% or less):
    1. NUST Business School (Public, ~150,000-200,000 PKR, requires ~80-85%, excellent business program) - IF student has 82%+
    2. Bahria University Islamabad (Private, ~180,000-250,000 PKR, requires ~75-80%, good business school)
    3. Air University (Public, ~120,000-180,000 PKR, requires ~75-80%, business programs)
    4. Riphah International University (Private, ~200,000-280,000 PKR, requires ~70-75%, business focus)
    5. Quaid-i-Azam University (Public, ~80,000-150,000 PKR, requires ~75-80%, affordable business programs)
  → Match admission requirements - if NUST requires 85%+ and student has 82%, consider other options first
  → Provide variety while ensuring admission eligibility!

Example 3: Student in Karachi, wants Engineering, low fee (under 50,000 PKR), has 68% aggregate:
  → Recommend DIVERSE options (all requiring 68% or less, typically 60-70%):
    1. NED University (Public, ~30,000-50,000 PKR, requires ~70-75%, top engineering) - Check if student meets requirement
    2. Karachi University (Public, ~20,000-40,000 PKR, requires ~65-70%, affordable)
    3. Dawood University (Public, ~25,000-45,000 PKR, requires ~60-65%, engineering programs)
    4. NUST Karachi (if applicable, requires ~80%+) - DO NOT recommend if student only has 68%
  → Focus on public universities within budget AND admission requirements
  → If student has 68%, prioritize universities requiring 60-70%, not those requiring 80%+

Example 4: Student in Lahore, willing to move to Karachi, wants Computer Science, medium fee (50,000-150,000 PKR):
  → Recommend DIVERSE options from BOTH cities (Lahore AND Karachi):
    From Lahore:
    1. UET Lahore (Public, ~50,000-70,000 PKR, excellent CS program)
    2. COMSATS Lahore (Public, ~60,000-90,000 PKR, strong IT programs)
    3. FAST Lahore (Private, ~80,000-120,000 PKR, top CS program)
    From Karachi:
    4. NED University (Public, ~40,000-60,000 PKR, excellent engineering/CS)
    5. FAST Karachi (Private, ~80,000-120,000 PKR, top CS program)
    6. Karachi University (Public, ~30,000-50,000 PKR, affordable CS)
  → CRITICAL: Include universities from BOTH current city (Lahore) AND preferred city (Karachi)
  → DO NOT limit to only preferred city - student should see options from both locations

Format your response as a JSON array with the following structure:
[
  {{
    "university_name": "Full University Name",
    "city": "City Name",
    "province": "Province Name",
    "recommendation_reason": "Detailed explanation of why this university is recommended, mentioning how it matches location, fee, field of study, AND admission requirements",
    "match_score": 85.5,
    "admission_requirements": "Required aggregate percentage (e.g., 75-80%) - MUST verify student's {user_profile.intermediate_percentage or 'percentage'} meets this",
    "achievements": "Notable achievements, rankings, and highlights",
    "fee_information": "Detailed fee structure and affordability (must match student's affordability range)",
    "programs_available": ["Program 1", "Program 2", ...],
    "pros": ["Advantage 1", "Advantage 2", ...],
    "cons": ["Disadvantage 1", "Disadvantage 2", ...],
    "ai_analysis": "Comprehensive analysis explaining why this university is suitable for THIS specific student, including confirmation that admission requirements are met"
  }},
  ...
]

CRITICAL VALIDATION CHECKLIST - VERIFY EACH RECOMMENDATION:
Before including ANY university, ask yourself:
1. ✅ Is it in the correct city? 
   - Student current city: {user_profile.current_city}
   - Can move: {'YES' if user_profile.can_move_to_other_cities else 'NO'}
   - Preferred cities (if can move): {', '.join(user_profile.preferred_cities) if user_profile.preferred_cities else 'Any city'}
   - If student CAN move and has preferred cities: 
     * University must be from EITHER current city ({user_profile.current_city}) OR preferred cities ({', '.join(user_profile.preferred_cities) if user_profile.preferred_cities else 'any city'})
     * CRITICAL: Your FINAL list of recommendations MUST include universities from BOTH current city AND preferred cities
     * DO NOT create a list with only preferred cities - you MUST include current city universities too
     * Example: If student in Lahore willing to move to Islamabad, your 8 recommendations should include ~4 from Lahore and ~4 from Islamabad
   - If student CANNOT move: University must be from current city ({user_profile.current_city}) ONLY
2. ✅ Does it match university type? (Student wants: {user_profile.get_university_type_display()}) 
   - If "Private": University must be PRIVATELY-OWNED (NOT government-owned). NO public universities like UET, COMSATS, Punjab University, NUST, QAU, etc.
   - If "Public": University must be GOVERNMENT-OWNED. NO private universities like LUMS, FAST, IBA, etc.
   - If "Any": Can be either public or private
3. ✅ Is it ACTUALLY KNOWN FOR the student's field? (Student wants: {study_field}) 
   - If Arts/Design → Recommend NCA, BNU, etc. (NOT UET, COMSATS, NUST)
   - If Engineering → Recommend UET, NUST, COMSATS, etc. (NOT NCA, BNU)
   - If Business → Recommend LUMS, IBA, etc. (NOT UET, COMSATS)
4. ✅ Does student's {user_profile.intermediate_percentage or 'percentage'} meet admission requirements?
5. ✅ Do fees match affordability: {fee_constraint}?
6. ✅ Does it match additional requirements: {user_profile.additional_requirements or 'None'}?

If ANY answer is NO, DO NOT recommend that university!

IMPORTANT INSTRUCTIONS:
1. Return ONLY valid JSON array, no additional text before or after
2. Each recommendation must be UNIQUE (no duplicates)
3. Provide 6-10 diverse universities (minimum 6, preferably 8-10)
4. LOCATION DISTRIBUTION IS MANDATORY: If student can move and has preferred cities, you MUST split your recommendations between current city and preferred cities. Do NOT recommend all from one city only.
4. UNIVERSITY TYPE MATCHING IS CRITICAL: Student wants {user_profile.get_university_type_display()} 
   - If "Private": Include ONLY privately-owned universities (LUMS, FAST, IBA, SZABIST, BNU, UMT, Bahria, Riphah, etc.) - NO government universities
   - If "Public": Include ONLY government-owned universities (UET, COMSATS, Punjab University, NUST, QAU, NED, Karachi University, etc.) - NO private universities
   - If "Any": Can include both types
5. FIELD OF STUDY MATCHING IS CRITICAL: Student wants {study_field} - recommend universities ACTUALLY KNOWN FOR this field
6. VERIFY ADMISSION REQUIREMENTS: Student has {user_profile.intermediate_percentage or 'N/A'}% - ONLY recommend universities where this percentage meets/exceeds their admission requirements
7. Verify fee structures match the affordability range exactly
8. Include universities specifically strong in the student's field: {study_field}
9. Research actual current fees AND admission requirements for each university
10. Match at least 3-4 universities that are TOP choices for the student's specific field of study AND match admission requirements
11. DO NOT repeat the same universities - if you recommended one, don't recommend it again. Find other options.
12. CRITICAL: Before recommending any university, verify ALL criteria using the checklist above.
13. For Arts/Design in Lahore: MUST consider NCA, BNU - NOT engineering universities like UET, COMSATS
14. Be creative and comprehensive in finding universities that match ALL criteria

FINAL REMINDER - LOCATION RULE:
{'⚠️ CRITICAL: Student is in ' + user_profile.current_city + ' and willing to move to ' + ', '.join(user_profile.preferred_cities) + '. You MUST include universities from BOTH ' + user_profile.current_city + ' AND ' + ', '.join(user_profile.preferred_cities) + ' in your recommendations. DO NOT recommend only from preferred cities - include current city too!' if user_profile.can_move_to_other_cities and user_profile.preferred_cities else ''}
"""
        
        return prompt
    
    def _parse_recommendations(self, response_text, user_profile):
        """Parse Gemini response into structured recommendations"""
        recommendations = []
        
        try:
            # Try to extract JSON from the response
            # Remove markdown code blocks if present
            text = response_text.strip()
            if text.startswith('```json'):
                text = text[7:]
            elif text.startswith('```'):
                text = text[3:]
            if text.endswith('```'):
                text = text[:-3]
            text = text.strip()
            
            # Parse JSON
            data = json.loads(text)
            
            if isinstance(data, list):
                for idx, rec in enumerate(data, 1):
                    recommendation = {
                        'user_profile': user_profile,
                        'university_name': rec.get('university_name', ''),
                        'city': rec.get('city', ''),
                        'province': rec.get('province', ''),
                        'recommendation_reason': rec.get('recommendation_reason', ''),
                        'match_score': float(rec.get('match_score', 0)),
                        'achievements': rec.get('achievements', ''),
                        'fee_information': rec.get('fee_information', ''),
                        'programs_available': rec.get('programs_available', []),
                        'pros': rec.get('pros', []),
                        'cons': rec.get('cons', []),
                        'ai_analysis': rec.get('ai_analysis', ''),
                        'rank': idx
                    }
                    recommendations.append(recommendation)
            else:
                # Single recommendation
                recommendations.append({
                    'user_profile': user_profile,
                    'university_name': data.get('university_name', ''),
                    'city': data.get('city', ''),
                    'province': data.get('province', ''),
                    'recommendation_reason': data.get('recommendation_reason', ''),
                    'match_score': float(data.get('match_score', 0)),
                    'achievements': data.get('achievements', ''),
                    'fee_information': data.get('fee_information', ''),
                    'programs_available': data.get('programs_available', []),
                    'pros': data.get('pros', []),
                    'cons': data.get('cons', []),
                    'ai_analysis': data.get('ai_analysis', ''),
                    'rank': 1
                })
                
        except json.JSONDecodeError as e:
            print(f"JSON parsing error: {str(e)}")
            print(f"Response text: {response_text[:500]}")
            # Fallback to text parsing or return fallback recommendations
            recommendations = self._get_fallback_recommendations(user_profile)
        except Exception as e:
            print(f"Error parsing recommendations: {str(e)}")
            recommendations = self._get_fallback_recommendations(user_profile)
        
        return recommendations
    
    def _get_fallback_recommendations(self, user_profile):
        """Get fallback recommendations if Gemini fails - based on location, field of study, and university type"""
        recommendations = []
        
        # Determine target city based on user preferences
        if user_profile.can_move_to_other_cities and user_profile.preferred_cities:
            target_city = user_profile.preferred_cities[0].lower()
        else:
            target_city = user_profile.current_city.lower()
        
        # Determine field of study from the chosen fields only; hobbies are used
        # only when no field was chosen (e.g. an "Art & Design" hobby must not mean an arts degree)
        field_programs = [f.strip() for f in (user_profile.preferred_field_of_study or '').split(',') if f.strip()]
        field_keywords = (user_profile.preferred_field_of_study or ' '.join(user_profile.interests)).lower()
        is_arts_design = any(keyword in field_keywords for keyword in ['art', 'design', 'architecture', 'creative', 'fine arts'])
        is_engineering = any(keyword in field_keywords for keyword in ['engineering', 'computer science', 'it', 'technology', 'software'])
        is_business = any(keyword in field_keywords for keyword in ['business', 'management', 'commerce', 'economics', 'mba'])
        
        # Location-based fallback universities
        fallback_universities = []
        
        if 'lahore' in target_city:
            # Arts/Design focused recommendations
            if is_arts_design:
                if user_profile.university_type in ['private', 'both']:
                    fallback_universities = [
                        {
                            'university_name': 'Beaconhouse National University (BNU)',
                            'city': 'Lahore',
                            'province': 'Punjab',
                            'recommendation_reason': 'Premier private university in Lahore specializing in arts, design, and architecture',
                            'match_score': 90.0,
                            'achievements': 'Renowned for excellence in arts, design, and creative fields',
                            'fee_information': 'Private university with fees (approximately 150,000-250,000 PKR per semester)',
                            'programs_available': field_programs or ['Arts and Design programs'],
                            'pros': ['Top private university for arts/design', 'Excellent facilities', 'Strong reputation in creative fields'],
                            'cons': ['Higher fees', 'Competitive admission'],
                            'ai_analysis': 'The premier private university in Lahore for arts, design, and architecture programs',
                        },
                    ]
                else:  # public only
                    fallback_universities = [
                        {
                            'university_name': 'National College of Arts (NCA)',
                            'city': 'Lahore',
                            'province': 'Punjab',
                            'recommendation_reason': 'Premier public institution in Lahore specializing in arts, design, and architecture',
                            'match_score': 95.0,
                            'achievements': 'Most prestigious arts institution in Pakistan, famous for arts and design',
                            'fee_information': 'Public institution with affordable fees (approximately 50,000-80,000 PKR per semester)',
                            'programs_available': field_programs or ['Arts, Design, and Architecture programs'],
                            'pros': ['Top public institution for arts/design', 'Most prestigious', 'Excellent reputation', 'Affordable'],
                            'cons': ['Highly competitive admission'],
                            'ai_analysis': 'The most prestigious public institution in Lahore for arts, design, and architecture',
                        },
                    ]
            # Engineering focused recommendations  
            elif is_engineering:
                if user_profile.university_type == 'private':
                    fallback_universities = [
                        {
                            'university_name': 'FAST National University Lahore',
                            'city': 'Lahore',
                            'province': 'Punjab',
                            'recommendation_reason': 'Top private university in Lahore for computer science and engineering',
                            'match_score': 85.0,
                            'achievements': 'Recognized for excellent computer science and IT programs',
                            'fee_information': 'Private university with moderate fees (approximately 120,000-180,000 PKR per semester)',
                            'programs_available': field_programs or ['Engineering and IT programs'],
                            'pros': ['Top IT programs', 'Private university', 'Modern curriculum', 'Good industry connections'],
                            'cons': ['Higher fees', 'Competitive admission'],
                            'ai_analysis': 'A top private engineering/IT university in Lahore',
                        },
                    ]
                else:  # public or both
                    fallback_universities = [
                        {
                            'university_name': 'University of Engineering and Technology (UET) Lahore',
                            'city': 'Lahore',
                            'province': 'Punjab',
                            'recommendation_reason': 'Premier public engineering university in Lahore with excellent programs',
                            'match_score': 90.0,
                            'achievements': 'One of the oldest and most prestigious engineering universities in Pakistan',
                            'fee_information': 'Public university with affordable fees (approximately 50,000-70,000 PKR per semester)',
                            'programs_available': field_programs or ['Engineering programs'],
                            'pros': ['Top engineering programs', 'Public university', 'Affordable', 'Strong reputation'],
                            'cons': ['Competitive admission', 'Large class sizes'],
                            'ai_analysis': 'A top public engineering university in Lahore',
                        },
                    ]
            # Default - general recommendations matching university type
            else:
                if user_profile.university_type == 'private':
                    fallback_universities = [
                        {
                            'university_name': 'Lahore University of Management Sciences (LUMS)',
                            'city': 'Lahore',
                            'province': 'Punjab',
                            'recommendation_reason': 'Top private university in Lahore with excellent programs',
                            'match_score': 85.0,
                            'achievements': 'Ranked among top universities in Pakistan',
                            'fee_information': 'Private university with fees (approximately 200,000-300,000 PKR per semester)',
                            'programs_available': field_programs or ['Various programs'],
                            'pros': ['High ranking', 'Excellent facilities', 'Strong reputation'],
                            'cons': ['Higher fees', 'Competitive admission'],
                            'ai_analysis': 'A highly ranked private university in Lahore',
                        },
                    ]
                else:  # public or both
                    fallback_universities = [
                        {
                            'university_name': 'Punjab University Lahore',
                            'city': 'Lahore',
                            'province': 'Punjab',
                            'recommendation_reason': 'Largest public university in Lahore with diverse programs',
                            'match_score': 75.0,
                            'achievements': 'One of the oldest and largest universities in Pakistan',
                            'fee_information': 'Public university with affordable fees (approximately 30,000-50,000 PKR per semester)',
                            'programs_available': field_programs or ['Various programs'],
                            'pros': ['Very affordable', 'Large university with many programs', 'Public university'],
                            'cons': ['Large class sizes', 'Administrative delays'],
                            'ai_analysis': 'An affordable public university option in Lahore',
                        },
                    ]
        elif 'karachi' in target_city:
            fallback_universities = [
                {
                    'university_name': 'NED University of Engineering and Technology',
                    'city': 'Karachi',
                    'province': 'Sindh',
                    'recommendation_reason': 'Premier public engineering university in Karachi',
                    'match_score': 85.0,
                    'achievements': 'One of the top engineering universities in Pakistan',
                    'fee_information': 'Public university with affordable fees (approximately 40,000-60,000 PKR per semester)',
                    'programs_available': field_programs or ['Engineering programs'],
                    'pros': ['Public university', 'Affordable', 'Excellent engineering programs', 'Strong reputation'],
                    'cons': ['Competitive admission'],
                    'ai_analysis': 'A top public engineering university in Karachi',
                },
                {
                    'university_name': 'Karachi University',
                    'city': 'Karachi',
                    'province': 'Sindh',
                    'recommendation_reason': 'Largest public university in Karachi with diverse programs',
                    'match_score': 75.0,
                    'achievements': 'One of the largest and oldest universities in Pakistan',
                    'fee_information': 'Public university with affordable fees (approximately 20,000-40,000 PKR per semester)',
                    'programs_available': field_programs or ['Various programs'],
                    'pros': ['Very affordable', 'Wide range of programs', 'Public university', 'Established reputation'],
                    'cons': ['Large class sizes', 'Administrative challenges'],
                    'ai_analysis': 'An affordable public university option in Karachi',
                },
                {
                    'university_name': 'FAST National University (Karachi Campus)',
                    'city': 'Karachi',
                    'province': 'Sindh',
                    'recommendation_reason': 'Strong private university in Karachi known for IT and computer science',
                    'match_score': 82.0,
                    'achievements': 'Recognized for excellent computer science and IT programs',
                    'fee_information': 'Private university with moderate fees (approximately 80,000-120,000 PKR per semester)',
                    'programs_available': field_programs or ['IT and Computer Science programs'],
                    'pros': ['Excellent IT programs', 'Good industry connections', 'Modern curriculum'],
                    'cons': ['Private university fees', 'Competitive admission'],
                    'ai_analysis': 'A strong private university option in Karachi for IT and computer science',
                },
                {
                    'university_name': 'SZABIST (Shaheed Zulfikar Ali Bhutto Institute)',
                    'city': 'Karachi',
                    'province': 'Sindh',
                    'recommendation_reason': 'Reputed private university in Karachi with quality business and IT programs',
                    'match_score': 78.0,
                    'achievements': 'Well-established private university with good academic standards',
                    'fee_information': 'Private university with moderate fees (approximately 100,000-140,000 PKR per semester)',
                    'programs_available': field_programs or ['Business and IT programs'],
                    'pros': ['Good reputation', 'Quality programs', 'Good facilities'],
                    'cons': ['Private university fees'],
                    'ai_analysis': 'A good private university option in Karachi',
                }
            ]
        elif 'islamabad' in target_city:
            fallback_universities = [
                {
                    'university_name': 'National University of Sciences and Technology (NUST)',
                    'city': 'Islamabad',
                    'province': 'Islamabad',
                    'recommendation_reason': 'Top-ranked public university in Islamabad with excellent programs',
                    'match_score': 90.0,
                    'achievements': 'Ranked #1 in Pakistan by QS Rankings, excellent research facilities',
                    'fee_information': 'Public university with moderate fees (approximately 100,000-150,000 PKR per semester)',
                    'programs_available': field_programs or ['Various programs'],
                    'pros': ['Top ranking', 'Excellent facilities', 'Strong reputation', 'Good research opportunities'],
                    'cons': ['Highly competitive admission', 'Large campus'],
                    'ai_analysis': 'The top-ranked university in Islamabad with excellent programs',
                },
                {
                    'university_name': 'Quaid-i-Azam University (QAU)',
                    'city': 'Islamabad',
                    'province': 'Islamabad',
                    'recommendation_reason': 'Premier public research university in Islamabad',
                    'match_score': 85.0,
                    'achievements': 'Top public research university, known for strong academic programs',
                    'fee_information': 'Public university with affordable fees (approximately 50,000-80,000 PKR per semester)',
                    'programs_available': field_programs or ['Various programs'],
                    'pros': ['Public university', 'Affordable', 'Strong research focus', 'Good reputation'],
                    'cons': ['Competitive admission', 'Limited engineering programs'],
                    'ai_analysis': 'A top public research university in Islamabad',
                },
                {
                    'university_name': 'FAST National University (Islamabad Campus)',
                    'city': 'Islamabad',
                    'province': 'Islamabad',
                    'recommendation_reason': 'Strong private university in Islamabad known for IT and computer science',
                    'match_score': 82.0,
                    'achievements': 'Recognized for excellent computer science and IT programs',
                    'fee_information': 'Private university with moderate fees (approximately 90,000-130,000 PKR per semester)',
                    'programs_available': field_programs or ['IT and Computer Science programs'],
                    'pros': ['Excellent IT programs', 'Good industry connections', 'Modern curriculum'],
                    'cons': ['Private university fees', 'Competitive admission'],
                    'ai_analysis': 'A strong private university option in Islamabad for IT and computer science',
                },
                {
                    'university_name': 'Air University',
                    'city': 'Islamabad',
                    'province': 'Islamabad',
                    'recommendation_reason': 'Public university in Islamabad with good engineering and technology programs',
                    'match_score': 78.0,
                    'achievements': 'Well-established public university with good academic standards',
                    'fee_information': 'Public university with moderate fees (approximately 80,000-120,000 PKR per semester)',
                    'programs_available': field_programs or ['Engineering and Technology programs'],
                    'pros': ['Public university', 'Good engineering programs', 'Modern facilities'],
                    'cons': ['Limited programs compared to larger universities'],
                    'ai_analysis': 'A good public university option in Islamabad',
                }
            ]
        else:
            # Generic fallback for other cities
            fallback_universities = [
                {
                    'university_name': f'Local University in {user_profile.current_city}',
                    'city': user_profile.current_city,
                    'province': user_profile.current_province,
                    'recommendation_reason': f'University in {user_profile.current_city} matching your preferences',
                    'match_score': 70.0,
                    'achievements': 'Contact university for details',
                    'fee_information': 'Contact university for current fee structure',
                    'programs_available': field_programs or ['Various programs'],
                    'pros': ['Local university', 'Matches location preference'],
                    'cons': ['Contact university for specific details'],
                    'ai_analysis': f'A university in {user_profile.current_city} that matches your location preference',
                }
            ]
        
        for idx, rec in enumerate(fallback_universities, 1):
            rec['user_profile'] = user_profile
            rec['rank'] = idx
            recommendations.append(rec)
        
        return recommendations

