# import requests
# from bs4 import BeautifulSoup
# from langchain_google_genai import ChatGoogleGenerativeAI
# from langchain_core.prompts import ChatPromptTemplate
# from langchain_core.output_parsers import PydanticOutputParser
# from .schemas import AutomationResponse

# class AIService:
#     def __init__(self):
#         self.llm = ChatGoogleGenerativeAI(
#             model="gemini-2.5-flash", 
#             google_api_key="YOUR_GEMINI_API_KEY"
#         )
#         self.parser = PydanticOutputParser(pydantic_object=AutomationResponse)

#     def fetch_remote_html(self, url):
#         """Visits the university portal and grabs the HTML code."""
#         try:
#             headers = {'User-Agent': 'Mozilla/5.0'} # Pretend to be a browser
#             response = requests.get(url, headers=headers, timeout=10)
#             response.raise_for_status()
#             return response.text
#         except Exception as e:
#             raise Exception(f"Failed to fetch portal HTML: {str(e)}")

#     def extract_form_structure(self, html_content):
#         """Simplifies HTML for the LLM."""
#         soup = BeautifulSoup(html_content, 'html.parser')
#         simplified_elements = []
#         for element in soup.find_all(['input', 'select', 'textarea', 'button']):
#             info = {
#                 "tag": element.name,
#                 "id": element.get('id'),
#                 "name": element.get('name'),
#                 "type": element.get('type', 'text'),
#                 "label": ""
#             }
#             if element.get('id'):
#                 lbl = soup.find('label', attrs={'for': element.get('id')})
#                 if lbl: info["label"] = lbl.get_text().strip()
#             simplified_elements.append(info)
#         return simplified_elements

#     def get_automation_instructions(self, target_url, student_data, app_id):
#         # 1. Fetch HTML automatically
#         html_content = self.fetch_remote_html(target_url)
        
#         # 2. Extract structure
#         form_structure = self.extract_form_structure(html_content)
        

#         prompt = ChatPromptTemplate.from_template(
#             "Map the following student data to the HTML form structure.\n"
#             "STUDENT PROFILE:\n{student_data}\n\n"
#             "FORM STRUCTURE:\n{form_structure}\n\n"
#             "URL: {url}\n"
#             "{format_instructions}"
#         )

#         chain = prompt | self.llm | self.parser
#         return chain.invoke({
#             "student_data": student_data,
#             "form_structure": form_structure,
#             "url": target_url,
#             "format_instructions": self.parser.get_format_instructions()
#         })

# """
# mapping/services.py

# Drop-in replacement. Key changes vs original:
#   - Prompt now explicitly instructs the LLM to produce click/wait steps
#     between React multi-step form pages (Next button navigation).
#   - application_id is derived from the student profile id + url hash
#     so it stays stable across calls.
#   - fetch_remote_html now passes a Referer header so Live Server doesn't
#     block the request.
#   - extract_form_structure also captures button elements with their text
#     so the LLM can identify "Next" / "Submit" buttons by label.
# """

# import hashlib
# import requests
# from bs4 import BeautifulSoup
# from langchain_google_genai import ChatGoogleGenerativeAI
# from langchain_core.prompts import ChatPromptTemplate
# from langchain_core.output_parsers import PydanticOutputParser

# from .schemas import AutomationResponse


# class AIService:
#     def __init__(self):
#         self.llm = ChatGoogleGenerativeAI(
#             model="gemini-2.5-flash",
#             google_api_key="YOUR_GEMINI_API_KEY",
#             temperature=0,
#         )
#         self.parser = PydanticOutputParser(pydantic_object=AutomationResponse)

#     # ------------------------------------------------------------------
#     # 1. Fetch HTML
#     # ------------------------------------------------------------------
#     def fetch_remote_html(self, url: str) -> str:
#         """Visits the university portal and grabs the HTML."""
#         try:
#             headers = {
#                 "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
#                               "AppleWebKit/537.36 (KHTML, like Gecko) "
#                               "Chrome/120.0.0.0 Safari/537.36",
#                 "Referer": url,
#             }
#             response = requests.get(url, headers=headers, timeout=15)
#             response.raise_for_status()
#             return response.text
#         except Exception as e:
#             raise Exception(f"Failed to fetch portal HTML: {str(e)}")

#     # ------------------------------------------------------------------
#     # 2. Extract form structure — now includes buttons
#     # ------------------------------------------------------------------
#     def extract_form_structure(self, html_content: str) -> list:
#         """
#         Simplifies HTML for the LLM.
#         Captures inputs, selects, textareas AND buttons so the model
#         can identify Next/Submit buttons for multi-step navigation.
#         """
#         soup = BeautifulSoup(html_content, "html.parser")
#         simplified_elements = []

#         for element in soup.find_all(["input", "select", "textarea", "button"]):
#             tag = element.name

#             # Skip hidden / submit-type inputs that are not buttons
#             el_type = element.get("type", "text")
#             if el_type == "hidden":
#                 continue

#             info = {
#                 "tag": tag,
#                 "id": element.get("id"),
#                 "name": element.get("name"),
#                 "type": el_type,
#                 "label": "",
#                 "text": "",        # for buttons
#                 "options": [],     # for selects
#             }

#             # Find associated <label>
#             if element.get("id"):
#                 lbl = soup.find("label", attrs={"for": element.get("id")})
#                 if lbl:
#                     info["label"] = lbl.get_text(strip=True)

#             # Button text
#             if tag == "button":
#                 info["text"] = element.get_text(strip=True)

#             # Select options
#             if tag == "select":
#                 info["options"] = [
#                     opt.get_text(strip=True)
#                     for opt in element.find_all("option")
#                     if opt.get_text(strip=True)
#                 ]

#             simplified_elements.append(info)

#         return simplified_elements

#     # ------------------------------------------------------------------
#     # 3. Stable application_id
#     # ------------------------------------------------------------------
#     @staticmethod
#     def make_app_id(student_id: int, url: str) -> int:
#         """Deterministic app id so the same student+url always gives the same id."""
#         raw = f"{student_id}:{url}"
#         return int(hashlib.md5(raw.encode()).hexdigest()[:8], 16) % 999999 + 1

#     # ------------------------------------------------------------------
#     # 4. Build the automation mapping
#     # ------------------------------------------------------------------
#     def get_automation_instructions(
#         self, target_url: str, student_data: dict, app_id: int
#     ) -> "AutomationResponse":
#         """
#         Fetches the target form, extracts its structure, then asks the LLM
#         to produce a step-by-step filling plan that handles multi-step
#         React forms (fill → click Next → fill → … → submit).
#         """

#         # Step A: fetch & parse
#         html_content = self.fetch_remote_html(target_url)
#         form_structure = self.extract_form_structure(html_content)

#         # Step B: build prompt — multi-step React aware
#         system_instructions = """
# You are an expert at mapping student profile data to HTML form fields for automated filling.

# The target form may be a MULTI-STEP React form where:
#   - Each "step" is shown one at a time.
#   - A "Next" button advances to the next step.
#   - A final "Submit" button completes the form.

# You must return a JSON plan that fills EACH step, clicks "Next" to advance,
# then submits. The JSON must follow this EXACT schema:

# {{
#   "application_id": {app_id},
#   "url": "{url}",
#   "steps": [
#     {{
#       "action": "fill",
#       "selector": null,
#       "fields": [
#         {{
#           "selector": "#css_id",
#           "type": "text | email | tel | date | number | select | checkbox | radio | textarea | file",
#           "value": "<matched student value or empty string>",
#           "confidence": 0.0
#         }}
#       ]
#     }},
#     {{
#       "action": "click",
#       "selector": "#next-button-id",
#       "fields": null,
#       "wait_ms": 900
#     }},
#     {{
#       "action": "fill",
#       "selector": null,
#       "fields": []
#     }},
#     {{
#       "action": "submit",
#       "selector": "#submit-button-id",
#       "fields": null
#     }}
#   ]
# }}

# STRICT RULES:
# 1. Use #id selectors wherever an id attribute exists; otherwise use [name="x"].
# 2. For multi-step forms insert a {{"action":"click","selector":"<Next btn>","fields":null,"wait_ms":900}}
#    BETWEEN each pair of fill steps.
# 3. For "select" fields: value must be the exact option text visible to the user.
# 4. For "checkbox" or "radio": value must be "true" or "false".
# 5. For "date": format as YYYY-MM-DD.
# 6. For "file": always set value to "".
# 7. confidence: 1.0 = exact match, 0.5 = partial/inferred, 0.0 = no match.
# 8. Include ALL fillable fields, even if confidence is 0.
# 9. Do NOT add markdown fences or extra explanation — return raw JSON only.
# """

#         prompt = ChatPromptTemplate.from_messages([
#             ("system", system_instructions),
#             ("human",
#              "STUDENT PROFILE DATA:\n{student_data}\n\n"
#              "FORM STRUCTURE (all inputs, selects, textareas, buttons):\n{form_structure}\n\n"
#              "TARGET URL: {url}\n\n"
#              "application_id for this mapping: {app_id}\n\n"
#              "{format_instructions}"),
#         ])

#         chain = prompt | self.llm | self.parser
#         result = chain.invoke({
#             "student_data": student_data,
#             "form_structure": form_structure,
#             "url": target_url,
#             "app_id": app_id,
#             "format_instructions": self.parser.get_format_instructions(),
#         })

#         return result

# import hashlib
# import requests
# from bs4 import BeautifulSoup
# from langchain_google_genai import ChatGoogleGenerativeAI
# from langchain_core.prompts import ChatPromptTemplate
# from langchain_core.output_parsers import PydanticOutputParser

# from .schemas import AutomationResponse


# class AIService:
#     def __init__(self):
#         self.llm = ChatGoogleGenerativeAI(
#             model="gemini-2.5-flash",
#             google_api_key="YOUR_GEMINI_API_KEY",
#             temperature=0,
#         )
#         self.parser = PydanticOutputParser(pydantic_object=AutomationResponse)

#     # ------------------------------------------------------------------
#     # 1. Fetch HTML
#     # ------------------------------------------------------------------
#     def fetch_remote_html(self, url: str) -> str:
#         try:
#             headers = {
#                 "User-Agent": "Mozilla/5.0",
#                 "Referer": url,
#             }
#             response = requests.get(url, headers=headers, timeout=15)
#             response.raise_for_status()
#             return response.text
#         except Exception as e:
#             raise Exception(f"Failed to fetch portal HTML: {str(e)}")

#     # ------------------------------------------------------------------
#     # 2. Extract form structure
#     # ------------------------------------------------------------------
#     def extract_form_structure(self, html_content: str) -> list:
#         soup = BeautifulSoup(html_content, "html.parser")
#         elements = []

#         for el in soup.find_all(["input", "select", "textarea", "button"]):
#             if el.get("type") == "hidden":
#                 continue

#             item = {
#                 "tag": el.name,
#                 "id": el.get("id"),
#                 "name": el.get("name"),
#                 "type": el.get("type", "text"),
#                 "label": "",
#                 "text": "",
#                 "options": [],
#             }

#             if el.get("id"):
#                 lbl = soup.find("label", attrs={"for": el.get("id")})
#                 if lbl:
#                     item["label"] = lbl.get_text(strip=True)

#             if el.name == "button":
#                 item["text"] = el.get_text(strip=True)

#             if el.name == "select":
#                 item["options"] = [
#                     opt.get_text(strip=True)
#                     for opt in el.find_all("option")
#                     if opt.get_text(strip=True)
#                 ]

#             elements.append(item)

#         return elements

#     # ------------------------------------------------------------------
#     # 3. Stable application ID
#     # ------------------------------------------------------------------
#     @staticmethod
#     def make_app_id(student_id: int, url: str) -> int:
#         raw = f"{student_id}:{url}"
#         return int(hashlib.md5(raw.encode()).hexdigest()[:8], 16) % 999999 + 1

#     # ------------------------------------------------------------------
#     # 4. MAIN AI FUNCTION (FIXED)
#     # ------------------------------------------------------------------
#     def get_automation_instructions(
#         self, target_url: str, student_data: dict, app_id: int
#     ) -> AutomationResponse:

#         html = self.fetch_remote_html(target_url)
#         form_structure = self.extract_form_structure(html)

#         # ✅ FULLY ESCAPED PROMPT
#         system_prompt = """
# You are an expert at mapping student data to HTML forms.

# Return STRICT JSON in this format:

# {{
#   "application_id": {app_id},
#   "url": "{url}",
#   "steps": [
#     {{
#       "action": "fill",
#       "selector": null,
#       "fields": [
#         {{
#           "selector": "#field_id",
#           "type": "text | email | tel | date | number | select | checkbox | radio | textarea | file",
#           "value": "value",
#           "confidence": 0.0
#         }}
#       ]
#     }},
#     {{
#       "action": "click",
#       "selector": "#next-button",
#       "fields": null,
#       "wait_ms": 900
#     }},
#     {{
#       "action": "submit",
#       "selector": "#submit-button",
#       "fields": null
#     }}
#   ]
# }}

# RULES:
# - Use #id if available, otherwise [name="x"]
# - Insert this between steps: {{"action":"click","selector":"Next","fields":null,"wait_ms":900}}
# - Select values must match exact option text
# - Checkbox/radio = true/false
# - Date = YYYY-MM-DD
# - File inputs = ""
# - Confidence: 1 exact, 0.5 guess, 0 no match
# - Return ONLY JSON (no explanation)
# """

#         prompt = ChatPromptTemplate.from_messages([
#             ("system", system_prompt),
#             ("human",
#              "STUDENT DATA:\n{student_data}\n\n"
#              "FORM STRUCTURE:\n{form_structure}\n\n"
#              "URL: {url}\n\n"
#              "APPLICATION ID: {app_id}\n\n"
#              "{format_instructions}")
#         ])

#         chain = prompt | self.llm | self.parser

#         return chain.invoke({
#             "student_data": student_data,
#             "form_structure": form_structure,
#             "url": target_url,
#             "app_id": app_id,
#             "format_instructions": self.parser.get_format_instructions(),
#         })
import hashlib
import time
from bs4 import BeautifulSoup

from django.conf import settings

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import PydanticOutputParser

from .schemas import AutomationResponse


class AIService:
    def __init__(self):
        self.llm = ChatGoogleGenerativeAI(
            model="gemini-2.5-flash",
            google_api_key=settings.GEMINI_API_KEY,  # from .env, never hard-coded
            temperature=0,
        )
        self.parser = PydanticOutputParser(pydantic_object=AutomationResponse)

    # ---------------------------
    # Stable App ID
    # ---------------------------
    @staticmethod
    def make_app_id(student_id: int, url: str) -> int:
        raw = f"{student_id}:{url}"
        return int(hashlib.md5(raw.encode()).hexdigest()[:8], 16) % 999999 + 1

    # ---------------------------
    # Extract fields
    # ---------------------------
    def extract_fields(self, driver):
        soup = BeautifulSoup(driver.page_source, "html.parser")
        elements = []

        for el in soup.find_all(["input", "select", "textarea"]):
            if el.get("type") == "hidden":
                continue

            selector = (
                f"#{el.get('id')}" if el.get("id")
                else f"[name='{el.get('name')}']" if el.get("name")
                else el.name
            )

            elements.append({
                "selector": selector,
                "type": el.get("type", "text"),
            })

        return elements

    # ---------------------------
    # LOGIN HANDLER 🔥
    # ---------------------------
    def handle_login(self, driver):
        try:
            email = driver.find_element(By.XPATH, "//input[@type='email']")
            password = driver.find_element(By.XPATH, "//input[@type='password']")

            print("🔐 Login detected → logging in...")

            email.send_keys("amenmunir1612@gmail.com")   # 🔥 CHANGE IF NEEDED
            password.send_keys("yourpassword")           # 🔥 CHANGE THIS

            login_btn = driver.find_element(
                By.XPATH,
                "//button[contains(text(),'Login') or contains(text(),'Sign in')]"
            )

            driver.execute_script("arguments[0].click();", login_btn)

            time.sleep(3)

        except:
            print("✅ No login page detected")

    # ---------------------------
    # MULTI STEP SCRAPER
    # ---------------------------
    def scrape_multi_step_form(self, url):
        options = Options()
        options.add_argument("--headless")
        options.add_argument("--no-sandbox")

        driver = webdriver.Chrome(options=options)
        all_steps = []

        try:
            driver.get(url)

            wait = WebDriverWait(driver, 10)

            # 🔐 HANDLE LOGIN FIRST
            self.handle_login(driver)

            # WAIT for form to appear
            wait.until(EC.presence_of_element_located((By.TAG_NAME, "input")))

            for step in range(10):  # allow more steps
                print(f"🧭 Step {step + 1}")

                fields = self.extract_fields(driver)

                if fields:
                    all_steps.append(fields)

                # CLICK NEXT
                try:
                    next_btn = driver.find_element(
                        By.XPATH,
                        "//button[contains(text(),'Next') or contains(text(),'next')]"
                    )

                    driver.execute_script("arguments[0].click();", next_btn)
                    time.sleep(2)

                except:
                    print("🚀 No Next → trying submit...")

                    try:
                        submit_btn = driver.find_element(
                            By.XPATH,
                            "//button[contains(text(),'Submit') or contains(text(),'submit')]"
                        )
                        print("✅ Submit detected")
                    except:
                        print("❌ No submit button found")

                    break

            return all_steps

        finally:
            driver.quit()

    # ---------------------------
    # MAIN FUNCTION
    # ---------------------------
    def get_automation_instructions(self, target_url, student_data, app_id):

        steps_data = self.scrape_multi_step_form(target_url)

        if not steps_data:
            raise Exception("No form steps found after login")

        system_prompt = """
You are an expert at mapping student data to multi-step forms.

Return STRICT JSON:

{{
  "application_id": {app_id},
  "url": "{url}",
  "steps": []
}}

RULES:
- Each step must have:
  fill → click → fill → click → ... → submit
- Use selectors provided
- Use student data
- Return only JSON
"""

        prompt = ChatPromptTemplate.from_messages([
            ("system", system_prompt),
            ("human",
             "STUDENT:\n{student_data}\n\n"
             "FORM STEPS:\n{steps_data}\n\n"
             "URL: {url}\n\n"
             "APP ID: {app_id}\n\n"
             "{format_instructions}")
        ])

        chain = prompt | self.llm | self.parser

        return chain.invoke({
            "student_data": student_data,
            "steps_data": steps_data,
            "url": target_url,
            "app_id": app_id,
            "format_instructions": self.parser.get_format_instructions(),
        })