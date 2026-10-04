# """
# apply_pipeline/services.py

# Two services:
#   1. AIService: Scrapes forms from portal + uses Gemini to generate mapping
#   2. AutomationService: Drives browser using the mapping to fill + submit
# """

# import hashlib
# import time
# import os
# import json
# from pathlib import Path

# from bs4 import BeautifulSoup

# from django.conf import settings

# from selenium import webdriver
# from selenium.webdriver.chrome.options import Options
# from selenium.webdriver.common.by import By
# from selenium.webdriver.support.ui import Select, WebDriverWait
# from selenium.webdriver.support import expected_conditions as EC
# from selenium.common.exceptions import TimeoutException, NoSuchElementException

# from langchain_google_genai import ChatGoogleGenerativeAI
# from langchain_core.prompts import ChatPromptTemplate
# from langchain_core.output_parsers import PydanticOutputParser

# from .schemas import AutomationResponse  # ✅ FIXED: Use relative import


# # ============================================================
# # AI SERVICE  —  scrapes form + generates mapping via Gemini
# # ============================================================

# class AIService:
#     """
#     Scrapes the multi-step form from a portal URL,
#     then uses Gemini to generate field mappings.
#     """
    
#     def __init__(self):
#         # ✅ FIXED: Check if GOOGLE_API_KEY is configured
#         api_key = getattr(settings, 'GEMINI_API_KEY', None)
#         if not api_key:
#             raise ValueError(
#                 "GOOGLE_API_KEY not set in Django settings. "
#                 "Add it to settings.py or set GOOGLE_API_KEY environment variable."
#             )
        
#         self.llm = ChatGoogleGenerativeAI(
#             model="gemini-2.5-flash",  # ✅ FIXED: Corrected model name
#             google_api_key=api_key,
#             temperature=0,
#         )
#         self.parser = PydanticOutputParser(pydantic_object=AutomationResponse)

#     # ------------------------------------------------------------------
#     # Extract form fields from current page
#     # ------------------------------------------------------------------
#     def extract_fields(self, driver):
#         """Extracts all form fields from the current page."""
#         soup = BeautifulSoup(driver.page_source, "html.parser")
#         elements = []

#         for el in soup.find_all(["input", "select", "textarea"]):
#             if el.get("type") == "hidden":
#                 continue

#             selector = (
#                 f"#{el.get('id')}" if el.get("id")
#                 else f"[name='{el.get('name')}']" if el.get("name")
#                 else f"[data-testid='{el.get('data-testid')}']" if el.get("data-testid")
#                 else None
#             )

#             if not selector:
#                 continue

#             elements.append({
#                 "selector": selector,
#                 "type": el.get("type", "text"),
#                 "label": el.get("placeholder", el.get("aria-label", "")),
#             })

#         return elements

#     # ------------------------------------------------------------------
#     # Login handler
#     # ------------------------------------------------------------------
#     def handle_login(self, driver):
#         """Attempts to log in if a login page is detected."""
#         try:
#             email = driver.find_element(By.XPATH, "//input[@type='email']")
#             password = driver.find_element(By.XPATH, "//input[@type='password']")

#             print("🔐 Login detected → logging in...")

#             portal_email = getattr(settings, "PORTAL_EMAIL", "")
#             portal_password = getattr(settings, "PORTAL_PASSWORD", "")

#             if not portal_email or not portal_password:
#                 print("⚠️  PORTAL_EMAIL or PORTAL_PASSWORD not set in settings")
#                 return

#             email.send_keys(portal_email)
#             password.send_keys(portal_password)

#             login_btn = driver.find_element(
#                 By.XPATH,
#                 "//button[contains(text(),'Login') or contains(text(),'Sign in') or contains(text(),'login')]"
#             )
#             driver.execute_script("arguments[0].click();", login_btn)
#             time.sleep(3)

#         except (NoSuchElementException, Exception):
#             print("✅ No login page detected")

#     # ------------------------------------------------------------------
#     # Scrape multi-step form
#     # ------------------------------------------------------------------
#     def scrape_multi_step_form(self, url):
#         """
#         Opens the URL, handles login, and scrapes all form steps.
#         Returns a list of steps, each containing form fields.
#         """
#         options = Options()
#         options.add_argument("--headless")
#         options.add_argument("--no-sandbox")
#         options.add_argument("--disable-dev-shm-usage")
#         options.add_argument("--window-size=1920,1080")

#         driver = None
#         all_steps = []

#         try:
#             driver = webdriver.Chrome(options=options)
#             driver.get(url)
#             wait = WebDriverWait(driver, 10)

#             self.handle_login(driver)

#             # ✅ FIXED: Wait for any form element to be present
#             try:
#                 wait.until(EC.presence_of_element_located((By.TAG_NAME, "input")))
#             except TimeoutException:
#                 print("⚠️  No input fields found")
#                 return []

#             # Scrape up to 10 steps
#             for step in range(10):
#                 print(f"🧭 Step {step + 1}")
#                 fields = self.extract_fields(driver)

#                 if fields:
#                     all_steps.append({
#                         "step_number": step + 1,
#                         "fields": fields
#                     })

#                 try:
#                     next_btn = driver.find_element(
#                         By.XPATH,
#                         "//button[contains(text(),'Next') or contains(text(),'next')]"
#                     )
#                     driver.execute_script("arguments[0].click();", next_btn)
#                     time.sleep(2)

#                 except NoSuchElementException:
#                     print("🚀 No Next button → trying submit...")
#                     try:
#                         driver.find_element(
#                             By.XPATH,
#                             "//button[contains(text(),'Submit') or contains(text(),'submit')]"
#                         )
#                         print("✅ Submit detected")
#                     except NoSuchElementException:
#                         print("❌ No submit button found")
#                     break

#             return all_steps

#         finally:
#             if driver:
#                 driver.quit()

#     # ------------------------------------------------------------------
#     # Main — generate mapping via Gemini
#     # ------------------------------------------------------------------
#     def get_automation_instructions(self, target_url, student_data, app_id):
#         """
#         Main entry point: scrapes form, then uses Gemini to generate mapping.
#         """
#         steps_data = self.scrape_multi_step_form(target_url)

#         if not steps_data:
#             raise Exception("No form steps found after login")

#         system_prompt = """
# You are an expert at mapping student data to multi-step forms.

# Given:
# 1. Student data (name, email, DOB, GPA, etc.)
# 2. Form steps with selectors and field types
# 3. Target URL

# Generate a complete automation plan.

# RESPONSE FORMAT: Return ONLY valid JSON. No markdown, no backticks.

# {{
#   "application_id": {app_id},
#   "url": "{url}",
#   "steps": [
#     {{
#       "action": "fill",
#       "fields": [
#         {{"selector": "#name", "type": "text", "value": "John Doe", "confidence": 0.95}}
#       ]
#     }},
#     {{
#       "action": "click",
#       "selector": "button:contains('Next')",
#       "wait_ms": 2000
#     }},
#     {{
#       "action": "submit",
#       "selector": "button:contains('Submit')",
#       "wait_ms": 3000
#     }}
#   ]
# }}

# RULES:
# - Each step is either "fill", "click", or "submit"
# - For "fill": provide all fields to fill
# - For "click"/"submit": provide the selector only
# - Use the exact selectors provided
# - Map student data to the matching fields
# - Set confidence to 0.0 if no match
# - Return ONLY JSON
# """

#         prompt = ChatPromptTemplate.from_messages([
#             ("system", system_prompt),
#             ("human",
#              "STUDENT DATA:\n{student_data}\n\n"
#              "FORM STEPS:\n{steps_data}\n\n"
#              "URL: {url}\n\n"
#              "APP ID: {app_id}")
#         ])

#         chain = prompt | self.llm | self.parser

#         try:
#             result = chain.invoke({
#                 "student_data": json.dumps(student_data, indent=2),
#                 "steps_data": json.dumps(steps_data, indent=2),
#                 "url": target_url,
#                 "app_id": app_id,
#             })
#             return result
#         except Exception as e:
#             print(f"❌ LLM parsing failed: {e}")
#             raise


# from datetime import datetime
# import time

# from selenium import webdriver
# from selenium.webdriver.chrome.options import Options
# from selenium.webdriver.common.by import By
# from selenium.webdriver.common.keys import Keys
# from selenium.webdriver.support.ui import WebDriverWait, Select
# from selenium.webdriver.support import expected_conditions as EC

# try:
#     import pyperclip
#     PYPERCLIP_AVAILABLE = True
# except ImportError:
#     PYPERCLIP_AVAILABLE = False


# class AutomationService:

#     # ============================================================
#     # NORMALIZATION LAYER
#     # ============================================================

#     def normalize_value(self, field_name, value):
#         if not value:
#             return value

#         value = str(value).strip()

#         city_map = {
#             "lahore": "Punjab",
#             "karachi": "Sindh",
#             "islamabad": "Islamabad",
#             "peshawar": "KPK",
#             "quetta": "Balochistan"
#         }

#         if field_name and "province" in field_name.lower():
#             return city_map.get(value.lower(), value)

#         return value

#     # ============================================================
#     # COURSE SEMANTIC NORMALIZATION
#     # ============================================================

#     def normalize_course(self, value):
#         if not value:
#             return []

#         v = str(value).lower().strip()

#         canonical_map = {
#             # LAW
#             "llb":                     ["llb", "law", "bachelor of law", "legal"],
#             "law":                     ["law", "llb", "legal studies", "legal"],
#             "bachelor of law":         ["law", "llb", "legal"],
#             "legal studies":           ["legal studies", "law", "llb"],

#             # COMPUTER SCIENCE
#             "cs":                      ["cs", "computer science", "bscs"],
#             "bscs":                    ["bscs", "computer science", "cs"],
#             "computer science":        ["computer science", "cs", "bscs"],

#             # SOFTWARE ENGINEERING
#             "bsse":                    ["bsse", "software engineering", "software"],
#             "software engineering":    ["software engineering", "bsse", "software"],

#             # INFORMATION TECHNOLOGY
#             "bsit":                    ["bsit", "information technology", "it", "bs information technology", "bs (it)"],
#             "it":                      ["it", "information technology", "bsit"],
#             "information technology":  ["information technology", "bsit", "it", "bs information technology"],

#             # BUSINESS
#             "bba":                     ["bba", "business administration", "business"],
#             "business administration": ["business administration", "bba", "business"],
#             "finance":                 ["finance", "bba finance", "business finance"],

#             # MEDICAL
#             "mbbs":                    ["mbbs", "medicine", "medical"],
#             "bds":                     ["bds", "dentistry", "dental"],
#             "nursing":                 ["nursing", "bsn", "bs nursing"],

#             # SOCIAL SCIENCE
#             "psychology":              ["psychology", "bs psychology"],
#             "sociology":               ["sociology", "bs sociology"],
#         }

#         candidates = canonical_map.get(v)
#         return candidates if candidates else [v]

#     # ============================================================
#     # DATE NORMALIZATION
#     # ============================================================

#     def normalize_date(self, value):
#         if not value:
#             return value

#         input_formats = [
#             "%Y-%m-%d",    # 2000-01-25  ← DB format
#             "%Y %m %d",    # 2000 01 25
#             "%Y/%m/%d",    # 2000/01/25
#             "%d-%m-%Y",    # 25-01-2000
#             "%d/%m/%Y",    # 25/01/2000
#             "%d %m %Y",    # 25 01 2000
#             "%m/%d/%Y",    # 01/25/2000
#             "%m-%d-%Y",    # 01-25-2000
#             "%d %b %Y",    # 25 Jan 2000
#             "%d %B %Y",    # 25 January 2000
#             "%B %d, %Y",   # January 25, 2000
#             "%b %d, %Y",   # Jan 25, 2000
#         ]

#         dt = None
#         for fmt in input_formats:
#             try:
#                 dt = datetime.strptime(str(value).strip(), fmt)
#                 break
#             except:
#                 continue

#         if not dt:
#             return {
#                 "iso":       value,
#                 "dmy":       value,
#                 "dmy_dash":  value,
#                 "dmy_slash": value,
#                 "mdy":       value,
#                 "long":      value,
#                 "dt":        None,
#                 "day":       "",
#                 "month":     "",
#                 "year":      ""
#             }

#         return {
#             "iso":       dt.strftime("%Y-%m-%d"),   # 2000-01-25
#             "dmy":       dt.strftime("%d %m %Y"),   # 25 01 2000
#             "dmy_dash":  dt.strftime("%d-%m-%Y"),   # 25-01-2000
#             "dmy_slash": dt.strftime("%d/%m/%Y"),   # 25/01/2000
#             "mdy":       dt.strftime("%m/%d/%Y"),   # 01/25/2000
#             "long":      dt.strftime("%d %b %Y"),   # 25 Jan 2000
#             "dt":        dt,
#             "day":       dt.strftime("%d"),          # 25
#             "month":     dt.strftime("%m"),          # 01
#             "year":      dt.strftime("%Y"),          # 2000
#         }

#     # ============================================================
#     # DETECT IF PAGE IS REACT
#     # ============================================================

#     def is_react_page(self, driver):
#         return driver.execute_script(
#             "return !!(window.__REACT_DEVTOOLS_GLOBAL_HOOK__ || "
#             "document.querySelector('[data-reactroot]') || "
#             "document.querySelector('#root'))"
#         )

#     # ============================================================
#     # DETECT DATE FORMAT FROM PORTAL FIELD
#     # ============================================================

#     def detect_date_format(self, element):
#         placeholder = (element.get_attribute("placeholder") or "").lower().strip()
#         pattern     = (element.get_attribute("pattern") or "").lower().strip()
#         data_format = (element.get_attribute("data-format") or "").lower().strip()
#         hint        = " ".join([placeholder, pattern, data_format])

#         print(f"📅 Date field hint: '{hint.strip()}'")

#         if any(x in hint for x in ["dd-mm-yyyy", "dd/mm/yyyy", "dd mm yyyy"]):
#             if "/" in placeholder:
#                 return "dmy_slash"
#             return "dmy_dash"

#         if any(x in hint for x in ["mm/dd/yyyy", "mm-dd-yyyy"]):
#             return "mdy"

#         if any(x in hint for x in ["yyyy-mm-dd", "yyyy/mm/dd"]):
#             return "iso"

#         return None

#     # ============================================================
#     # REACT NATIVE INPUT VALUE SETTER (core trick)
#     # ============================================================

#     def react_set_value(self, driver, element, value):
#         """
#         Sets value on a React-controlled input/textarea by using the native
#         setter before React wrapped it, then fires input + change events.
#         """
#         driver.execute_script("""
#             var el  = arguments[0];
#             var val = arguments[1];

#             // Pick correct prototype — textarea vs input
#             var proto = el.tagName.toLowerCase() === 'textarea'
#                 ? window.HTMLTextAreaElement.prototype
#                 : window.HTMLInputElement.prototype;

#             var nativeSetter = Object.getOwnPropertyDescriptor(proto, 'value').set;
#             nativeSetter.call(el, val);
#             el.dispatchEvent(new Event('input',  { bubbles: true }));
#             el.dispatchEvent(new Event('change', { bubbles: true }));
#         """, element, value)

#     # ============================================================
#     # FILL DATE — REACT PAGE
#     # ============================================================

#     def fill_date_react(self, driver, element, formats):
#         input_type = (element.get_attribute("type") or "").lower()
#         fmt_key    = self.detect_date_format(element)

#         print(f"📅 React date → input_type='{input_type}' fmt_key='{fmt_key}'")

#         # ---- Native <input type="date"> in React ----
#         if input_type == "date":
#             self.fill_react_native_date(driver, element, formats, fmt_key)
#             return

#         # ---- Text-based masked date input in React ----
#         # Determine format to send
#         # Priority: placeholder hint → dmy_dash default (DD-MM-YYYY)
#         # because Pakistani portals almost universally use this
#         if fmt_key:
#             formatted = formats.get(fmt_key, formats["dmy_dash"])
#         else:
#             formatted = formats["dmy_dash"]

#         print(f"📅 React masked date → sending: '{formatted}'")

#         # Step 1: Focus the field
#         driver.execute_script("arguments[0].click();", element)
#         time.sleep(0.2)

#         # Step 2: Select all + delete to clear React state properly
#         element.send_keys(Keys.CONTROL + "a")
#         time.sleep(0.1)
#         element.send_keys(Keys.DELETE)
#         time.sleep(0.1)

#         # Step 3: Try nativeInputValueSetter first
#         self.react_set_value(driver, element, formatted)
#         time.sleep(0.2)

#         current = element.get_attribute("value")
#         print(f"📅 After nativeSetter: '{current}'")

#         if current and current != "":
#             return

#         # Step 4: Clipboard paste fallback
#         if PYPERCLIP_AVAILABLE:
#             try:
#                 pyperclip.copy(formatted)
#                 element.send_keys(Keys.CONTROL + "v")
#                 time.sleep(0.3)
#                 current = element.get_attribute("value")
#                 print(f"📅 After clipboard paste: '{current}'")
#                 if current and current != "":
#                     return
#             except Exception as e:
#                 print(f"📅 Clipboard paste failed: {e}")

#         # Step 5: Character by character (last resort)
#         print(f"📅 Typing char by char: '{formatted}'")
#         driver.execute_script("arguments[0].click();", element)
#         element.send_keys(Keys.CONTROL + "a")
#         element.send_keys(Keys.DELETE)
#         time.sleep(0.1)
#         for char in formatted:
#             element.send_keys(char)
#             time.sleep(0.05)

#         final = element.get_attribute("value")
#         print(f"📅 Final value: '{final}'")

#     # ============================================================
#     # FILL REACT NATIVE DATE INPUT <input type="date">
#     # ============================================================

#     def fill_react_native_date(self, driver, element, formats, fmt_key):
#         iso = formats["iso"]  # YYYY-MM-DD — what native date inputs store

#         # Try nativeInputValueSetter with ISO
#         self.react_set_value(driver, element, iso)
#         time.sleep(0.2)

#         current = element.get_attribute("value")
#         print(f"📅 React native date after nativeSetter: '{current}'")

#         if current == iso:
#             return

#         # Fallback: slot-by-slot keyboard fill
#         # Chrome's native date input slot order: MM → DD → YYYY
#         day   = formats["day"]
#         month = formats["month"]
#         year  = formats["year"]

#         driver.execute_script("arguments[0].click();", element)
#         time.sleep(0.2)

#         element.send_keys(month)   # fills MM slot
#         time.sleep(0.1)
#         element.send_keys(day)     # fills DD slot (auto-advances)
#         time.sleep(0.1)
#         element.send_keys(year)    # fills YYYY slot (auto-advances)
#         time.sleep(0.1)

#         final = element.get_attribute("value")
#         print(f"📅 React native date after slot-fill: '{final}'")

#     # ============================================================
#     # FILL NATIVE HTML DATE INPUT (non-React)
#     # ============================================================

#     def fill_native_date(self, driver, element, formats):
#         iso = formats["iso"]

#         driver.execute_script("arguments[0].value = arguments[1];", element, iso)
#         driver.execute_script(
#             "arguments[0].dispatchEvent(new Event('input',  {bubbles:true}));"
#             "arguments[0].dispatchEvent(new Event('change', {bubbles:true}));",
#             element
#         )

#         current = element.get_attribute("value")
#         if current == iso:
#             print(f"📅 Native date set via JS: {iso}")
#             return

#         element.clear()
#         element.send_keys(iso)
#         print(f"📅 Native date set via send_keys: {iso}")

#     # ============================================================
#     # FILL CUSTOM DATE PICKER (non-React text input)
#     # ============================================================

#     def fill_custom_date(self, driver, element, formats):
#         fmt_key = self.detect_date_format(element)

#         if fmt_key:
#             formatted = formats.get(fmt_key, formats["dmy_dash"])
#             print(f"📅 Custom date → {fmt_key} → {formatted}")
#             element.clear()
#             time.sleep(0.2)
#             element.send_keys(formatted)
#         else:
#             print(f"📅 No hint — probing formats...")
#             for key in ["dmy_dash", "dmy_slash", "dmy", "iso", "mdy"]:
#                 candidate = formats.get(key)
#                 if not candidate:
#                     continue
#                 element.clear()
#                 time.sleep(0.2)
#                 element.send_keys(candidate)
#                 time.sleep(0.3)
#                 current = element.get_attribute("value")
#                 if current and current != "":
#                     print(f"📅 Probe succeeded: '{key}' → {candidate}")
#                     return

#             # JS inject fallback
#             driver.execute_script("arguments[0].value = arguments[1];", element, formats["dmy_dash"])
#             driver.execute_script(
#                 "arguments[0].dispatchEvent(new Event('input',  {bubbles:true}));"
#                 "arguments[0].dispatchEvent(new Event('change', {bubbles:true}));",
#                 element
#             )

#         final = element.get_attribute("value")
#         print(f"📅 Custom date final value: '{final}'")

#     # ============================================================
#     # MAIN RUNNER
#     # ============================================================

#     def run(self, mapping):

#         url   = mapping.get("url")
#         steps = mapping.get("steps", [])

#         if not url:
#             return {"status": "failed", "message": "No URL provided"}

#         options = Options()
#         options.add_argument("--start-maximized")

#         driver = webdriver.Chrome(options=options)
#         driver.get(url)

#         completed_steps = 0

#         try:
#             for step in steps:

#                 action = step.get("action")

#                 # ====================================================
#                 # FILL ACTION
#                 # ====================================================
#                 if action == "fill":

#                     for field in step.get("fields", []):

#                         selector   = field.get("selector")
#                         field_type = field.get("type", "text")
#                         raw_value  = field.get("value")

#                         value = self.normalize_value(selector, raw_value)

#                         print(f"🧠 Filling {selector} → {value}")

#                         try:
#                             element = self.wait_for_element(driver, selector)

#                             driver.execute_script(
#                                 "arguments[0].scrollIntoView({block:'center'});",
#                                 element
#                             )

#                             self.fill_field(driver, element, field_type, value)

#                             print(f"✅ Filled {selector}")
#                             time.sleep(0.3)

#                         except Exception as e:
#                             print(f"❌ FAILED FIELD: {selector} → {e}")
#                             driver.quit()
#                             return {
#                                 "status": "failed",
#                                 "message": f"Error filling {selector}",
#                                 "error": str(e),
#                                 "completed_steps": completed_steps
#                             }

#                     completed_steps += 1

#                 # ====================================================
#                 # CLICK / SUBMIT
#                 # ====================================================
#                 elif action in ["click", "submit"]:

#                     try:
#                         element = self.wait_for_element(
#                             driver,
#                             step.get("selector"),
#                             clickable=True
#                         )

#                         driver.execute_script("arguments[0].click();", element)
#                         time.sleep(step.get("wait_ms", 2000) / 1000)

#                         if action == "submit":
#                             return {
#                                 "status": "success",
#                                 "message": "Form submitted successfully",
#                                 "completed_steps": completed_steps + 1
#                             }

#                         completed_steps += 1

#                     except Exception as e:
#                         driver.quit()
#                         return {
#                             "status": "failed",
#                             "message": f"{action} failed",
#                             "error": str(e),
#                             "completed_steps": completed_steps
#                         }

#             driver.quit()
#             return {"status": "success", "completed_steps": completed_steps}

#         except Exception as e:
#             driver.quit()
#             return {"status": "failed", "error": str(e)}

#     # ============================================================
#     # ELEMENT HANDLER
#     # ============================================================

#     def wait_for_element(self, driver, selector, timeout=10, clickable=False):

#         wait = WebDriverWait(driver, timeout)
#         by   = By.CSS_SELECTOR

#         if selector.startswith("#"):
#             by       = By.ID
#             selector = selector[1:]

#         elif selector.startswith("//"):
#             by = By.XPATH

#         elif selector.startswith("[name="):
#             by       = By.NAME
#             selector = selector.split("'")[1]

#         # ✅ FIX: handle button:contains('...') and *:contains('...')
#         elif ":contains(" in selector:
#             # Extract tag and text — e.g. "button:contains('Next')" → tag=button, text=Next
#             import re
#             match = re.match(r"^(\w+)?:contains\(['\"](.+?)['\"]\)$", selector.strip())
#             if match:
#                 tag  = match.group(1) or "*"
#                 text = match.group(2)
#                 # Convert to XPath
#                 selector = f"//{tag}[normalize-space(.)='{text}']"
#             else:
#                 # Fallback: search any element containing the text
#                 text = selector.split(":contains(")[1].strip("'\")")
#                 selector = f"//*[normalize-space(.)='{text}']"
#             by = By.XPATH

#         if clickable:
#             return wait.until(EC.element_to_be_clickable((by, selector)))

#         return wait.until(EC.presence_of_element_located((by, selector)))

#         # ============================================================
#     # FIELD FILLING
#     # ============================================================

#     def fill_field(self, driver, element, field_type, value):

#         tag        = element.tag_name.lower()
#         input_type = (element.get_attribute("type") or "").lower()
#         is_react   = self.is_react_page(driver)

#         # ---------------- CHECKBOX / RADIO ----------------
#         if input_type in ["checkbox", "radio"]:
#             if str(value).lower() in ["true", "1", "yes"]:
#                 driver.execute_script("arguments[0].click();", element)
#             return

#         # ---------------- DATE ROUTING ----------------
#         if field_type == "date" or input_type == "date":
#             formats = self.normalize_date(value)

#             if not formats.get("dt"):
#                 element.clear()
#                 element.send_keys(str(value))
#                 return

#             if is_react:
#                 self.fill_date_react(driver, element, formats)
#             elif input_type == "date":
#                 fmt_key = self.detect_date_format(element)
#                 if fmt_key and fmt_key != "iso":
#                     self.fill_custom_date(driver, element, formats)
#                 else:
#                     self.fill_native_date(driver, element, formats)
#             else:
#                 self.fill_custom_date(driver, element, formats)

#             return

#         # ---------------- SELECT DROPDOWN ----------------
#         if tag == "select":
#             select    = Select(element)
#             options   = [opt.text.strip() for opt in select.options]
#             opt_lower = [opt.lower() for opt in options]

#             candidates = self.normalize_course(value)
#             print(f"🔍 Dropdown candidates: {candidates}")
#             print(f"🔍 Available options:   {options}")

#             for target in candidates:
#                 t = target.lower().strip()

#                 # 1. Exact match
#                 for i, opt in enumerate(opt_lower):
#                     if opt == t:
#                         select.select_by_visible_text(options[i])
#                         print(f"✅ Exact match: {options[i]}")
#                         return

#                 # 2. Option is substring of candidate
#                 for i, opt in enumerate(opt_lower):
#                     if opt and opt in t:
#                         select.select_by_visible_text(options[i])
#                         print(f"✅ Reverse-contains: {options[i]}")
#                         return

#                 # 3. Candidate is substring of option
#                 for i, opt in enumerate(opt_lower):
#                     if t and t in opt:
#                         select.select_by_visible_text(options[i])
#                         print(f"✅ Contains: {options[i]}")
#                         return

#                 # 4. Word-level overlap
#                 target_words = set(t.split())
#                 for i, opt in enumerate(opt_lower):
#                     if target_words & set(opt.split()):
#                         select.select_by_visible_text(options[i])
#                         print(f"✅ Word-overlap: {options[i]}")
#                         return

#             raise Exception(
#                 f"Dropdown option not found for value: '{value}'. "
#                 f"Available: {options}"
#             )

#         # ---------------- TEXT / TEXTAREA ----------------
#         if tag in ["input", "textarea"]:
#             if is_react:
#                 self.react_set_value(driver, element, str(value))
#             else:
#                 element.clear()
#                 element.send_keys(str(value))
#             return

#         # ---------------- FALLBACK ----------------
#         driver.execute_script("arguments[0].value = arguments[1];", element, value)

# besttttttttttt

# """
# apply_pipline/services.py  —  COMPLETE FIXED VERSION

# Fixes in this version:
#   1. File upload: use send_keys(abs_path) only, never clear() or react_set_value
#   2. wait_for_element: file inputs use presence_of_element_located (not clickable)
#   3. wait_for_element: :contains() now uses XPath contains() with lowercase translate
#      so "Submit Application", "SUBMIT", "  Submit  " all match
#   4. Submit fallback: if selector fails, scans all visible buttons and clicks the
#      best match — logs what buttons are on screen to help debug
#   5. Screenshot on submit failure saved to MEDIA_ROOT/screenshots/
#   6. AIService.extract_fields: file inputs included with accept attribute
#   7. AIService prompt: explicit file-field mapping rules for Gemini
#   8. resolve_file_path: resolves relative paths via MEDIA_ROOT then BASE_DIR
# """

# import hashlib
# import time
# import os
# import re
# import json
# from pathlib import Path
# from datetime import datetime

# from bs4 import BeautifulSoup

# from django.conf import settings

# from selenium import webdriver
# from selenium.webdriver.chrome.options import Options
# from selenium.webdriver.common.by import By
# from selenium.webdriver.common.keys import Keys
# from selenium.webdriver.support.ui import Select, WebDriverWait
# from selenium.webdriver.support import expected_conditions as EC
# from selenium.common.exceptions import TimeoutException, NoSuchElementException

# from langchain_google_genai import ChatGoogleGenerativeAI
# from langchain_core.prompts import ChatPromptTemplate
# from langchain_core.output_parsers import PydanticOutputParser

# from .schemas import AutomationResponse

# try:
#     import pyperclip
#     PYPERCLIP_AVAILABLE = True
# except ImportError:
#     PYPERCLIP_AVAILABLE = False


# # ============================================================
# # AI SERVICE  —  scrapes form + generates mapping via Gemini
# # ============================================================

# class AIService:
#     """
#     Scrapes the multi-step form from a portal URL,
#     then uses Gemini to generate field mappings including file uploads.
#     """

#     def __init__(self):
#         api_key = getattr(settings, 'GEMINI_API_KEY', None)
#         if not api_key:
#             raise ValueError(
#                 "GEMINI_API_KEY not set in Django settings. "
#                 "Add GEMINI_API_KEY to settings.py."
#             )

#         self.llm = ChatGoogleGenerativeAI(
#             model="gemini-2.5-flash",
#             google_api_key=api_key,
#             temperature=0,
#         )
#         self.parser = PydanticOutputParser(pydantic_object=AutomationResponse)

#     # ------------------------------------------------------------------
#     # Stable App ID
#     # ------------------------------------------------------------------
#     @staticmethod
#     def make_app_id(student_id: int, url: str) -> int:
#         raw = f"{student_id}:{url}"
#         return int(hashlib.md5(raw.encode()).hexdigest()[:8], 16) % 999999 + 1

#     # ------------------------------------------------------------------
#     # Extract form fields — includes file inputs
#     # ------------------------------------------------------------------
#     def extract_fields(self, driver):
#         """
#         Extracts all form fields from the current page.
#         FILE inputs are included — they are essential for document upload mapping.
#         """
#         soup = BeautifulSoup(driver.page_source, "html.parser")
#         elements = []

#         for el in soup.find_all(["input", "select", "textarea"]):
#             # Only skip truly hidden inputs (type=hidden), NOT file inputs
#             if el.get("type") == "hidden":
#                 continue

#             el_type = el.get("type", "text").lower()

#             # Build the best selector we can
#             selector = None
#             if el.get("id"):
#                 selector = f"#{el.get('id')}"
#             elif el.get("name"):
#                 selector = f"[name='{el.get('name')}']"
#             elif el.get("data-testid"):
#                 selector = f"[data-testid='{el.get('data-testid')}']"

#             if not selector:
#                 continue

#             field_info = {
#                 "selector": selector,
#                 "type": el_type,
#                 "label": el.get("placeholder", el.get("aria-label", el.get("name", ""))),
#             }

#             # For file inputs, capture accept attribute so Gemini knows what file type is expected
#             if el_type == "file":
#                 field_info["accept"] = el.get("accept", "")  # e.g. ".pdf,image/*"

#             elements.append(field_info)

#         return elements

#     # ------------------------------------------------------------------
#     # Login handler
#     # ------------------------------------------------------------------
#     def handle_login(self, driver):
#         """Attempts to log in if a login page is detected."""
#         try:
#             email_el    = driver.find_element(By.XPATH, "//input[@type='email']")
#             password_el = driver.find_element(By.XPATH, "//input[@type='password']")

#             print("🔐 Login detected → logging in...")

#             portal_email    = getattr(settings, "PORTAL_EMAIL", "")
#             portal_password = getattr(settings, "PORTAL_PASSWORD", "")

#             if not portal_email or not portal_password:
#                 print("⚠️  PORTAL_EMAIL or PORTAL_PASSWORD not set in settings")
#                 return

#             email_el.send_keys(portal_email)
#             password_el.send_keys(portal_password)

#             login_btn = driver.find_element(
#                 By.XPATH,
#                 "//button[contains(text(),'Login') or contains(text(),'Sign in') or contains(text(),'login')]"
#             )
#             driver.execute_script("arguments[0].click();", login_btn)
#             time.sleep(3)

#         except (NoSuchElementException, Exception):
#             print("✅ No login page detected")

#     # ------------------------------------------------------------------
#     # Scrape multi-step form
#     # ------------------------------------------------------------------
#     def scrape_multi_step_form(self, url):
#         """
#         Opens the URL, handles login, and scrapes all form steps.
#         Returns a list of steps, each containing form fields.
#         """
#         options = Options()
#         options.add_argument("--headless")
#         options.add_argument("--no-sandbox")
#         options.add_argument("--disable-dev-shm-usage")
#         options.add_argument("--window-size=1920,1080")

#         driver     = None
#         all_steps  = []

#         try:
#             driver = webdriver.Chrome(options=options)
#             driver.get(url)
#             wait = WebDriverWait(driver, 10)

#             self.handle_login(driver)

#             try:
#                 wait.until(EC.presence_of_element_located((By.TAG_NAME, "input")))
#             except TimeoutException:
#                 print("⚠️  No input fields found")
#                 return []

#             for step in range(10):
#                 print(f"🧭 Step {step + 1}")
#                 fields = self.extract_fields(driver)

#                 if fields:
#                     all_steps.append({
#                         "step_number": step + 1,
#                         "fields": fields
#                     })

#                 try:
#                     next_btn = driver.find_element(
#                         By.XPATH,
#                         "//button[contains(text(),'Next') or contains(text(),'next')]"
#                     )
#                     driver.execute_script("arguments[0].click();", next_btn)
#                     time.sleep(2)

#                 except NoSuchElementException:
#                     print("🚀 No Next button → trying submit...")
#                     try:
#                         driver.find_element(
#                             By.XPATH,
#                             "//button[contains(text(),'Submit') or contains(text(),'submit')]"
#                         )
#                         print("✅ Submit detected")
#                     except NoSuchElementException:
#                         print("❌ No submit button found")
#                     break

#             return all_steps

#         finally:
#             if driver:
#                 driver.quit()

#     # ------------------------------------------------------------------
#     # Main — generate mapping via Gemini
#     # ------------------------------------------------------------------
#     def get_automation_instructions(self, target_url, student_data, app_id):
#         """
#         Main entry point: scrapes form, then uses Gemini to generate mapping.
#         File fields are explicitly handled in the prompt.
#         """
#         steps_data = self.scrape_multi_step_form(target_url)

#         if not steps_data:
#             raise Exception("No form steps found after login")

#         system_prompt = """
# You are an expert at mapping student data to multi-step university application forms.

# Given:
# 1. Student data (name, email, DOB, GPA, and FILE PATHS like photo, cnic_image, transcript, etc.)
# 2. Form steps with field selectors, types, labels, and accept attributes
# 3. Target URL

# Generate a complete automation plan as STRICT JSON. No markdown. No backticks.

# RESPONSE FORMAT:
# {{
#   "application_id": {app_id},
#   "url": "{url}",
#   "steps": [
#     {{
#       "action": "fill",
#       "fields": [
#         {{"selector": "#name", "type": "text", "value": "John Doe", "confidence": 0.95}},
#         {{"selector": "#photo", "type": "file", "value": "/absolute/path/to/photo.jpg", "confidence": 0.90}}
#       ]
#     }},
#     {{
#       "action": "click",
#       "selector": "button:contains('Next')",
#       "wait_ms": 2000
#     }},
#     {{
#       "action": "submit",
#       "selector": "button:contains('Submit')",
#       "wait_ms": 3000
#     }}
#   ]
# }}

# CRITICAL RULES FOR FILE FIELDS:
# - When you see a field with "type": "file", you MUST map it to the matching file path from student data.
# - Common file field mappings:
#     * selector contains "photo", "picture", "image", "avatar" → use student_data.photo or student_data.profile_picture
#     * selector contains "cnic", "id_card", "national"        → use student_data.cnic_image or student_data.id_card
#     * selector contains "transcript", "result", "marks"      → use student_data.transcript or student_data.result_card
#     * selector contains "certificate", "degree"              → use student_data.degree_certificate
#     * selector contains "domicile"                           → use student_data.domicile
#     * selector contains "character", "conduct"               → use student_data.character_certificate
#     * selector contains "matric"                             → use student_data.matric_certificate or student_data.matric_result
#     * selector contains "inter", "fsc", "hssc"               → use student_data.inter_certificate or student_data.inter_result
# - The value for a file field must be the ABSOLUTE FILE PATH string from student data.
# - If no matching file exists in student data, set value to "" and confidence to 0.0.
# - NEVER skip file fields — always include them in the fill step.

# GENERAL RULES:
# - Each step is either "fill", "click", or "submit"
# - For "fill": provide ALL fields on that page, including file fields
# - For "click"/"submit": provide the selector only
# - Use the exact selectors provided
# - Set confidence to 0.0 if no match found
# - Return ONLY valid JSON, nothing else
# """

#         prompt = ChatPromptTemplate.from_messages([
#             ("system", system_prompt),
#             ("human",
#              "STUDENT DATA:\n{student_data}\n\n"
#              "FORM STEPS (includes file input fields):\n{steps_data}\n\n"
#              "URL: {url}\n\n"
#              "APP ID: {app_id}")
#         ])

#         chain = prompt | self.llm | self.parser

#         try:
#             result = chain.invoke({
#                 "student_data": json.dumps(student_data, indent=2),
#                 "steps_data":   json.dumps(steps_data, indent=2),
#                 "url":          target_url,
#                 "app_id":       app_id,
#             })
#             return result
#         except Exception as e:
#             print(f"❌ LLM parsing failed: {e}")
#             raise


# # ============================================================
# # AUTOMATION SERVICE  —  drives browser using the mapping
# # ============================================================

# class AutomationService:

#     # ============================================================
#     # NORMALIZATION
#     # ============================================================

#     def normalize_value(self, field_name, value):
#         if not value:
#             return value

#         value = str(value).strip()

#         city_map = {
#             "lahore":    "Punjab",
#             "karachi":   "Sindh",
#             "islamabad": "Islamabad",
#             "peshawar":  "KPK",
#             "quetta":    "Balochistan"
#         }

#         if field_name and "province" in field_name.lower():
#             return city_map.get(value.lower(), value)

#         return value

#     def normalize_course(self, value):
#         if not value:
#             return []

#         v = str(value).lower().strip()

#         canonical_map = {
#             "llb":                     ["llb", "law", "bachelor of law", "legal"],
#             "law":                     ["law", "llb", "legal studies", "legal"],
#             "cs":                      ["cs", "computer science", "bscs"],
#             "bscs":                    ["bscs", "computer science", "cs"],
#             "computer science":        ["computer science", "cs", "bscs"],
#             "bsse":                    ["bsse", "software engineering", "software"],
#             "software engineering":    ["software engineering", "bsse", "software"],
#             "bsit":                    ["bsit", "information technology", "it", "bs information technology", "bs (it)"],
#             "it":                      ["it", "information technology", "bsit"],
#             "information technology":  ["information technology", "bsit", "it", "bs information technology"],
#             "bba":                     ["bba", "business administration", "business"],
#             "business administration": ["business administration", "bba", "business"],
#             "finance":                 ["finance", "bba finance", "business finance"],
#             "mbbs":                    ["mbbs", "medicine", "medical"],
#             "bds":                     ["bds", "dentistry", "dental"],
#             "nursing":                 ["nursing", "bsn", "bs nursing"],
#             "psychology":              ["psychology", "bs psychology"],
#             "sociology":               ["sociology", "bs sociology"],
#         }

#         candidates = canonical_map.get(v)
#         return candidates if candidates else [v]

#     def normalize_date(self, value):
#         if not value:
#             return value

#         input_formats = [
#             "%Y-%m-%d", "%Y %m %d", "%Y/%m/%d",
#             "%d-%m-%Y", "%d/%m/%Y", "%d %m %Y",
#             "%m/%d/%Y", "%m-%d-%Y",
#             "%d %b %Y", "%d %B %Y",
#             "%B %d, %Y", "%b %d, %Y",
#         ]

#         dt = None
#         for fmt in input_formats:
#             try:
#                 dt = datetime.strptime(str(value).strip(), fmt)
#                 break
#             except Exception:
#                 continue

#         if not dt:
#             return {
#                 "iso": value, "dmy": value, "dmy_dash": value,
#                 "dmy_slash": value, "mdy": value, "long": value,
#                 "dt": None, "day": "", "month": "", "year": ""
#             }

#         return {
#             "iso":       dt.strftime("%Y-%m-%d"),
#             "dmy":       dt.strftime("%d %m %Y"),
#             "dmy_dash":  dt.strftime("%d-%m-%Y"),
#             "dmy_slash": dt.strftime("%d/%m/%Y"),
#             "mdy":       dt.strftime("%m/%d/%Y"),
#             "long":      dt.strftime("%d %b %Y"),
#             "dt":        dt,
#             "day":       dt.strftime("%d"),
#             "month":     dt.strftime("%m"),
#             "year":      dt.strftime("%Y"),
#         }

#     # ============================================================
#     # REACT DETECTION
#     # ============================================================

#     def is_react_page(self, driver):
#         return driver.execute_script(
#             "return !!(window.__REACT_DEVTOOLS_GLOBAL_HOOK__ || "
#             "document.querySelector('[data-reactroot]') || "
#             "document.querySelector('#root'))"
#         )

#     # ============================================================
#     # DATE HELPERS
#     # ============================================================

#     def detect_date_format(self, element):
#         placeholder = (element.get_attribute("placeholder") or "").lower().strip()
#         pattern     = (element.get_attribute("pattern") or "").lower().strip()
#         data_format = (element.get_attribute("data-format") or "").lower().strip()
#         hint        = " ".join([placeholder, pattern, data_format])

#         print(f"📅 Date field hint: '{hint.strip()}'")

#         if any(x in hint for x in ["dd-mm-yyyy", "dd/mm/yyyy", "dd mm yyyy"]):
#             return "dmy_slash" if "/" in placeholder else "dmy_dash"
#         if any(x in hint for x in ["mm/dd/yyyy", "mm-dd-yyyy"]):
#             return "mdy"
#         if any(x in hint for x in ["yyyy-mm-dd", "yyyy/mm/dd"]):
#             return "iso"
#         return None

#     def react_set_value(self, driver, element, value):
#         """
#         Sets value on a React-controlled input/textarea by bypassing
#         React's synthetic event system using the native setter.
#         """
#         driver.execute_script("""
#             var el  = arguments[0];
#             var val = arguments[1];
#             var proto = el.tagName.toLowerCase() === 'textarea'
#                 ? window.HTMLTextAreaElement.prototype
#                 : window.HTMLInputElement.prototype;
#             var nativeSetter = Object.getOwnPropertyDescriptor(proto, 'value').set;
#             nativeSetter.call(el, val);
#             el.dispatchEvent(new Event('input',  { bubbles: true }));
#             el.dispatchEvent(new Event('change', { bubbles: true }));
#         """, element, value)

#     def fill_date_react(self, driver, element, formats):
#         input_type = (element.get_attribute("type") or "").lower()
#         fmt_key    = self.detect_date_format(element)

#         print(f"📅 React date → input_type='{input_type}' fmt_key='{fmt_key}'")

#         if input_type == "date":
#             self.fill_react_native_date(driver, element, formats, fmt_key)
#             return

#         formatted = formats.get(fmt_key, formats["dmy_dash"]) if fmt_key else formats["dmy_dash"]
#         print(f"📅 React masked date → sending: '{formatted}'")

#         driver.execute_script("arguments[0].click();", element)
#         time.sleep(0.2)
#         element.send_keys(Keys.CONTROL + "a")
#         time.sleep(0.1)
#         element.send_keys(Keys.DELETE)
#         time.sleep(0.1)

#         self.react_set_value(driver, element, formatted)
#         time.sleep(0.2)

#         current = element.get_attribute("value")
#         if current and current != "":
#             return

#         if PYPERCLIP_AVAILABLE:
#             try:
#                 pyperclip.copy(formatted)
#                 element.send_keys(Keys.CONTROL + "v")
#                 time.sleep(0.3)
#                 if element.get_attribute("value"):
#                     return
#             except Exception as e:
#                 print(f"📅 Clipboard paste failed: {e}")

#         driver.execute_script("arguments[0].click();", element)
#         element.send_keys(Keys.CONTROL + "a")
#         element.send_keys(Keys.DELETE)
#         time.sleep(0.1)
#         for char in formatted:
#             element.send_keys(char)
#             time.sleep(0.05)

#     def fill_react_native_date(self, driver, element, formats, fmt_key):
#         iso = formats["iso"]
#         self.react_set_value(driver, element, iso)
#         time.sleep(0.2)

#         if element.get_attribute("value") == iso:
#             return

#         driver.execute_script("arguments[0].click();", element)
#         time.sleep(0.2)
#         element.send_keys(formats["month"])
#         time.sleep(0.1)
#         element.send_keys(formats["day"])
#         time.sleep(0.1)
#         element.send_keys(formats["year"])
#         time.sleep(0.1)

#     def fill_native_date(self, driver, element, formats):
#         iso = formats["iso"]
#         driver.execute_script("arguments[0].value = arguments[1];", element, iso)
#         driver.execute_script(
#             "arguments[0].dispatchEvent(new Event('input',  {bubbles:true}));"
#             "arguments[0].dispatchEvent(new Event('change', {bubbles:true}));",
#             element
#         )
#         if element.get_attribute("value") != iso:
#             element.clear()
#             element.send_keys(iso)

#     def fill_custom_date(self, driver, element, formats):
#         fmt_key = self.detect_date_format(element)
#         if fmt_key:
#             formatted = formats.get(fmt_key, formats["dmy_dash"])
#             element.clear()
#             time.sleep(0.2)
#             element.send_keys(formatted)
#         else:
#             for key in ["dmy_dash", "dmy_slash", "dmy", "iso", "mdy"]:
#                 candidate = formats.get(key)
#                 if not candidate:
#                     continue
#                 element.clear()
#                 time.sleep(0.2)
#                 element.send_keys(candidate)
#                 time.sleep(0.3)
#                 if element.get_attribute("value"):
#                     return
#             driver.execute_script("arguments[0].value = arguments[1];", element, formats["dmy_dash"])
#             driver.execute_script(
#                 "arguments[0].dispatchEvent(new Event('input',  {bubbles:true}));"
#                 "arguments[0].dispatchEvent(new Event('change', {bubbles:true}));",
#                 element
#             )

#     # ============================================================
#     # FILE PATH RESOLUTION
#     # ============================================================

#     def resolve_file_path(self, value):
#         """
#         Resolves a file path value to an absolute path that Selenium can use.
#         Handles:
#           - Already-absolute paths  (/home/... or C:\\...)
#           - Django MEDIA_ROOT relative paths  (media/documents/photo.jpg)
#           - Bare filenames  (photo.jpg)
#         Raises FileNotFoundError if the file cannot be found.
#         """
#         if not value:
#             raise ValueError("File path is empty")

#         path = str(value).strip()

#         # 1. Already absolute and exists
#         if os.path.isabs(path) and os.path.isfile(path):
#             return path

#         # 2. Relative to MEDIA_ROOT (most common Django pattern)
#         media_root = getattr(settings, "MEDIA_ROOT", "")
#         if media_root:
#             # Strip leading /media/ prefix if already included in path
#             clean = path.lstrip("/\\")
#             if clean.startswith("media/") or clean.startswith("media\\"):
#                 clean = clean[6:]  # remove "media/" prefix — MEDIA_ROOT already points there
#             candidate = os.path.join(str(media_root), clean)
#             if os.path.isfile(candidate):
#                 return os.path.abspath(candidate)

#         # 3. Relative to BASE_DIR
#         base_dir = getattr(settings, "BASE_DIR", "")
#         if base_dir:
#             candidate = os.path.join(str(base_dir), path.lstrip("/\\"))
#             if os.path.isfile(candidate):
#                 return os.path.abspath(candidate)

#         # 4. Absolute attempt (remove leading slash and try again on Windows)
#         abs_attempt = os.path.abspath(path)
#         if os.path.isfile(abs_attempt):
#             return abs_attempt

#         raise FileNotFoundError(
#             f"File not found: '{value}'. "
#             f"Tried: MEDIA_ROOT='{media_root}', BASE_DIR='{base_dir}'"
#         )

#     # ============================================================
#     # SCREENSHOT HELPER
#     # ============================================================

#     def take_screenshot(self, driver, name="screenshot"):
#         """Saves a screenshot to MEDIA_ROOT/screenshots/ and returns the path."""
#         try:
#             media_root = getattr(settings, "MEDIA_ROOT", "")
#             if media_root:
#                 folder = Path(str(media_root)) / "screenshots"
#             else:
#                 folder = Path("screenshots")
#             folder.mkdir(parents=True, exist_ok=True)
#             path = folder / f"{name}_{int(time.time())}.png"
#             driver.save_screenshot(str(path))
#             print(f"📸 Screenshot saved: {path}")
#             return str(path)
#         except Exception as e:
#             print(f"⚠️  Screenshot failed: {e}")
#             return None

#     # ============================================================
#     # SUBMIT BUTTON FALLBACK
#     # ============================================================

#     def find_submit_button(self, driver):
#         """
#         Scans all visible buttons on the page and returns the best
#         submit candidate. Logs what it finds to help debugging.
#         """
#         # Collect all buttons and input[type=submit]
#         candidates = driver.find_elements(
#             By.XPATH,
#             "//button | //input[@type='submit']"
#         )

#         visible = []
#         for btn in candidates:
#             try:
#                 if btn.is_displayed():
#                     text = (btn.text or btn.get_attribute("value") or "").strip()
#                     visible.append((btn, text))
#             except Exception:
#                 pass

#         if not visible:
#             print("❌ No visible buttons found on page")
#             return None

#         print(f"🔍 Visible buttons on page: {[t for _, t in visible]}")

#         # Priority keywords (case-insensitive)
#         priority = ["submit", "apply", "finish", "done", "complete", "send"]

#         for keyword in priority:
#             for btn, text in visible:
#                 if keyword in text.lower():
#                     print(f"✅ Fallback submit button found: '{text}'")
#                     return btn

#         # Last resort: return the last visible button (usually submit)
#         btn, text = visible[-1]
#         print(f"⚠️  Using last visible button as submit fallback: '{text}'")
#         return btn

#     # ============================================================
#     # MAIN RUNNER
#     # ============================================================

#     def run(self, mapping):
#         url   = mapping.get("url")
#         steps = mapping.get("steps", [])

#         if not url:
#             return {"status": "failed", "message": "No URL provided"}

#         options = Options()
#         options.add_argument("--start-maximized")

#         driver = webdriver.Chrome(options=options)
#         driver.get(url)

#         completed_steps = 0

#         try:
#             for step in steps:
#                 action = step.get("action")

#                 # ====================================================
#                 # FILL ACTION
#                 # ====================================================
#                 if action == "fill":
#                     for field in step.get("fields", []):
#                         selector   = field.get("selector")
#                         field_type = (field.get("type") or "text").lower()
#                         raw_value  = field.get("value")

#                         # Skip empty non-file fields
#                         if (raw_value is None or raw_value == "") and field_type != "file":
#                             print(f"⏭️  Skipping empty field: {selector}")
#                             continue

#                         # Skip file fields with no path
#                         if field_type == "file" and not raw_value:
#                             print(f"⏭️  No file path for {selector}, skipping")
#                             continue

#                         value = self.normalize_value(selector, raw_value)

#                         print(f"🧠 Filling [{field_type}] {selector} → {value}")

#                         try:
#                             element = self.wait_for_element(
#                                 driver,
#                                 selector,
#                                 # FILE inputs must NOT use clickable wait —
#                                 # they are often hidden/invisible but still accept send_keys
#                                 clickable=(field_type != "file")
#                             )

#                             # Only scroll non-file elements
#                             if field_type != "file":
#                                 driver.execute_script(
#                                     "arguments[0].scrollIntoView({block:'center'});",
#                                     element
#                                 )

#                             self.fill_field(driver, element, field_type, value)
#                             print(f"✅ Filled {selector}")
#                             time.sleep(0.3)

#                         except Exception as e:
#                             print(f"❌ FAILED FIELD: {selector} → {e}")
#                             self.take_screenshot(driver, f"fail_field_{selector.strip('#[]')}")
#                             driver.quit()
#                             return {
#                                 "status": "failed",
#                                 "message": f"Error filling {selector}",
#                                 "error": str(e),
#                                 "completed_steps": completed_steps
#                             }

#                     completed_steps += 1

#                 # ====================================================
#                 # CLICK / SUBMIT
#                 # ====================================================
#                 elif action in ["click", "submit"]:
#                     selector = step.get("selector")
#                     wait_ms  = step.get("wait_ms", 2000)

#                     try:
#                         element = self.wait_for_element(driver, selector, clickable=True)
#                     except Exception as primary_err:
#                         print(f"⚠️  Primary selector failed: '{selector}' → {primary_err}")

#                         if action == "submit":
#                             # ── SUBMIT FALLBACK ──────────────────────────────
#                             print("🔄 Trying submit button fallback scan...")
#                             self.take_screenshot(driver, "before_submit_fallback")
#                             element = self.find_submit_button(driver)

#                             if not element:
#                                 self.take_screenshot(driver, "submit_no_button_found")
#                                 driver.quit()
#                                 return {
#                                     "status": "failed",
#                                     "message": "Submit button not found (primary + fallback both failed)",
#                                     "error": str(primary_err),
#                                     "completed_steps": completed_steps
#                                 }
#                         else:
#                             # For non-submit clicks, fail immediately
#                             driver.quit()
#                             return {
#                                 "status": "failed",
#                                 "message": f"click failed — element not found: '{selector}'",
#                                 "error": str(primary_err),
#                                 "completed_steps": completed_steps
#                             }

#                     try:
#                         driver.execute_script("arguments[0].scrollIntoView({block:'center'});", element)
#                         time.sleep(0.3)
#                         driver.execute_script("arguments[0].click();", element)
#                         time.sleep(wait_ms / 1000)

#                         if action == "submit":
#                             self.take_screenshot(driver, "submit_success")
#                             driver.quit()
#                             return {
#                                 "status": "success",
#                                 "message": "Form submitted successfully",
#                                 "completed_steps": completed_steps + 1
#                             }

#                         completed_steps += 1

#                     except Exception as click_err:
#                         self.take_screenshot(driver, f"fail_{action}")
#                         driver.quit()
#                         return {
#                             "status": "failed",
#                             "message": f"{action} element found but click failed",
#                             "error": str(click_err),
#                             "completed_steps": completed_steps
#                         }

#             driver.quit()
#             return {"status": "success", "completed_steps": completed_steps}

#         except Exception as e:
#             self.take_screenshot(driver, "unexpected_error")
#             driver.quit()
#             return {"status": "failed", "error": str(e)}

#     # ============================================================
#     # ELEMENT WAITER — :contains() uses XPath contains() with
#     # lowercase translate so text matching is case-insensitive
#     # and partial (handles "Submit Application", "SUBMIT", etc.)
#     # ============================================================

#     def wait_for_element(self, driver, selector, timeout=10, clickable=False):
#         wait = WebDriverWait(driver, timeout)
#         by   = By.CSS_SELECTOR

#         if selector.startswith("#"):
#             by       = By.ID
#             selector = selector[1:]

#         elif selector.startswith("//"):
#             by = By.XPATH

#         elif selector.startswith("[name="):
#             by       = By.NAME
#             selector = selector.split("'")[1]

#         elif ":contains(" in selector:
#             match = re.match(r"^(\w+)?:contains\(['\"](.+?)['\"]\)$", selector.strip())
#             if match:
#                 tag  = match.group(1) or "*"
#                 text = match.group(2).lower()
#                 # ✅ KEY FIX: contains() + translate() for case-insensitive partial match
#                 # Handles: "Submit", "SUBMIT", "Submit Application", "  Submit  "
#                 selector = (
#                     f"//{tag}[contains("
#                     f"translate(normalize-space(.), "
#                     f"'ABCDEFGHIJKLMNOPQRSTUVWXYZ', "
#                     f"'abcdefghijklmnopqrstuvwxyz'), "
#                     f"'{text}')]"
#                 )
#             else:
#                 # Fallback for malformed :contains()
#                 text = selector.split(":contains(")[1].strip("'\")")
#                 selector = (
#                     f"//*[contains("
#                     f"translate(normalize-space(.), "
#                     f"'ABCDEFGHIJKLMNOPQRSTUVWXYZ', "
#                     f"'abcdefghijklmnopqrstuvwxyz'), "
#                     f"'{text.lower()}')]"
#                 )
#             by = By.XPATH

#         if clickable:
#             return wait.until(EC.element_to_be_clickable((by, selector)))

#         return wait.until(EC.presence_of_element_located((by, selector)))

#     # ============================================================
#     # FIELD FILLING — file upload handled first before all else
#     # ============================================================

#     def fill_field(self, driver, element, field_type, value):
#         tag        = element.tag_name.lower()
#         input_type = (element.get_attribute("type") or "").lower()
#         is_react   = self.is_react_page(driver)

#         # --------------------------------------------------------
#         # FILE UPLOAD — must be first, before any other branch.
#         # NEVER call .clear(), react_set_value, or JS .value setter
#         # on a file input — browsers block all of these for security.
#         # send_keys(absolute_path) is the ONLY valid approach.
#         # --------------------------------------------------------
#         if field_type == "file" or input_type == "file":
#             try:
#                 abs_path = self.resolve_file_path(value)
#             except (FileNotFoundError, ValueError) as e:
#                 raise Exception(f"File upload failed — {e}")

#             print(f"📎 Uploading file: {abs_path}")

#             # Make hidden file inputs interactable (common pattern in portals)
#             driver.execute_script("""
#                 arguments[0].style.display    = 'block';
#                 arguments[0].style.opacity    = '1';
#                 arguments[0].style.visibility = 'visible';
#             """, element)
#             time.sleep(0.2)

#             # send_keys is the ONLY correct way to interact with file inputs
#             element.send_keys(abs_path)

#             # Fire change event so React/Angular/Vue pick up the new file
#             driver.execute_script(
#                 "arguments[0].dispatchEvent(new Event('change', {bubbles: true}));",
#                 element
#             )
#             print(f"✅ File uploaded: {os.path.basename(abs_path)}")
#             return

#         # --------------------------------------------------------
#         # CHECKBOX / RADIO
#         # --------------------------------------------------------
#         if input_type in ["checkbox", "radio"]:
#             if str(value).lower() in ["true", "1", "yes"]:
#                 driver.execute_script("arguments[0].click();", element)
#             return

#         # --------------------------------------------------------
#         # DATE ROUTING
#         # --------------------------------------------------------
#         if field_type == "date" or input_type == "date":
#             formats = self.normalize_date(value)

#             if not formats.get("dt"):
#                 element.clear()
#                 element.send_keys(str(value))
#                 return

#             if is_react:
#                 self.fill_date_react(driver, element, formats)
#             elif input_type == "date":
#                 fmt_key = self.detect_date_format(element)
#                 if fmt_key and fmt_key != "iso":
#                     self.fill_custom_date(driver, element, formats)
#                 else:
#                     self.fill_native_date(driver, element, formats)
#             else:
#                 self.fill_custom_date(driver, element, formats)
#             return

#         # --------------------------------------------------------
#         # SELECT DROPDOWN
#         # --------------------------------------------------------
#         if tag == "select":
#             select     = Select(element)
#             options    = [opt.text.strip() for opt in select.options]
#             opt_lower  = [opt.lower() for opt in options]
#             candidates = self.normalize_course(value)

#             print(f"🔍 Dropdown candidates: {candidates}")
#             print(f"🔍 Available options:   {options}")

#             for target in candidates:
#                 t = target.lower().strip()

#                 # 1. Exact match
#                 for i, opt in enumerate(opt_lower):
#                     if opt == t:
#                         select.select_by_visible_text(options[i])
#                         print(f"✅ Exact match: {options[i]}")
#                         return

#                 # 2. Option is substring of candidate
#                 for i, opt in enumerate(opt_lower):
#                     if opt and opt in t:
#                         select.select_by_visible_text(options[i])
#                         print(f"✅ Reverse-contains: {options[i]}")
#                         return

#                 # 3. Candidate is substring of option
#                 for i, opt in enumerate(opt_lower):
#                     if t and t in opt:
#                         select.select_by_visible_text(options[i])
#                         print(f"✅ Contains: {options[i]}")
#                         return

#                 # 4. Word-level overlap
#                 target_words = set(t.split())
#                 for i, opt in enumerate(opt_lower):
#                     if target_words & set(opt.split()):
#                         select.select_by_visible_text(options[i])
#                         print(f"✅ Word-overlap: {options[i]}")
#                         return

#             raise Exception(
#                 f"Dropdown option not found for value: '{value}'. "
#                 f"Available: {options}"
#             )

#         # --------------------------------------------------------
#         # TEXT / TEXTAREA
#         # --------------------------------------------------------
#         if tag in ["input", "textarea"]:
#             if is_react:
#                 self.react_set_value(driver, element, str(value))
#             else:
#                 element.clear()
#                 element.send_keys(str(value))
#             return

#         # --------------------------------------------------------
#         # FALLBACK — JS value injection
#         # --------------------------------------------------------
#         driver.execute_script("arguments[0].value = arguments[1];", element, value)
#         driver.execute_script(
#             "arguments[0].dispatchEvent(new Event('change', {bubbles:true}));",
#             element
#         )



# """
# automation_pipeline/services.py  —  COMPLETE VERSION

# KEY CHANGE FROM PREVIOUS VERSION:
#   The scraper now captures the login page fields (email + password) and maps
#   them to the logged-in user's portal credentials (PORTAL_EMAIL / PORTAL_PASSWORD).
#   The automation then replays the ENTIRE flow from scratch — login step first,
#   then all application form steps — using only the mapping JSON.

#   This means:
#     - No separate _portal_login() pre-step in automation
#     - No duplicate login logic split between scraper and runner
#     - The mapping JSON is self-contained: give it to AutomationService.run()
#       and it handles login + all form steps in sequence

#   How login scraping works:
#     1. Scraper opens the URL.
#     2. If a password field is detected → scrape those fields, mark step as
#        action="login", then click login and wait for the form to appear.
#     3. Gemini receives the login fields AND the application form fields.
#     4. Gemini maps PORTAL_EMAIL → email field, PORTAL_PASSWORD → password field.
#     5. Automation replays: fill login → click login → fill step 1 → next → ...
# """

# import hashlib
# import time
# import os
# import re
# import json
# from pathlib import Path
# from datetime import datetime

# from bs4 import BeautifulSoup

# from django.conf import settings

# from selenium import webdriver
# from selenium.webdriver.chrome.options import Options
# from selenium.webdriver.common.by import By
# from selenium.webdriver.common.keys import Keys
# from selenium.webdriver.support.ui import Select, WebDriverWait
# from selenium.webdriver.support import expected_conditions as EC
# from selenium.common.exceptions import TimeoutException, NoSuchElementException

# from langchain_google_genai import ChatGoogleGenerativeAI
# from langchain_core.prompts import ChatPromptTemplate
# from langchain_core.output_parsers import PydanticOutputParser

# from .schemas import AutomationResponse

# try:
#     import pyperclip
#     PYPERCLIP_AVAILABLE = True
# except ImportError:
#     PYPERCLIP_AVAILABLE = False


# # ─────────────────────────────────────────────────────────────────────────────
# # Constants
# # ─────────────────────────────────────────────────────────────────────────────

# NEXT_KEYWORDS = [
#     "next", "continue", "proceed", "forward",
#     "آگے", "اگلا", "اگلہ",
#     "next step", "next page", "save & next", "save and next", "save & continue",
# ]
# SUBMIT_KEYWORDS = [
#     "submit", "finish", "complete", "send", "apply",
#     "جمع کریں", "submit application", "final submit",
# ]
# LOGIN_KEYWORDS = ["login", "log in", "sign in", "signin", "لاگ ان"]
# NEXT_ID_HINTS  = ["next", "continue", "proceed", "forward", "step"]

# REACT_STEP_TIMEOUT  = 8
# REACT_POLL_INTERVAL = 0.25


# # ─────────────────────────────────────────────────────────────────────────────
# # Smart button finders
# # ─────────────────────────────────────────────────────────────────────────────

# def _btn_text(driver, el):
#     """Full textContent via JS — catches text inside child <span> nodes."""
#     try:
#         return (driver.execute_script("return arguments[0].textContent;", el) or "").strip()
#     except Exception:
#         return (el.text or "").strip()


# def _find_button_by_keywords(driver, keywords):
#     """
#     Generic button finder. Tries in order:
#       1. id/name/class contains a keyword
#       2. textContent contains a keyword
#       3. aria-label contains a keyword
#     Returns WebElement or None.
#     """
#     all_btns = driver.find_elements(
#         By.CSS_SELECTOR, "button, input[type='submit'], a[role='button']"
#     )

#     # Strategy 1: attribute hint
#     for kw in keywords:
#         for el in driver.find_elements(
#             By.CSS_SELECTOR,
#             f"button[id*='{kw}'], button[name*='{kw}'], button[class*='{kw}'], "
#             f"input[type='submit'][id*='{kw}'], a[id*='{kw}']"
#         ):
#             if el.is_displayed() and el.is_enabled():
#                 return el

#     # Strategy 2: textContent
#     for el in all_btns:
#         if not (el.is_displayed() and el.is_enabled()):
#             continue
#         text = _btn_text(driver, el).lower()
#         if any(kw in text for kw in keywords):
#             return el

#     # Strategy 3: aria-label
#     for el in all_btns:
#         if not (el.is_displayed() and el.is_enabled()):
#             continue
#         label = (el.get_attribute("aria-label") or "").lower()
#         if any(kw in label for kw in keywords):
#             return el

#     return None


# def _find_next_button(driver):
#     btn = _find_button_by_keywords(driver, NEXT_KEYWORDS)
#     if btn:
#         print(f"🔍 Next btn: {_btn_text(driver, btn)!r}")
#         return btn
#     # Heuristic: last visible non-back button
#     ignore = {"back", "previous", "cancel", "reset", "واپس", "پچھلا"}
#     all_btns = driver.find_elements(By.CSS_SELECTOR, "button, input[type='submit']")
#     visible  = [
#         el for el in all_btns
#         if el.is_displayed() and el.is_enabled()
#         and not any(x in _btn_text(driver, el).lower() for x in ignore)
#     ]
#     if visible:
#         el = visible[-1]
#         print(f"🔍 Next btn (last-button heuristic): {_btn_text(driver, el)!r}")
#         return el
#     print("⚠️  No Next button found")
#     return None


# def _find_submit_button(driver):
#     btn = _find_button_by_keywords(driver, SUBMIT_KEYWORDS)
#     if btn:
#         print(f"🔍 Submit btn: {_btn_text(driver, btn)!r}")
#         return btn
#     all_btns = driver.find_elements(By.CSS_SELECTOR, "button, input[type='submit']")
#     visible  = [e for e in all_btns if e.is_displayed() and e.is_enabled()]
#     if visible:
#         print(f"🔍 Submit btn (last fallback): {_btn_text(driver, visible[-1])!r}")
#         return visible[-1]
#     return None


# def _find_login_button(driver):
#     btn = _find_button_by_keywords(driver, LOGIN_KEYWORDS)
#     if btn:
#         print(f"🔍 Login btn: {_btn_text(driver, btn)!r}")
#         return btn
#     # Fallback: the only submit button on a login page
#     all_btns = driver.find_elements(
#         By.CSS_SELECTOR, "button[type='submit'], input[type='submit']"
#     )
#     visible = [e for e in all_btns if e.is_displayed() and e.is_enabled()]
#     if visible:
#         print(f"🔍 Login btn (submit fallback): {_btn_text(driver, visible[0])!r}")
#         return visible[0]
#     return None


# # ─────────────────────────────────────────────────────────────────────────────
# # DOM change detection
# # ─────────────────────────────────────────────────────────────────────────────

# def _wait_for_react_hydration(driver, timeout=15):
#     deadline = time.time() + timeout
#     while time.time() < deadline:
#         try:
#             root = driver.find_elements(By.CSS_SELECTOR, "#root, #app, [data-reactroot]")
#             container = root[0] if root else driver.find_element(By.TAG_NAME, "body")
#             inputs = container.find_elements(
#                 By.CSS_SELECTOR, "input:not([type='hidden']), select, textarea"
#             )
#             if any(el.is_displayed() for el in inputs):
#                 return True
#         except Exception:
#             pass
#         time.sleep(REACT_POLL_INTERVAL)
#     return False


# def _get_visible_field_count(driver):
#     try:
#         els = driver.find_elements(
#             By.CSS_SELECTOR, "input:not([type='hidden']), select, textarea"
#         )
#         return len([e for e in els if e.is_displayed()])
#     except Exception:
#         return 0


# def _wait_for_dom_change(driver, prev_count, prev_url, timeout=REACT_STEP_TIMEOUT):
#     deadline = time.time() + timeout
#     while time.time() < deadline:
#         try:
#             if driver.current_url != prev_url:
#                 time.sleep(0.5)
#                 _wait_for_react_hydration(driver, timeout=5)
#                 return True
#             count = _get_visible_field_count(driver)
#             if count != prev_count and count > 0:
#                 time.sleep(0.3)
#                 return True
#         except Exception:
#             pass
#         time.sleep(REACT_POLL_INTERVAL)
#     return False


# def _is_login_page(driver):
#     """Returns True if the current page has a visible password field."""
#     try:
#         pwd = driver.find_elements(By.XPATH, "//input[@type='password']")
#         return any(el.is_displayed() for el in pwd)
#     except Exception:
#         return False


# # ─────────────────────────────────────────────────────────────────────────────
# # Screenshot helpers
# # ─────────────────────────────────────────────────────────────────────────────

# def _screenshots_dir(app_id) -> Path:
#     d = Path(settings.MEDIA_ROOT) / "screenshots" / str(app_id)
#     d.mkdir(parents=True, exist_ok=True)
#     return d


# def _take_screenshot(driver, app_id, step_index: int, label: str) -> dict:
#     d        = _screenshots_dir(app_id)
#     filename = f"step_{step_index:02d}_{label}.png"
#     filepath = d / filename
#     try:
#         driver.save_screenshot(str(filepath))
#         print(f"📸 {filepath}")
#     except Exception as e:
#         print(f"⚠️  Screenshot failed: {e}")
#         return {}
#     return {
#         "step":     step_index,
#         "label":    label,
#         "filename": filename,
#         "url":      f"{settings.MEDIA_URL}screenshots/{app_id}/{filename}",
#     }


# def _save_manifest(app_id, entries: list):
#     path = _screenshots_dir(app_id) / "manifest.json"
#     with open(path, "w") as f:
#         json.dump({"app_id": app_id, "screenshots": [e for e in entries if e]}, f, indent=2)


# # ─────────────────────────────────────────────────────────────────────────────
# # Field extraction helper (shared by scraper)
# # ─────────────────────────────────────────────────────────────────────────────

# def _extract_fields_from_page(driver, include_password=False):
#     """
#     Extracts all visible form fields from the current page.
#     include_password=True is used when scraping the login page.
#     include_password=False (default) skips password fields on form pages.
#     """
#     soup     = BeautifulSoup(driver.page_source, "html.parser")
#     elements = []

#     for el in soup.find_all(["input", "select", "textarea"]):
#         el_type = el.get("type", "text").lower() if el.name == "input" else el.name

#         if el_type == "hidden":
#             continue
#         if el_type == "password" and not include_password:
#             continue

#         if el.get("id"):
#             selector = f"#{el.get('id')}"
#         elif el.get("name"):
#             selector = f"[name='{el.get('name')}']"
#         elif el.get("data-testid"):
#             selector = f"[data-testid='{el.get('data-testid')}']"
#         else:
#             continue

#         # Prefer <label for="..."> text, then fall back to placeholder/aria-label
#         label = ""
#         if el.get("id"):
#             lbl = soup.find("label", attrs={"for": el.get("id")})
#             if lbl:
#                 label = lbl.get_text(strip=True)
#         if not label:
#             label = el.get("placeholder") or el.get("aria-label") or el.get("name") or ""

#         entry = {"selector": selector, "type": el_type, "label": label}
#         if el_type == "file":
#             entry["accept"] = el.get("accept", "")
#         if el.name == "select":
#             entry["options"] = [
#                 o.get_text(strip=True) for o in el.find_all("option")
#                 if o.get_text(strip=True)
#             ]
#         elements.append(entry)

#     return elements


# # ─────────────────────────────────────────────────────────────────────────────
# # AI SERVICE
# # ─────────────────────────────────────────────────────────────────────────────

# class AIService:

#     def __init__(self):
#         api_key = getattr(settings, "GEMINI_API_KEY", None)
#         if not api_key:
#             raise ValueError("GEMINI_API_KEY not set in Django settings.")
#         self.llm = ChatGoogleGenerativeAI(
#             model="gemini-2.5-flash",
#             google_api_key=api_key,
#             temperature=0,
#         )
#         self.parser = PydanticOutputParser(pydantic_object=AutomationResponse)

#     @staticmethod
#     def make_app_id(student_id, url: str) -> int:
#         raw = f"{student_id}:{url}"
#         return int(hashlib.md5(raw.encode()).hexdigest()[:8], 16) % 999999 + 1

#     # ------------------------------------------------------------------
#     # Scrape entire flow: login page (if present) + all form steps
#     # ------------------------------------------------------------------
#     def scrape_full_flow(self, url):
#         """
#         Opens the URL and scrapes:
#           - If a login page is detected: scrapes login fields, performs login,
#             waits for the application form to appear, then scrapes all form steps.
#           - If no login page: scrapes all form steps directly.

#         Returns a list of page dicts:
#           [
#             { "page_type": "login",       "page_number": 0, "fields": [...] },
#             { "page_type": "application", "page_number": 1, "fields": [...] },
#             { "page_type": "application", "page_number": 2, "fields": [...] },
#             ...
#           ]

#         Each page includes the login button / next button / submit button
#         selector so Gemini can emit the correct click/submit actions.
#         """
#         options = Options()
#         options.add_argument("--headless=new")   # full V8 for React
#         options.add_argument("--no-sandbox")
#         options.add_argument("--disable-dev-shm-usage")
#         options.add_argument("--window-size=1920,1080")

#         driver = None
#         pages  = []

#         try:
#             driver = webdriver.Chrome(options=options)
#             driver.get(url)

#             # Wait for initial render
#             _wait_for_react_hydration(driver, timeout=15)

#             # ── LOGIN PAGE ──────────────────────────────────────────────
#             if _is_login_page(driver):
#                 print("🔐 Login page detected during scraping")

#                 # Scrape login fields INCLUDING password
#                 login_fields = _extract_fields_from_page(driver, include_password=True)

#                 # Find the login button and record its selector
#                 login_btn       = _find_login_button(driver)
#                 login_btn_sel   = None
#                 if login_btn:
#                     btn_id = login_btn.get_attribute("id")
#                     login_btn_sel = f"#{btn_id}" if btn_id else "LOGIN_BUTTON"

#                 pages.append({
#                     "page_type":    "login",
#                     "page_number":  0,
#                     "fields":       login_fields,
#                     "submit_selector": login_btn_sel or "LOGIN_BUTTON",
#                 })
#                 print(f"   Scraped {len(login_fields)} login fields")
                
#                 # Perform login so we can scrape the real form pages
#                 portal_email = "student"
#                 portal_password = "au2024"

#                 if portal_email and portal_password and login_btn:
#                     try:
#                         # Fill credentials
#                         try:
#                             email_el = driver.find_element(By.XPATH, "//input[@type='email']")
#                         except NoSuchElementException:
#                             email_el = driver.find_element(By.XPATH, "//input[@type='text']")
#                         pass_el = driver.find_element(By.XPATH, "//input[@type='password']")
#                         email_el.send_keys(portal_email)
#                         pass_el.send_keys(portal_password)
#                         driver.execute_script("arguments[0].click();", login_btn)

#                         # Wait for login to complete (password field disappears)
#                         WebDriverWait(driver, 15).until(
#                             EC.invisibility_of_element_located(
#                                 (By.XPATH, "//input[@type='password']")
#                             )
#                         )
#                         print("✅ Scraping login succeeded — waiting for form...")
#                         time.sleep(2)
#                         _wait_for_react_hydration(driver, timeout=10)
#                     except Exception as e:
#                         print(f"⚠️  Scraping login failed: {e} — form pages may be incomplete")
#                 else:
#                     print("⚠️  PORTAL_EMAIL/PORTAL_PASSWORD not set or no login button found")

#             # ── APPLICATION FORM PAGES ──────────────────────────────────
#             for step_num in range(1, 11):
#                 print(f"\n🧭 Scraping application page {step_num}...")
#                 time.sleep(0.5)

#                 # Skip if still on login page
#                 if _is_login_page(driver):
#                     print("   Still on login page — login may have failed")
#                     break

#                 fields = _extract_fields_from_page(driver, include_password=False)
#                 print(f"   {len(fields)} fields found")

#                 prev_count = _get_visible_field_count(driver)
#                 prev_url   = driver.current_url

#                 # Find the next/submit button and record its selector too
#                 next_btn   = _find_next_button(driver)
#                 submit_btn = _find_submit_button(driver) if not next_btn else None

#                 next_sel   = None
#                 submit_sel = None

#                 if next_btn:
#                     nid = next_btn.get_attribute("id")
#                     next_sel = f"#{nid}" if nid else "NEXT_BUTTON"
#                 if submit_btn and not next_btn:
#                     sid = submit_btn.get_attribute("id")
#                     submit_sel = f"#{sid}" if sid else "SUBMIT_BUTTON"

#                 pages.append({
#                     "page_type":       "application",
#                     "page_number":     step_num,
#                     "fields":          fields,
#                     "next_selector":   next_sel,
#                     "submit_selector": submit_sel,
#                 })

#                 if not next_btn:
#                     print("   ✅ No Next button — end of form")
#                     break

#                 try:
#                     driver.execute_script(
#                         "arguments[0].scrollIntoView({block:'center'});", next_btn)
#                     driver.execute_script("arguments[0].click();", next_btn)
#                     print("   ▶ Clicked Next — waiting for DOM change...")
#                     changed = _wait_for_dom_change(driver, prev_count, prev_url)
#                     if not changed:
#                         print("   ⚠️  DOM didn't change — may be last step")
#                         break
#                 except Exception as e:
#                     print(f"   ❌ Error clicking Next: {e}")
#                     break

#             return pages

#         finally:
#             if driver:
#                 driver.quit()

#     # ------------------------------------------------------------------
#     # Generate mapping via Gemini
#     # ------------------------------------------------------------------
#     def get_automation_instructions(self, target_url, student_data, app_id):
#         """
#         Scrapes the full portal flow (login + form pages), then asks Gemini
#         to produce a complete mapping including the login step.
#         """
#         pages = self.scrape_full_flow(target_url)
#         if not pages:
#             raise Exception("No pages found — check the portal URL")

#         portal_email    = getattr(settings, "PORTAL_EMAIL", "")
#         portal_password = getattr(settings, "PORTAL_PASSWORD", "")

#         # Inject portal credentials into student_data so Gemini can map them
#         student_data_with_creds = {
#             **student_data,
#             "_portal_email":    portal_email,
#             "_portal_password": portal_password,
#         }

#         system_prompt = """
# You are an expert at mapping student data to multi-page university portal flows.

# The pages list includes:
#   - A "login" page (page_type="login") if the portal requires authentication
#   - One or more "application" pages (page_type="application")

# You must generate a COMPLETE automation plan that covers ALL pages in order:
#   1. Fill login credentials → click login button → wait for form
#   2. Fill application step 1 → click Next → ...
#   3. Fill last step → submit

# Return ONLY valid JSON (no markdown, no backticks). Example structure:

# {{
#   "application_id": <integer>,
#   "url": "<target url>",
#   "steps": [
#     {{
#       "action": "fill",
#       "page_type": "login",
#       "fields": [
#         {{"selector": "#email",    "type": "email",    "value": "<_portal_email value>",    "confidence": 1.0}},
#         {{"selector": "#password", "type": "password", "value": "<_portal_password value>", "confidence": 1.0}}
#       ]
#     }},
#     {{
#       "action": "login_click",
#       "selector": "<submit_selector from login page, or LOGIN_BUTTON>",
#       "wait_ms": 3000
#     }},
#     {{
#       "action": "fill",
#       "page_type": "application",
#       "fields": [
#         {{"selector": "#name", "type": "text", "value": "Ali Khan", "confidence": 0.95}},
#         {{"selector": "#photo","type": "file", "value": "/abs/path/photo.jpg", "confidence": 0.9}}
#       ]
#     }},
#     {{"action": "click",  "selector": "NEXT_BUTTON",   "wait_ms": 2000}},
#     {{"action": "fill",   "page_type": "application", "fields": [...]}},
#     {{"action": "submit", "selector": "SUBMIT_BUTTON", "wait_ms": 3000}}
#   ]
# }}

# RULES:
# 1. LOGIN STEP:
#    - Map "_portal_email" → the email/username input field on the login page.
#    - Map "_portal_password" → the password input field on the login page.
#    - Use the exact selectors from the login page fields.
#    - The login click action must use "action": "login_click" so the automation
#      engine knows to wait for the password field to disappear after clicking.

# 2. CLICK / SUBMIT selectors:
#    - For click (Next) actions: use "NEXT_BUTTON" unless the page gave a specific
#      next_selector — in that case use the specific one.
#    - For submit: use "SUBMIT_BUTTON" unless the page gave a specific submit_selector.
#    - For login_click: use the submit_selector from the login page, or "LOGIN_BUTTON".
#    - NEVER invent button CSS selectors — the engine resolves these at runtime.

# 3. FILL selectors must be the exact strings from the scraped page fields.

# 4. FILE FIELDS:
#    photo/picture/avatar  → student.photo
#    cnic/id_card          → student.cnic_image
#    transcript/result     → student.transcript
#    matric                → student.matric_certificate
#    inter/fsc/hssc        → student.inter_certificate
#    domicile              → student.domicile
#    Set value="" and confidence=0.0 if no match.

# 5. confidence: 1.0=exact, 0.5=inferred, 0.0=no match.
# 6. Include ALL fields even if confidence is 0.
# 7. Return ONLY JSON.
# """

#         prompt = ChatPromptTemplate.from_messages([
#             ("system", system_prompt),
#             ("human",
#              "STUDENT DATA (includes _portal_email and _portal_password):\n{student_data}\n\n"
#              "SCRAPED PAGES (login + application steps):\n{pages_data}\n\n"
#              "URL: {url}\nAPP ID: {app_id}"),
#         ])

#         chain  = prompt | self.llm | self.parser
#         result = chain.invoke({
#             "student_data": json.dumps(student_data_with_creds, indent=2),
#             "pages_data":   json.dumps(pages, indent=2),
#             "url":          target_url,
#             "app_id":       app_id,
#         })
#         return result


# # ─────────────────────────────────────────────────────────────────────────────
# # AUTOMATION SERVICE
# # ─────────────────────────────────────────────────────────────────────────────

# class AutomationService:

#     # ── Normalization ──────────────────────────────────────────────────────

#     def normalize_value(self, field_name, value):
#         if not value:
#             return value
#         value    = str(value).strip()
#         city_map = {
#             "lahore": "Punjab", "karachi": "Sindh", "islamabad": "Islamabad",
#             "peshawar": "KPK",  "quetta": "Balochistan",
#         }
#         if field_name and "province" in field_name.lower():
#             return city_map.get(value.lower(), value)
#         return value

#     def normalize_course(self, value):
#         if not value:
#             return []
#         v = str(value).lower().strip()
#         m = {
#             "cs":                     ["cs","computer science","bscs"],
#             "bscs":                   ["bscs","computer science","cs"],
#             "computer science":       ["computer science","cs","bscs"],
#             "bsse":                   ["bsse","software engineering","software"],
#             "software engineering":   ["software engineering","bsse","software"],
#             "bsit":                   ["bsit","information technology","it","bs information technology","bs (it)"],
#             "it":                     ["it","information technology","bsit"],
#             "information technology": ["information technology","bsit","it","bs information technology"],
#             "bba":                    ["bba","business administration","business"],
#             "business administration":["business administration","bba","business"],
#             "finance":                ["finance","bba finance","business finance"],
#             "mbbs":                   ["mbbs","medicine","medical"],
#             "bds":                    ["bds","dentistry","dental"],
#             "nursing":                ["nursing","bsn","bs nursing"],
#             "psychology":             ["psychology","bs psychology"],
#             "sociology":              ["sociology","bs sociology"],
#             "llb":                    ["llb","law","bachelor of law","legal"],
#             "law":                    ["law","llb","legal studies","legal"],
#         }
#         return m.get(v, [v])

#     def normalize_date(self, value):
#         if not value:
#             return value
#         fmts = [
#             "%Y-%m-%d","%Y %m %d","%Y/%m/%d",
#             "%d-%m-%Y","%d/%m/%Y","%d %m %Y",
#             "%m/%d/%Y","%m-%d-%Y",
#             "%d %b %Y","%d %B %Y","%B %d, %Y","%b %d, %Y",
#         ]
#         dt = None
#         for fmt in fmts:
#             try: dt = datetime.strptime(str(value).strip(), fmt); break
#             except Exception: continue
#         if not dt:
#             return {"iso":value,"dmy":value,"dmy_dash":value,"dmy_slash":value,
#                     "mdy":value,"long":value,"dt":None,"day":"","month":"","year":""}
#         return {
#             "iso":       dt.strftime("%Y-%m-%d"),
#             "dmy":       dt.strftime("%d %m %Y"),
#             "dmy_dash":  dt.strftime("%d-%m-%Y"),
#             "dmy_slash": dt.strftime("%d/%m/%Y"),
#             "mdy":       dt.strftime("%m/%d/%Y"),
#             "long":      dt.strftime("%d %b %Y"),
#             "dt":        dt,
#             "day":       dt.strftime("%d"),
#             "month":     dt.strftime("%m"),
#             "year":      dt.strftime("%Y"),
#         }

#     # ── React helpers ──────────────────────────────────────────────────────

#     def is_react_page(self, driver):
#         return driver.execute_script(
#             "return !!(window.__REACT_DEVTOOLS_GLOBAL_HOOK__ || "
#             "document.querySelector('[data-reactroot]') || "
#             "document.querySelector('#root'))"
#         )

#     def react_set_value(self, driver, element, value):
#         driver.execute_script("""
#             var el = arguments[0], val = arguments[1];
#             var proto = el.tagName.toLowerCase() === 'textarea'
#                 ? window.HTMLTextAreaElement.prototype
#                 : window.HTMLInputElement.prototype;
#             Object.getOwnPropertyDescriptor(proto, 'value').set.call(el, val);
#             el.dispatchEvent(new Event('input',  { bubbles: true }));
#             el.dispatchEvent(new Event('change', { bubbles: true }));
#         """, element, value)

#     # ── Date helpers ───────────────────────────────────────────────────────

#     def detect_date_format(self, element):
#         hint = " ".join([
#             element.get_attribute("placeholder") or "",
#             element.get_attribute("pattern")     or "",
#             element.get_attribute("data-format") or "",
#         ]).lower()
#         if any(x in hint for x in ["dd-mm-yyyy","dd/mm/yyyy","dd mm yyyy"]):
#             return "dmy_slash" if "/" in hint else "dmy_dash"
#         if any(x in hint for x in ["mm/dd/yyyy","mm-dd-yyyy"]): return "mdy"
#         if "yyyy-mm-dd" in hint: return "iso"
#         return None

#     def fill_date_react(self, driver, element, formats):
#         input_type = (element.get_attribute("type") or "").lower()
#         fmt_key    = self.detect_date_format(element)
#         if input_type == "date":
#             self.fill_react_native_date(driver, element, formats, fmt_key); return
#         formatted = formats.get(fmt_key, formats["dmy_dash"]) if fmt_key else formats["dmy_dash"]
#         self.react_set_value(driver, element, formatted); time.sleep(0.2)
#         if element.get_attribute("value"): return
#         if PYPERCLIP_AVAILABLE:
#             try:
#                 pyperclip.copy(formatted)
#                 element.send_keys(Keys.CONTROL + "v"); time.sleep(0.3)
#                 if element.get_attribute("value"): return
#             except Exception: pass
#         driver.execute_script("arguments[0].click();", element)
#         element.send_keys(Keys.CONTROL + "a"); element.send_keys(Keys.DELETE)
#         for char in formatted: element.send_keys(char); time.sleep(0.04)

#     def fill_react_native_date(self, driver, element, formats, fmt_key):
#         self.react_set_value(driver, element, formats["iso"]); time.sleep(0.2)
#         if element.get_attribute("value") == formats["iso"]: return
#         driver.execute_script("arguments[0].click();", element)
#         element.send_keys(formats["month"]); time.sleep(0.1)
#         element.send_keys(formats["day"]);   time.sleep(0.1)
#         element.send_keys(formats["year"])

#     def fill_native_date(self, driver, element, formats):
#         iso = formats["iso"]
#         driver.execute_script("arguments[0].value = arguments[1];", element, iso)
#         driver.execute_script(
#             "arguments[0].dispatchEvent(new Event('input',{bubbles:true}));"
#             "arguments[0].dispatchEvent(new Event('change',{bubbles:true}));", element)
#         if element.get_attribute("value") != iso:
#             element.clear(); element.send_keys(iso)

#     def fill_custom_date(self, driver, element, formats):
#         fmt_key = self.detect_date_format(element)
#         if fmt_key:
#             element.clear(); time.sleep(0.2)
#             element.send_keys(formats.get(fmt_key, formats["dmy_dash"]))
#         else:
#             for key in ["dmy_dash","dmy_slash","dmy","iso","mdy"]:
#                 element.clear(); time.sleep(0.2)
#                 element.send_keys(formats.get(key,"")); time.sleep(0.3)
#                 if element.get_attribute("value"): return
#             driver.execute_script("arguments[0].value = arguments[1];", element, formats["dmy_dash"])
#             driver.execute_script(
#                 "arguments[0].dispatchEvent(new Event('input',{bubbles:true}));"
#                 "arguments[0].dispatchEvent(new Event('change',{bubbles:true}));", element)

#     # ── File path resolver ─────────────────────────────────────────────────

#     def resolve_file_path(self, value):
#         if not value:
#             raise ValueError("File path is empty")
#         path = str(value).strip()
#         if os.path.isabs(path) and os.path.isfile(path): return path
#         media_root = getattr(settings, "MEDIA_ROOT", "")
#         if media_root:
#             clean = path.lstrip("/\\")
#             if clean.startswith("media/") or clean.startswith("media\\"):
#                 clean = clean[6:]
#             candidate = os.path.join(str(media_root), clean)
#             if os.path.isfile(candidate): return os.path.abspath(candidate)
#         base_dir = getattr(settings, "BASE_DIR", "")
#         if base_dir:
#             candidate = os.path.join(str(base_dir), path.lstrip("/\\"))
#             if os.path.isfile(candidate): return os.path.abspath(candidate)
#         abs_attempt = os.path.abspath(path)
#         if os.path.isfile(abs_attempt): return abs_attempt
#         raise FileNotFoundError(
#             f"File not found: '{value}' — tried MEDIA_ROOT='{media_root}', BASE_DIR='{base_dir}'"
#         )

#     # ── wait_for_element ───────────────────────────────────────────────────

#     def wait_for_element(self, driver, selector, timeout=10, clickable=False):
#         # Magic smart-finder values
#         if selector in ("NEXT_BUTTON",  "next_button"):
#             deadline = time.time() + timeout
#             while time.time() < deadline:
#                 el = _find_next_button(driver)
#                 if el: return el
#                 time.sleep(REACT_POLL_INTERVAL)
#             raise TimeoutException("No Next button found")

#         if selector in ("SUBMIT_BUTTON", "submit_button"):
#             deadline = time.time() + timeout
#             while time.time() < deadline:
#                 el = _find_submit_button(driver)
#                 if el: return el
#                 time.sleep(REACT_POLL_INTERVAL)
#             raise TimeoutException("No Submit button found")

#         if selector in ("LOGIN_BUTTON", "login_button"):
#             deadline = time.time() + timeout
#             while time.time() < deadline:
#                 el = _find_login_button(driver)
#                 if el: return el
#                 time.sleep(REACT_POLL_INTERVAL)
#             raise TimeoutException("No Login button found")

#         # :contains() → case-insensitive XPath
#         if ":contains(" in selector:
#             match = re.match(r"^(\w+)?:contains\(['\"](.+?)['\"]\)$", selector.strip())
#             if match:
#                 tag, text = match.group(1) or "*", match.group(2).lower()
#             else:
#                 tag  = "*"
#                 text = selector.split(":contains(")[1].strip("'\")")
#             xpath = (
#                 f"//{tag}[contains("
#                 f"translate(normalize-space(.),"
#                 f"'ABCDEFGHIJKLMNOPQRSTUVWXYZ','abcdefghijklmnopqrstuvwxyz'),"
#                 f"'{text.lower()}')]"
#             )
#             wait = WebDriverWait(driver, timeout)
#             cond = EC.element_to_be_clickable if clickable else EC.presence_of_element_located
#             try:
#                 return wait.until(cond((By.XPATH, xpath)))
#             except TimeoutException:
#                 # Fall through to keyword-based smart finder
#                 fn = _find_login_button  if any(kw in selector.lower() for kw in LOGIN_KEYWORDS) \
#                      else _find_next_button if any(kw in selector.lower() for kw in NEXT_KEYWORDS) \
#                      else _find_submit_button
#                 el = fn(driver)
#                 if el: return el
#                 raise

#         # Standard selectors
#         wait = WebDriverWait(driver, timeout)
#         by   = By.CSS_SELECTOR
#         if selector.startswith("#"):
#             by, selector = By.ID, selector[1:]
#         elif selector.startswith("//"):
#             by = By.XPATH
#         elif selector.startswith("[name="):
#             by, selector = By.NAME, selector.split("'")[1]

#         # File inputs are invisible — always use presence
#         try:
#             el_type = driver.find_element(by, selector).get_attribute("type") or ""
#             if el_type == "file": clickable = False
#         except Exception:
#             pass

#         cond = EC.element_to_be_clickable if clickable else EC.presence_of_element_located
#         return wait.until(cond((by, selector)))

#     # ── fill_field ─────────────────────────────────────────────────────────

#     def fill_field(self, driver, element, field_type, value):
#         tag        = element.tag_name.lower()
#         input_type = (element.get_attribute("type") or "").lower()
#         is_react   = self.is_react_page(driver)

#         # FILE — send_keys only, never clear/value setter
#         if field_type == "file" or input_type == "file":
#             try:
#                 abs_path = self.resolve_file_path(value)
#             except (FileNotFoundError, ValueError) as e:
#                 raise Exception(f"File upload failed — {e}")
#             driver.execute_script("""
#                 arguments[0].style.display    = 'block';
#                 arguments[0].style.opacity    = '1';
#                 arguments[0].style.visibility = 'visible';
#             """, element)
#             time.sleep(0.2)
#             element.send_keys(abs_path)
#             driver.execute_script(
#                 "arguments[0].dispatchEvent(new Event('change',{bubbles:true}));", element)
#             print(f"✅ File: {os.path.basename(abs_path)}")
#             return

#         # PASSWORD — plain send_keys (never react_set_value; portals track state internally)
#         if input_type == "password":
#             element.clear()
#             element.send_keys(str(value))
#             return

#         # CHECKBOX / RADIO
#         if input_type in ["checkbox", "radio"]:
#             if str(value).lower() in ["true","1","yes"]:
#                 driver.execute_script("arguments[0].click();", element)
#             return

#         # DATE
#         if field_type == "date" or input_type == "date":
#             formats = self.normalize_date(value)
#             if not formats.get("dt"):
#                 element.clear(); element.send_keys(str(value)); return
#             if is_react:
#                 self.fill_date_react(driver, element, formats)
#             elif input_type == "date":
#                 fmt_key = self.detect_date_format(element)
#                 (self.fill_custom_date if (fmt_key and fmt_key != "iso") else self.fill_native_date)(
#                     driver, element, formats)
#             else:
#                 self.fill_custom_date(driver, element, formats)
#             return

#         # SELECT
#         if tag == "select":
#             sel     = Select(element)
#             options = [o.text.strip() for o in sel.options]
#             opt_low = [o.lower() for o in options]
#             for target in self.normalize_course(value):
#                 t = target.lower().strip()
#                 for i, opt in enumerate(opt_low):
#                     if opt == t:                           sel.select_by_visible_text(options[i]); return
#                 for i, opt in enumerate(opt_low):
#                     if opt and opt in t:                  sel.select_by_visible_text(options[i]); return
#                 for i, opt in enumerate(opt_low):
#                     if t and t in opt:                    sel.select_by_visible_text(options[i]); return
#                 for i, opt in enumerate(opt_low):
#                     if set(t.split()) & set(opt.split()): sel.select_by_visible_text(options[i]); return
#             raise Exception(f"Dropdown option not found for '{value}'. Available: {options}")

#         # TEXT / TEXTAREA / EMAIL
#         if tag in ["input", "textarea"]:
#             self.react_set_value(driver, element, str(value)) if is_react \
#                 else (element.clear() or element.send_keys(str(value)))
#             return

#         # FALLBACK
#         driver.execute_script("arguments[0].value = arguments[1];", element, value)
#         driver.execute_script(
#             "arguments[0].dispatchEvent(new Event('change',{bubbles:true}));", element)

#     # ── Main runner ────────────────────────────────────────────────────────

#     def run(self, mapping: dict) -> dict:
#         """
#         Executes the full automation flow from the mapping JSON.
#         Step types:
#           "fill"        — fill form fields (login page or application page)
#           "login_click" — click the login button and wait for form to load
#           "click"       — click Next button between application steps
#           "submit"      — click the final submit button
#         """
#         url    = mapping.get("url")
#         steps  = mapping.get("steps", [])
#         app_id = mapping.get("application_id", 0)

#         if not url:
#             return {"status":"failed","message":"No URL provided","screenshots":[]}

#         options = Options()
#         options.add_argument("--start-maximized")
#         # Uncomment to run headless:
#         # options.add_argument("--headless=new")

#         driver = webdriver.Chrome(options=options)
#         driver.get(url)
#         _wait_for_react_hydration(driver, timeout=15)

#         completed_steps = 0
#         screenshot_log  = []

#         def _snap(idx, label):
#             entry = _take_screenshot(driver, app_id, idx, label)
#             if entry: screenshot_log.append(entry)

#         try:
#             for step_idx, step in enumerate(steps, start=1):
#                 action = step.get("action")

#                 # ── FILL (login page or application page) ─────────────────
#                 if action == "fill":
#                     page_type = step.get("page_type", "application")
#                     print(f"\n📝 Fill step {step_idx} [{page_type}]")

#                     for field in step.get("fields", []):
#                         selector   = field.get("selector")
#                         field_type = (field.get("type") or "text").lower()
#                         raw_value  = field.get("value")

#                         if (raw_value is None or raw_value == "") and field_type != "file":
#                             continue
#                         if field_type == "file" and not raw_value:
#                             print(f"⏭️  No file path for {selector}")
#                             continue

#                         value = self.normalize_value(selector, raw_value)
#                         print(f"   🖊  [{field_type}] {selector} → {value!r}")

#                         try:
#                             element = self.wait_for_element(
#                                 driver, selector, clickable=(field_type != "file"))
#                             if field_type != "file":
#                                 driver.execute_script(
#                                     "arguments[0].scrollIntoView({block:'center'});", element)
#                             self.fill_field(driver, element, field_type, value)
#                             time.sleep(0.2)
#                         except Exception as e:
#                             print(f"   ❌ Failed {selector}: {e}")
#                             _snap(step_idx, f"error_fill_{page_type}_step{step_idx}")
#                             _save_manifest(app_id, screenshot_log)
#                             driver.quit()
#                             return {
#                                 "status":"failed","message":f"Error filling {selector}",
#                                 "error":str(e),"completed_steps":completed_steps,
#                                 "screenshots":screenshot_log,
#                             }

#                     _snap(step_idx, f"filled_{page_type}_step{step_idx}")
#                     completed_steps += 1

#                 # ── LOGIN CLICK — click login btn, wait for form to appear ──
#                 elif action == "login_click":
#                     selector = step.get("selector", "LOGIN_BUTTON")
#                     wait_ms  = step.get("wait_ms", 3000)
#                     print(f"\n🔐 Login click (selector: {selector!r})")

#                     element = None
#                     try:
#                         element = self.wait_for_element(driver, selector, clickable=True)
#                     except Exception as e:
#                         print(f"⚠️  Login button '{selector}' not found: {e}")
#                         element = _find_login_button(driver)

#                     if not element:
#                         _snap(step_idx, "error_login_button_not_found")
#                         _save_manifest(app_id, screenshot_log)
#                         driver.quit()
#                         return {
#                             "status":"failed","message":"Login button not found",
#                             "completed_steps":completed_steps,"screenshots":screenshot_log,
#                         }

#                     driver.execute_script("arguments[0].scrollIntoView({block:'center'});", element)
#                     driver.execute_script("arguments[0].click();", element)
#                     print("   ▶ Clicked login — waiting for password field to disappear...")

#                     # Wait for login to complete: password field disappears
#                     try:
#                         WebDriverWait(driver, 15).until(
#                             EC.invisibility_of_element_located(
#                                 (By.XPATH, "//input[@type='password']")
#                             )
#                         )
#                         print("   ✅ Login successful — form is now visible")
#                         time.sleep(1.5)
#                         _wait_for_react_hydration(driver, timeout=10)
#                     except TimeoutException:
#                         _snap(step_idx, "error_login_timeout")
#                         _save_manifest(app_id, screenshot_log)
#                         driver.quit()
#                         return {
#                             "status":"failed",
#                             "message":"Login timed out — password field never disappeared. Check credentials.",
#                             "completed_steps":completed_steps,"screenshots":screenshot_log,
#                         }

#                     _snap(step_idx, "after_login")
#                     completed_steps += 1

#                 # ── CLICK (Next between application steps) ─────────────────
#                 elif action == "click":
#                     selector   = step.get("selector", "NEXT_BUTTON")
#                     wait_ms    = step.get("wait_ms", 1500)
#                     prev_count = _get_visible_field_count(driver)
#                     prev_url   = driver.current_url

#                     print(f"\n▶  Next click (selector: {selector!r})")

#                     element = None
#                     try:
#                         element = self.wait_for_element(driver, selector, clickable=True)
#                     except Exception as e:
#                         print(f"⚠️  Next selector failed: {e} — trying smart finder")
#                         element = _find_next_button(driver)

#                     if not element:
#                         _snap(step_idx, f"error_next_not_found_step{step_idx}")
#                         _save_manifest(app_id, screenshot_log)
#                         driver.quit()
#                         return {
#                             "status":"failed","message":"Next button not found",
#                             "completed_steps":completed_steps,"screenshots":screenshot_log,
#                         }

#                     driver.execute_script("arguments[0].scrollIntoView({block:'center'});", element)
#                     driver.execute_script("arguments[0].click();", element)

#                     changed = _wait_for_dom_change(driver, prev_count, prev_url)
#                     if not changed:
#                         print("   ⚠️  DOM unchanged — using wait_ms fallback")
#                         time.sleep(wait_ms / 1000)

#                     _snap(step_idx, f"after_next_step{step_idx}")
#                     completed_steps += 1

#                 # ── SUBMIT ─────────────────────────────────────────────────
#                 elif action == "submit":
#                     selector = step.get("selector", "SUBMIT_BUTTON")
#                     wait_ms  = step.get("wait_ms", 3000)

#                     print(f"\n✅ Submit (selector: {selector!r})")

#                     element = None
#                     try:
#                         element = self.wait_for_element(driver, selector, clickable=True)
#                     except Exception as e:
#                         print(f"⚠️  Submit selector failed: {e} — trying smart finder")
#                         _snap(step_idx, "before_submit_fallback")
#                         element = _find_submit_button(driver)

#                     if not element:
#                         _snap(step_idx, "error_submit_not_found")
#                         _save_manifest(app_id, screenshot_log)
#                         driver.quit()
#                         return {
#                             "status":"failed","message":"Submit button not found",
#                             "completed_steps":completed_steps,"screenshots":screenshot_log,
#                         }

#                     try:
#                         driver.execute_script(
#                             "arguments[0].scrollIntoView({block:'center'});", element)
#                         driver.execute_script("arguments[0].click();", element)
#                         time.sleep(wait_ms / 1000)
#                     except Exception as e:
#                         _snap(step_idx, "error_submit_click")
#                         _save_manifest(app_id, screenshot_log)
#                         driver.quit()
#                         return {
#                             "status":"failed","message":"Submit click failed",
#                             "error":str(e),"completed_steps":completed_steps,
#                             "screenshots":screenshot_log,
#                         }

#                     _snap(step_idx, "final_submitted")
#                     # Stable final.png alias
#                     if screenshot_log:
#                         import shutil
#                         src = _screenshots_dir(app_id) / screenshot_log[-1]["filename"]
#                         dst = _screenshots_dir(app_id) / "final.png"
#                         if src.exists():
#                             shutil.copy2(str(src), str(dst))
#                             screenshot_log.append({
#                                 "step":step_idx,"label":"final","filename":"final.png",
#                                 "url":f"{settings.MEDIA_URL}screenshots/{app_id}/final.png",
#                             })

#                     _save_manifest(app_id, screenshot_log)
#                     driver.quit()
#                     return {
#                         "status":"success","message":"Form submitted successfully",
#                         "completed_steps":completed_steps + 1,"screenshots":screenshot_log,
#                     }

#             _save_manifest(app_id, screenshot_log)
#             driver.quit()
#             return {"status":"success","completed_steps":completed_steps,
#                     "screenshots":screenshot_log}

#         except Exception as e:
#             try:
#                 _snap(0, "unexpected_error")
#                 _save_manifest(app_id, screenshot_log)
#                 driver.quit()
#             except Exception:
#                 pass
#             return {"status":"failed","error":str(e),"screenshots":screenshot_log}

# """
# automation_pipeline/services.py  —  COMPLETE VERSION

# KEY CHANGE FROM PREVIOUS VERSION:
#   The scraper now captures the login page fields (email + password) and maps
#   them to the logged-in user's portal credentials (PORTAL_EMAIL / PORTAL_PASSWORD).
#   The automation then replays the ENTIRE flow from scratch — login step first,
#   then all application form steps — using only the mapping JSON.

#   This means:
#     - No separate _portal_login() pre-step in automation
#     - No duplicate login logic split between scraper and runner
#     - The mapping JSON is self-contained: give it to AutomationService.run()
#       and it handles login + all form steps in sequence

#   How login scraping works:
#     1. Scraper opens the URL.
#     2. If a password field is detected → scrape those fields, mark step as
#        action="login", then click login and wait for the form to appear.
#     3. Gemini receives the login fields AND the application form fields.
#     4. Gemini maps PORTAL_EMAIL → email field, PORTAL_PASSWORD → password field.
#     5. Automation replays: fill login → click login → fill step 1 → next → ...

#   Screenshot strategy (3 shots only, no mid-step noise):
#     1. after_login.png     — right after login succeeds
#     2. before_submit.png   — after the last fill step, scrolled to top,
#                              showing all data filled before submit is clicked
#     3. after_submit.png    — after the submit button is clicked

#   Folder structure:
#     media/screenshots/<student_id>/<uni_slug>/
#     where uni_slug is derived from the portal URL hostname so each university
#     gets its own separate folder per student. e.g.:
#       media/screenshots/14/portals-aiou-edu-pk/
#       media/screenshots/14/apply-umt-edu-pk/
#       media/screenshots/15/portals-aiou-edu-pk/
# """

# import hashlib
# import time
# import os
# import re
# import json
# from pathlib import Path
# from datetime import datetime
# from urllib.parse import urlparse

# from bs4 import BeautifulSoup

# from django.conf import settings

# from selenium import webdriver
# from selenium.webdriver.chrome.options import Options
# from selenium.webdriver.common.by import By
# from selenium.webdriver.common.keys import Keys
# from selenium.webdriver.support.ui import Select, WebDriverWait
# from selenium.webdriver.support import expected_conditions as EC
# from selenium.common.exceptions import TimeoutException, NoSuchElementException

# from langchain_google_genai import ChatGoogleGenerativeAI
# from langchain_core.prompts import ChatPromptTemplate
# from langchain_core.output_parsers import PydanticOutputParser

# from .schemas import AutomationResponse

# try:
#     import pyperclip
#     PYPERCLIP_AVAILABLE = True
# except ImportError:
#     PYPERCLIP_AVAILABLE = False


# # ─────────────────────────────────────────────────────────────────────────────
# # Constants
# # ─────────────────────────────────────────────────────────────────────────────

# NEXT_KEYWORDS = [
#     "next", "continue", "proceed", "forward",
#     "آگے", "اگلا", "اگلہ",
#     "next step", "next page", "save & next", "save and next", "save & continue",
# ]
# SUBMIT_KEYWORDS = [
#     "submit", "finish", "complete", "send", "apply",
#     "جمع کریں", "submit application", "final submit",
# ]
# LOGIN_KEYWORDS = ["login", "log in", "sign in", "signin", "لاگ ان"]
# NEXT_ID_HINTS  = ["next", "continue", "proceed", "forward", "step"]

# REACT_STEP_TIMEOUT  = 8
# REACT_POLL_INTERVAL = 0.25


# # ─────────────────────────────────────────────────────────────────────────────
# # Smart button finders
# # ─────────────────────────────────────────────────────────────────────────────

# def _btn_text(driver, el):
#     """Full textContent via JS — catches text inside child <span> nodes."""
#     try:
#         return (driver.execute_script("return arguments[0].textContent;", el) or "").strip()
#     except Exception:
#         return (el.text or "").strip()


# def _find_button_by_keywords(driver, keywords):
#     """
#     Generic button finder. Tries in order:
#       1. id/name/class contains a keyword
#       2. textContent contains a keyword
#       3. aria-label contains a keyword
#     Returns WebElement or None.
#     """
#     all_btns = driver.find_elements(
#         By.CSS_SELECTOR, "button, input[type='submit'], a[role='button']"
#     )

#     # Strategy 1: attribute hint
#     for kw in keywords:
#         for el in driver.find_elements(
#             By.CSS_SELECTOR,
#             f"button[id*='{kw}'], button[name*='{kw}'], button[class*='{kw}'], "
#             f"input[type='submit'][id*='{kw}'], a[id*='{kw}']"
#         ):
#             if el.is_displayed() and el.is_enabled():
#                 return el

#     # Strategy 2: textContent
#     for el in all_btns:
#         if not (el.is_displayed() and el.is_enabled()):
#             continue
#         text = _btn_text(driver, el).lower()
#         if any(kw in text for kw in keywords):
#             return el

#     # Strategy 3: aria-label
#     for el in all_btns:
#         if not (el.is_displayed() and el.is_enabled()):
#             continue
#         label = (el.get_attribute("aria-label") or "").lower()
#         if any(kw in label for kw in keywords):
#             return el

#     return None


# def _find_next_button(driver):
#     btn = _find_button_by_keywords(driver, NEXT_KEYWORDS)
#     if btn:
#         print(f"🔍 Next btn: {_btn_text(driver, btn)!r}")
#         return btn
#     # Heuristic: last visible non-back button
#     ignore = {"back", "previous", "cancel", "reset", "واپس", "پچھلا"}
#     all_btns = driver.find_elements(By.CSS_SELECTOR, "button, input[type='submit']")
#     visible  = [
#         el for el in all_btns
#         if el.is_displayed() and el.is_enabled()
#         and not any(x in _btn_text(driver, el).lower() for x in ignore)
#     ]
#     if visible:
#         el = visible[-1]
#         print(f"🔍 Next btn (last-button heuristic): {_btn_text(driver, el)!r}")
#         return el
#     print("⚠️  No Next button found")
#     return None


# def _find_submit_button(driver):
#     btn = _find_button_by_keywords(driver, SUBMIT_KEYWORDS)
#     if btn:
#         print(f"🔍 Submit btn: {_btn_text(driver, btn)!r}")
#         return btn
#     all_btns = driver.find_elements(By.CSS_SELECTOR, "button, input[type='submit']")
#     visible  = [e for e in all_btns if e.is_displayed() and e.is_enabled()]
#     if visible:
#         print(f"🔍 Submit btn (last fallback): {_btn_text(driver, visible[-1])!r}")
#         return visible[-1]
#     return None


# def _find_login_button(driver):
#     btn = _find_button_by_keywords(driver, LOGIN_KEYWORDS)
#     if btn:
#         print(f"🔍 Login btn: {_btn_text(driver, btn)!r}")
#         return btn
#     # Fallback: the only submit button on a login page
#     all_btns = driver.find_elements(
#         By.CSS_SELECTOR, "button[type='submit'], input[type='submit']"
#     )
#     visible = [e for e in all_btns if e.is_displayed() and e.is_enabled()]
#     if visible:
#         print(f"🔍 Login btn (submit fallback): {_btn_text(driver, visible[0])!r}")
#         return visible[0]
#     return None


# # ─────────────────────────────────────────────────────────────────────────────
# # DOM change detection
# # ─────────────────────────────────────────────────────────────────────────────

# def _wait_for_react_hydration(driver, timeout=15):
#     deadline = time.time() + timeout
#     while time.time() < deadline:
#         try:
#             root = driver.find_elements(By.CSS_SELECTOR, "#root, #app, [data-reactroot]")
#             container = root[0] if root else driver.find_element(By.TAG_NAME, "body")
#             inputs = container.find_elements(
#                 By.CSS_SELECTOR, "input:not([type='hidden']), select, textarea"
#             )
#             if any(el.is_displayed() for el in inputs):
#                 return True
#         except Exception:
#             pass
#         time.sleep(REACT_POLL_INTERVAL)
#     return False


# def _get_visible_field_count(driver):
#     try:
#         els = driver.find_elements(
#             By.CSS_SELECTOR, "input:not([type='hidden']), select, textarea"
#         )
#         return len([e for e in els if e.is_displayed()])
#     except Exception:
#         return 0


# def _wait_for_dom_change(driver, prev_count, prev_url, timeout=REACT_STEP_TIMEOUT):
#     deadline = time.time() + timeout
#     while time.time() < deadline:
#         try:
#             if driver.current_url != prev_url:
#                 time.sleep(0.5)
#                 _wait_for_react_hydration(driver, timeout=5)
#                 return True
#             count = _get_visible_field_count(driver)
#             if count != prev_count and count > 0:
#                 time.sleep(0.3)
#                 return True
#         except Exception:
#             pass
#         time.sleep(REACT_POLL_INTERVAL)
#     return False


# def _is_login_page(driver):
#     """Returns True if the current page has a visible password field."""
#     try:
#         pwd = driver.find_elements(By.XPATH, "//input[@type='password']")
#         return any(el.is_displayed() for el in pwd)
#     except Exception:
#         return False


# # ─────────────────────────────────────────────────────────────────────────────
# # Screenshot helpers
# # ─────────────────────────────────────────────────────────────────────────────

# def _uni_slug(url: str) -> str:
#     """
#     Derives a safe directory name from the portal URL hostname.
#     e.g. "https://portals.aiou.edu.pk/admission" → "portals-aiou-edu-pk"
#     """
#     try:
#         host = urlparse(url).hostname or "unknown"
#         return re.sub(r"[^a-z0-9]+", "-", host.lower()).strip("-")
#     except Exception:
#         return "unknown"


# def _screenshots_dir(student_id, portal_url: str) -> Path:
#     """
#     Returns (and creates) the screenshot folder for this student + university.
#     Path: media/screenshots/<student_id>/<uni_slug>/
#     """
#     slug = _uni_slug(portal_url)
#     d = Path(settings.MEDIA_ROOT) / "screenshots" / str(student_id) / slug
#     d.mkdir(parents=True, exist_ok=True)
#     return d


# def _take_screenshot(driver, student_id, portal_url: str, label: str) -> dict:
#     d        = _screenshots_dir(student_id, portal_url)
#     slug     = _uni_slug(portal_url)
#     filename = f"{label}.png"
#     filepath = d / filename
#     try:
#         driver.save_screenshot(str(filepath))
#         print(f"📸 {filepath}")
#     except Exception as e:
#         print(f"⚠️  Screenshot failed: {e}")
#         return {}
#     return {
#         "label":    label,
#         "filename": filename,
#         "url":      f"{settings.MEDIA_URL}screenshots/{student_id}/{slug}/{filename}",
#     }


# def _save_manifest(student_id, portal_url: str, entries: list):
#     d    = _screenshots_dir(student_id, portal_url)
#     path = d / "manifest.json"
#     with open(path, "w") as f:
#         json.dump({
#             "student_id":  student_id,
#             "portal":      portal_url,
#             "screenshots": [e for e in entries if e],
#         }, f, indent=2)


# # ─────────────────────────────────────────────────────────────────────────────
# # Field extraction helper (shared by scraper)
# # ─────────────────────────────────────────────────────────────────────────────

# def _extract_fields_from_page(driver, include_password=False):
#     """
#     Extracts all visible form fields from the current page.
#     include_password=True is used when scraping the login page.
#     include_password=False (default) skips password fields on form pages.
#     """
#     soup     = BeautifulSoup(driver.page_source, "html.parser")
#     elements = []

#     for el in soup.find_all(["input", "select", "textarea"]):
#         el_type = el.get("type", "text").lower() if el.name == "input" else el.name

#         if el_type == "hidden":
#             continue
#         if el_type == "password" and not include_password:
#             continue

#         if el.get("id"):
#             selector = f"#{el.get('id')}"
#         elif el.get("name"):
#             selector = f"[name='{el.get('name')}']"
#         elif el.get("data-testid"):
#             selector = f"[data-testid='{el.get('data-testid')}']"
#         else:
#             continue

#         # Prefer <label for="..."> text, then fall back to placeholder/aria-label
#         label = ""
#         if el.get("id"):
#             lbl = soup.find("label", attrs={"for": el.get("id")})
#             if lbl:
#                 label = lbl.get_text(strip=True)
#         if not label:
#             label = el.get("placeholder") or el.get("aria-label") or el.get("name") or ""

#         entry = {"selector": selector, "type": el_type, "label": label}
#         if el_type == "file":
#             entry["accept"] = el.get("accept", "")
#         if el.name == "select":
#             entry["options"] = [
#                 o.get_text(strip=True) for o in el.find_all("option")
#                 if o.get_text(strip=True)
#             ]
#         elements.append(entry)

#     return elements


# # ─────────────────────────────────────────────────────────────────────────────
# # AI SERVICE
# # ─────────────────────────────────────────────────────────────────────────────

# class AIService:

#     def __init__(self):
#         api_key = getattr(settings, "GEMINI_API_KEY", None)
#         if not api_key:
#             raise ValueError("GEMINI_API_KEY not set in Django settings.")
#         self.llm = ChatGoogleGenerativeAI(
#             model="gemini-2.5-flash",
#             google_api_key=api_key,
#             temperature=0,
#         )
#         self.parser = PydanticOutputParser(pydantic_object=AutomationResponse)

#     @staticmethod
#     def make_app_id(student_id, url: str) -> int:
#         raw = f"{student_id}:{url}"
#         return int(hashlib.md5(raw.encode()).hexdigest()[:8], 16) % 999999 + 1

#     # ------------------------------------------------------------------
#     # Scrape entire flow: login page (if present) + all form steps
#     # ------------------------------------------------------------------
#     def scrape_full_flow(self, url):
#         """
#         Opens the URL and scrapes:
#           - If a login page is detected: scrapes login fields, performs login,
#             waits for the application form to appear, then scrapes all form steps.
#           - If no login page: scrapes all form steps directly.

#         Returns a list of page dicts:
#           [
#             { "page_type": "login",       "page_number": 0, "fields": [...] },
#             { "page_type": "application", "page_number": 1, "fields": [...] },
#             { "page_type": "application", "page_number": 2, "fields": [...] },
#             ...
#           ]

#         Each page includes the login button / next button / submit button
#         selector so Gemini can emit the correct click/submit actions.
#         """
#         options = Options()
#         options.add_argument("--headless=new")   # full V8 for React
#         options.add_argument("--no-sandbox")
#         options.add_argument("--disable-dev-shm-usage")
#         options.add_argument("--window-size=1920,1080")

#         driver = None
#         pages  = []

#         try:
#             driver = webdriver.Chrome(options=options)
#             driver.get(url)

#             # Wait for initial render
#             _wait_for_react_hydration(driver, timeout=15)

#             # ── LOGIN PAGE ──────────────────────────────────────────────
#             if _is_login_page(driver):
#                 print("🔐 Login page detected during scraping")

#                 # Scrape login fields INCLUDING password
#                 login_fields = _extract_fields_from_page(driver, include_password=True)

#                 # Find the login button and record its selector
#                 login_btn       = _find_login_button(driver)
#                 login_btn_sel   = None
#                 if login_btn:
#                     btn_id = login_btn.get_attribute("id")
#                     login_btn_sel = f"#{btn_id}" if btn_id else "LOGIN_BUTTON"

#                 pages.append({
#                     "page_type":    "login",
#                     "page_number":  0,
#                     "fields":       login_fields,
#                     "submit_selector": login_btn_sel or "LOGIN_BUTTON",
#                 })
#                 print(f"   Scraped {len(login_fields)} login fields")

#                 # Perform login so we can scrape the real form pages
#                 portal_email = "student"
#                 portal_password = "au2024"

#                 if portal_email and portal_password and login_btn:
#                     try:
#                         # Fill credentials
#                         try:
#                             email_el = driver.find_element(By.XPATH, "//input[@type='email']")
#                         except NoSuchElementException:
#                             email_el = driver.find_element(By.XPATH, "//input[@type='text']")
#                         pass_el = driver.find_element(By.XPATH, "//input[@type='password']")
#                         email_el.send_keys(portal_email)
#                         pass_el.send_keys(portal_password)
#                         driver.execute_script("arguments[0].click();", login_btn)

#                         # Wait for login to complete (password field disappears)
#                         WebDriverWait(driver, 15).until(
#                             EC.invisibility_of_element_located(
#                                 (By.XPATH, "//input[@type='password']")
#                             )
#                         )
#                         print("✅ Scraping login succeeded — waiting for form...")
#                         time.sleep(2)
#                         _wait_for_react_hydration(driver, timeout=10)
#                     except Exception as e:
#                         print(f"⚠️  Scraping login failed: {e} — form pages may be incomplete")
#                 else:
#                     print("⚠️  PORTAL_EMAIL/PORTAL_PASSWORD not set or no login button found")

#             # ── APPLICATION FORM PAGES ──────────────────────────────────
#             for step_num in range(1, 11):
#                 print(f"\n🧭 Scraping application page {step_num}...")
#                 time.sleep(0.5)

#                 # Skip if still on login page
#                 if _is_login_page(driver):
#                     print("   Still on login page — login may have failed")
#                     break

#                 fields = _extract_fields_from_page(driver, include_password=False)
#                 print(f"   {len(fields)} fields found")

#                 prev_count = _get_visible_field_count(driver)
#                 prev_url   = driver.current_url

#                 # Find the next/submit button and record its selector too
#                 next_btn   = _find_next_button(driver)
#                 submit_btn = _find_submit_button(driver) if not next_btn else None

#                 next_sel   = None
#                 submit_sel = None

#                 if next_btn:
#                     nid = next_btn.get_attribute("id")
#                     next_sel = f"#{nid}" if nid else "NEXT_BUTTON"
#                 if submit_btn and not next_btn:
#                     sid = submit_btn.get_attribute("id")
#                     submit_sel = f"#{sid}" if sid else "SUBMIT_BUTTON"

#                 pages.append({
#                     "page_type":       "application",
#                     "page_number":     step_num,
#                     "fields":          fields,
#                     "next_selector":   next_sel,
#                     "submit_selector": submit_sel,
#                 })

#                 if not next_btn:
#                     print("   ✅ No Next button — end of form")
#                     break

#                 try:
#                     driver.execute_script(
#                         "arguments[0].scrollIntoView({block:'center'});", next_btn)
#                     driver.execute_script("arguments[0].click();", next_btn)
#                     print("   ▶ Clicked Next — waiting for DOM change...")
#                     changed = _wait_for_dom_change(driver, prev_count, prev_url)
#                     if not changed:
#                         print("   ⚠️  DOM didn't change — may be last step")
#                         break
#                 except Exception as e:
#                     print(f"   ❌ Error clicking Next: {e}")
#                     break

#             return pages

#         finally:
#             if driver:
#                 driver.quit()

#     # ------------------------------------------------------------------
#     # Generate mapping via Gemini
#     # ------------------------------------------------------------------
#     def get_automation_instructions(self, target_url, student_data, app_id):
#         """
#         Scrapes the full portal flow (login + form pages), then asks Gemini
#         to produce a complete mapping including the login step.
#         """
#         pages = self.scrape_full_flow(target_url)
#         if not pages:
#             raise Exception("No pages found — check the portal URL")

#         portal_email    = getattr(settings, "PORTAL_EMAIL", "")
#         portal_password = getattr(settings, "PORTAL_PASSWORD", "")

#         # Inject portal credentials into student_data so Gemini can map them
#         student_data_with_creds = {
#             **student_data,
#             "_portal_email":    portal_email,
#             "_portal_password": portal_password,
#         }

#         system_prompt = """
# You are an expert at mapping student data to multi-page university portal flows.

# The pages list includes:
#   - A "login" page (page_type="login") if the portal requires authentication
#   - One or more "application" pages (page_type="application")

# You must generate a COMPLETE automation plan that covers ALL pages in order:
#   1. Fill login credentials → click login button → wait for form
#   2. Fill application step 1 → click Next → ...
#   3. Fill last step → submit

# Return ONLY valid JSON (no markdown, no backticks). Example structure:

# {{
#   "application_id": <integer>,
#   "url": "<target url>",
#   "steps": [
#     {{
#       "action": "fill",
#       "page_type": "login",
#       "fields": [
#         {{"selector": "#email",    "type": "email",    "value": "<_portal_email value>",    "confidence": 1.0}},
#         {{"selector": "#password", "type": "password", "value": "<_portal_password value>", "confidence": 1.0}}
#       ]
#     }},
#     {{
#       "action": "login_click",
#       "selector": "<submit_selector from login page, or LOGIN_BUTTON>",
#       "wait_ms": 3000
#     }},
#     {{
#       "action": "fill",
#       "page_type": "application",
#       "fields": [
#         {{"selector": "#name", "type": "text", "value": "Ali Khan", "confidence": 0.95}},
#         {{"selector": "#photo","type": "file", "value": "/abs/path/photo.jpg", "confidence": 0.9}}
#       ]
#     }},
#     {{"action": "click",  "selector": "NEXT_BUTTON",   "wait_ms": 2000}},
#     {{"action": "fill",   "page_type": "application", "fields": [...]}},
#     {{"action": "submit", "selector": "SUBMIT_BUTTON", "wait_ms": 3000}}
#   ]
# }}

# RULES:
# 1. LOGIN STEP:
#    - Map "_portal_email" → the email/username input field on the login page.
#    - Map "_portal_password" → the password input field on the login page.
#    - Use the exact selectors from the login page fields.
#    - The login click action must use "action": "login_click" so the automation
#      engine knows to wait for the password field to disappear after clicking.

# 2. CLICK / SUBMIT selectors:
#    - For click (Next) actions: use "NEXT_BUTTON" unless the page gave a specific
#      next_selector — in that case use the specific one.
#    - For submit: use "SUBMIT_BUTTON" unless the page gave a specific submit_selector.
#    - For login_click: use the submit_selector from the login page, or "LOGIN_BUTTON".
#    - NEVER invent button CSS selectors — the engine resolves these at runtime.

# 3. FILL selectors must be the exact strings from the scraped page fields.

# 4. FILE FIELDS:
#    photo/picture/avatar  → student.photo
#    cnic/id_card          → student.cnic_image
#    transcript/result     → student.transcript
#    matric                → student.matric_certificate
#    inter/fsc/hssc        → student.inter_certificate
#    domicile              → student.domicile
#    Set value="" and confidence=0.0 if no match.

# 5. confidence: 1.0=exact, 0.5=inferred, 0.0=no match.
# 6. Include ALL fields even if confidence is 0.
# 7. Return ONLY JSON.
# """

#         prompt = ChatPromptTemplate.from_messages([
#             ("system", system_prompt),
#             ("human",
#              "STUDENT DATA (includes _portal_email and _portal_password):\n{student_data}\n\n"
#              "SCRAPED PAGES (login + application steps):\n{pages_data}\n\n"
#              "URL: {url}\nAPP ID: {app_id}"),
#         ])

#         chain  = prompt | self.llm | self.parser
#         result = chain.invoke({
#             "student_data": json.dumps(student_data_with_creds, indent=2),
#             "pages_data":   json.dumps(pages, indent=2),
#             "url":          target_url,
#             "app_id":       app_id,
#         })
#         return result


# # ─────────────────────────────────────────────────────────────────────────────
# # AUTOMATION SERVICE
# # ─────────────────────────────────────────────────────────────────────────────

# class AutomationService:

#     # ── Normalization ──────────────────────────────────────────────────────

#     def normalize_value(self, field_name, value):
#         if not value:
#             return value
#         value    = str(value).strip()
#         city_map = {
#             "lahore": "Punjab", "karachi": "Sindh", "islamabad": "Islamabad",
#             "peshawar": "KPK",  "quetta": "Balochistan",
#         }
#         if field_name and "province" in field_name.lower():
#             return city_map.get(value.lower(), value)
#         return value

#     def normalize_course(self, value):
#         if not value:
#             return []
#         v = str(value).lower().strip()
#         m = {
#             "cs":                     ["cs","computer science","bscs"],
#             "bscs":                   ["bscs","computer science","cs"],
#             "computer science":       ["computer science","cs","bscs"],
#             "bsse":                   ["bsse","software engineering","software"],
#             "software engineering":   ["software engineering","bsse","software"],
#             "bsit":                   ["bsit","information technology","it","bs information technology","bs (it)"],
#             "it":                     ["it","information technology","bsit"],
#             "information technology": ["information technology","bsit","it","bs information technology"],
#             "bba":                    ["bba","business administration","business"],
#             "business administration":["business administration","bba","business"],
#             "finance":                ["finance","bba finance","business finance"],
#             "mbbs":                   ["mbbs","medicine","medical"],
#             "bds":                    ["bds","dentistry","dental"],
#             "nursing":                ["nursing","bsn","bs nursing"],
#             "psychology":             ["psychology","bs psychology"],
#             "sociology":              ["sociology","bs sociology"],
#             "llb":                    ["llb","law","bachelor of law","legal"],
#             "law":                    ["law","llb","legal studies","legal"],
#         }
#         return m.get(v, [v])

#     def normalize_date(self, value):
#         if not value:
#             return value
#         fmts = [
#             "%Y-%m-%d","%Y %m %d","%Y/%m/%d",
#             "%d-%m-%Y","%d/%m/%Y","%d %m %Y",
#             "%m/%d/%Y","%m-%d-%Y",
#             "%d %b %Y","%d %B %Y","%B %d, %Y","%b %d, %Y",
#         ]
#         dt = None
#         for fmt in fmts:
#             try: dt = datetime.strptime(str(value).strip(), fmt); break
#             except Exception: continue
#         if not dt:
#             return {"iso":value,"dmy":value,"dmy_dash":value,"dmy_slash":value,
#                     "mdy":value,"long":value,"dt":None,"day":"","month":"","year":""}
#         return {
#             "iso":       dt.strftime("%Y-%m-%d"),
#             "dmy":       dt.strftime("%d %m %Y"),
#             "dmy_dash":  dt.strftime("%d-%m-%Y"),
#             "dmy_slash": dt.strftime("%d/%m/%Y"),
#             "mdy":       dt.strftime("%m/%d/%Y"),
#             "long":      dt.strftime("%d %b %Y"),
#             "dt":        dt,
#             "day":       dt.strftime("%d"),
#             "month":     dt.strftime("%m"),
#             "year":      dt.strftime("%Y"),
#         }

#     # ── React helpers ──────────────────────────────────────────────────────

#     def is_react_page(self, driver):
#         return driver.execute_script(
#             "return !!(window.__REACT_DEVTOOLS_GLOBAL_HOOK__ || "
#             "document.querySelector('[data-reactroot]') || "
#             "document.querySelector('#root'))"
#         )

#     def react_set_value(self, driver, element, value):
#         driver.execute_script("""
#             var el = arguments[0], val = arguments[1];
#             var proto = el.tagName.toLowerCase() === 'textarea'
#                 ? window.HTMLTextAreaElement.prototype
#                 : window.HTMLInputElement.prototype;
#             Object.getOwnPropertyDescriptor(proto, 'value').set.call(el, val);
#             el.dispatchEvent(new Event('input',  { bubbles: true }));
#             el.dispatchEvent(new Event('change', { bubbles: true }));
#         """, element, value)

#     # ── Date helpers ───────────────────────────────────────────────────────

#     def detect_date_format(self, element):
#         hint = " ".join([
#             element.get_attribute("placeholder") or "",
#             element.get_attribute("pattern")     or "",
#             element.get_attribute("data-format") or "",
#         ]).lower()
#         if any(x in hint for x in ["dd-mm-yyyy","dd/mm/yyyy","dd mm yyyy"]):
#             return "dmy_slash" if "/" in hint else "dmy_dash"
#         if any(x in hint for x in ["mm/dd/yyyy","mm-dd-yyyy"]): return "mdy"
#         if "yyyy-mm-dd" in hint: return "iso"
#         return None

#     def fill_date_react(self, driver, element, formats):
#         input_type = (element.get_attribute("type") or "").lower()
#         fmt_key    = self.detect_date_format(element)
#         if input_type == "date":
#             self.fill_react_native_date(driver, element, formats, fmt_key); return
#         formatted = formats.get(fmt_key, formats["dmy_dash"]) if fmt_key else formats["dmy_dash"]
#         self.react_set_value(driver, element, formatted); time.sleep(0.2)
#         if element.get_attribute("value"): return
#         if PYPERCLIP_AVAILABLE:
#             try:
#                 pyperclip.copy(formatted)
#                 element.send_keys(Keys.CONTROL + "v"); time.sleep(0.3)
#                 if element.get_attribute("value"): return
#             except Exception: pass
#         driver.execute_script("arguments[0].click();", element)
#         element.send_keys(Keys.CONTROL + "a"); element.send_keys(Keys.DELETE)
#         for char in formatted: element.send_keys(char); time.sleep(0.04)

#     def fill_react_native_date(self, driver, element, formats, fmt_key):
#         self.react_set_value(driver, element, formats["iso"]); time.sleep(0.2)
#         if element.get_attribute("value") == formats["iso"]: return
#         driver.execute_script("arguments[0].click();", element)
#         element.send_keys(formats["month"]); time.sleep(0.1)
#         element.send_keys(formats["day"]);   time.sleep(0.1)
#         element.send_keys(formats["year"])

#     def fill_native_date(self, driver, element, formats):
#         iso = formats["iso"]
#         driver.execute_script("arguments[0].value = arguments[1];", element, iso)
#         driver.execute_script(
#             "arguments[0].dispatchEvent(new Event('input',{bubbles:true}));"
#             "arguments[0].dispatchEvent(new Event('change',{bubbles:true}));", element)
#         if element.get_attribute("value") != iso:
#             element.clear(); element.send_keys(iso)

#     def fill_custom_date(self, driver, element, formats):
#         fmt_key = self.detect_date_format(element)
#         if fmt_key:
#             element.clear(); time.sleep(0.2)
#             element.send_keys(formats.get(fmt_key, formats["dmy_dash"]))
#         else:
#             for key in ["dmy_dash","dmy_slash","dmy","iso","mdy"]:
#                 element.clear(); time.sleep(0.2)
#                 element.send_keys(formats.get(key,"")); time.sleep(0.3)
#                 if element.get_attribute("value"): return
#             driver.execute_script("arguments[0].value = arguments[1];", element, formats["dmy_dash"])
#             driver.execute_script(
#                 "arguments[0].dispatchEvent(new Event('input',{bubbles:true}));"
#                 "arguments[0].dispatchEvent(new Event('change',{bubbles:true}));", element)

#     # ── File path resolver ─────────────────────────────────────────────────

#     def resolve_file_path(self, value):
#         if not value:
#             raise ValueError("File path is empty")
#         path = str(value).strip()
#         if os.path.isabs(path) and os.path.isfile(path): return path
#         media_root = getattr(settings, "MEDIA_ROOT", "")
#         if media_root:
#             clean = path.lstrip("/\\")
#             if clean.startswith("media/") or clean.startswith("media\\"):
#                 clean = clean[6:]
#             candidate = os.path.join(str(media_root), clean)
#             if os.path.isfile(candidate): return os.path.abspath(candidate)
#         base_dir = getattr(settings, "BASE_DIR", "")
#         if base_dir:
#             candidate = os.path.join(str(base_dir), path.lstrip("/\\"))
#             if os.path.isfile(candidate): return os.path.abspath(candidate)
#         abs_attempt = os.path.abspath(path)
#         if os.path.isfile(abs_attempt): return abs_attempt
#         raise FileNotFoundError(
#             f"File not found: '{value}' — tried MEDIA_ROOT='{media_root}', BASE_DIR='{base_dir}'"
#         )

#     # ── wait_for_element ───────────────────────────────────────────────────

#     def wait_for_element(self, driver, selector, timeout=10, clickable=False):
#         # Magic smart-finder values
#         if selector in ("NEXT_BUTTON",  "next_button"):
#             deadline = time.time() + timeout
#             while time.time() < deadline:
#                 el = _find_next_button(driver)
#                 if el: return el
#                 time.sleep(REACT_POLL_INTERVAL)
#             raise TimeoutException("No Next button found")

#         if selector in ("SUBMIT_BUTTON", "submit_button"):
#             deadline = time.time() + timeout
#             while time.time() < deadline:
#                 el = _find_submit_button(driver)
#                 if el: return el
#                 time.sleep(REACT_POLL_INTERVAL)
#             raise TimeoutException("No Submit button found")

#         if selector in ("LOGIN_BUTTON", "login_button"):
#             deadline = time.time() + timeout
#             while time.time() < deadline:
#                 el = _find_login_button(driver)
#                 if el: return el
#                 time.sleep(REACT_POLL_INTERVAL)
#             raise TimeoutException("No Login button found")

#         # :contains() → case-insensitive XPath
#         if ":contains(" in selector:
#             match = re.match(r"^(\w+)?:contains\(['\"](.+?)['\"]\)$", selector.strip())
#             if match:
#                 tag, text = match.group(1) or "*", match.group(2).lower()
#             else:
#                 tag  = "*"
#                 text = selector.split(":contains(")[1].strip("'\")")
#             xpath = (
#                 f"//{tag}[contains("
#                 f"translate(normalize-space(.),"
#                 f"'ABCDEFGHIJKLMNOPQRSTUVWXYZ','abcdefghijklmnopqrstuvwxyz'),"
#                 f"'{text.lower()}')]"
#             )
#             wait = WebDriverWait(driver, timeout)
#             cond = EC.element_to_be_clickable if clickable else EC.presence_of_element_located
#             try:
#                 return wait.until(cond((By.XPATH, xpath)))
#             except TimeoutException:
#                 # Fall through to keyword-based smart finder
#                 fn = _find_login_button  if any(kw in selector.lower() for kw in LOGIN_KEYWORDS) \
#                      else _find_next_button if any(kw in selector.lower() for kw in NEXT_KEYWORDS) \
#                      else _find_submit_button
#                 el = fn(driver)
#                 if el: return el
#                 raise

#         # Standard selectors
#         wait = WebDriverWait(driver, timeout)
#         by   = By.CSS_SELECTOR
#         if selector.startswith("#"):
#             by, selector = By.ID, selector[1:]
#         elif selector.startswith("//"):
#             by = By.XPATH
#         elif selector.startswith("[name="):
#             by, selector = By.NAME, selector.split("'")[1]

#         # File inputs are invisible — always use presence
#         try:
#             el_type = driver.find_element(by, selector).get_attribute("type") or ""
#             if el_type == "file": clickable = False
#         except Exception:
#             pass

#         cond = EC.element_to_be_clickable if clickable else EC.presence_of_element_located
#         return wait.until(cond((by, selector)))

#     # ── fill_field ─────────────────────────────────────────────────────────

#     def fill_field(self, driver, element, field_type, value):
#         tag        = element.tag_name.lower()
#         input_type = (element.get_attribute("type") or "").lower()
#         is_react   = self.is_react_page(driver)

#         # FILE — send_keys only, never clear/value setter
#         if field_type == "file" or input_type == "file":
#             try:
#                 abs_path = self.resolve_file_path(value)
#             except (FileNotFoundError, ValueError) as e:
#                 raise Exception(f"File upload failed — {e}")
#             driver.execute_script("""
#                 arguments[0].style.display    = 'block';
#                 arguments[0].style.opacity    = '1';
#                 arguments[0].style.visibility = 'visible';
#             """, element)
#             time.sleep(0.2)
#             element.send_keys(abs_path)
#             driver.execute_script(
#                 "arguments[0].dispatchEvent(new Event('change',{bubbles:true}));", element)
#             print(f"✅ File: {os.path.basename(abs_path)}")
#             return

#         # PASSWORD — plain send_keys (never react_set_value; portals track state internally)
#         if input_type == "password":
#             element.clear()
#             element.send_keys(str(value))
#             return

#         # CHECKBOX / RADIO
#         if input_type in ["checkbox", "radio"]:
#             if str(value).lower() in ["true","1","yes"]:
#                 driver.execute_script("arguments[0].click();", element)
#             return

#         # DATE
#         if field_type == "date" or input_type == "date":
#             formats = self.normalize_date(value)
#             if not formats.get("dt"):
#                 element.clear(); element.send_keys(str(value)); return
#             if is_react:
#                 self.fill_date_react(driver, element, formats)
#             elif input_type == "date":
#                 fmt_key = self.detect_date_format(element)
#                 (self.fill_custom_date if (fmt_key and fmt_key != "iso") else self.fill_native_date)(
#                     driver, element, formats)
#             else:
#                 self.fill_custom_date(driver, element, formats)
#             return

#         # SELECT
#         if tag == "select":
#             sel     = Select(element)
#             options = [o.text.strip() for o in sel.options]
#             opt_low = [o.lower() for o in options]
#             for target in self.normalize_course(value):
#                 t = target.lower().strip()
#                 for i, opt in enumerate(opt_low):
#                     if opt == t:                           sel.select_by_visible_text(options[i]); return
#                 for i, opt in enumerate(opt_low):
#                     if opt and opt in t:                  sel.select_by_visible_text(options[i]); return
#                 for i, opt in enumerate(opt_low):
#                     if t and t in opt:                    sel.select_by_visible_text(options[i]); return
#                 for i, opt in enumerate(opt_low):
#                     if set(t.split()) & set(opt.split()): sel.select_by_visible_text(options[i]); return
#             raise Exception(f"Dropdown option not found for '{value}'. Available: {options}")

#         # TEXT / TEXTAREA / EMAIL
#         if tag in ["input", "textarea"]:
#             self.react_set_value(driver, element, str(value)) if is_react \
#                 else (element.clear() or element.send_keys(str(value)))
#             return

#         # FALLBACK
#         driver.execute_script("arguments[0].value = arguments[1];", element, value)
#         driver.execute_script(
#             "arguments[0].dispatchEvent(new Event('change',{bubbles:true}));", element)

#     # ── Main runner ────────────────────────────────────────────────────────

#     def run(self, mapping: dict) -> dict:
#         """
#         Executes the full automation flow from the mapping JSON.
#         Step types:
#           "fill"        — fill form fields (login page or application page)
#           "login_click" — click the login button and wait for form to load
#           "click"       — click Next button between application steps
#           "submit"      — click the final submit button

#         Screenshots (3 total, stored in media/screenshots/<student_id>/<uni_slug>/):
#           1. after_login.png    — right after login succeeds
#           2. before_submit.png  — after last fill step, scrolled to top,
#                                   all data visible before submit is clicked
#           3. after_submit.png   — after submit button is clicked
#         """
#         url        = mapping.get("url")
#         steps      = mapping.get("steps", [])
#         student_id = mapping.get("application_id", 0)  # profile id used as student id

#         if not url:
#             return {"status":"failed","message":"No URL provided","screenshots":[]}

#         options = Options()
#         options.add_argument("--start-maximized")
#         # Uncomment to run headless:
#         # options.add_argument("--headless=new")

#         driver = webdriver.Chrome(options=options)
#         driver.get(url)
#         _wait_for_react_hydration(driver, timeout=15)

#         completed_steps = 0
#         screenshot_log  = []

#         # Find the index of the last "fill" step with page_type="application"
#         # so we know exactly when to take the before_submit screenshot
#         last_app_fill_idx = None
#         for i, s in enumerate(steps):
#             if s.get("action") == "fill" and s.get("page_type") == "application":
#                 last_app_fill_idx = i

#         def _snap(label):
#             entry = _take_screenshot(driver, student_id, url, label)
#             if entry:
#                 screenshot_log.append(entry)

#         try:
#             for step_idx, step in enumerate(steps):
#                 action = step.get("action")

#                 # ── FILL (login page or application page) ─────────────────
#                 if action == "fill":
#                     page_type = step.get("page_type", "application")
#                     print(f"\n📝 Fill step {step_idx} [{page_type}]")

#                     for field in step.get("fields", []):
#                         selector   = field.get("selector")
#                         field_type = (field.get("type") or "text").lower()
#                         raw_value  = field.get("value")

#                         if (raw_value is None or raw_value == "") and field_type != "file":
#                             continue
#                         if field_type == "file" and not raw_value:
#                             print(f"⏭️  No file path for {selector}")
#                             continue

#                         value = self.normalize_value(selector, raw_value)
#                         print(f"   🖊  [{field_type}] {selector} → {value!r}")

#                         try:
#                             element = self.wait_for_element(
#                                 driver, selector, clickable=(field_type != "file"))
#                             if field_type != "file":
#                                 driver.execute_script(
#                                     "arguments[0].scrollIntoView({block:'center'});", element)
#                             self.fill_field(driver, element, field_type, value)
#                             time.sleep(0.2)
#                         except Exception as e:
#                             print(f"   ❌ Failed {selector}: {e}")
#                             _save_manifest(student_id, url, screenshot_log)
#                             driver.quit()
#                             return {
#                                 "status":"failed","message":f"Error filling {selector}",
#                                 "error":str(e),"completed_steps":completed_steps,
#                                 "screenshots":screenshot_log,
#                             }

#                     # Screenshot 2: taken only after the LAST application fill step,
#                     # showing the fully filled form before submit is clicked
#                     if step_idx == last_app_fill_idx:
#                         time.sleep(0.7)
#                         driver.execute_script("window.scrollTo(0, 0);")
#                         time.sleep(0.2)
#                         _snap("before_submit")
#                         print("📸 before_submit screenshot taken")

#                     completed_steps += 1

#                 # ── LOGIN CLICK — click login btn, wait for form to appear ──
#                 elif action == "login_click":
#                     selector = step.get("selector", "LOGIN_BUTTON")
#                     wait_ms  = step.get("wait_ms", 3000)
#                     print(f"\n🔐 Login click (selector: {selector!r})")

#                     element = None
#                     try:
#                         element = self.wait_for_element(driver, selector, clickable=True)
#                     except Exception as e:
#                         print(f"⚠️  Login button '{selector}' not found: {e}")
#                         element = _find_login_button(driver)

#                     if not element:
#                         _save_manifest(student_id, url, screenshot_log)
#                         driver.quit()
#                         return {
#                             "status":"failed","message":"Login button not found",
#                             "completed_steps":completed_steps,"screenshots":screenshot_log,
#                         }

#                     driver.execute_script("arguments[0].scrollIntoView({block:'center'});", element)
#                     driver.execute_script("arguments[0].click();", element)
#                     print("   ▶ Clicked login — waiting for password field to disappear...")

#                     # Wait for login to complete: password field disappears
#                     try:
#                         WebDriverWait(driver, 15).until(
#                             EC.invisibility_of_element_located(
#                                 (By.XPATH, "//input[@type='password']")
#                             )
#                         )
#                         print("   ✅ Login successful — form is now visible")
#                         time.sleep(1.5)
#                         _wait_for_react_hydration(driver, timeout=10)
#                     except TimeoutException:
#                         _save_manifest(student_id, url, screenshot_log)
#                         driver.quit()
#                         return {
#                             "status":"failed",
#                             "message":"Login timed out — password field never disappeared. Check credentials.",
#                             "completed_steps":completed_steps,"screenshots":screenshot_log,
#                         }

#                     # Screenshot 1: right after login succeeds, form is visible
#                     time.sleep(0.5)
#                     driver.execute_script("window.scrollTo(0, 0);")
#                     time.sleep(0.2)
#                     _snap("after_login")
#                     print("📸 after_login screenshot taken")
#                     completed_steps += 1

#                 # ── CLICK (Next between application steps) ─────────────────
#                 elif action == "click":
#                     selector   = step.get("selector", "NEXT_BUTTON")
#                     wait_ms    = step.get("wait_ms", 1500)
#                     prev_count = _get_visible_field_count(driver)
#                     prev_url   = driver.current_url

#                     print(f"\n▶  Next click (selector: {selector!r})")

#                     element = None
#                     try:
#                         element = self.wait_for_element(driver, selector, clickable=True)
#                     except Exception as e:
#                         print(f"⚠️  Next selector failed: {e} — trying smart finder")
#                         element = _find_next_button(driver)

#                     if not element:
#                         _save_manifest(student_id, url, screenshot_log)
#                         driver.quit()
#                         return {
#                             "status":"failed","message":"Next button not found",
#                             "completed_steps":completed_steps,"screenshots":screenshot_log,
#                         }

#                     driver.execute_script("arguments[0].scrollIntoView({block:'center'});", element)
#                     driver.execute_script("arguments[0].click();", element)
                    
#                     completed_steps += 1
#                     time.sleep(0.3)
#                     _snap("beofre_submit")
#                     print("📸before_submit screenshot taken")
#                     changed = _wait_for_dom_change(driver, prev_count, prev_url)
#                     if not changed:
#                         print("   ⚠️  DOM unchanged — using wait_ms fallback")
#                         time.sleep(wait_ms / 1000)


#                 # ── SUBMIT ─────────────────────────────────────────────────
#                 elif action == "submit":
#                     selector = step.get("selector", "SUBMIT_BUTTON")
#                     wait_ms  = step.get("wait_ms", 3000)
                    
#                     completed_steps += 1
#                     time.sleep(0.3)
#                     _snap("submittt")
#                     print("📸submittt screenshot taken")
#                     print(f"\n✅ Submit (selector: {selector!r})")

#                     element = None
#                     try:
#                         element = self.wait_for_element(driver, selector, clickable=True)
#                     except Exception as e:
#                         print(f"⚠️  Submit selector failed: {e} — trying smart finder")
#                         element = _find_submit_button(driver)

#                     if not element:
#                         _save_manifest(student_id, url, screenshot_log)
#                         driver.quit()
#                         return {
#                             "status":"failed","message":"Submit button not found",
#                             "completed_steps":completed_steps,"screenshots":screenshot_log,
#                         }

#                     try:
#                         driver.execute_script(
#                             "arguments[0].scrollIntoView({block:'center'});", element)
#                         driver.execute_script("arguments[0].click();", element)
#                         time.sleep(wait_ms / 1000)
#                     except Exception as e:
#                         _save_manifest(student_id, url, screenshot_log)
#                         driver.quit()
#                         return {
#                             "status":"failed","message":"Submit click failed",
#                             "error":str(e),"completed_steps":completed_steps,
#                             "screenshots":screenshot_log,
#                         }

#                     # Screenshot 3: after submit button is clicked
#                     driver.execute_script("window.scrollTo(0, 0);")
#                     time.sleep(0.3)
#                     _snap("after_submit")
#                     print("📸 after_submit screenshot taken")

#                     _save_manifest(student_id, url, screenshot_log)
#                     driver.quit()
#                     return {
#                         "status":"success","message":"Form submitted successfully",
#                         "completed_steps":completed_steps + 1,"screenshots":screenshot_log,
#                     }

#             _save_manifest(student_id, url, screenshot_log)
#             driver.quit()
#             return {"status":"success","completed_steps":completed_steps,
#                     "screenshots":screenshot_log}

#         except Exception as e:
#             try:
#                 _save_manifest(student_id, url, screenshot_log)
#                 driver.quit()
#             except Exception:
#                 pass
#             return {"status":"failed","error":str(e),"screenshots":screenshot_log}



# below is besttt


# """
# automation_pipeline/services.py  —  COMPLETE VERSION

# KEY CHANGE FROM PREVIOUS VERSION:
#   The scraper now captures the login page fields (email + password) and maps
#   them to the logged-in user's portal credentials (PORTAL_EMAIL / PORTAL_PASSWORD).
#   The automation then replays the ENTIRE flow from scratch — login step first,
#   then all application form steps — using only the mapping JSON.

#   This means:
#     - No separate _portal_login() pre-step in automation
#     - No duplicate login logic split between scraper and runner
#     - The mapping JSON is self-contained: give it to AutomationService.run()
#       and it handles login + all form steps in sequence

#   How login scraping works:
#     1. Scraper opens the URL.
#     2. If a password field is detected → scrape those fields, mark step as
#        action="login", then click login and wait for the form to appear.
#     3. Gemini receives the login fields AND the application form fields.
#     4. Gemini maps PORTAL_EMAIL → email field, PORTAL_PASSWORD → password field.
#     5. Automation replays: fill login → click login → fill step 1 → next → ...

#   Screenshot strategy (3 shots only, no mid-step noise):
#     1. after_login.png     — right after login succeeds
#     2. before_submit.png   — after the last fill step, scrolled to top,
#                              showing all data filled before submit is clicked
#     3. after_submit.png    — after the submit button is clicked

#   Folder structure:
#     media/screenshots/<student_id>/<uni_slug>/
#     where uni_slug is derived from the portal URL hostname so each university
#     gets its own separate folder per student. e.g.:
#       media/screenshots/14/portals-aiou-edu-pk/
#       media/screenshots/14/apply-umt-edu-pk/
#       media/screenshots/15/portals-aiou-edu-pk/
# """

# import hashlib
# import time
# import os
# import re
# import json
# from pathlib import Path
# from datetime import datetime
# from urllib.parse import urlparse

# from bs4 import BeautifulSoup

# from django.conf import settings

# from selenium import webdriver
# from selenium.webdriver.chrome.options import Options
# from selenium.webdriver.common.by import By
# from selenium.webdriver.common.keys import Keys
# from selenium.webdriver.support.ui import Select, WebDriverWait
# from selenium.webdriver.support import expected_conditions as EC
# from selenium.common.exceptions import TimeoutException, NoSuchElementException

# from langchain_google_genai import ChatGoogleGenerativeAI
# from langchain_core.prompts import ChatPromptTemplate
# from langchain_core.output_parsers import PydanticOutputParser

# from .schemas import AutomationResponse

# try:
#     import pyperclip
#     PYPERCLIP_AVAILABLE = True
# except ImportError:
#     PYPERCLIP_AVAILABLE = False


# # ─────────────────────────────────────────────────────────────────────────────
# # Constants
# # ─────────────────────────────────────────────────────────────────────────────

# NEXT_KEYWORDS = [
#     "next", "continue", "proceed", "forward",
#     "آگے", "اگلا", "اگلہ",
#     "next step", "next page", "save & next", "save and next", "save & continue",
# ]
# SUBMIT_KEYWORDS = [
#     "submit", "finish", "complete", "send", "apply",
#     "جمع کریں", "submit application", "final submit",
# ]
# LOGIN_KEYWORDS = ["login", "log in", "sign in", "signin", "لاگ ان"]
# NEXT_ID_HINTS  = ["next", "continue", "proceed", "forward", "step"]

# REACT_STEP_TIMEOUT  = 8
# REACT_POLL_INTERVAL = 0.25


# # ─────────────────────────────────────────────────────────────────────────────
# # Smart button finders
# # ─────────────────────────────────────────────────────────────────────────────

# def _btn_text(driver, el):
#     """Full textContent via JS — catches text inside child <span> nodes."""
#     try:
#         return (driver.execute_script("return arguments[0].textContent;", el) or "").strip()
#     except Exception:
#         return (el.text or "").strip()


# def _find_button_by_keywords(driver, keywords):
#     """
#     Generic button finder. Tries in order:
#       1. id/name/class contains a keyword
#       2. textContent contains a keyword
#       3. aria-label contains a keyword
#     Returns WebElement or None.
#     """
#     all_btns = driver.find_elements(
#         By.CSS_SELECTOR, "button, input[type='submit'], a[role='button']"
#     )

#     # Strategy 1: attribute hint
#     for kw in keywords:
#         for el in driver.find_elements(
#             By.CSS_SELECTOR,
#             f"button[id*='{kw}'], button[name*='{kw}'], button[class*='{kw}'], "
#             f"input[type='submit'][id*='{kw}'], a[id*='{kw}']"
#         ):
#             if el.is_displayed() and el.is_enabled():
#                 return el

#     # Strategy 2: textContent
#     for el in all_btns:
#         if not (el.is_displayed() and el.is_enabled()):
#             continue
#         text = _btn_text(driver, el).lower()
#         if any(kw in text for kw in keywords):
#             return el

#     # Strategy 3: aria-label
#     for el in all_btns:
#         if not (el.is_displayed() and el.is_enabled()):
#             continue
#         label = (el.get_attribute("aria-label") or "").lower()
#         if any(kw in label for kw in keywords):
#             return el

#     return None


# def _find_next_button(driver):
#     btn = _find_button_by_keywords(driver, NEXT_KEYWORDS)
#     if btn:
#         print(f"🔍 Next btn: {_btn_text(driver, btn)!r}")
#         return btn
#     # Heuristic: last visible non-back button
#     ignore = {"back", "previous", "cancel", "reset", "واپس", "پچھلا"}
#     all_btns = driver.find_elements(By.CSS_SELECTOR, "button, input[type='submit']")
#     visible  = [
#         el for el in all_btns
#         if el.is_displayed() and el.is_enabled()
#         and not any(x in _btn_text(driver, el).lower() for x in ignore)
#     ]
#     if visible:
#         el = visible[-1]
#         print(f"🔍 Next btn (last-button heuristic): {_btn_text(driver, el)!r}")
#         return el
#     print("⚠️  No Next button found")
#     return None


# def _find_submit_button(driver):
#     btn = _find_button_by_keywords(driver, SUBMIT_KEYWORDS)
#     if btn:
#         print(f"🔍 Submit btn: {_btn_text(driver, btn)!r}")
#         return btn
#     all_btns = driver.find_elements(By.CSS_SELECTOR, "button, input[type='submit']")
#     visible  = [e for e in all_btns if e.is_displayed() and e.is_enabled()]
#     if visible:
#         print(f"🔍 Submit btn (last fallback): {_btn_text(driver, visible[-1])!r}")
#         return visible[-1]
#     return None


# def _find_login_button(driver):
#     btn = _find_button_by_keywords(driver, LOGIN_KEYWORDS)
#     if btn:
#         print(f"🔍 Login btn: {_btn_text(driver, btn)!r}")
#         return btn
#     # Fallback: the only submit button on a login page
#     all_btns = driver.find_elements(
#         By.CSS_SELECTOR, "button[type='submit'], input[type='submit']"
#     )
#     visible = [e for e in all_btns if e.is_displayed() and e.is_enabled()]
#     if visible:
#         print(f"🔍 Login btn (submit fallback): {_btn_text(driver, visible[0])!r}")
#         return visible[0]
#     return None


# # ─────────────────────────────────────────────────────────────────────────────
# # DOM change detection
# # ─────────────────────────────────────────────────────────────────────────────

# def _wait_for_react_hydration(driver, timeout=15):
#     deadline = time.time() + timeout
#     while time.time() < deadline:
#         try:
#             root = driver.find_elements(By.CSS_SELECTOR, "#root, #app, [data-reactroot]")
#             container = root[0] if root else driver.find_element(By.TAG_NAME, "body")
#             inputs = container.find_elements(
#                 By.CSS_SELECTOR, "input:not([type='hidden']), select, textarea"
#             )
#             if any(el.is_displayed() for el in inputs):
#                 return True
#         except Exception:
#             pass
#         time.sleep(REACT_POLL_INTERVAL)
#     return False


# def _get_visible_field_count(driver):
#     try:
#         els = driver.find_elements(
#             By.CSS_SELECTOR, "input:not([type='hidden']), select, textarea"
#         )
#         return len([e for e in els if e.is_displayed()])
#     except Exception:
#         return 0


# def _wait_for_dom_change(driver, prev_count, prev_url, timeout=REACT_STEP_TIMEOUT):
#     deadline = time.time() + timeout
#     while time.time() < deadline:
#         try:
#             if driver.current_url != prev_url:
#                 time.sleep(0.5)
#                 _wait_for_react_hydration(driver, timeout=5)
#                 return True
#             count = _get_visible_field_count(driver)
#             if count != prev_count and count > 0:
#                 time.sleep(0.3)
#                 return True
#         except Exception:
#             pass
#         time.sleep(REACT_POLL_INTERVAL)
#     return False


# def _is_login_page(driver):
#     """Returns True if the current page has a visible password field."""
#     try:
#         pwd = driver.find_elements(By.XPATH, "//input[@type='password']")
#         return any(el.is_displayed() for el in pwd)
#     except Exception:
#         return False


# # ─────────────────────────────────────────────────────────────────────────────
# # Screenshot helpers
# # ─────────────────────────────────────────────────────────────────────────────
# def _uni_slug(url: str) -> str:
#     """
#     Examples:

#     http://localhost:4000/uet
#     -> localhost-4000-uet

#     http://localhost:5000/umt
#     -> localhost-5000-umt
#     """

#     try:
#         parsed = urlparse(url)

#         host = parsed.hostname or "unknown"
#         port = parsed.port or ""

#         path = parsed.path.strip("/")

#         slug_parts = [host]

#         if port:
#             slug_parts.append(str(port))

#         if path:
#             slug_parts.append(path.replace("/", "-"))

#         slug = "-".join(slug_parts)

#         return re.sub(r"[^a-z0-9\-]+", "-", slug.lower()).strip("-")

#     except Exception:
#         return "unknown"


# def _screenshots_dir(student_id, portal_url: str) -> Path:
#     """
#     Returns (and creates) the screenshot folder for this student + university.
#     Path: media/screenshots/<student_id>/<uni_slug>/
#     """
#     slug = _uni_slug(portal_url)
#     d = Path(settings.MEDIA_ROOT) / "screenshots" / str(student_id) / slug
#     d.mkdir(parents=True, exist_ok=True)
#     return d


# def _take_screenshot(driver, student_id, portal_url: str, label: str) -> dict:
#     d        = _screenshots_dir(student_id, portal_url)
#     slug     = _uni_slug(portal_url)
#     filename = f"{label}.png"
#     filepath = d / filename
#     try:
#         driver.save_screenshot(str(filepath))
#         print(f"📸 {filepath}")
#     except Exception as e:
#         print(f"⚠️  Screenshot failed: {e}")
#         return {}
#     return {
#         "label":    label,
#         "filename": filename,
#         "url":      f"{settings.MEDIA_URL}screenshots/{student_id}/{slug}/{filename}",
#     }


# def _save_manifest(student_id, portal_url: str, entries: list):
#     d    = _screenshots_dir(student_id, portal_url)
#     path = d / "manifest.json"
#     with open(path, "w") as f:
#         json.dump({
#             "student_id":  student_id,
#             "portal":      portal_url,
#             "screenshots": [e for e in entries if e],
#         }, f, indent=2)


# # ─────────────────────────────────────────────────────────────────────────────
# # Field extraction helper (shared by scraper)
# # ─────────────────────────────────────────────────────────────────────────────

# def _extract_fields_from_page(driver, include_password=False):
#     """
#     Extracts all visible form fields from the current page.
#     include_password=True is used when scraping the login page.
#     include_password=False (default) skips password fields on form pages.
#     """
#     soup     = BeautifulSoup(driver.page_source, "html.parser")
#     elements = []

#     for el in soup.find_all(["input", "select", "textarea"]):
#         el_type = el.get("type", "text").lower() if el.name == "input" else el.name

#         if el_type == "hidden":
#             continue
#         if el_type == "password" and not include_password:
#             continue

#         if el.get("id"):
#             selector = f"#{el.get('id')}"
#         elif el.get("name"):
#             selector = f"[name='{el.get('name')}']"
#         elif el.get("data-testid"):
#             selector = f"[data-testid='{el.get('data-testid')}']"
#         else:
#             continue

#         # Prefer <label for="..."> text, then fall back to placeholder/aria-label
#         label = ""
#         if el.get("id"):
#             lbl = soup.find("label", attrs={"for": el.get("id")})
#             if lbl:
#                 label = lbl.get_text(strip=True)
#         if not label:
#             label = el.get("placeholder") or el.get("aria-label") or el.get("name") or ""

#         entry = {"selector": selector, "type": el_type, "label": label}
#         if el_type == "file":
#             entry["accept"] = el.get("accept", "")
#         if el.name == "select":
#             entry["options"] = [
#                 o.get_text(strip=True) for o in el.find_all("option")
#                 if o.get_text(strip=True)
#             ]
#         elements.append(entry)

#     return elements


# # ─────────────────────────────────────────────────────────────────────────────
# # AI SERVICE
# # ─────────────────────────────────────────────────────────────────────────────

# class AIService:

#     def __init__(self):
#         api_key = getattr(settings, "GEMINI_API_KEY", None)
#         if not api_key:
#             raise ValueError("GEMINI_API_KEY not set in Django settings.")
#         self.llm = ChatGoogleGenerativeAI(
#             model="gemini-2.5-flash",
#             google_api_key=api_key,
#             temperature=0,
#         )
#         self.parser = PydanticOutputParser(pydantic_object=AutomationResponse)

#     @staticmethod
#     def make_app_id(student_id, url: str) -> int:
#         raw = f"{student_id}:{url}"
#         return int(hashlib.md5(raw.encode()).hexdigest()[:8], 16) % 999999 + 1

#     # ------------------------------------------------------------------
#     # Scrape entire flow: login page (if present) + all form steps
#     # ------------------------------------------------------------------
#     def scrape_full_flow(self, url):
#         """
#         Opens the URL and scrapes:
#           - If a login page is detected: scrapes login fields, performs login,
#             waits for the application form to appear, then scrapes all form steps.
#           - If no login page: scrapes all form steps directly.

#         Returns a list of page dicts:
#           [
#             { "page_type": "login",       "page_number": 0, "fields": [...] },
#             { "page_type": "application", "page_number": 1, "fields": [...] },
#             { "page_type": "application", "page_number": 2, "fields": [...] },
#             ...
#           ]

#         Each page includes the login button / next button / submit button
#         selector so Gemini can emit the correct click/submit actions.
#         """
#         options = Options()
#         options.add_argument("--headless=new")   # full V8 for React
#         options.add_argument("--no-sandbox")
#         options.add_argument("--disable-dev-shm-usage")
#         options.add_argument("--window-size=1920,1080")

#         driver = None
#         pages  = []

#         try:
#             driver = webdriver.Chrome(options=options)
#             driver.get(url)

#             # Wait for initial render
#             _wait_for_react_hydration(driver, timeout=15)

#             # ── LOGIN PAGE ──────────────────────────────────────────────
#             if _is_login_page(driver):
#                 print("🔐 Login page detected during scraping")

#                 # Scrape login fields INCLUDING password
#                 login_fields = _extract_fields_from_page(driver, include_password=True)

#                 # Find the login button and record its selector
#                 login_btn       = _find_login_button(driver)
#                 login_btn_sel   = None
#                 if login_btn:
#                     btn_id = login_btn.get_attribute("id")
#                     login_btn_sel = f"#{btn_id}" if btn_id else "LOGIN_BUTTON"

#                 pages.append({
#                     "page_type":    "login",
#                     "page_number":  0,
#                     "fields":       login_fields,
#                     "submit_selector": login_btn_sel or "LOGIN_BUTTON",
#                 })
#                 print(f"   Scraped {len(login_fields)} login fields")

#                 # Perform login so we can scrape the real form pages
#                 portal_email = "student"
#                 portal_password = "au2024"

#                 if portal_email and portal_password and login_btn:
#                     try:
#                         # Fill credentials
#                         try:
#                             email_el = driver.find_element(By.XPATH, "//input[@type='email']")
#                         except NoSuchElementException:
#                             email_el = driver.find_element(By.XPATH, "//input[@type='text']")
#                         pass_el = driver.find_element(By.XPATH, "//input[@type='password']")
#                         email_el.send_keys(portal_email)
#                         pass_el.send_keys(portal_password)
#                         driver.execute_script("arguments[0].click();", login_btn)

#                         # Wait for login to complete (password field disappears)
#                         WebDriverWait(driver, 15).until(
#                             EC.invisibility_of_element_located(
#                                 (By.XPATH, "//input[@type='password']")
#                             )
#                         )
#                         print("✅ Scraping login succeeded — waiting for form...")
#                         time.sleep(2)
#                         _wait_for_react_hydration(driver, timeout=10)
#                     except Exception as e:
#                         print(f"⚠️  Scraping login failed: {e} — form pages may be incomplete")
#                 else:
#                     print("⚠️  PORTAL_EMAIL/PORTAL_PASSWORD not set or no login button found")

#             # ── APPLICATION FORM PAGES ──────────────────────────────────
#             for step_num in range(1, 11):
#                 print(f"\n🧭 Scraping application page {step_num}...")
#                 time.sleep(0.5)

#                 # Skip if still on login page
#                 if _is_login_page(driver):
#                     print("   Still on login page — login may have failed")
#                     break

#                 fields = _extract_fields_from_page(driver, include_password=False)
#                 print(f"   {len(fields)} fields found")

#                 prev_count = _get_visible_field_count(driver)
#                 prev_url   = driver.current_url

#                 # Find the next/submit button and record its selector too
#                 next_btn   = _find_next_button(driver)
#                 submit_btn = _find_submit_button(driver) if not next_btn else None

#                 next_sel   = None
#                 submit_sel = None

#                 if next_btn:
#                     nid = next_btn.get_attribute("id")
#                     next_sel = f"#{nid}" if nid else "NEXT_BUTTON"
#                 if submit_btn and not next_btn:
#                     sid = submit_btn.get_attribute("id")
#                     submit_sel = f"#{sid}" if sid else "SUBMIT_BUTTON"

#                 pages.append({
#                     "page_type":       "application",
#                     "page_number":     step_num,
#                     "fields":          fields,
#                     "next_selector":   next_sel,
#                     "submit_selector": submit_sel,
#                 })

#                 if not next_btn:
#                     print("   ✅ No Next button — end of form")
#                     break

#                 try:
#                     driver.execute_script(
#                         "arguments[0].scrollIntoView({block:'center'});", next_btn)
#                     driver.execute_script("arguments[0].click();", next_btn)
#                     print("   ▶ Clicked Next — waiting for DOM change...")
#                     changed = _wait_for_dom_change(driver, prev_count, prev_url)
#                     if not changed:
#                         print("   ⚠️  DOM didn't change — may be last step")
#                         break
#                 except Exception as e:
#                     print(f"   ❌ Error clicking Next: {e}")
#                     break

#             return pages

#         finally:
#             if driver:
#                 driver.quit()

#     # ------------------------------------------------------------------
#     # Generate mapping via Gemini
#     # ------------------------------------------------------------------
#     def get_automation_instructions(self, target_url, student_data, app_id):
#         """
#         Scrapes the full portal flow (login + form pages), then asks Gemini
#         to produce a complete mapping including the login step.
#         """
#         pages = self.scrape_full_flow(target_url)
#         if not pages:
#             raise Exception("No pages found — check the portal URL")

#         portal_email    = getattr(settings, "PORTAL_EMAIL", "")
#         portal_password = getattr(settings, "PORTAL_PASSWORD", "")

#         # Inject portal credentials into student_data so Gemini can map them
#         student_data_with_creds = {
#             **student_data,
#             "_portal_email":    portal_email,
#             "_portal_password": portal_password,
#         }

#         system_prompt = """
# You are an expert at mapping student data to multi-page university portal flows.

# The pages list includes:
#   - A "login" page (page_type="login") if the portal requires authentication
#   - One or more "application" pages (page_type="application")

# You must generate a COMPLETE automation plan that covers ALL pages in order:
#   1. Fill login credentials → click login button → wait for form
#   2. Fill application step 1 → click Next → ...
#   3. Fill last step → submit

# Return ONLY valid JSON (no markdown, no backticks). Example structure:

# {{
#   "application_id": <integer>,
#   "url": "<target url>",
#   "steps": [
#     {{
#       "action": "fill",
#       "page_type": "login",
#       "fields": [
#         {{"selector": "#email",    "type": "email",    "value": "<_portal_email value>",    "confidence": 1.0}},
#         {{"selector": "#password", "type": "password", "value": "<_portal_password value>", "confidence": 1.0}}
#       ]
#     }},
#     {{
#       "action": "login_click",
#       "selector": "<submit_selector from login page, or LOGIN_BUTTON>",
#       "wait_ms": 3000
#     }},
#     {{
#       "action": "fill",
#       "page_type": "application",
#       "fields": [
#         {{"selector": "#name", "type": "text", "value": "Ali Khan", "confidence": 0.95}},
#         {{"selector": "#photo","type": "file", "value": "/abs/path/photo.jpg", "confidence": 0.9}}
#       ]
#     }},
#     {{"action": "click",  "selector": "NEXT_BUTTON",   "wait_ms": 2000}},
#     {{"action": "fill",   "page_type": "application", "fields": [...]}},
#     {{"action": "submit", "selector": "SUBMIT_BUTTON", "wait_ms": 3000}}
#   ]
# }}

# RULES:
# 1. LOGIN STEP:
#    - Map "_portal_email" → the email/username input field on the login page.
#    - Map "_portal_password" → the password input field on the login page.
#    - Use the exact selectors from the login page fields.
#    - The login click action must use "action": "login_click" so the automation
#      engine knows to wait for the password field to disappear after clicking.

# 2. CLICK / SUBMIT selectors:
#    - For click (Next) actions: use "NEXT_BUTTON" unless the page gave a specific
#      next_selector — in that case use the specific one.
#    - For submit: use "SUBMIT_BUTTON" unless the page gave a specific submit_selector.
#    - For login_click: use the submit_selector from the login page, or "LOGIN_BUTTON".
#    - NEVER invent button CSS selectors — the engine resolves these at runtime.

# 3. FILL selectors must be the exact strings from the scraped page fields.

# 4. FILE FIELDS:
#    photo/picture/avatar  → student.photo
#    cnic/id_card          → student.cnic_image
#    transcript/result     → student.transcript
#    matric                → student.matric_certificate
#    inter/fsc/hssc        → student.inter_certificate
#    domicile              → student.domicile
#    Set value="" and confidence=0.0 if no match.

# 5. confidence: 1.0=exact, 0.5=inferred, 0.0=no match.
# 6. Include ALL fields even if confidence is 0.
# 7. Return ONLY JSON.
# """

#         prompt = ChatPromptTemplate.from_messages([
#             ("system", system_prompt),
#             ("human",
#              "STUDENT DATA (includes _portal_email and _portal_password):\n{student_data}\n\n"
#              "SCRAPED PAGES (login + application steps):\n{pages_data}\n\n"
#              "URL: {url}\nAPP ID: {app_id}"),
#         ])

#         chain  = prompt | self.llm | self.parser
#         result = chain.invoke({
#             "student_data": json.dumps(student_data_with_creds, indent=2),
#             "pages_data":   json.dumps(pages, indent=2),
#             "url":          target_url,
#             "app_id":       app_id,
#         })
#         return result


# # ─────────────────────────────────────────────────────────────────────────────
# # AUTOMATION SERVICE
# # ─────────────────────────────────────────────────────────────────────────────

# class AutomationService:

#     # ── Normalization ──────────────────────────────────────────────────────

#     def normalize_value(self, field_name, value):
#         if not value:
#             return value
#         value    = str(value).strip()
#         city_map = {
#             "lahore": "Punjab", "karachi": "Sindh", "islamabad": "Islamabad",
#             "peshawar": "KPK",  "quetta": "Balochistan",
#         }
#         if field_name and "province" in field_name.lower():
#             return city_map.get(value.lower(), value)
#         return value

#     def normalize_course(self, value):
#         if not value:
#             return []
#         v = str(value).lower().strip()
#         m = {
#             "cs":                     ["cs","computer science","bscs"],
#             "bscs":                   ["bscs","computer science","cs"],
#             "computer science":       ["computer science","cs","bscs"],
#             "bsse":                   ["bsse","software engineering","software"],
#             "software engineering":   ["software engineering","bsse","software"],
#             "bsit":                   ["bsit","information technology","it","bs information technology","bs (it)"],
#             "it":                     ["it","information technology","bsit"],
#             "information technology": ["information technology","bsit","it","bs information technology"],
#             "bba":                    ["bba","business administration","business"],
#             "business administration":["business administration","bba","business"],
#             "finance":                ["finance","bba finance","business finance"],
#             "mbbs":                   ["mbbs","medicine","medical"],
#             "bds":                    ["bds","dentistry","dental"],
#             "nursing":                ["nursing","bsn","bs nursing"],
#             "psychology":             ["psychology","bs psychology"],
#             "sociology":              ["sociology","bs sociology"],
#             "llb":                    ["llb","law","bachelor of law","legal"],
#             "law":                    ["law","llb","legal studies","legal"],
#         }
#         return m.get(v, [v])

#     def normalize_date(self, value):
#         if not value:
#             return value
#         fmts = [
#             "%Y-%m-%d","%Y %m %d","%Y/%m/%d",
#             "%d-%m-%Y","%d/%m/%Y","%d %m %Y",
#             "%m/%d/%Y","%m-%d-%Y",
#             "%d %b %Y","%d %B %Y","%B %d, %Y","%b %d, %Y",
#         ]
#         dt = None
#         for fmt in fmts:
#             try: dt = datetime.strptime(str(value).strip(), fmt); break
#             except Exception: continue
#         if not dt:
#             return {"iso":value,"dmy":value,"dmy_dash":value,"dmy_slash":value,
#                     "mdy":value,"long":value,"dt":None,"day":"","month":"","year":""}
#         return {
#             "iso":       dt.strftime("%Y-%m-%d"),
#             "dmy":       dt.strftime("%d %m %Y"),
#             "dmy_dash":  dt.strftime("%d-%m-%Y"),
#             "dmy_slash": dt.strftime("%d/%m/%Y"),
#             "mdy":       dt.strftime("%m/%d/%Y"),
#             "long":      dt.strftime("%d %b %Y"),
#             "dt":        dt,
#             "day":       dt.strftime("%d"),
#             "month":     dt.strftime("%m"),
#             "year":      dt.strftime("%Y"),
#         }

#     # ── React helpers ──────────────────────────────────────────────────────

#     def is_react_page(self, driver):
#         return driver.execute_script(
#             "return !!(window.__REACT_DEVTOOLS_GLOBAL_HOOK__ || "
#             "document.querySelector('[data-reactroot]') || "
#             "document.querySelector('#root'))"
#         )

#     def react_set_value(self, driver, element, value):
#         driver.execute_script("""
#             var el = arguments[0], val = arguments[1];
#             var proto = el.tagName.toLowerCase() === 'textarea'
#                 ? window.HTMLTextAreaElement.prototype
#                 : window.HTMLInputElement.prototype;
#             Object.getOwnPropertyDescriptor(proto, 'value').set.call(el, val);
#             el.dispatchEvent(new Event('input',  { bubbles: true }));
#             el.dispatchEvent(new Event('change', { bubbles: true }));
#         """, element, value)

#     # ── Date helpers ───────────────────────────────────────────────────────

#     def detect_date_format(self, element):
#         hint = " ".join([
#             element.get_attribute("placeholder") or "",
#             element.get_attribute("pattern")     or "",
#             element.get_attribute("data-format") or "",
#         ]).lower()
#         if any(x in hint for x in ["dd-mm-yyyy","dd/mm/yyyy","dd mm yyyy"]):
#             return "dmy_slash" if "/" in hint else "dmy_dash"
#         if any(x in hint for x in ["mm/dd/yyyy","mm-dd-yyyy"]): return "mdy"
#         if "yyyy-mm-dd" in hint: return "iso"
#         return None

#     def fill_date_react(self, driver, element, formats):
#         input_type = (element.get_attribute("type") or "").lower()
#         fmt_key    = self.detect_date_format(element)
#         if input_type == "date":
#             self.fill_react_native_date(driver, element, formats, fmt_key); return
#         formatted = formats.get(fmt_key, formats["dmy_dash"]) if fmt_key else formats["dmy_dash"]
#         self.react_set_value(driver, element, formatted); time.sleep(0.2)
#         if element.get_attribute("value"): return
#         if PYPERCLIP_AVAILABLE:
#             try:
#                 pyperclip.copy(formatted)
#                 element.send_keys(Keys.CONTROL + "v"); time.sleep(0.3)
#                 if element.get_attribute("value"): return
#             except Exception: pass
#         driver.execute_script("arguments[0].click();", element)
#         element.send_keys(Keys.CONTROL + "a"); element.send_keys(Keys.DELETE)
#         for char in formatted: element.send_keys(char); time.sleep(0.04)

#     def fill_react_native_date(self, driver, element, formats, fmt_key):
#         self.react_set_value(driver, element, formats["iso"]); time.sleep(0.2)
#         if element.get_attribute("value") == formats["iso"]: return
#         driver.execute_script("arguments[0].click();", element)
#         element.send_keys(formats["month"]); time.sleep(0.1)
#         element.send_keys(formats["day"]);   time.sleep(0.1)
#         element.send_keys(formats["year"])

#     def fill_native_date(self, driver, element, formats):
#         iso = formats["iso"]
#         driver.execute_script("arguments[0].value = arguments[1];", element, iso)
#         driver.execute_script(
#             "arguments[0].dispatchEvent(new Event('input',{bubbles:true}));"
#             "arguments[0].dispatchEvent(new Event('change',{bubbles:true}));", element)
#         if element.get_attribute("value") != iso:
#             element.clear(); element.send_keys(iso)

#     def fill_custom_date(self, driver, element, formats):
#         fmt_key = self.detect_date_format(element)
#         if fmt_key:
#             element.clear(); time.sleep(0.2)
#             element.send_keys(formats.get(fmt_key, formats["dmy_dash"]))
#         else:
#             for key in ["dmy_dash","dmy_slash","dmy","iso","mdy"]:
#                 element.clear(); time.sleep(0.2)
#                 element.send_keys(formats.get(key,"")); time.sleep(0.3)
#                 if element.get_attribute("value"): return
#             driver.execute_script("arguments[0].value = arguments[1];", element, formats["dmy_dash"])
#             driver.execute_script(
#                 "arguments[0].dispatchEvent(new Event('input',{bubbles:true}));"
#                 "arguments[0].dispatchEvent(new Event('change',{bubbles:true}));", element)

#     # ── File path resolver ─────────────────────────────────────────────────

#     def resolve_file_path(self, value):
#         if not value:
#             raise ValueError("File path is empty")
#         path = str(value).strip()
#         if os.path.isabs(path) and os.path.isfile(path): return path
#         media_root = getattr(settings, "MEDIA_ROOT", "")
#         if media_root:
#             clean = path.lstrip("/\\")
#             if clean.startswith("media/") or clean.startswith("media\\"):
#                 clean = clean[6:]
#             candidate = os.path.join(str(media_root), clean)
#             if os.path.isfile(candidate): return os.path.abspath(candidate)
#         base_dir = getattr(settings, "BASE_DIR", "")
#         if base_dir:
#             candidate = os.path.join(str(base_dir), path.lstrip("/\\"))
#             if os.path.isfile(candidate): return os.path.abspath(candidate)
#         abs_attempt = os.path.abspath(path)
#         if os.path.isfile(abs_attempt): return abs_attempt
#         raise FileNotFoundError(
#             f"File not found: '{value}' — tried MEDIA_ROOT='{media_root}', BASE_DIR='{base_dir}'"
#         )

#     # ── wait_for_element ───────────────────────────────────────────────────

#     def wait_for_element(self, driver, selector, timeout=10, clickable=False):
#         # Magic smart-finder values
#         if selector in ("NEXT_BUTTON",  "next_button"):
#             deadline = time.time() + timeout
#             while time.time() < deadline:
#                 el = _find_next_button(driver)
#                 if el: return el
#                 time.sleep(REACT_POLL_INTERVAL)
#             raise TimeoutException("No Next button found")

#         if selector in ("SUBMIT_BUTTON", "submit_button"):
#             deadline = time.time() + timeout
#             while time.time() < deadline:
#                 el = _find_submit_button(driver)
#                 if el: return el
#                 time.sleep(REACT_POLL_INTERVAL)
#             raise TimeoutException("No Submit button found")

#         if selector in ("LOGIN_BUTTON", "login_button"):
#             deadline = time.time() + timeout
#             while time.time() < deadline:
#                 el = _find_login_button(driver)
#                 if el: return el
#                 time.sleep(REACT_POLL_INTERVAL)
#             raise TimeoutException("No Login button found")

#         # :contains() → case-insensitive XPath
#         if ":contains(" in selector:
#             match = re.match(r"^(\w+)?:contains\(['\"](.+?)['\"]\)$", selector.strip())
#             if match:
#                 tag, text = match.group(1) or "*", match.group(2).lower()
#             else:
#                 tag  = "*"
#                 text = selector.split(":contains(")[1].strip("'\")")
#             xpath = (
#                 f"//{tag}[contains("
#                 f"translate(normalize-space(.),"
#                 f"'ABCDEFGHIJKLMNOPQRSTUVWXYZ','abcdefghijklmnopqrstuvwxyz'),"
#                 f"'{text.lower()}')]"
#             )
#             wait = WebDriverWait(driver, timeout)
#             cond = EC.element_to_be_clickable if clickable else EC.presence_of_element_located
#             try:
#                 return wait.until(cond((By.XPATH, xpath)))
#             except TimeoutException:
#                 # Fall through to keyword-based smart finder
#                 fn = _find_login_button  if any(kw in selector.lower() for kw in LOGIN_KEYWORDS) \
#                      else _find_next_button if any(kw in selector.lower() for kw in NEXT_KEYWORDS) \
#                      else _find_submit_button
#                 el = fn(driver)
#                 if el: return el
#                 raise

#         # Standard selectors
#         wait = WebDriverWait(driver, timeout)
#         by   = By.CSS_SELECTOR
#         if selector.startswith("#"):
#             by, selector = By.ID, selector[1:]
#         elif selector.startswith("//"):
#             by = By.XPATH
#         elif selector.startswith("[name="):
#             by, selector = By.NAME, selector.split("'")[1]

#         # File inputs are invisible — always use presence
#         try:
#             el_type = driver.find_element(by, selector).get_attribute("type") or ""
#             if el_type == "file": clickable = False
#         except Exception:
#             pass

#         cond = EC.element_to_be_clickable if clickable else EC.presence_of_element_located
#         return wait.until(cond((by, selector)))

#     # ── fill_field ─────────────────────────────────────────────────────────

#     def fill_field(self, driver, element, field_type, value):
#         tag        = element.tag_name.lower()
#         input_type = (element.get_attribute("type") or "").lower()
#         is_react   = self.is_react_page(driver)

#         # FILE — send_keys only, never clear/value setter
#         if field_type == "file" or input_type == "file":
#             try:
#                 abs_path = self.resolve_file_path(value)
#             except (FileNotFoundError, ValueError) as e:
#                 raise Exception(f"File upload failed — {e}")
#             driver.execute_script("""
#                 arguments[0].style.display    = 'block';
#                 arguments[0].style.opacity    = '1';
#                 arguments[0].style.visibility = 'visible';
#             """, element)
#             time.sleep(0.2)
#             element.send_keys(abs_path)
#             driver.execute_script(
#                 "arguments[0].dispatchEvent(new Event('change',{bubbles:true}));", element)
#             print(f"✅ File: {os.path.basename(abs_path)}")
#             return

#         # PASSWORD — plain send_keys (never react_set_value; portals track state internally)
#         if input_type == "password":
#             element.clear()
#             element.send_keys(str(value))
#             return

#         # CHECKBOX / RADIO
#         if input_type in ["checkbox", "radio"]:
#             if str(value).lower() in ["true","1","yes"]:
#                 driver.execute_script("arguments[0].click();", element)
#             return

#         # DATE
#         if field_type == "date" or input_type == "date":
#             formats = self.normalize_date(value)
#             if not formats.get("dt"):
#                 element.clear(); element.send_keys(str(value)); return
#             if is_react:
#                 self.fill_date_react(driver, element, formats)
#             elif input_type == "date":
#                 fmt_key = self.detect_date_format(element)
#                 (self.fill_custom_date if (fmt_key and fmt_key != "iso") else self.fill_native_date)(
#                     driver, element, formats)
#             else:
#                 self.fill_custom_date(driver, element, formats)
#             return

#         # SELECT
#         if tag == "select":
#             sel     = Select(element)
#             options = [o.text.strip() for o in sel.options]
#             opt_low = [o.lower() for o in options]
#             for target in self.normalize_course(value):
#                 t = target.lower().strip()
#                 for i, opt in enumerate(opt_low):
#                     if opt == t:                           sel.select_by_visible_text(options[i]); return
#                 for i, opt in enumerate(opt_low):
#                     if opt and opt in t:                  sel.select_by_visible_text(options[i]); return
#                 for i, opt in enumerate(opt_low):
#                     if t and t in opt:                    sel.select_by_visible_text(options[i]); return
#                 for i, opt in enumerate(opt_low):
#                     if set(t.split()) & set(opt.split()): sel.select_by_visible_text(options[i]); return
#             raise Exception(f"Dropdown option not found for '{value}'. Available: {options}")

#         # TEXT / TEXTAREA / EMAIL
#         if tag in ["input", "textarea"]:
#             self.react_set_value(driver, element, str(value)) if is_react \
#                 else (element.clear() or element.send_keys(str(value)))
#             return

#         # FALLBACK
#         driver.execute_script("arguments[0].value = arguments[1];", element, value)
#         driver.execute_script(
#             "arguments[0].dispatchEvent(new Event('change',{bubbles:true}));", element)

#     # ── Main runner ────────────────────────────────────────────────────────

#     def run(self, mapping: dict) -> dict:
#         """
#         Executes the full automation flow from the mapping JSON.
#         Step types:
#           "fill"        — fill form fields (login page or application page)
#           "login_click" — click the login button and wait for form to load
#           "click"       — click Next button between application steps
#           "submit"      — click the final submit button

#         Screenshots (3 total, stored in media/screenshots/<student_id>/<uni_slug>/):
#           1. after_login.png    — right after login succeeds
#           2. before_submit.png  — after last fill step, scrolled to top,
#                                   all data visible before submit is clicked
#           3. after_submit.png   — after submit button is clicked
#         """
#         url        = mapping.get("url")
#         steps      = mapping.get("steps", [])
#         student_id = mapping.get("application_id", 0)  # profile id used as student id

#         if not url:
#             return {"status":"failed","message":"No URL provided","screenshots":[]}

#         options = Options()
#         options.add_argument("--start-maximized")
#         # Uncomment to run headless:
#         # options.add_argument("--headless=new")

#         driver = webdriver.Chrome(options=options)
#         driver.get(url)
#         _wait_for_react_hydration(driver, timeout=15)

#         completed_steps = 0
#         screenshot_log  = []

#         # Find the index of the last "fill" step with page_type="application"
#         # so we know exactly when to take the before_submit screenshot
#         last_app_fill_idx = None
#         for i, s in enumerate(steps):
#             if s.get("action") == "fill" and s.get("page_type") == "application":
#                 last_app_fill_idx = i

#         def _snap(label):
#             entry = _take_screenshot(driver, student_id, url, label)
#             if entry:
#                 screenshot_log.append(entry)

#         try:
#             for step_idx, step in enumerate(steps):
#                 action = step.get("action")

#                 # ── FILL (login page or application page) ─────────────────
#                 if action == "fill":
#                     page_type = step.get("page_type", "application")
#                     print(f"\n📝 Fill step {step_idx} [{page_type}]")

#                     for field in step.get("fields", []):
#                         selector   = field.get("selector")
#                         field_type = (field.get("type") or "text").lower()
#                         raw_value  = field.get("value")

#                         if (raw_value is None or raw_value == "") and field_type != "file":
#                             continue
#                         if field_type == "file" and not raw_value:
#                             print(f"⏭️  No file path for {selector}")
#                             continue

#                         value = self.normalize_value(selector, raw_value)
#                         print(f"   🖊  [{field_type}] {selector} → {value!r}")

#                         try:
#                             element = self.wait_for_element(
#                                 driver, selector, clickable=(field_type != "file"))
#                             if field_type != "file":
#                                 driver.execute_script(
#                                     "arguments[0].scrollIntoView({block:'center'});", element)
#                             self.fill_field(driver, element, field_type, value)
#                             time.sleep(0.2)
#                         except Exception as e:
#                             print(f"   ❌ Failed {selector}: {e}")
#                             _save_manifest(student_id, url, screenshot_log)
#                             driver.quit()
#                             return {
#                                 "status":"failed","message":f"Error filling {selector}",
#                                 "error":str(e),"completed_steps":completed_steps,
#                                 "screenshots":screenshot_log,
#                             }

#                     # Screenshot 2: taken only after the LAST application fill step,
#                     # showing the fully filled form before submit is clicked
#                     if step_idx == last_app_fill_idx:
#                         time.sleep(0.7)
#                         driver.execute_script("window.scrollTo(0, 0);")
#                         time.sleep(0.2)
#                         _snap("before_submit")
#                         print("📸 before_submit screenshot taken")

#                     completed_steps += 1

#                 # ── LOGIN CLICK — click login btn, wait for form to appear ──
#                 elif action == "login_click":
#                     selector = step.get("selector", "LOGIN_BUTTON")
#                     wait_ms  = step.get("wait_ms", 3000)
#                     print(f"\n🔐 Login click (selector: {selector!r})")

#                     element = None
#                     try:
#                         element = self.wait_for_element(driver, selector, clickable=True)
#                     except Exception as e:
#                         print(f"⚠️  Login button '{selector}' not found: {e}")
#                         element = _find_login_button(driver)

#                     if not element:
#                         _save_manifest(student_id, url, screenshot_log)
#                         driver.quit()
#                         return {
#                             "status":"failed","message":"Login button not found",
#                             "completed_steps":completed_steps,"screenshots":screenshot_log,
#                         }

#                     driver.execute_script("arguments[0].scrollIntoView({block:'center'});", element)
#                     driver.execute_script("arguments[0].click();", element)
#                     print("   ▶ Clicked login — waiting for password field to disappear...")

#                     # Wait for login to complete: password field disappears
#                     try:
#                         WebDriverWait(driver, 15).until(
#                             EC.invisibility_of_element_located(
#                                 (By.XPATH, "//input[@type='password']")
#                             )
#                         )
#                         print("   ✅ Login successful — form is now visible")
#                         time.sleep(1.5)
#                         _wait_for_react_hydration(driver, timeout=10)
#                     except TimeoutException:
#                         _save_manifest(student_id, url, screenshot_log)
#                         driver.quit()
#                         return {
#                             "status":"failed",
#                             "message":"Login timed out — password field never disappeared. Check credentials.",
#                             "completed_steps":completed_steps,"screenshots":screenshot_log,
#                         }

#                     # Screenshot 1: right after login succeeds, form is visible
#                     time.sleep(0.5)
#                     driver.execute_script("window.scrollTo(0, 0);")
#                     time.sleep(0.2)
#                     _snap("after_login")
#                     print("📸 after_login screenshot taken")
#                     completed_steps += 1

#                 # ── CLICK (Next between application steps) ─────────────────
#                 elif action == "click":
#                     selector   = step.get("selector", "NEXT_BUTTON")
#                     wait_ms    = step.get("wait_ms", 1500)
#                     prev_count = _get_visible_field_count(driver)
#                     prev_url   = driver.current_url

#                     print(f"\n▶  Next click (selector: {selector!r})")

#                     element = None
#                     try:
#                         element = self.wait_for_element(driver, selector, clickable=True)
#                     except Exception as e:
#                         print(f"⚠️  Next selector failed: {e} — trying smart finder")
#                         element = _find_next_button(driver)

#                     if not element:
#                         _save_manifest(student_id, url, screenshot_log)
#                         driver.quit()
#                         return {
#                             "status":"failed","message":"Next button not found",
#                             "completed_steps":completed_steps,"screenshots":screenshot_log,
#                         }

#                     driver.execute_script("arguments[0].scrollIntoView({block:'center'});", element)
#                     driver.execute_script("arguments[0].click();", element)
                    
#                     completed_steps += 1

#                     changed = _wait_for_dom_change(driver, prev_count, prev_url)
#                     if not changed:
#                         print("   ⚠️  DOM unchanged — using wait_ms fallback")
#                         time.sleep(wait_ms / 1000)


#                 # ── SUBMIT ─────────────────────────────────────────────────
#                 elif action == "submit":
#                     selector = step.get("selector", "SUBMIT_BUTTON")
#                     wait_ms  = step.get("wait_ms", 3000)
                    
#                     completed_steps += 1
#                     time.sleep(0.3)
#                     _snap("submittt")
#                     print("📸submittt screenshot taken")
#                     print(f"\n✅ Submit (selector: {selector!r})")

#                     element = None
#                     try:
#                         element = self.wait_for_element(driver, selector, clickable=True)
#                     except Exception as e:
#                         print(f"⚠️  Submit selector failed: {e} — trying smart finder")
#                         element = _find_submit_button(driver)

#                     if not element:
#                         _save_manifest(student_id, url, screenshot_log)
#                         driver.quit()
#                         return {
#                             "status":"failed","message":"Submit button not found",
#                             "completed_steps":completed_steps,"screenshots":screenshot_log,
#                         }

#                     try:
#                         driver.execute_script(
#                             "arguments[0].scrollIntoView({block:'center'});", element)
#                         driver.execute_script("arguments[0].click();", element)
#                         time.sleep(wait_ms / 1000)
#                     except Exception as e:
#                         _save_manifest(student_id, url, screenshot_log)
#                         driver.quit()
#                         return {
#                             "status":"failed","message":"Submit click failed",
#                             "error":str(e),"completed_steps":completed_steps,
#                             "screenshots":screenshot_log,
#                         }

#                     # Screenshot 3: after submit button is clicked
#                     driver.execute_script("window.scrollTo(0, 0);")
#                     time.sleep(0.3)
#                     _snap("after_submit")
#                     print("📸 after_submit screenshot taken")

#                     _save_manifest(student_id, url, screenshot_log)
#                     driver.quit()
#                     return {
#                         "status":"success","message":"Form submitted successfully",
#                         "completed_steps":completed_steps + 1,"screenshots":screenshot_log,
#                     }

#             _save_manifest(student_id, url, screenshot_log)
#             driver.quit()
#             return {"status":"success","completed_steps":completed_steps,
#                     "screenshots":screenshot_log}

#         except Exception as e:
#             try:
#                 _save_manifest(student_id, url, screenshot_log)
#                 driver.quit()
#             except Exception:
#                 pass
#             return {"status":"failed","error":str(e),"screenshots":screenshot_log}

# multiple 

# """
# automation_pipeline/services.py  —  FIXED VERSION

# KEY FIXES IN THIS VERSION:

# 1. DOM CHANGE DETECTION — completely rewritten
#    - No longer uses URL changes or input COUNT changes
#    - Now hashes the FULL visible form/container innerHTML
#    - Uses multiple hash strategies: form tag, main container, full body
#    - Waits until the hash changes before declaring a new step
#    - This correctly handles React SPAs where URL never changes and
#      field count may be identical across steps

# 2. SCRAPER CALL SITE FIX
#    - scrape_full_flow() was passing prev_signature to _wait_for_dom_change()
#      but the function signature expected prev_count + prev_url (old signature)
#    - Now the function only takes prev_signature — fully consistent

# 3. UPLOAD FIELD DETECTION — now uses Selenium live DOM inspection
#    - BeautifulSoup static HTML misses React-rendered file inputs
#    - New _extract_fields_selenium() uses driver.find_elements() directly
#    - Explicitly detects:
#        * input[type="file"] (including hidden/invisible ones)
#        * React upload buttons by text: "upload", "browse", "click document", etc.
#        * drag-drop containers with data-upload / dropzone attributes

# 4. STEP LIMIT — raised from 10 to 15 pages to handle longer forms
# """

# import hashlib
# import time
# import os
# import re
# import json
# from pathlib import Path
# from datetime import datetime
# from urllib.parse import urlparse

# from bs4 import BeautifulSoup

# from django.conf import settings

# from selenium import webdriver
# from selenium.webdriver.chrome.options import Options
# from selenium.webdriver.common.by import By
# from selenium.webdriver.common.keys import Keys
# from selenium.webdriver.support.ui import Select, WebDriverWait
# from selenium.webdriver.support import expected_conditions as EC
# from selenium.common.exceptions import TimeoutException, NoSuchElementException

# from langchain_google_genai import ChatGoogleGenerativeAI
# from langchain_core.prompts import ChatPromptTemplate
# from langchain_core.output_parsers import PydanticOutputParser

# from .schemas import AutomationResponse

# try:
#     import pyperclip
#     PYPERCLIP_AVAILABLE = True
# except ImportError:
#     PYPERCLIP_AVAILABLE = False


# # ─────────────────────────────────────────────────────────────────────────────
# # Constants
# # ─────────────────────────────────────────────────────────────────────────────

# NEXT_KEYWORDS = [
#     "next", "continue", "proceed", "forward",
#     "آگے", "اگلا", "اگلہ",
#     "next step", "next page", "save & next", "save and next", "save & continue",
# ]
# SUBMIT_KEYWORDS = [
#     "submit", "finish", "complete", "send", "apply",
#     "جمع کریں", "submit application", "final submit",
# ]
# LOGIN_KEYWORDS  = ["login", "log in", "sign in", "signin", "لاگ ان"]
# NEXT_ID_HINTS   = ["next", "continue", "proceed", "forward", "step"]
# UPLOAD_KEYWORDS = ["upload", "browse", "click document", "choose file", "select file",
#                    "attach", "drag", "drop file", "pick file"]

# REACT_STEP_TIMEOUT  = 8
# REACT_POLL_INTERVAL = 0.25
# MAX_FORM_STEPS      = 15   # raised from 10


# # ─────────────────────────────────────────────────────────────────────────────
# # Smart button finders
# # ─────────────────────────────────────────────────────────────────────────────

# def _btn_text(driver, el):
#     try:
#         return (driver.execute_script("return arguments[0].textContent;", el) or "").strip()
#     except Exception:
#         return (el.text or "").strip()


# def _find_button_by_keywords(driver, keywords):
#     all_btns = driver.find_elements(
#         By.CSS_SELECTOR, "button, input[type='submit'], a[role='button']"
#     )
#     for kw in keywords:
#         for el in driver.find_elements(
#             By.CSS_SELECTOR,
#             f"button[id*='{kw}'], button[name*='{kw}'], button[class*='{kw}'], "
#             f"input[type='submit'][id*='{kw}'], a[id*='{kw}']"
#         ):
#             if el.is_displayed() and el.is_enabled():
#                 return el
#     for el in all_btns:
#         if not (el.is_displayed() and el.is_enabled()):
#             continue
#         text = _btn_text(driver, el).lower()
#         if any(kw in text for kw in keywords):
#             return el
#     for el in all_btns:
#         if not (el.is_displayed() and el.is_enabled()):
#             continue
#         label = (el.get_attribute("aria-label") or "").lower()
#         if any(kw in label for kw in keywords):
#             return el
#     return None


# def _find_next_button(driver):
#     btn = _find_button_by_keywords(driver, NEXT_KEYWORDS)
#     if btn:
#         print(f"🔍 Next btn: {_btn_text(driver, btn)!r}")
#         return btn
#     ignore = {"back", "previous", "cancel", "reset", "واپس", "پچھلا"}
#     all_btns = driver.find_elements(By.CSS_SELECTOR, "button, input[type='submit']")
#     visible  = [
#         el for el in all_btns
#         if el.is_displayed() and el.is_enabled()
#         and not any(x in _btn_text(driver, el).lower() for x in ignore)
#     ]
#     if visible:
#         el = visible[-1]
#         print(f"🔍 Next btn (last-button heuristic): {_btn_text(driver, el)!r}")
#         return el
#     print("⚠️  No Next button found")
#     return None


# def _find_submit_button(driver):
#     btn = _find_button_by_keywords(driver, SUBMIT_KEYWORDS)
#     if btn:
#         print(f"🔍 Submit btn: {_btn_text(driver, btn)!r}")
#         return btn
#     all_btns = driver.find_elements(By.CSS_SELECTOR, "button, input[type='submit']")
#     visible  = [e for e in all_btns if e.is_displayed() and e.is_enabled()]
#     if visible:
#         print(f"🔍 Submit btn (last fallback): {_btn_text(driver, visible[-1])!r}")
#         return visible[-1]
#     return None


# def _find_login_button(driver):
#     btn = _find_button_by_keywords(driver, LOGIN_KEYWORDS)
#     if btn:
#         print(f"🔍 Login btn: {_btn_text(driver, btn)!r}")
#         return btn
#     all_btns = driver.find_elements(
#         By.CSS_SELECTOR, "button[type='submit'], input[type='submit']"
#     )
#     visible = [e for e in all_btns if e.is_displayed() and e.is_enabled()]
#     if visible:
#         print(f"🔍 Login btn (submit fallback): {_btn_text(driver, visible[0])!r}")
#         return visible[0]
#     return None


# # ─────────────────────────────────────────────────────────────────────────────
# # DOM CHANGE DETECTION  ← completely rewritten
# # ─────────────────────────────────────────────────────────────────────────────

# def _get_form_signature(driver):
#     """
#     Returns a stable MD5 hash of the currently visible form HTML.

#     Strategy (tries in order, uses first that works):
#       1. The first VISIBLE <form> element's innerHTML
#       2. A React container: #root, #app, main, [role="main"]
#       3. Full document body innerHTML (last resort)

#     Hashing innerHTML (not just field count or URL) is reliable for
#     React SPAs because React replaces the internal DOM on step change
#     even when URL and field count stay the same.
#     """
#     try:
#         # Strategy 1: visible <form>
#         forms = driver.find_elements(By.TAG_NAME, "form")
#         for f in forms:
#             try:
#                 if f.is_displayed():
#                     html = f.get_attribute("innerHTML") or ""
#                     if len(html) > 50:
#                         return hashlib.md5(html.encode("utf-8", errors="replace")).hexdigest()
#             except Exception:
#                 continue

#         # Strategy 2: React root / main content container
#         for selector in ["main", "[role='main']", "#root", "#app", ".app", "[data-reactroot]"]:
#             try:
#                 els = driver.find_elements(By.CSS_SELECTOR, selector)
#                 for el in els:
#                     if el.is_displayed():
#                         html = el.get_attribute("innerHTML") or ""
#                         if len(html) > 50:
#                             return hashlib.md5(html.encode("utf-8", errors="replace")).hexdigest()
#             except Exception:
#                 continue

#         # Strategy 3: full body
#         body = driver.find_element(By.TAG_NAME, "body")
#         html = body.get_attribute("innerHTML") or ""
#         return hashlib.md5(html.encode("utf-8", errors="replace")).hexdigest()

#     except Exception:
#         return ""


# def _wait_for_dom_change(driver, prev_signature, timeout=12):
#     """
#     Polls until the form signature changes from prev_signature.
#     Returns True if change detected, False if timed out.

#     timeout raised to 12s to handle slow React renders.
#     """
#     deadline = time.time() + timeout
#     while time.time() < deadline:
#         try:
#             new_sig = _get_form_signature(driver)
#             if new_sig and new_sig != prev_signature:
#                 # Small grace period for React to finish rendering
#                 time.sleep(0.6)
#                 _wait_for_react_hydration(driver, timeout=5)
#                 return True
#         except Exception:
#             pass
#         time.sleep(0.25)
#     return False


# def _wait_for_react_hydration(driver, timeout=15):
#     deadline = time.time() + timeout
#     while time.time() < deadline:
#         try:
#             root   = driver.find_elements(By.CSS_SELECTOR, "#root, #app, [data-reactroot]")
#             container = root[0] if root else driver.find_element(By.TAG_NAME, "body")
#             inputs = container.find_elements(
#                 By.CSS_SELECTOR, "input:not([type='hidden']), select, textarea"
#             )
#             if any(el.is_displayed() for el in inputs):
#                 return True
#         except Exception:
#             pass
#         time.sleep(REACT_POLL_INTERVAL)
#     return False


# def _is_login_page(driver):
#     try:
#         pwd = driver.find_elements(By.XPATH, "//input[@type='password']")
#         return any(el.is_displayed() for el in pwd)
#     except Exception:
#         return False


# # ─────────────────────────────────────────────────────────────────────────────
# # FIELD EXTRACTION  ← now uses live Selenium DOM + upload detection
# # ─────────────────────────────────────────────────────────────────────────────

# def _extract_fields_from_page(driver, include_password=False):
#     """
#     PRIMARY: BeautifulSoup static parse (fast, catches most fields).
#     THEN: Selenium live DOM pass to catch React-rendered file inputs
#           and upload components that BS4 misses.
#     """
#     fields       = _extract_fields_bs4(driver, include_password)
#     extra_fields = _extract_upload_fields_selenium(driver, fields)

#     seen = {f["selector"] for f in fields}
#     for ef in extra_fields:
#         if ef["selector"] not in seen:
#             fields.append(ef)
#             seen.add(ef["selector"])

#     return fields


# def _extract_fields_bs4(driver, include_password=False):
#     """Original BeautifulSoup extraction — unchanged logic."""
#     soup     = BeautifulSoup(driver.page_source, "html.parser")
#     elements = []

#     for el in soup.find_all(["input", "select", "textarea"]):
#         el_type = el.get("type", "text").lower() if el.name == "input" else el.name
#         if el_type == "hidden":
#             continue
#         if el_type == "password" and not include_password:
#             continue

#         if el.get("id"):
#             selector = f"#{el.get('id')}"
#         elif el.get("name"):
#             selector = f"[name='{el.get('name')}']"
#         elif el.get("data-testid"):
#             selector = f"[data-testid='{el.get('data-testid')}']"
#         else:
#             continue

#         label = ""
#         if el.get("id"):
#             lbl = soup.find("label", attrs={"for": el.get("id")})
#             if lbl:
#                 label = lbl.get_text(strip=True)
#         if not label:
#             label = el.get("placeholder") or el.get("aria-label") or el.get("name") or ""

#         entry = {"selector": selector, "type": el_type, "label": label}
#         if el_type == "file":
#             entry["accept"] = el.get("accept", "")
#         if el.name == "select":
#             entry["options"] = [
#                 o.get_text(strip=True) for o in el.find_all("option")
#                 if o.get_text(strip=True)
#             ]
#         elements.append(entry)

#     return elements


# def _extract_upload_fields_selenium(driver, existing_fields):
#     """
#     Uses live Selenium DOM to find upload-related elements that BS4 misses:
#       1. input[type='file'] elements (including invisible/hidden ones)
#       2. Buttons/divs with upload-related text
#       3. Dropzone containers
#     """
#     extra = []
#     existing_selectors = {f["selector"] for f in existing_fields}

#     # ── 1. All file inputs (including hidden ones React hides) ──────────────
#     try:
#         file_inputs = driver.find_elements(By.CSS_SELECTOR, "input[type='file']")
#         for el in file_inputs:
#             el_id   = el.get_attribute("id")
#             el_name = el.get_attribute("name")
#             el_test = el.get_attribute("data-testid")

#             if el_id:
#                 selector = f"#{el_id}"
#             elif el_name:
#                 selector = f"[name='{el_name}']"
#             elif el_test:
#                 selector = f"[data-testid='{el_test}']"
#             else:
#                 # Generate a unique selector using class or index
#                 el_class = el.get_attribute("class") or ""
#                 if el_class:
#                     first_class = el_class.split()[0]
#                     selector    = f"input.{first_class}[type='file']"
#                 else:
#                     continue

#             if selector in existing_selectors:
#                 continue

#             # Try to find a label for context
#             label = el.get_attribute("aria-label") or el.get_attribute("name") or ""
#             if el_id:
#                 try:
#                     lbl_el = driver.find_element(By.CSS_SELECTOR, f"label[for='{el_id}']")
#                     label  = lbl_el.text.strip() or label
#                 except Exception:
#                     pass

#             accept = el.get_attribute("accept") or ""
#             print(f"   📎 Found file input via Selenium: {selector!r} label={label!r} accept={accept!r}")
#             extra.append({
#                 "selector": selector,
#                 "type":     "file",
#                 "label":    label,
#                 "accept":   accept,
#             })
#     except Exception as e:
#         print(f"   ⚠️  Selenium file input scan error: {e}")

#     # ── 2. Upload buttons / divs with upload-related text ───────────────────
#     try:
#         candidates = driver.find_elements(
#             By.CSS_SELECTOR,
#             "button, div[role='button'], label[role='button'], "
#             "div[class*='upload'], div[class*='drop'], div[class*='dropzone'], "
#             "label[class*='upload'], span[class*='upload']"
#         )
#         for el in candidates:
#             try:
#                 text = (driver.execute_script(
#                     "return arguments[0].textContent;", el) or "").strip().lower()
#             except Exception:
#                 text = (el.text or "").strip().lower()

#             if not any(kw in text for kw in UPLOAD_KEYWORDS):
#                 continue
#             if not el.is_displayed():
#                 continue

#             # Only include if it wraps or is associated with a file input
#             # (label[for=...] pattern is the most reliable)
#             for_attr = el.get_attribute("for") or ""
#             if for_attr:
#                 selector = f"#{for_attr}"
#                 if selector not in existing_selectors:
#                     label = el.text.strip()
#                     print(f"   📎 Found upload label via Selenium: {selector!r} text={label!r}")
#                     extra.append({
#                         "selector": selector,
#                         "type":     "file",
#                         "label":    label,
#                         "accept":   "",
#                     })
#     except Exception as e:
#         print(f"   ⚠️  Selenium upload button scan error: {e}")

#     # ── 3. Dropzone containers ───────────────────────────────────────────────
#     try:
#         dropzones = driver.find_elements(
#             By.CSS_SELECTOR,
#             "[data-dropzone], [class*='dropzone'], [class*='drop-zone'], "
#             "[data-upload], [class*='file-upload']"
#         )
#         for el in dropzones:
#             if not el.is_displayed():
#                 continue
#             el_id = el.get_attribute("id")
#             if not el_id:
#                 continue
#             selector = f"#{el_id}"
#             if selector in existing_selectors:
#                 continue
#             label = el.get_attribute("aria-label") or el.text.strip()[:40] or "dropzone"
#             print(f"   📎 Found dropzone via Selenium: {selector!r}")
#             extra.append({
#                 "selector": selector,
#                 "type":     "file",
#                 "label":    label,
#                 "accept":   "",
#             })
#     except Exception as e:
#         print(f"   ⚠️  Selenium dropzone scan error: {e}")

#     return extra


# # ─────────────────────────────────────────────────────────────────────────────
# # Screenshot helpers
# # ─────────────────────────────────────────────────────────────────────────────

# def _uni_slug(url: str) -> str:
#     try:
#         parsed     = urlparse(url)
#         host       = parsed.hostname or "unknown"
#         port       = parsed.port or ""
#         path       = parsed.path.strip("/")
#         slug_parts = [host]
#         if port:
#             slug_parts.append(str(port))
#         if path:
#             slug_parts.append(path.replace("/", "-"))
#         slug = "-".join(slug_parts)
#         return re.sub(r"[^a-z0-9\-]+", "-", slug.lower()).strip("-")
#     except Exception:
#         return "unknown"


# def _screenshots_dir(student_id, portal_url: str) -> Path:
#     slug = _uni_slug(portal_url)
#     d    = Path(settings.MEDIA_ROOT) / "screenshots" / str(student_id) / slug
#     d.mkdir(parents=True, exist_ok=True)
#     return d


# def _take_screenshot(driver, student_id, portal_url: str, label: str) -> dict:
#     d        = _screenshots_dir(student_id, portal_url)
#     slug     = _uni_slug(portal_url)
#     filename = f"{label}.png"
#     filepath = d / filename
#     try:
#         driver.save_screenshot(str(filepath))
#         print(f"📸 {filepath}")
#     except Exception as e:
#         print(f"⚠️  Screenshot failed: {e}")
#         return {}
#     return {
#         "label":    label,
#         "filename": filename,
#         "url":      f"{settings.MEDIA_URL}screenshots/{student_id}/{slug}/{filename}",
#     }


# def _save_manifest(student_id, portal_url: str, entries: list):
#     d    = _screenshots_dir(student_id, portal_url)
#     path = d / "manifest.json"
#     with open(path, "w") as f:
#         json.dump({
#             "student_id":  student_id,
#             "portal":      portal_url,
#             "screenshots": [e for e in entries if e],
#         }, f, indent=2)


# # ─────────────────────────────────────────────────────────────────────────────
# # AI SERVICE
# # ─────────────────────────────────────────────────────────────────────────────

# class AIService:

#     def __init__(self):
#         api_key = getattr(settings, "GEMINI_API_KEY", None)
#         if not api_key:
#             raise ValueError("GEMINI_API_KEY not set in Django settings.")
#         self.llm = ChatGoogleGenerativeAI(
#             model="gemini-2.5-flash",
#             google_api_key=api_key,
#             temperature=0,
#         )
#         self.parser = PydanticOutputParser(pydantic_object=AutomationResponse)

#     @staticmethod
#     def make_app_id(student_id, url: str) -> int:
#         raw = f"{student_id}:{url}"
#         return int(hashlib.md5(raw.encode()).hexdigest()[:8], 16) % 999999 + 1

#     # ------------------------------------------------------------------
#     # Scrape entire flow: login page (if present) + all form steps
#     # ------------------------------------------------------------------
#     def scrape_full_flow(self, url):
#         """
#         Opens the URL and scrapes:
#           - If a login page is detected: scrapes login fields, performs login,
#             waits for the application form to appear, then scrapes all form steps.
#           - If no login page: scrapes all form steps directly.

#         FIX: DOM change detection now uses HTML signature hashing,
#              not URL or field count. This correctly handles React SPAs.
#         """
#         options = Options()
#         options.add_argument("--headless=new")
#         options.add_argument("--no-sandbox")
#         options.add_argument("--disable-dev-shm-usage")
#         options.add_argument("--window-size=1920,1080")

#         driver = None
#         pages  = []

#         try:
#             driver = webdriver.Chrome(options=options)
#             driver.get(url)
#             _wait_for_react_hydration(driver, timeout=15)

#             # ── LOGIN PAGE ──────────────────────────────────────────────────
#             if _is_login_page(driver):
#                 print("🔐 Login page detected during scraping")
#                 login_fields  = _extract_fields_from_page(driver, include_password=True)
#                 login_btn     = _find_login_button(driver)
#                 login_btn_sel = None
#                 if login_btn:
#                     btn_id        = login_btn.get_attribute("id")
#                     login_btn_sel = f"#{btn_id}" if btn_id else "LOGIN_BUTTON"

#                 pages.append({
#                     "page_type":       "login",
#                     "page_number":     0,
#                     "fields":          login_fields,
#                     "submit_selector": login_btn_sel or "LOGIN_BUTTON",
#                 })
#                 print(f"   Scraped {len(login_fields)} login fields")

#                 portal_email    = "student"
#                 portal_password = "au2024"

#                 if portal_email and portal_password and login_btn:
#                     try:
#                         try:
#                             email_el = driver.find_element(By.XPATH, "//input[@type='email']")
#                         except NoSuchElementException:
#                             email_el = driver.find_element(By.XPATH, "//input[@type='text']")
#                         pass_el = driver.find_element(By.XPATH, "//input[@type='password']")
#                         email_el.send_keys(portal_email)
#                         pass_el.send_keys(portal_password)
#                         driver.execute_script("arguments[0].click();", login_btn)
#                         WebDriverWait(driver, 15).until(
#                             EC.invisibility_of_element_located(
#                                 (By.XPATH, "//input[@type='password']")
#                             )
#                         )
#                         print("✅ Scraping login succeeded — waiting for form...")
#                         time.sleep(2)
#                         _wait_for_react_hydration(driver, timeout=10)
#                     except Exception as e:
#                         print(f"⚠️  Scraping login failed: {e}")
#                 else:
#                     print("⚠️  Credentials not set or no login button found")

#             # ── APPLICATION FORM PAGES ──────────────────────────────────────
#             for step_num in range(1, MAX_FORM_STEPS + 1):
#                 print(f"\n🧭 Scraping application page {step_num}...")
#                 time.sleep(0.5)

#                 if _is_login_page(driver):
#                     print("   Still on login page — login may have failed")
#                     break

#                 fields = _extract_fields_from_page(driver, include_password=False)
#                 print(f"   {len(fields)} fields found "
#                       f"({sum(1 for f in fields if f['type']=='file')} file inputs)")

#                 # ── TAKE SIGNATURE BEFORE CLICKING NEXT ────────────────────
#                 # This is the critical fix: hash the form HTML NOW, before click
#                 prev_signature = _get_form_signature(driver)

#                 next_btn   = _find_next_button(driver)
#                 submit_btn = _find_submit_button(driver) if not next_btn else None

#                 next_sel   = None
#                 submit_sel = None
#                 if next_btn:
#                     nid      = next_btn.get_attribute("id")
#                     next_sel = f"#{nid}" if nid else "NEXT_BUTTON"
#                 if submit_btn and not next_btn:
#                     sid        = submit_btn.get_attribute("id")
#                     submit_sel = f"#{sid}" if sid else "SUBMIT_BUTTON"

#                 pages.append({
#                     "page_type":       "application",
#                     "page_number":     step_num,
#                     "fields":          fields,
#                     "next_selector":   next_sel,
#                     "submit_selector": submit_sel,
#                 })

#                 if not next_btn:
#                     print("   ✅ No Next button — end of form")
#                     break

#                 # ── CLICK NEXT ──────────────────────────────────────────────
#                 try:
#                     driver.execute_script(
#                         "arguments[0].scrollIntoView({block:'center'});", next_btn)
#                     driver.execute_script("arguments[0].click();", next_btn)
#                     print("   ▶ Clicked Next — waiting for DOM signature change...")

#                     # FIX: pass prev_signature (not count+url)
#                     changed = _wait_for_dom_change(driver, prev_signature, timeout=12)

#                     if changed:
#                         print(f"   ✅ DOM changed — proceeding to page {step_num + 1}")
#                     else:
#                         # One more attempt: maybe React delayed the render
#                         new_sig = _get_form_signature(driver)
#                         if new_sig != prev_signature:
#                             print(f"   ✅ DOM changed on recheck — proceeding to page {step_num + 1}")
#                         else:
#                             print("   ⚠️  DOM signature unchanged after 12s — treating as last step")
#                             break

#                 except Exception as e:
#                     print(f"   ❌ Error clicking Next: {e}")
#                     break

#             total = len([p for p in pages if p["page_type"] == "application"])
#             print(f"\n✅ Scraping complete: {total} application pages total")
#             return pages

#         finally:
#             if driver:
#                 driver.quit()

#     # ------------------------------------------------------------------
#     # Generate mapping via Gemini
#     # ------------------------------------------------------------------
#     def get_automation_instructions(self, target_url, student_data, app_id):
#         pages = self.scrape_full_flow(target_url)
#         if not pages:
#             raise Exception("No pages found — check the portal URL")

#         portal_email    = getattr(settings, "PORTAL_EMAIL", "")
#         portal_password = getattr(settings, "PORTAL_PASSWORD", "")

#         student_data_with_creds = {
#             **student_data,
#             "_portal_email":    portal_email,
#             "_portal_password": portal_password,
#         }

#         system_prompt = """
# You are an expert at mapping student data to multi-page university portal flows.

# The pages list includes:
#   - A "login" page (page_type="login") if the portal requires authentication
#   - One or more "application" pages (page_type="application")

# You must generate a COMPLETE automation plan that covers ALL pages in order:
#   1. Fill login credentials → click login button → wait for form
#   2. Fill application step 1 → click Next → ...
#   3. Fill last step → submit

# Return ONLY valid JSON (no markdown, no backticks). Example structure:

# {{
#   "application_id": <integer>,
#   "url": "<target url>",
#   "steps": [
#     {{
#       "action": "fill",
#       "page_type": "login",
#       "fields": [
#         {{"selector": "#email",    "type": "email",    "value": "<_portal_email value>",    "confidence": 1.0}},
#         {{"selector": "#password", "type": "password", "value": "<_portal_password value>", "confidence": 1.0}}
#       ]
#     }},
#     {{
#       "action": "login_click",
#       "selector": "<submit_selector from login page, or LOGIN_BUTTON>",
#       "wait_ms": 3000
#     }},
#     {{
#       "action": "fill",
#       "page_type": "application",
#       "fields": [
#         {{"selector": "#name", "type": "text", "value": "Ali Khan", "confidence": 0.95}},
#         {{"selector": "#photo","type": "file", "value": "/abs/path/photo.jpg", "confidence": 0.9}}
#       ]
#     }},
#     {{"action": "click",  "selector": "NEXT_BUTTON",   "wait_ms": 2000}},
#     {{"action": "fill",   "page_type": "application", "fields": [...]}},
#     {{"action": "submit", "selector": "SUBMIT_BUTTON", "wait_ms": 3000}}
#   ]
# }}

# RULES:
# 1. LOGIN STEP:
#    - Map "_portal_email" → the email/username input field on the login page.
#    - Map "_portal_password" → the password input field on the login page.
#    - Use the exact selectors from the login page fields.
#    - The login click action must use "action": "login_click".

# 2. CLICK / SUBMIT selectors:
#    - For click (Next) actions: use "NEXT_BUTTON" unless the page gave a specific next_selector.
#    - For submit: use "SUBMIT_BUTTON" unless the page gave a specific submit_selector.
#    - For login_click: use the submit_selector from the login page, or "LOGIN_BUTTON".
#    - NEVER invent button CSS selectors.

# 3. FILL selectors must be the exact strings from the scraped page fields.

# 4. FILE FIELDS:
#    photo/picture/avatar  → student.photo
#    cnic/id_card          → student.cnic_image
#    transcript/result     → student.transcript
#    matric                → student.matric_certificate
#    inter/fsc/hssc        → student.inter_certificate
#    domicile              → student.domicile
#    Set value="" and confidence=0.0 if no match.

# 5. confidence: 1.0=exact, 0.5=inferred, 0.0=no match.
# 6. Include ALL fields from ALL pages even if confidence is 0.
# 7. Return ONLY JSON.
# """

#         prompt = ChatPromptTemplate.from_messages([
#             ("system", system_prompt),
#             ("human",
#              "STUDENT DATA (includes _portal_email and _portal_password):\n{student_data}\n\n"
#              "SCRAPED PAGES (login + application steps):\n{pages_data}\n\n"
#              "URL: {url}\nAPP ID: {app_id}"),
#         ])

#         chain  = prompt | self.llm | self.parser
#         result = chain.invoke({
#             "student_data": json.dumps(student_data_with_creds, indent=2),
#             "pages_data":   json.dumps(pages, indent=2),
#             "url":          target_url,
#             "app_id":       app_id,
#         })
#         return result


# # ─────────────────────────────────────────────────────────────────────────────
# # AUTOMATION SERVICE
# # ─────────────────────────────────────────────────────────────────────────────

# class AutomationService:

#     # ── Normalization ──────────────────────────────────────────────────────

#     def normalize_value(self, field_name, value):
#         if not value:
#             return value
#         value    = str(value).strip()
#         city_map = {
#             "lahore": "Punjab", "karachi": "Sindh", "islamabad": "Islamabad",
#             "peshawar": "KPK",  "quetta": "Balochistan",
#         }
#         if field_name and "province" in field_name.lower():
#             return city_map.get(value.lower(), value)
#         return value

#     def normalize_course(self, value):
#         if not value:
#             return []
#         v = str(value).lower().strip()
#         m = {
#             "cs":                     ["cs","computer science","bscs"],
#             "bscs":                   ["bscs","computer science","cs"],
#             "computer science":       ["computer science","cs","bscs"],
#             "bsse":                   ["bsse","software engineering","software"],
#             "software engineering":   ["software engineering","bsse","software"],
#             "bsit":                   ["bsit","information technology","it","bs information technology","bs (it)"],
#             "it":                     ["it","information technology","bsit"],
#             "information technology": ["information technology","bsit","it","bs information technology"],
#             "bba":                    ["bba","business administration","business"],
#             "business administration":["business administration","bba","business"],
#             "finance":                ["finance","bba finance","business finance"],
#             "mbbs":                   ["mbbs","medicine","medical"],
#             "bds":                    ["bds","dentistry","dental"],
#             "nursing":                ["nursing","bsn","bs nursing"],
#             "psychology":             ["psychology","bs psychology"],
#             "sociology":              ["sociology","bs sociology"],
#             "llb":                    ["llb","law","bachelor of law","legal"],
#             "law":                    ["law","llb","legal studies","legal"],
#         }
#         return m.get(v, [v])

#     def normalize_date(self, value):
#         if not value:
#             return value
#         fmts = [
#             "%Y-%m-%d","%Y %m %d","%Y/%m/%d",
#             "%d-%m-%Y","%d/%m/%Y","%d %m %Y",
#             "%m/%d/%Y","%m-%d-%Y",
#             "%d %b %Y","%d %B %Y","%B %d, %Y","%b %d, %Y",
#         ]
#         dt = None
#         for fmt in fmts:
#             try: dt = datetime.strptime(str(value).strip(), fmt); break
#             except Exception: continue
#         if not dt:
#             return {"iso":value,"dmy":value,"dmy_dash":value,"dmy_slash":value,
#                     "mdy":value,"long":value,"dt":None,"day":"","month":"","year":""}
#         return {
#             "iso":       dt.strftime("%Y-%m-%d"),
#             "dmy":       dt.strftime("%d %m %Y"),
#             "dmy_dash":  dt.strftime("%d-%m-%Y"),
#             "dmy_slash": dt.strftime("%d/%m/%Y"),
#             "mdy":       dt.strftime("%m/%d/%Y"),
#             "long":      dt.strftime("%d %b %Y"),
#             "dt":        dt,
#             "day":       dt.strftime("%d"),
#             "month":     dt.strftime("%m"),
#             "year":      dt.strftime("%Y"),
#         }

#     # ── React helpers ──────────────────────────────────────────────────────

#     def is_react_page(self, driver):
#         return driver.execute_script(
#             "return !!(window.__REACT_DEVTOOLS_GLOBAL_HOOK__ || "
#             "document.querySelector('[data-reactroot]') || "
#             "document.querySelector('#root'))"
#         )

#     def react_set_value(self, driver, element, value):
#         driver.execute_script("""
#             var el = arguments[0], val = arguments[1];
#             var proto = el.tagName.toLowerCase() === 'textarea'
#                 ? window.HTMLTextAreaElement.prototype
#                 : window.HTMLInputElement.prototype;
#             Object.getOwnPropertyDescriptor(proto, 'value').set.call(el, val);
#             el.dispatchEvent(new Event('input',  { bubbles: true }));
#             el.dispatchEvent(new Event('change', { bubbles: true }));
#         """, element, value)

#     # ── Date helpers ───────────────────────────────────────────────────────

#     def detect_date_format(self, element):
#         hint = " ".join([
#             element.get_attribute("placeholder") or "",
#             element.get_attribute("pattern")     or "",
#             element.get_attribute("data-format") or "",
#         ]).lower()
#         if any(x in hint for x in ["dd-mm-yyyy","dd/mm/yyyy","dd mm yyyy"]):
#             return "dmy_slash" if "/" in hint else "dmy_dash"
#         if any(x in hint for x in ["mm/dd/yyyy","mm-dd-yyyy"]): return "mdy"
#         if "yyyy-mm-dd" in hint: return "iso"
#         return None

#     def fill_date_react(self, driver, element, formats):
#         input_type = (element.get_attribute("type") or "").lower()
#         fmt_key    = self.detect_date_format(element)
#         if input_type == "date":
#             self.fill_react_native_date(driver, element, formats, fmt_key); return
#         formatted = formats.get(fmt_key, formats["dmy_dash"]) if fmt_key else formats["dmy_dash"]
#         self.react_set_value(driver, element, formatted); time.sleep(0.2)
#         if element.get_attribute("value"): return
#         if PYPERCLIP_AVAILABLE:
#             try:
#                 pyperclip.copy(formatted)
#                 element.send_keys(Keys.CONTROL + "v"); time.sleep(0.3)
#                 if element.get_attribute("value"): return
#             except Exception: pass
#         driver.execute_script("arguments[0].click();", element)
#         element.send_keys(Keys.CONTROL + "a"); element.send_keys(Keys.DELETE)
#         for char in formatted: element.send_keys(char); time.sleep(0.04)

#     def fill_react_native_date(self, driver, element, formats, fmt_key):
#         self.react_set_value(driver, element, formats["iso"]); time.sleep(0.2)
#         if element.get_attribute("value") == formats["iso"]: return
#         driver.execute_script("arguments[0].click();", element)
#         element.send_keys(formats["month"]); time.sleep(0.1)
#         element.send_keys(formats["day"]);   time.sleep(0.1)
#         element.send_keys(formats["year"])

#     def fill_native_date(self, driver, element, formats):
#         iso = formats["iso"]
#         driver.execute_script("arguments[0].value = arguments[1];", element, iso)
#         driver.execute_script(
#             "arguments[0].dispatchEvent(new Event('input',{bubbles:true}));"
#             "arguments[0].dispatchEvent(new Event('change',{bubbles:true}));", element)
#         if element.get_attribute("value") != iso:
#             element.clear(); element.send_keys(iso)

#     def fill_custom_date(self, driver, element, formats):
#         fmt_key = self.detect_date_format(element)
#         if fmt_key:
#             element.clear(); time.sleep(0.2)
#             element.send_keys(formats.get(fmt_key, formats["dmy_dash"]))
#         else:
#             for key in ["dmy_dash","dmy_slash","dmy","iso","mdy"]:
#                 element.clear(); time.sleep(0.2)
#                 element.send_keys(formats.get(key,"")); time.sleep(0.3)
#                 if element.get_attribute("value"): return
#             driver.execute_script("arguments[0].value = arguments[1];", element, formats["dmy_dash"])
#             driver.execute_script(
#                 "arguments[0].dispatchEvent(new Event('input',{bubbles:true}));"
#                 "arguments[0].dispatchEvent(new Event('change',{bubbles:true}));", element)

#     # ── File path resolver ─────────────────────────────────────────────────

#     def resolve_file_path(self, value):
#         if not value:
#             raise ValueError("File path is empty")
#         path = str(value).strip()
#         if os.path.isabs(path) and os.path.isfile(path): return path
#         media_root = getattr(settings, "MEDIA_ROOT", "")
#         if media_root:
#             clean = path.lstrip("/\\")
#             if clean.startswith("media/") or clean.startswith("media\\"):
#                 clean = clean[6:]
#             candidate = os.path.join(str(media_root), clean)
#             if os.path.isfile(candidate): return os.path.abspath(candidate)
#         base_dir = getattr(settings, "BASE_DIR", "")
#         if base_dir:
#             candidate = os.path.join(str(base_dir), path.lstrip("/\\"))
#             if os.path.isfile(candidate): return os.path.abspath(candidate)
#         abs_attempt = os.path.abspath(path)
#         if os.path.isfile(abs_attempt): return abs_attempt
#         raise FileNotFoundError(
#             f"File not found: '{value}' — tried MEDIA_ROOT='{media_root}', BASE_DIR='{base_dir}'"
#         )

#     # ── wait_for_element ───────────────────────────────────────────────────

#     def wait_for_element(self, driver, selector, timeout=10, clickable=False):
#         if selector in ("NEXT_BUTTON", "next_button"):
#             deadline = time.time() + timeout
#             while time.time() < deadline:
#                 el = _find_next_button(driver)
#                 if el: return el
#                 time.sleep(REACT_POLL_INTERVAL)
#             raise TimeoutException("No Next button found")

#         if selector in ("SUBMIT_BUTTON", "submit_button"):
#             deadline = time.time() + timeout
#             while time.time() < deadline:
#                 el = _find_submit_button(driver)
#                 if el: return el
#                 time.sleep(REACT_POLL_INTERVAL)
#             raise TimeoutException("No Submit button found")

#         if selector in ("LOGIN_BUTTON", "login_button"):
#             deadline = time.time() + timeout
#             while time.time() < deadline:
#                 el = _find_login_button(driver)
#                 if el: return el
#                 time.sleep(REACT_POLL_INTERVAL)
#             raise TimeoutException("No Login button found")

#         if ":contains(" in selector:
#             match = re.match(r"^(\w+)?:contains\(['\"](.+?)['\"]\)$", selector.strip())
#             if match:
#                 tag, text = match.group(1) or "*", match.group(2).lower()
#             else:
#                 tag  = "*"
#                 text = selector.split(":contains(")[1].strip("'\")")
#             xpath = (
#                 f"//{tag}[contains("
#                 f"translate(normalize-space(.),"
#                 f"'ABCDEFGHIJKLMNOPQRSTUVWXYZ','abcdefghijklmnopqrstuvwxyz'),"
#                 f"'{text.lower()}')]"
#             )
#             wait = WebDriverWait(driver, timeout)
#             cond = EC.element_to_be_clickable if clickable else EC.presence_of_element_located
#             try:
#                 return wait.until(cond((By.XPATH, xpath)))
#             except TimeoutException:
#                 fn = _find_login_button  if any(kw in selector.lower() for kw in LOGIN_KEYWORDS) \
#                      else _find_next_button if any(kw in selector.lower() for kw in NEXT_KEYWORDS) \
#                      else _find_submit_button
#                 el = fn(driver)
#                 if el: return el
#                 raise

#         wait = WebDriverWait(driver, timeout)
#         by   = By.CSS_SELECTOR
#         if selector.startswith("#"):
#             by, selector = By.ID, selector[1:]
#         elif selector.startswith("//"):
#             by = By.XPATH
#         elif selector.startswith("[name="):
#             by, selector = By.NAME, selector.split("'")[1]

#         try:
#             el_type = driver.find_element(by, selector).get_attribute("type") or ""
#             if el_type == "file": clickable = False
#         except Exception:
#             pass

#         cond = EC.element_to_be_clickable if clickable else EC.presence_of_element_located
#         return wait.until(cond((by, selector)))

#     # ── fill_field ─────────────────────────────────────────────────────────

#     def fill_field(self, driver, element, field_type, value):
#         tag        = element.tag_name.lower()
#         input_type = (element.get_attribute("type") or "").lower()
#         is_react   = self.is_react_page(driver)

#         if field_type == "file" or input_type == "file":
#             try:
#                 abs_path = self.resolve_file_path(value)
#             except (FileNotFoundError, ValueError) as e:
#                 raise Exception(f"File upload failed — {e}")
#             driver.execute_script("""
#                 arguments[0].style.display    = 'block';
#                 arguments[0].style.opacity    = '1';
#                 arguments[0].style.visibility = 'visible';
#             """, element)
#             time.sleep(0.2)
#             element.send_keys(abs_path)
#             driver.execute_script(
#                 "arguments[0].dispatchEvent(new Event('change',{bubbles:true}));", element)
#             print(f"✅ File: {os.path.basename(abs_path)}")
#             return

#         if input_type == "password":
#             element.clear()
#             element.send_keys(str(value))
#             return

#         if input_type in ["checkbox", "radio"]:
#             if str(value).lower() in ["true","1","yes"]:
#                 driver.execute_script("arguments[0].click();", element)
#             return

#         if field_type == "date" or input_type == "date":
#             formats = self.normalize_date(value)
#             if not formats.get("dt"):
#                 element.clear(); element.send_keys(str(value)); return
#             if is_react:
#                 self.fill_date_react(driver, element, formats)
#             elif input_type == "date":
#                 fmt_key = self.detect_date_format(element)
#                 (self.fill_custom_date if (fmt_key and fmt_key != "iso") else self.fill_native_date)(
#                     driver, element, formats)
#             else:
#                 self.fill_custom_date(driver, element, formats)
#             return

#         if tag == "select":
#             sel     = Select(element)
#             options = [o.text.strip() for o in sel.options]
#             opt_low = [o.lower() for o in options]
#             for target in self.normalize_course(value):
#                 t = target.lower().strip()
#                 for i, opt in enumerate(opt_low):
#                     if opt == t:                           sel.select_by_visible_text(options[i]); return
#                 for i, opt in enumerate(opt_low):
#                     if opt and opt in t:                  sel.select_by_visible_text(options[i]); return
#                 for i, opt in enumerate(opt_low):
#                     if t and t in opt:                    sel.select_by_visible_text(options[i]); return
#                 for i, opt in enumerate(opt_low):
#                     if set(t.split()) & set(opt.split()): sel.select_by_visible_text(options[i]); return
#             raise Exception(f"Dropdown option not found for '{value}'. Available: {options}")

#         if tag in ["input", "textarea"]:
#             self.react_set_value(driver, element, str(value)) if is_react \
#                 else (element.clear() or element.send_keys(str(value)))
#             return

#         driver.execute_script("arguments[0].value = arguments[1];", element, value)
#         driver.execute_script(
#             "arguments[0].dispatchEvent(new Event('change',{bubbles:true}));", element)

#     # ── Main runner ────────────────────────────────────────────────────────

#     def run(self, mapping: dict) -> dict:
#         """
#         FIX: click step now passes prev_signature to _wait_for_dom_change
#              instead of prev_count + prev_url.
#         """
#         url        = mapping.get("url")
#         steps      = mapping.get("steps", [])
#         student_id = mapping.get("application_id", 0)

#         if not url:
#             return {"status":"failed","message":"No URL provided","screenshots":[]}

#         options = Options()
#         options.add_argument("--start-maximized")

#         driver = webdriver.Chrome(options=options)
#         driver.get(url)
#         _wait_for_react_hydration(driver, timeout=15)

#         completed_steps = 0
#         screenshot_log  = []

#         last_app_fill_idx = None
#         for i, s in enumerate(steps):
#             if s.get("action") == "fill" and s.get("page_type") == "application":
#                 last_app_fill_idx = i

#         def _snap(label):
#             entry = _take_screenshot(driver, student_id, url, label)
#             if entry:
#                 screenshot_log.append(entry)

#         try:
#             for step_idx, step in enumerate(steps):
#                 action = step.get("action")

#                 if action == "fill":
#                     page_type = step.get("page_type", "application")
#                     print(f"\n📝 Fill step {step_idx} [{page_type}]")

#                     for field in step.get("fields", []):
#                         selector   = field.get("selector")
#                         field_type = (field.get("type") or "text").lower()
#                         raw_value  = field.get("value")

#                         if (raw_value is None or raw_value == "") and field_type != "file":
#                             continue
#                         if field_type == "file" and not raw_value:
#                             print(f"⏭️  No file path for {selector}")
#                             continue

#                         value = self.normalize_value(selector, raw_value)
#                         print(f"   🖊  [{field_type}] {selector} → {value!r}")

#                         try:
#                             element = self.wait_for_element(
#                                 driver, selector, clickable=(field_type != "file"))
#                             if field_type != "file":
#                                 driver.execute_script(
#                                     "arguments[0].scrollIntoView({block:'center'});", element)
#                             self.fill_field(driver, element, field_type, value)
#                             time.sleep(0.2)
#                         except Exception as e:
#                             print(f"   ❌ Failed {selector}: {e}")
#                             _save_manifest(student_id, url, screenshot_log)
#                             driver.quit()
#                             return {
#                                 "status":"failed","message":f"Error filling {selector}",
#                                 "error":str(e),"completed_steps":completed_steps,
#                                 "screenshots":screenshot_log,
#                             }

#                     if step_idx == last_app_fill_idx:
#                         time.sleep(0.7)
#                         driver.execute_script("window.scrollTo(0, 0);")
#                         time.sleep(0.2)
#                         _snap("before_submit")
#                         print("📸 before_submit screenshot taken")

#                     completed_steps += 1

#                 elif action == "login_click":
#                     selector = step.get("selector", "LOGIN_BUTTON")
#                     wait_ms  = step.get("wait_ms", 3000)
#                     print(f"\n🔐 Login click (selector: {selector!r})")

#                     element = None
#                     try:
#                         element = self.wait_for_element(driver, selector, clickable=True)
#                     except Exception as e:
#                         print(f"⚠️  Login button '{selector}' not found: {e}")
#                         element = _find_login_button(driver)

#                     if not element:
#                         _save_manifest(student_id, url, screenshot_log)
#                         driver.quit()
#                         return {
#                             "status":"failed","message":"Login button not found",
#                             "completed_steps":completed_steps,"screenshots":screenshot_log,
#                         }

#                     driver.execute_script("arguments[0].scrollIntoView({block:'center'});", element)
#                     driver.execute_script("arguments[0].click();", element)
#                     print("   ▶ Clicked login — waiting for password field to disappear...")

#                     try:
#                         WebDriverWait(driver, 15).until(
#                             EC.invisibility_of_element_located(
#                                 (By.XPATH, "//input[@type='password']")
#                             )
#                         )
#                         print("   ✅ Login successful")
#                         time.sleep(1.5)
#                         _wait_for_react_hydration(driver, timeout=10)
#                     except TimeoutException:
#                         _save_manifest(student_id, url, screenshot_log)
#                         driver.quit()
#                         return {
#                             "status":"failed",
#                             "message":"Login timed out — password field never disappeared.",
#                             "completed_steps":completed_steps,"screenshots":screenshot_log,
#                         }

#                     time.sleep(0.5)
#                     driver.execute_script("window.scrollTo(0, 0);")
#                     time.sleep(0.2)
#                     _snap("after_login")
#                     print("📸 after_login screenshot taken")
#                     completed_steps += 1

#                 elif action == "click":
#                     selector = step.get("selector", "NEXT_BUTTON")
#                     wait_ms  = step.get("wait_ms", 1500)
#                     print(f"\n▶  Next click (selector: {selector!r})")

#                     # FIX: take signature BEFORE clicking
#                     prev_signature = _get_form_signature(driver)

#                     element = None
#                     try:
#                         element = self.wait_for_element(driver, selector, clickable=True)
#                     except Exception as e:
#                         print(f"⚠️  Next selector failed: {e} — trying smart finder")
#                         element = _find_next_button(driver)

#                     if not element:
#                         _save_manifest(student_id, url, screenshot_log)
#                         driver.quit()
#                         return {
#                             "status":"failed","message":"Next button not found",
#                             "completed_steps":completed_steps,"screenshots":screenshot_log,
#                         }

#                     driver.execute_script("arguments[0].scrollIntoView({block:'center'});", element)
#                     driver.execute_script("arguments[0].click();", element)
#                     completed_steps += 1

#                     # FIX: pass prev_signature (not count+url)
#                     changed = _wait_for_dom_change(driver, prev_signature, timeout=12)
#                     if not changed:
#                         print("   ⚠️  DOM unchanged — using wait_ms fallback")
#                         time.sleep(wait_ms / 1000)

#                 elif action == "submit":
#                     selector = step.get("selector", "SUBMIT_BUTTON")
#                     wait_ms  = step.get("wait_ms", 3000)

#                     completed_steps += 1
#                     time.sleep(0.3)
#                     _snap("before_final_submit")
#                     print("📸 before_final_submit screenshot taken")
#                     print(f"\n✅ Submit (selector: {selector!r})")

#                     element = None
#                     try:
#                         element = self.wait_for_element(driver, selector, clickable=True)
#                     except Exception as e:
#                         print(f"⚠️  Submit selector failed: {e} — trying smart finder")
#                         element = _find_submit_button(driver)

#                     if not element:
#                         _save_manifest(student_id, url, screenshot_log)
#                         driver.quit()
#                         return {
#                             "status":"failed","message":"Submit button not found",
#                             "completed_steps":completed_steps,"screenshots":screenshot_log,
#                         }

#                     try:
#                         driver.execute_script(
#                             "arguments[0].scrollIntoView({block:'center'});", element)
#                         driver.execute_script("arguments[0].click();", element)
#                         time.sleep(wait_ms / 1000)
#                     except Exception as e:
#                         _save_manifest(student_id, url, screenshot_log)
#                         driver.quit()
#                         return {
#                             "status":"failed","message":"Submit click failed",
#                             "error":str(e),"completed_steps":completed_steps,
#                             "screenshots":screenshot_log,
#                         }

#                     driver.execute_script("window.scrollTo(0, 0);")
#                     time.sleep(0.3)
#                     _snap("after_submit")
#                     print("📸 after_submit screenshot taken")

#                     _save_manifest(student_id, url, screenshot_log)
#                     driver.quit()
#                     return {
#                         "status":"success","message":"Form submitted successfully",
#                         "completed_steps":completed_steps + 1,"screenshots":screenshot_log,
#                     }

#             _save_manifest(student_id, url, screenshot_log)
#             driver.quit()
#             return {"status":"success","completed_steps":completed_steps,
#                     "screenshots":screenshot_log}

#         except Exception as e:
#             try:
#                 _save_manifest(student_id, url, screenshot_log)
#                 driver.quit()
#             except Exception:
#                 pass
#             return {"status":"failed","error":str(e),"screenshots":screenshot_log}



# workds on multi step 
# """
# automation_pipeline/services.py  —  FIXED VERSION

# KEY FIXES IN THIS VERSION:

# 1. DOM CHANGE DETECTION — completely rewritten
#    - No longer uses URL changes or input COUNT changes
#    - Now hashes the FULL visible form/container innerHTML
#    - Uses multiple hash strategies: form tag, main container, full body
#    - Waits until the hash changes before declaring a new step
#    - This correctly handles React SPAs where URL never changes and
#      field count may be identical across steps

# 2. SCRAPER CALL SITE FIX
#    - scrape_full_flow() was passing prev_signature to _wait_for_dom_change()
#      but the function signature expected prev_count + prev_url (old signature)
#    - Now the function only takes prev_signature — fully consistent

# 3. UPLOAD FIELD DETECTION — now uses Selenium live DOM inspection
#    - BeautifulSoup static HTML misses React-rendered file inputs
#    - New _extract_fields_selenium() uses driver.find_elements() directly
#    - Explicitly detects:
#        * input[type="file"] (including hidden/invisible ones)
#        * React upload buttons by text: "upload", "browse", "click document", etc.
#        * drag-drop containers with data-upload / dropzone attributes

# 4. STEP LIMIT — raised from 10 to 15 pages to handle longer forms
# """

# import hashlib
# import time
# import os
# import re
# import json
# from pathlib import Path
# from datetime import datetime
# from urllib.parse import urlparse

# from bs4 import BeautifulSoup

# from django.conf import settings

# from selenium import webdriver
# from selenium.webdriver.chrome.options import Options
# from selenium.webdriver.common.by import By
# from selenium.webdriver.common.keys import Keys
# from selenium.webdriver.support.ui import Select, WebDriverWait
# from selenium.webdriver.support import expected_conditions as EC
# from selenium.common.exceptions import TimeoutException, NoSuchElementException

# from langchain_google_genai import ChatGoogleGenerativeAI
# from langchain_core.prompts import ChatPromptTemplate
# from langchain_core.output_parsers import PydanticOutputParser

# from .schemas import AutomationResponse

# try:
#     import pyperclip
#     PYPERCLIP_AVAILABLE = True
# except ImportError:
#     PYPERCLIP_AVAILABLE = False


# # ─────────────────────────────────────────────────────────────────────────────
# # Constants
# # ─────────────────────────────────────────────────────────────────────────────

# NEXT_KEYWORDS = [
#     "next", "continue", "proceed", "forward",
#     "آگے", "اگلا", "اگلہ",
#     "next step", "next page", "save & next", "save and next", "save & continue",
# ]
# SUBMIT_KEYWORDS = [
#     "submit", "finish", "complete", "send", "apply",
#     "جمع کریں", "submit application", "final submit",
# ]
# LOGIN_KEYWORDS  = ["login", "log in", "sign in", "signin", "لاگ ان"]
# NEXT_ID_HINTS   = ["next", "continue", "proceed", "forward", "step"]
# UPLOAD_KEYWORDS = ["upload", "browse", "click document", "choose file", "select file",
#                    "attach", "drag", "drop file", "pick file"]

# REACT_STEP_TIMEOUT  = 8
# REACT_POLL_INTERVAL = 0.25
# MAX_FORM_STEPS      = 15   # raised from 10


# # ─────────────────────────────────────────────────────────────────────────────
# # Smart button finders
# # ─────────────────────────────────────────────────────────────────────────────

# def _btn_text(driver, el):
#     try:
#         return (driver.execute_script("return arguments[0].textContent;", el) or "").strip()
#     except Exception:
#         return (el.text or "").strip()


# def _find_button_by_keywords(driver, keywords):
#     all_btns = driver.find_elements(
#         By.CSS_SELECTOR, "button, input[type='submit'], a[role='button']"
#     )
#     for kw in keywords:
#         for el in driver.find_elements(
#             By.CSS_SELECTOR,
#             f"button[id*='{kw}'], button[name*='{kw}'], button[class*='{kw}'], "
#             f"input[type='submit'][id*='{kw}'], a[id*='{kw}']"
#         ):
#             if el.is_displayed() and el.is_enabled():
#                 return el
#     for el in all_btns:
#         if not (el.is_displayed() and el.is_enabled()):
#             continue
#         text = _btn_text(driver, el).lower()
#         if any(kw in text for kw in keywords):
#             return el
#     for el in all_btns:
#         if not (el.is_displayed() and el.is_enabled()):
#             continue
#         label = (el.get_attribute("aria-label") or "").lower()
#         if any(kw in label for kw in keywords):
#             return el
#     return None


# def _find_next_button(driver):
#     btn = _find_button_by_keywords(driver, NEXT_KEYWORDS)
#     if btn:
#         print(f"🔍 Next btn: {_btn_text(driver, btn)!r}")
#         return btn
#     ignore = {"back", "previous", "cancel", "reset", "واپس", "پچھلا"}
#     all_btns = driver.find_elements(By.CSS_SELECTOR, "button, input[type='submit']")
#     visible  = [
#         el for el in all_btns
#         if el.is_displayed() and el.is_enabled()
#         and not any(x in _btn_text(driver, el).lower() for x in ignore)
#     ]
#     if visible:
#         el = visible[-1]
#         print(f"🔍 Next btn (last-button heuristic): {_btn_text(driver, el)!r}")
#         return el
#     print("⚠️  No Next button found")
#     return None


# def _find_submit_button(driver):
#     btn = _find_button_by_keywords(driver, SUBMIT_KEYWORDS)
#     if btn:
#         print(f"🔍 Submit btn: {_btn_text(driver, btn)!r}")
#         return btn
#     all_btns = driver.find_elements(By.CSS_SELECTOR, "button, input[type='submit']")
#     visible  = [e for e in all_btns if e.is_displayed() and e.is_enabled()]
#     if visible:
#         print(f"🔍 Submit btn (last fallback): {_btn_text(driver, visible[-1])!r}")
#         return visible[-1]
#     return None


# def _find_login_button(driver):
#     btn = _find_button_by_keywords(driver, LOGIN_KEYWORDS)
#     if btn:
#         print(f"🔍 Login btn: {_btn_text(driver, btn)!r}")
#         return btn
#     all_btns = driver.find_elements(
#         By.CSS_SELECTOR, "button[type='submit'], input[type='submit']"
#     )
#     visible = [e for e in all_btns if e.is_displayed() and e.is_enabled()]
#     if visible:
#         print(f"🔍 Login btn (submit fallback): {_btn_text(driver, visible[0])!r}")
#         return visible[0]
#     return None


# # ─────────────────────────────────────────────────────────────────────────────
# # DOM CHANGE DETECTION  ← completely rewritten
# # ─────────────────────────────────────────────────────────────────────────────

# def _get_form_signature(driver):
#     """
#     Returns a stable MD5 hash of the currently visible form HTML.

#     Strategy (tries in order, uses first that works):
#       1. The first VISIBLE <form> element's innerHTML
#       2. A React container: #root, #app, main, [role="main"]
#       3. Full document body innerHTML (last resort)

#     Hashing innerHTML (not just field count or URL) is reliable for
#     React SPAs because React replaces the internal DOM on step change
#     even when URL and field count stay the same.
#     """
#     try:
#         # Strategy 1: visible <form>
#         forms = driver.find_elements(By.TAG_NAME, "form")
#         for f in forms:
#             try:
#                 if f.is_displayed():
#                     html = f.get_attribute("innerHTML") or ""
#                     if len(html) > 50:
#                         return hashlib.md5(html.encode("utf-8", errors="replace")).hexdigest()
#             except Exception:
#                 continue

#         # Strategy 2: React root / main content container
#         for selector in ["main", "[role='main']", "#root", "#app", ".app", "[data-reactroot]"]:
#             try:
#                 els = driver.find_elements(By.CSS_SELECTOR, selector)
#                 for el in els:
#                     if el.is_displayed():
#                         html = el.get_attribute("innerHTML") or ""
#                         if len(html) > 50:
#                             return hashlib.md5(html.encode("utf-8", errors="replace")).hexdigest()
#             except Exception:
#                 continue

#         # Strategy 3: full body
#         body = driver.find_element(By.TAG_NAME, "body")
#         html = body.get_attribute("innerHTML") or ""
#         return hashlib.md5(html.encode("utf-8", errors="replace")).hexdigest()

#     except Exception:
#         return ""


# def _wait_for_dom_change(driver, prev_signature, timeout=12):
#     """
#     Polls until the form signature changes from prev_signature.
#     Returns True if change detected, False if timed out.

#     timeout raised to 12s to handle slow React renders.
#     """
#     deadline = time.time() + timeout
#     while time.time() < deadline:
#         try:
#             new_sig = _get_form_signature(driver)
#             if new_sig and new_sig != prev_signature:
#                 # Small grace period for React to finish rendering
#                 time.sleep(0.6)
#                 _wait_for_react_hydration(driver, timeout=5)
#                 return True
#         except Exception:
#             pass
#         time.sleep(0.25)
#     return False


# def _wait_for_react_hydration(driver, timeout=15):
#     deadline = time.time() + timeout
#     while time.time() < deadline:
#         try:
#             root   = driver.find_elements(By.CSS_SELECTOR, "#root, #app, [data-reactroot]")
#             container = root[0] if root else driver.find_element(By.TAG_NAME, "body")
#             inputs = container.find_elements(
#                 By.CSS_SELECTOR, "input:not([type='hidden']), select, textarea"
#             )
#             if any(el.is_displayed() for el in inputs):
#                 return True
#         except Exception:
#             pass
#         time.sleep(REACT_POLL_INTERVAL)
#     return False


# def _is_login_page(driver):
#     try:
#         pwd = driver.find_elements(By.XPATH, "//input[@type='password']")
#         return any(el.is_displayed() for el in pwd)
#     except Exception:
#         return False


# # ─────────────────────────────────────────────────────────────────────────────
# # FIELD EXTRACTION  ← now uses live Selenium DOM + upload detection
# # ─────────────────────────────────────────────────────────────────────────────

# def _extract_fields_from_page(driver, include_password=False):
#     """
#     PRIMARY: BeautifulSoup static parse (fast, catches most fields).
#     THEN: Selenium live DOM pass to catch React-rendered file inputs
#           and upload components that BS4 misses.
#     """
#     fields       = _extract_fields_bs4(driver, include_password)
#     extra_fields = _extract_upload_fields_selenium(driver, fields)

#     seen = {f["selector"] for f in fields}
#     for ef in extra_fields:
#         if ef["selector"] not in seen:
#             fields.append(ef)
#             seen.add(ef["selector"])

#     return fields


# def _extract_fields_bs4(driver, include_password=False):
#     """Original BeautifulSoup extraction — unchanged logic."""
#     soup     = BeautifulSoup(driver.page_source, "html.parser")
#     elements = []

#     for el in soup.find_all(["input", "select", "textarea"]):
#         el_type = el.get("type", "text").lower() if el.name == "input" else el.name
#         if el_type == "hidden":
#             continue
#         if el_type == "password" and not include_password:
#             continue

#         if el.get("id"):
#             selector = f"#{el.get('id')}"
#         elif el.get("name"):
#             selector = f"[name='{el.get('name')}']"
#         elif el.get("data-testid"):
#             selector = f"[data-testid='{el.get('data-testid')}']"
#         else:
#             continue

#         label = ""
#         if el.get("id"):
#             lbl = soup.find("label", attrs={"for": el.get("id")})
#             if lbl:
#                 label = lbl.get_text(strip=True)
#         if not label:
#             label = el.get("placeholder") or el.get("aria-label") or el.get("name") or ""

#         entry = {"selector": selector, "type": el_type, "label": label}
#         if el_type == "file":
#             entry["accept"] = el.get("accept", "")
#         if el.name == "select":
#             entry["options"] = [
#                 o.get_text(strip=True) for o in el.find_all("option")
#                 if o.get_text(strip=True)
#             ]
#         elements.append(entry)

#     return elements


# def _extract_upload_fields_selenium(driver, existing_fields):
#     """
#     Uses live Selenium DOM to find upload-related elements that BS4 misses:
#       1. input[type='file'] elements (including invisible/hidden ones)
#       2. Buttons/divs with upload-related text
#       3. Dropzone containers
#     """
#     extra = []
#     existing_selectors = {f["selector"] for f in existing_fields}

#     # ── 1. All file inputs (including hidden ones React hides) ──────────────
#     try:
#         file_inputs = driver.find_elements(By.CSS_SELECTOR, "input[type='file']")
#         for el in file_inputs:
#             el_id   = el.get_attribute("id")
#             el_name = el.get_attribute("name")
#             el_test = el.get_attribute("data-testid")

#             if el_id:
#                 selector = f"#{el_id}"
#             elif el_name:
#                 selector = f"[name='{el_name}']"
#             elif el_test:
#                 selector = f"[data-testid='{el_test}']"
#             else:
#                 # Generate a unique selector using class or index
#                 el_class = el.get_attribute("class") or ""
#                 if el_class:
#                     first_class = el_class.split()[0]
#                     selector    = f"input.{first_class}[type='file']"
#                 else:
#                     continue

#             if selector in existing_selectors:
#                 continue

#             # Try to find a label for context
#             label = el.get_attribute("aria-label") or el.get_attribute("name") or ""
#             if el_id:
#                 try:
#                     lbl_el = driver.find_element(By.CSS_SELECTOR, f"label[for='{el_id}']")
#                     label  = lbl_el.text.strip() or label
#                 except Exception:
#                     pass

#             accept = el.get_attribute("accept") or ""
#             print(f"   📎 Found file input via Selenium: {selector!r} label={label!r} accept={accept!r}")
#             extra.append({
#                 "selector": selector,
#                 "type":     "file",
#                 "label":    label,
#                 "accept":   accept,
#             })
#     except Exception as e:
#         print(f"   ⚠️  Selenium file input scan error: {e}")

#     # ── 2. Upload buttons / divs with upload-related text ───────────────────
#     try:
#         candidates = driver.find_elements(
#             By.CSS_SELECTOR,
#             "button, div[role='button'], label[role='button'], "
#             "div[class*='upload'], div[class*='drop'], div[class*='dropzone'], "
#             "label[class*='upload'], span[class*='upload']"
#         )
#         for el in candidates:
#             try:
#                 text = (driver.execute_script(
#                     "return arguments[0].textContent;", el) or "").strip().lower()
#             except Exception:
#                 text = (el.text or "").strip().lower()

#             if not any(kw in text for kw in UPLOAD_KEYWORDS):
#                 continue
#             if not el.is_displayed():
#                 continue

#             # Only include if it wraps or is associated with a file input
#             # (label[for=...] pattern is the most reliable)
#             for_attr = el.get_attribute("for") or ""
#             if for_attr:
#                 selector = f"#{for_attr}"
#                 if selector not in existing_selectors:
#                     label = el.text.strip()
#                     print(f"   📎 Found upload label via Selenium: {selector!r} text={label!r}")
#                     extra.append({
#                         "selector": selector,
#                         "type":     "file",
#                         "label":    label,
#                         "accept":   "",
#                     })
#     except Exception as e:
#         print(f"   ⚠️  Selenium upload button scan error: {e}")

#     # ── 3. Dropzone containers ───────────────────────────────────────────────
#     try:
#         dropzones = driver.find_elements(
#             By.CSS_SELECTOR,
#             "[data-dropzone], [class*='dropzone'], [class*='drop-zone'], "
#             "[data-upload], [class*='file-upload']"
#         )
#         for el in dropzones:
#             if not el.is_displayed():
#                 continue
#             el_id = el.get_attribute("id")
#             if not el_id:
#                 continue
#             selector = f"#{el_id}"
#             if selector in existing_selectors:
#                 continue
#             label = el.get_attribute("aria-label") or el.text.strip()[:40] or "dropzone"
#             print(f"   📎 Found dropzone via Selenium: {selector!r}")
#             extra.append({
#                 "selector": selector,
#                 "type":     "file",
#                 "label":    label,
#                 "accept":   "",
#             })
#     except Exception as e:
#         print(f"   ⚠️  Selenium dropzone scan error: {e}")

#     return extra


# # ─────────────────────────────────────────────────────────────────────────────
# # Screenshot helpers
# # ─────────────────────────────────────────────────────────────────────────────

# def _uni_slug(url: str) -> str:
#     try:
#         parsed     = urlparse(url)
#         host       = parsed.hostname or "unknown"
#         port       = parsed.port or ""
#         path       = parsed.path.strip("/")
#         slug_parts = [host]
#         if port:
#             slug_parts.append(str(port))
#         if path:
#             slug_parts.append(path.replace("/", "-"))
#         slug = "-".join(slug_parts)
#         return re.sub(r"[^a-z0-9\-]+", "-", slug.lower()).strip("-")
#     except Exception:
#         return "unknown"


# def _screenshots_dir(student_id, portal_url: str) -> Path:
#     slug = _uni_slug(portal_url)
#     d    = Path(settings.MEDIA_ROOT) / "screenshots" / str(student_id) / slug
#     d.mkdir(parents=True, exist_ok=True)
#     return d


# def _take_screenshot(driver, student_id, portal_url: str, label: str) -> dict:
#     d        = _screenshots_dir(student_id, portal_url)
#     slug     = _uni_slug(portal_url)
#     filename = f"{label}.png"
#     filepath = d / filename
#     try:
#         driver.save_screenshot(str(filepath))
#         print(f"📸 {filepath}")
#     except Exception as e:
#         print(f"⚠️  Screenshot failed: {e}")
#         return {}
#     return {
#         "label":    label,
#         "filename": filename,
#         "url":      f"{settings.MEDIA_URL}screenshots/{student_id}/{slug}/{filename}",
#     }


# def _save_manifest(student_id, portal_url: str, entries: list):
#     d    = _screenshots_dir(student_id, portal_url)
#     path = d / "manifest.json"
#     with open(path, "w") as f:
#         json.dump({
#             "student_id":  student_id,
#             "portal":      portal_url,
#             "screenshots": [e for e in entries if e],
#         }, f, indent=2)


# # ─────────────────────────────────────────────────────────────────────────────
# # AI SERVICE
# # ─────────────────────────────────────────────────────────────────────────────

# class AIService:

#     def __init__(self):
#         api_key = getattr(settings, "GEMINI_API_KEY", None)
#         if not api_key:
#             raise ValueError("GEMINI_API_KEY not set in Django settings.")
#         self.llm = ChatGoogleGenerativeAI(
#             model="gemini-2.5-flash",
#             google_api_key=api_key,
#             temperature=0,
#         )
#         self.parser = PydanticOutputParser(pydantic_object=AutomationResponse)

#     @staticmethod
#     def make_app_id(student_id, url: str) -> int:
#         raw = f"{student_id}:{url}"
#         return int(hashlib.md5(raw.encode()).hexdigest()[:8], 16) % 999999 + 1

#     # ------------------------------------------------------------------
#     # Scrape entire flow: login page (if present) + all form steps
#     # ------------------------------------------------------------------
#     def scrape_full_flow(self, url):
#         """
#         Opens the URL and scrapes:
#           - If a login page is detected: scrapes login fields, performs login,
#             waits for the application form to appear, then scrapes all form steps.
#           - If no login page: scrapes all form steps directly.

#         FIX: DOM change detection now uses HTML signature hashing,
#              not URL or field count. This correctly handles React SPAs.
#         """
#         options = Options()
#         options.add_argument("--headless=new")
#         options.add_argument("--no-sandbox")
#         options.add_argument("--disable-dev-shm-usage")
#         options.add_argument("--window-size=1920,1080")

#         driver = None
#         pages  = []

#         try:
#             driver = webdriver.Chrome(options=options)
#             driver.get(url)
#             _wait_for_react_hydration(driver, timeout=15)

#             # ── LOGIN PAGE ──────────────────────────────────────────────────
#             if _is_login_page(driver):
#                 print("🔐 Login page detected during scraping")
#                 login_fields  = _extract_fields_from_page(driver, include_password=True)
#                 login_btn     = _find_login_button(driver)
#                 login_btn_sel = None
#                 if login_btn:
#                     btn_id        = login_btn.get_attribute("id")
#                     login_btn_sel = f"#{btn_id}" if btn_id else "LOGIN_BUTTON"

#                 pages.append({
#                     "page_type":       "login",
#                     "page_number":     0,
#                     "fields":          login_fields,
#                     "submit_selector": login_btn_sel or "LOGIN_BUTTON",
#                 })
#                 print(f"   Scraped {len(login_fields)} login fields")

#                 portal_email    = "student"
#                 portal_password = "au2024"

#                 if portal_email and portal_password and login_btn:
#                     try:
#                         try:
#                             email_el = driver.find_element(By.XPATH, "//input[@type='email']")
#                         except NoSuchElementException:
#                             email_el = driver.find_element(By.XPATH, "//input[@type='text']")
#                         pass_el = driver.find_element(By.XPATH, "//input[@type='password']")
#                         email_el.send_keys(portal_email)
#                         pass_el.send_keys(portal_password)
#                         driver.execute_script("arguments[0].click();", login_btn)
#                         WebDriverWait(driver, 15).until(
#                             EC.invisibility_of_element_located(
#                                 (By.XPATH, "//input[@type='password']")
#                             )
#                         )
#                         print("✅ Scraping login succeeded — waiting for form...")
#                         time.sleep(2)
#                         _wait_for_react_hydration(driver, timeout=10)
#                     except Exception as e:
#                         print(f"⚠️  Scraping login failed: {e}")
#                 else:
#                     print("⚠️  Credentials not set or no login button found")

#             # ── APPLICATION FORM PAGES ──────────────────────────────────────
#             SUBMIT_ONLY_KEYWORDS = ["submit", "finish", "complete", "send", "apply",
#                                     "submit application", "final submit", "جمع کریں"]

#             for step_num in range(1, MAX_FORM_STEPS + 1):
#                 print(f"\n🧭 Scraping application page {step_num}...")
#                 time.sleep(0.5)

#                 if _is_login_page(driver):
#                     print("   Still on login page — login may have failed")
#                     break

#                 fields = _extract_fields_from_page(driver, include_password=False)
#                 print(f"   {len(fields)} fields found "
#                       f"({sum(1 for f in fields if f['type']=='file')} file inputs)")

#                 # ── STOP: 0 fields = confirmation/success page ──────────────
#                 if len(fields) == 0:
#                     print("   ✅ No fields found — this is a confirmation/success page. Stopping.")
#                     break

#                 # ── TAKE SIGNATURE BEFORE DECIDING WHAT TO DO ──────────────
#                 prev_signature = _get_form_signature(driver)

#                 # Check all visible buttons to decide: Next step or Submit?
#                 all_btns = driver.find_elements(By.CSS_SELECTOR, "button, input[type='submit']")
#                 visible_btns = [
#                     b for b in all_btns
#                     if b.is_displayed() and b.is_enabled()
#                 ]
#                 btn_texts = [_btn_text(driver, b).lower() for b in visible_btns]
#                 print(f"   Visible buttons: {[_btn_text(driver, b) for b in visible_btns]}")

#                 # A page is a SUBMIT page if:
#                 #   - it has a submit-like button AND
#                 #   - it has NO next-like button
#                 has_next   = any(
#                     any(kw in t for kw in NEXT_KEYWORDS)
#                     for t in btn_texts
#                 )
#                 has_submit = any(
#                     any(kw in t for kw in SUBMIT_ONLY_KEYWORDS)
#                     for t in btn_texts
#                 )

#                 next_btn   = _find_next_button(driver) if has_next else None
#                 submit_btn = None

#                 if not has_next and has_submit:
#                     # This is the final page — record submit selector and stop
#                     submit_btn_el = _find_submit_button(driver)
#                     sid           = submit_btn_el.get_attribute("id") if submit_btn_el else None
#                     submit_sel    = f"#{sid}" if sid else "SUBMIT_BUTTON"
#                     pages.append({
#                         "page_type":       "application",
#                         "page_number":     step_num,
#                         "fields":          fields,
#                         "next_selector":   None,
#                         "submit_selector": submit_sel,
#                     })
#                     print(f"   ✅ Submit page detected (btn: {submit_sel!r}) — end of form")
#                     break

#                 # ── Regular next page ───────────────────────────────────────
#                 next_sel = None
#                 if next_btn:
#                     nid      = next_btn.get_attribute("id")
#                     next_sel = f"#{nid}" if nid else "NEXT_BUTTON"

#                 pages.append({
#                     "page_type":       "application",
#                     "page_number":     step_num,
#                     "fields":          fields,
#                     "next_selector":   next_sel,
#                     "submit_selector": None,
#                 })

#                 if not next_btn:
#                     print("   ✅ No Next button — end of form")
#                     break

#                 # ── CLICK NEXT ──────────────────────────────────────────────
#                 try:
#                     driver.execute_script(
#                         "arguments[0].scrollIntoView({block:'center'});", next_btn)
#                     driver.execute_script("arguments[0].click();", next_btn)
#                     print("   ▶ Clicked Next — waiting for DOM signature change...")

#                     changed = _wait_for_dom_change(driver, prev_signature, timeout=12)

#                     if changed:
#                         print(f"   ✅ DOM changed — proceeding to page {step_num + 1}")
#                     else:
#                         new_sig = _get_form_signature(driver)
#                         if new_sig != prev_signature:
#                             print(f"   ✅ DOM changed on recheck — proceeding to page {step_num + 1}")
#                         else:
#                             print("   ⚠️  DOM signature unchanged after 12s — treating as last step")
#                             break

#                 except Exception as e:
#                     print(f"   ❌ Error clicking Next: {e}")
#                     break

#             total = len([p for p in pages if p["page_type"] == "application"])
#             print(f"\n✅ Scraping complete: {total} application pages total")
#             return pages

#         finally:
#             if driver:
#                 driver.quit()

#     # ------------------------------------------------------------------
#     # Generate mapping via Gemini
#     # ------------------------------------------------------------------
#     def get_automation_instructions(self, target_url, student_data, app_id):
#         pages = self.scrape_full_flow(target_url)
#         if not pages:
#             raise Exception("No pages found — check the portal URL")

#         portal_email    = getattr(settings, "PORTAL_EMAIL", "")
#         portal_password = getattr(settings, "PORTAL_PASSWORD", "")

#         student_data_with_creds = {
#             **student_data,
#             "_portal_email":    portal_email,
#             "_portal_password": portal_password,
#         }

#         system_prompt = """
# You are an expert at mapping student data to multi-page university portal flows.

# The pages list includes:
#   - A "login" page (page_type="login") if the portal requires authentication
#   - One or more "application" pages (page_type="application")

# You must generate a COMPLETE automation plan that covers ALL pages in order:
#   1. Fill login credentials → click login button → wait for form
#   2. Fill application step 1 → click Next → ...
#   3. Fill last step → submit

# Return ONLY valid JSON (no markdown, no backticks). Example structure:

# {{
#   "application_id": <integer>,
#   "url": "<target url>",
#   "steps": [
#     {{
#       "action": "fill",
#       "page_type": "login",
#       "fields": [
#         {{"selector": "#email",    "type": "email",    "value": "<_portal_email value>",    "confidence": 1.0}},
#         {{"selector": "#password", "type": "password", "value": "<_portal_password value>", "confidence": 1.0}}
#       ]
#     }},
#     {{
#       "action": "login_click",
#       "selector": "<submit_selector from login page, or LOGIN_BUTTON>",
#       "wait_ms": 3000
#     }},
#     {{
#       "action": "fill",
#       "page_type": "application",
#       "fields": [
#         {{"selector": "#name", "type": "text", "value": "Ali Khan", "confidence": 0.95}},
#         {{"selector": "#photo","type": "file", "value": "/abs/path/photo.jpg", "confidence": 0.9}}
#       ]
#     }},
#     {{"action": "click",  "selector": "NEXT_BUTTON",   "wait_ms": 2000}},
#     {{"action": "fill",   "page_type": "application", "fields": [...]}},
#     {{"action": "submit", "selector": "SUBMIT_BUTTON", "wait_ms": 3000}}
#   ]
# }}

# RULES:
# 1. LOGIN STEP:
#    - Map "_portal_email" → the email/username input field on the login page.
#    - Map "_portal_password" → the password input field on the login page.
#    - Use the exact selectors from the login page fields.
#    - The login click action must use "action": "login_click".

# 2. CLICK / SUBMIT selectors:
#    - For click (Next) actions: use "NEXT_BUTTON" unless the page gave a specific next_selector.
#    - For submit: use "SUBMIT_BUTTON" unless the page gave a specific submit_selector.
#    - For login_click: use the submit_selector from the login page, or "LOGIN_BUTTON".
#    - NEVER invent button CSS selectors.

# 3. FILL selectors must be the exact strings from the scraped page fields.

# 4. FILE FIELDS:
#    photo/picture/avatar  → student.photo
#    cnic/id_card          → student.cnic_image
#    transcript/result     → student.transcript
#    matric                → student.matric_certificate
#    inter/fsc/hssc        → student.inter_certificate
#    domicile              → student.domicile
#    Set value="" and confidence=0.0 if no match.

# 5. confidence: 1.0=exact, 0.5=inferred, 0.0=no match.
# 6. Include ALL fields from ALL pages even if confidence is 0.
# 7. Return ONLY JSON.
# """

#         prompt = ChatPromptTemplate.from_messages([
#             ("system", system_prompt),
#             ("human",
#              "STUDENT DATA (includes _portal_email and _portal_password):\n{student_data}\n\n"
#              "SCRAPED PAGES (login + application steps):\n{pages_data}\n\n"
#              "URL: {url}\nAPP ID: {app_id}"),
#         ])

#         chain  = prompt | self.llm | self.parser
#         result = chain.invoke({
#             "student_data": json.dumps(student_data_with_creds, indent=2),
#             "pages_data":   json.dumps(pages, indent=2),
#             "url":          target_url,
#             "app_id":       app_id,
#         })
#         return result


# # ─────────────────────────────────────────────────────────────────────────────
# # AUTOMATION SERVICE
# # ─────────────────────────────────────────────────────────────────────────────

# class AutomationService:

#     # ── Normalization ──────────────────────────────────────────────────────

#     def normalize_value(self, field_name, value):
#         if not value:
#             return value
#         value    = str(value).strip()
#         city_map = {
#             "lahore": "Punjab", "karachi": "Sindh", "islamabad": "Islamabad",
#             "peshawar": "KPK",  "quetta": "Balochistan",
#         }
#         if field_name and "province" in field_name.lower():
#             return city_map.get(value.lower(), value)
#         return value

#     def normalize_course(self, value):
#         if not value:
#             return []
#         v = str(value).lower().strip()
#         m = {
#             "cs":                     ["cs","computer science","bscs"],
#             "bscs":                   ["bscs","computer science","cs"],
#             "computer science":       ["computer science","cs","bscs"],
#             "bsse":                   ["bsse","software engineering","software"],
#             "software engineering":   ["software engineering","bsse","software"],
#             "bsit":                   ["bsit","information technology","it","bs information technology","bs (it)"],
#             "it":                     ["it","information technology","bsit"],
#             "information technology": ["information technology","bsit","it","bs information technology"],
#             "bba":                    ["bba","business administration","business"],
#             "business administration":["business administration","bba","business"],
#             "finance":                ["finance","bba finance","business finance"],
#             "mbbs":                   ["mbbs","medicine","medical"],
#             "bds":                    ["bds","dentistry","dental"],
#             "nursing":                ["nursing","bsn","bs nursing"],
#             "psychology":             ["psychology","bs psychology"],
#             "sociology":              ["sociology","bs sociology"],
#             "llb":                    ["llb","law","bachelor of law","legal"],
#             "law":                    ["law","llb","legal studies","legal"],
#         }
#         return m.get(v, [v])

#     def normalize_date(self, value):
#         if not value:
#             return value
#         fmts = [
#             "%Y-%m-%d","%Y %m %d","%Y/%m/%d",
#             "%d-%m-%Y","%d/%m/%Y","%d %m %Y",
#             "%m/%d/%Y","%m-%d-%Y",
#             "%d %b %Y","%d %B %Y","%B %d, %Y","%b %d, %Y",
#         ]
#         dt = None
#         for fmt in fmts:
#             try: dt = datetime.strptime(str(value).strip(), fmt); break
#             except Exception: continue
#         if not dt:
#             return {"iso":value,"dmy":value,"dmy_dash":value,"dmy_slash":value,
#                     "mdy":value,"long":value,"dt":None,"day":"","month":"","year":""}
#         return {
#             "iso":       dt.strftime("%Y-%m-%d"),
#             "dmy":       dt.strftime("%d %m %Y"),
#             "dmy_dash":  dt.strftime("%d-%m-%Y"),
#             "dmy_slash": dt.strftime("%d/%m/%Y"),
#             "mdy":       dt.strftime("%m/%d/%Y"),
#             "long":      dt.strftime("%d %b %Y"),
#             "dt":        dt,
#             "day":       dt.strftime("%d"),
#             "month":     dt.strftime("%m"),
#             "year":      dt.strftime("%Y"),
#         }

#     # ── React helpers ──────────────────────────────────────────────────────

#     def is_react_page(self, driver):
#         return driver.execute_script(
#             "return !!(window.__REACT_DEVTOOLS_GLOBAL_HOOK__ || "
#             "document.querySelector('[data-reactroot]') || "
#             "document.querySelector('#root'))"
#         )

#     def react_set_value(self, driver, element, value):
#         driver.execute_script("""
#             var el = arguments[0], val = arguments[1];
#             var proto = el.tagName.toLowerCase() === 'textarea'
#                 ? window.HTMLTextAreaElement.prototype
#                 : window.HTMLInputElement.prototype;
#             Object.getOwnPropertyDescriptor(proto, 'value').set.call(el, val);
#             el.dispatchEvent(new Event('input',  { bubbles: true }));
#             el.dispatchEvent(new Event('change', { bubbles: true }));
#         """, element, value)

#     # ── Date helpers ───────────────────────────────────────────────────────

#     def detect_date_format(self, element):
#         hint = " ".join([
#             element.get_attribute("placeholder") or "",
#             element.get_attribute("pattern")     or "",
#             element.get_attribute("data-format") or "",
#         ]).lower()
#         if any(x in hint for x in ["dd-mm-yyyy","dd/mm/yyyy","dd mm yyyy"]):
#             return "dmy_slash" if "/" in hint else "dmy_dash"
#         if any(x in hint for x in ["mm/dd/yyyy","mm-dd-yyyy"]): return "mdy"
#         if "yyyy-mm-dd" in hint: return "iso"
#         return None

#     def fill_date_react(self, driver, element, formats):
#         input_type = (element.get_attribute("type") or "").lower()
#         fmt_key    = self.detect_date_format(element)
#         if input_type == "date":
#             self.fill_react_native_date(driver, element, formats, fmt_key); return
#         formatted = formats.get(fmt_key, formats["dmy_dash"]) if fmt_key else formats["dmy_dash"]
#         self.react_set_value(driver, element, formatted); time.sleep(0.2)
#         if element.get_attribute("value"): return
#         if PYPERCLIP_AVAILABLE:
#             try:
#                 pyperclip.copy(formatted)
#                 element.send_keys(Keys.CONTROL + "v"); time.sleep(0.3)
#                 if element.get_attribute("value"): return
#             except Exception: pass
#         driver.execute_script("arguments[0].click();", element)
#         element.send_keys(Keys.CONTROL + "a"); element.send_keys(Keys.DELETE)
#         for char in formatted: element.send_keys(char); time.sleep(0.04)

#     def fill_react_native_date(self, driver, element, formats, fmt_key):
#         self.react_set_value(driver, element, formats["iso"]); time.sleep(0.2)
#         if element.get_attribute("value") == formats["iso"]: return
#         driver.execute_script("arguments[0].click();", element)
#         element.send_keys(formats["month"]); time.sleep(0.1)
#         element.send_keys(formats["day"]);   time.sleep(0.1)
#         element.send_keys(formats["year"])

#     def fill_native_date(self, driver, element, formats):
#         iso = formats["iso"]
#         driver.execute_script("arguments[0].value = arguments[1];", element, iso)
#         driver.execute_script(
#             "arguments[0].dispatchEvent(new Event('input',{bubbles:true}));"
#             "arguments[0].dispatchEvent(new Event('change',{bubbles:true}));", element)
#         if element.get_attribute("value") != iso:
#             element.clear(); element.send_keys(iso)

#     def fill_custom_date(self, driver, element, formats):
#         fmt_key = self.detect_date_format(element)
#         if fmt_key:
#             element.clear(); time.sleep(0.2)
#             element.send_keys(formats.get(fmt_key, formats["dmy_dash"]))
#         else:
#             for key in ["dmy_dash","dmy_slash","dmy","iso","mdy"]:
#                 element.clear(); time.sleep(0.2)
#                 element.send_keys(formats.get(key,"")); time.sleep(0.3)
#                 if element.get_attribute("value"): return
#             driver.execute_script("arguments[0].value = arguments[1];", element, formats["dmy_dash"])
#             driver.execute_script(
#                 "arguments[0].dispatchEvent(new Event('input',{bubbles:true}));"
#                 "arguments[0].dispatchEvent(new Event('change',{bubbles:true}));", element)

#     # ── File path resolver ─────────────────────────────────────────────────

#     def resolve_file_path(self, value):
#         if not value:
#             raise ValueError("File path is empty")
#         path = str(value).strip()
#         if os.path.isabs(path) and os.path.isfile(path): return path
#         media_root = getattr(settings, "MEDIA_ROOT", "")
#         if media_root:
#             clean = path.lstrip("/\\")
#             if clean.startswith("media/") or clean.startswith("media\\"):
#                 clean = clean[6:]
#             candidate = os.path.join(str(media_root), clean)
#             if os.path.isfile(candidate): return os.path.abspath(candidate)
#         base_dir = getattr(settings, "BASE_DIR", "")
#         if base_dir:
#             candidate = os.path.join(str(base_dir), path.lstrip("/\\"))
#             if os.path.isfile(candidate): return os.path.abspath(candidate)
#         abs_attempt = os.path.abspath(path)
#         if os.path.isfile(abs_attempt): return abs_attempt
#         raise FileNotFoundError(
#             f"File not found: '{value}' — tried MEDIA_ROOT='{media_root}', BASE_DIR='{base_dir}'"
#         )

#     # ── wait_for_element ───────────────────────────────────────────────────

#     def wait_for_element(self, driver, selector, timeout=10, clickable=False):
#         if selector in ("NEXT_BUTTON", "next_button"):
#             deadline = time.time() + timeout
#             while time.time() < deadline:
#                 el = _find_next_button(driver)
#                 if el: return el
#                 time.sleep(REACT_POLL_INTERVAL)
#             raise TimeoutException("No Next button found")

#         if selector in ("SUBMIT_BUTTON", "submit_button"):
#             deadline = time.time() + timeout
#             while time.time() < deadline:
#                 el = _find_submit_button(driver)
#                 if el: return el
#                 time.sleep(REACT_POLL_INTERVAL)
#             raise TimeoutException("No Submit button found")

#         if selector in ("LOGIN_BUTTON", "login_button"):
#             deadline = time.time() + timeout
#             while time.time() < deadline:
#                 el = _find_login_button(driver)
#                 if el: return el
#                 time.sleep(REACT_POLL_INTERVAL)
#             raise TimeoutException("No Login button found")

#         if ":contains(" in selector:
#             match = re.match(r"^(\w+)?:contains\(['\"](.+?)['\"]\)$", selector.strip())
#             if match:
#                 tag, text = match.group(1) or "*", match.group(2).lower()
#             else:
#                 tag  = "*"
#                 text = selector.split(":contains(")[1].strip("'\")")
#             xpath = (
#                 f"//{tag}[contains("
#                 f"translate(normalize-space(.),"
#                 f"'ABCDEFGHIJKLMNOPQRSTUVWXYZ','abcdefghijklmnopqrstuvwxyz'),"
#                 f"'{text.lower()}')]"
#             )
#             wait = WebDriverWait(driver, timeout)
#             cond = EC.element_to_be_clickable if clickable else EC.presence_of_element_located
#             try:
#                 return wait.until(cond((By.XPATH, xpath)))
#             except TimeoutException:
#                 fn = _find_login_button  if any(kw in selector.lower() for kw in LOGIN_KEYWORDS) \
#                      else _find_next_button if any(kw in selector.lower() for kw in NEXT_KEYWORDS) \
#                      else _find_submit_button
#                 el = fn(driver)
#                 if el: return el
#                 raise

#         wait = WebDriverWait(driver, timeout)
#         by   = By.CSS_SELECTOR
#         if selector.startswith("#"):
#             by, selector = By.ID, selector[1:]
#         elif selector.startswith("//"):
#             by = By.XPATH
#         elif selector.startswith("[name="):
#             by, selector = By.NAME, selector.split("'")[1]

#         try:
#             el_type = driver.find_element(by, selector).get_attribute("type") or ""
#             if el_type == "file": clickable = False
#         except Exception:
#             pass

#         cond = EC.element_to_be_clickable if clickable else EC.presence_of_element_located
#         return wait.until(cond((by, selector)))

#     # ── fill_field ─────────────────────────────────────────────────────────

#     def fill_field(self, driver, element, field_type, value):
#         tag        = element.tag_name.lower()
#         input_type = (element.get_attribute("type") or "").lower()
#         is_react   = self.is_react_page(driver)

#         if field_type == "file" or input_type == "file":
#             try:
#                 abs_path = self.resolve_file_path(value)
#             except (FileNotFoundError, ValueError) as e:
#                 raise Exception(f"File upload failed — {e}")
#             driver.execute_script("""
#                 arguments[0].style.display    = 'block';
#                 arguments[0].style.opacity    = '1';
#                 arguments[0].style.visibility = 'visible';
#             """, element)
#             time.sleep(0.2)
#             element.send_keys(abs_path)
#             driver.execute_script(
#                 "arguments[0].dispatchEvent(new Event('change',{bubbles:true}));", element)
#             print(f"✅ File: {os.path.basename(abs_path)}")
#             return

#         if input_type == "password":
#             element.clear()
#             element.send_keys(str(value))
#             return

#         if input_type in ["checkbox", "radio"]:
#             if str(value).lower() in ["true","1","yes"]:
#                 driver.execute_script("arguments[0].click();", element)
#             return

#         if field_type == "date" or input_type == "date":
#             formats = self.normalize_date(value)
#             if not formats.get("dt"):
#                 element.clear(); element.send_keys(str(value)); return
#             if is_react:
#                 self.fill_date_react(driver, element, formats)
#             elif input_type == "date":
#                 fmt_key = self.detect_date_format(element)
#                 (self.fill_custom_date if (fmt_key and fmt_key != "iso") else self.fill_native_date)(
#                     driver, element, formats)
#             else:
#                 self.fill_custom_date(driver, element, formats)
#             return

#         if tag == "select":
#             sel     = Select(element)
#             options = [o.text.strip() for o in sel.options]
#             opt_low = [o.lower() for o in options]
#             for target in self.normalize_course(value):
#                 t = target.lower().strip()
#                 for i, opt in enumerate(opt_low):
#                     if opt == t:                           sel.select_by_visible_text(options[i]); return
#                 for i, opt in enumerate(opt_low):
#                     if opt and opt in t:                  sel.select_by_visible_text(options[i]); return
#                 for i, opt in enumerate(opt_low):
#                     if t and t in opt:                    sel.select_by_visible_text(options[i]); return
#                 for i, opt in enumerate(opt_low):
#                     if set(t.split()) & set(opt.split()): sel.select_by_visible_text(options[i]); return
#             raise Exception(f"Dropdown option not found for '{value}'. Available: {options}")

#         if tag in ["input", "textarea"]:
#             self.react_set_value(driver, element, str(value)) if is_react \
#                 else (element.clear() or element.send_keys(str(value)))
#             return

#         driver.execute_script("arguments[0].value = arguments[1];", element, value)
#         driver.execute_script(
#             "arguments[0].dispatchEvent(new Event('change',{bubbles:true}));", element)

#     # ── Main runner ────────────────────────────────────────────────────────

#     def run(self, mapping: dict) -> dict:
#         """
#         FIX: click step now passes prev_signature to _wait_for_dom_change
#              instead of prev_count + prev_url.
#         """
#         url        = mapping.get("url")
#         steps      = mapping.get("steps", [])
#         student_id = mapping.get("application_id", 0)

#         if not url:
#             return {"status":"failed","message":"No URL provided","screenshots":[]}

#         options = Options()
#         options.add_argument("--start-maximized")

#         driver = webdriver.Chrome(options=options)
#         driver.get(url)
#         _wait_for_react_hydration(driver, timeout=15)

#         completed_steps = 0
#         screenshot_log  = []

#         last_app_fill_idx = None
#         for i, s in enumerate(steps):
#             if s.get("action") == "fill" and s.get("page_type") == "application":
#                 last_app_fill_idx = i

#         def _snap(label):
#             entry = _take_screenshot(driver, student_id, url, label)
#             if entry:
#                 screenshot_log.append(entry)

#         try:
#             for step_idx, step in enumerate(steps):
#                 action = step.get("action")

#                 if action == "fill":
#                     page_type = step.get("page_type", "application")
#                     print(f"\n📝 Fill step {step_idx} [{page_type}]")

#                     for field in step.get("fields", []):
#                         selector   = field.get("selector")
#                         field_type = (field.get("type") or "text").lower()
#                         raw_value  = field.get("value")

#                         if (raw_value is None or raw_value == "") and field_type != "file":
#                             continue
#                         if field_type == "file" and not raw_value:
#                             print(f"⏭️  No file path for {selector}")
#                             continue

#                         value = self.normalize_value(selector, raw_value)
#                         print(f"   🖊  [{field_type}] {selector} → {value!r}")

#                         try:
#                             element = self.wait_for_element(
#                                 driver, selector, clickable=(field_type != "file"))
#                             if field_type != "file":
#                                 driver.execute_script(
#                                     "arguments[0].scrollIntoView({block:'center'});", element)
#                             self.fill_field(driver, element, field_type, value)
#                             time.sleep(0.2)
#                         except Exception as e:
#                             print(f"   ❌ Failed {selector}: {e}")
#                             _save_manifest(student_id, url, screenshot_log)
#                             driver.quit()
#                             return {
#                                 "status":"failed","message":f"Error filling {selector}",
#                                 "error":str(e),"completed_steps":completed_steps,
#                                 "screenshots":screenshot_log,
#                             }

#                     if step_idx == last_app_fill_idx:
#                         time.sleep(0.7)
#                         driver.execute_script("window.scrollTo(0, 0);")
#                         time.sleep(0.2)
#                         _snap("before_submit")
#                         print("📸 before_submit screenshot taken")

#                     completed_steps += 1

#                 elif action == "login_click":
#                     selector = step.get("selector", "LOGIN_BUTTON")
#                     wait_ms  = step.get("wait_ms", 3000)
#                     print(f"\n🔐 Login click (selector: {selector!r})")

#                     element = None
#                     try:
#                         element = self.wait_for_element(driver, selector, clickable=True)
#                     except Exception as e:
#                         print(f"⚠️  Login button '{selector}' not found: {e}")
#                         element = _find_login_button(driver)

#                     if not element:
#                         _save_manifest(student_id, url, screenshot_log)
#                         driver.quit()
#                         return {
#                             "status":"failed","message":"Login button not found",
#                             "completed_steps":completed_steps,"screenshots":screenshot_log,
#                         }

#                     driver.execute_script("arguments[0].scrollIntoView({block:'center'});", element)
#                     driver.execute_script("arguments[0].click();", element)
#                     print("   ▶ Clicked login — waiting for password field to disappear...")

#                     try:
#                         WebDriverWait(driver, 15).until(
#                             EC.invisibility_of_element_located(
#                                 (By.XPATH, "//input[@type='password']")
#                             )
#                         )
#                         print("   ✅ Login successful")
#                         time.sleep(1.5)
#                         _wait_for_react_hydration(driver, timeout=10)
#                     except TimeoutException:
#                         _save_manifest(student_id, url, screenshot_log)
#                         driver.quit()
#                         return {
#                             "status":"failed",
#                             "message":"Login timed out — password field never disappeared.",
#                             "completed_steps":completed_steps,"screenshots":screenshot_log,
#                         }

#                     time.sleep(0.5)
#                     driver.execute_script("window.scrollTo(0, 0);")
#                     time.sleep(0.2)
#                     _snap("after_login")
#                     print("📸 after_login screenshot taken")
#                     completed_steps += 1

#                 elif action == "click":
#                     selector = step.get("selector", "NEXT_BUTTON")
#                     wait_ms  = step.get("wait_ms", 1500)
#                     print(f"\n▶  Next click (selector: {selector!r})")

#                     # FIX: take signature BEFORE clicking
#                     prev_signature = _get_form_signature(driver)

#                     element = None
#                     try:
#                         element = self.wait_for_element(driver, selector, clickable=True)
#                     except Exception as e:
#                         print(f"⚠️  Next selector failed: {e} — trying smart finder")
#                         element = _find_next_button(driver)

#                     if not element:
#                         _save_manifest(student_id, url, screenshot_log)
#                         driver.quit()
#                         return {
#                             "status":"failed","message":"Next button not found",
#                             "completed_steps":completed_steps,"screenshots":screenshot_log,
#                         }

#                     driver.execute_script("arguments[0].scrollIntoView({block:'center'});", element)
#                     driver.execute_script("arguments[0].click();", element)
#                     completed_steps += 1

#                     # FIX: pass prev_signature (not count+url)
#                     changed = _wait_for_dom_change(driver, prev_signature, timeout=12)
#                     if not changed:
#                         print("   ⚠️  DOM unchanged — using wait_ms fallback")
#                         time.sleep(wait_ms / 1000)

#                 elif action == "submit":
#                     selector = step.get("selector", "SUBMIT_BUTTON")
#                     wait_ms  = step.get("wait_ms", 3000)

#                     completed_steps += 1
#                     time.sleep(0.3)
#                     _snap("before_final_submit")
#                     print("📸 before_final_submit screenshot taken")
#                     print(f"\n✅ Submit (selector: {selector!r})")

#                     element = None
#                     try:
#                         element = self.wait_for_element(driver, selector, clickable=True)
#                     except Exception as e:
#                         print(f"⚠️  Submit selector failed: {e} — trying smart finder")
#                         element = _find_submit_button(driver)

#                     if not element:
#                         _save_manifest(student_id, url, screenshot_log)
#                         driver.quit()
#                         return {
#                             "status":"failed","message":"Submit button not found",
#                             "completed_steps":completed_steps,"screenshots":screenshot_log,
#                         }

#                     try:
#                         driver.execute_script(
#                             "arguments[0].scrollIntoView({block:'center'});", element)
#                         driver.execute_script("arguments[0].click();", element)
#                         time.sleep(wait_ms / 1000)
#                     except Exception as e:
#                         _save_manifest(student_id, url, screenshot_log)
#                         driver.quit()
#                         return {
#                             "status":"failed","message":"Submit click failed",
#                             "error":str(e),"completed_steps":completed_steps,
#                             "screenshots":screenshot_log,
#                         }

#                     driver.execute_script("window.scrollTo(0, 0);")
#                     time.sleep(0.3)
#                     _snap("after_submit")
#                     print("📸 after_submit screenshot taken")

#                     _save_manifest(student_id, url, screenshot_log)
#                     driver.quit()
#                     return {
#                         "status":"success","message":"Form submitted successfully",
#                         "completed_steps":completed_steps + 1,"screenshots":screenshot_log,
#                     }

#             _save_manifest(student_id, url, screenshot_log)
#             driver.quit()
#             return {"status":"success","completed_steps":completed_steps,
#                     "screenshots":screenshot_log}

#         except Exception as e:
#             try:
#                 _save_manifest(student_id, url, screenshot_log)
#                 driver.quit()
#             except Exception:
#                 pass
#             return {"status":"failed","error":str(e),"screenshots":screenshot_log}

"""
automation_pipeline/services.py  —  FIXED VERSION

KEY FIXES IN THIS VERSION:

1. DOM CHANGE DETECTION — completely rewritten
   - No longer uses URL changes or input COUNT changes
   - Now hashes the FULL visible form/container innerHTML
   - Uses multiple hash strategies: form tag, main container, full body
   - Waits until the hash changes before declaring a new step
   - This correctly handles React SPAs where URL never changes and
     field count may be identical across steps

2. SCRAPER CALL SITE FIX
   - scrape_full_flow() was passing prev_signature to _wait_for_dom_change()
     but the function signature expected prev_count + prev_url (old signature)
   - Now the function only takes prev_signature — fully consistent

3. UPLOAD FIELD DETECTION — now uses Selenium live DOM inspection
   - BeautifulSoup static HTML misses React-rendered file inputs
   - New _extract_fields_selenium() uses driver.find_elements() directly
   - Explicitly detects:
       * input[type="file"] (including hidden/invisible ones)
       * React upload buttons by text: "upload", "browse", "click document", etc.
       * drag-drop containers with data-upload / dropzone attributes

4. STEP LIMIT — raised from 10 to 15 pages to handle longer forms
"""

import hashlib
import time
import os
import re
import json
from pathlib import Path
from datetime import datetime
from urllib.parse import urlparse

from bs4 import BeautifulSoup

from django.conf import settings

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import Select, WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import PydanticOutputParser

from .schemas import AutomationResponse

try:
    import pyperclip
    PYPERCLIP_AVAILABLE = True
except ImportError:
    PYPERCLIP_AVAILABLE = False


# ─────────────────────────────────────────────────────────────────────────────
# Constants
# ─────────────────────────────────────────────────────────────────────────────

NEXT_KEYWORDS = [
    "next", "continue", "proceed", "forward",
    "آگے", "اگلا", "اگلہ",
    "next step", "next page", "save & next", "save and next", "save & continue",
]
SUBMIT_KEYWORDS = [
    "submit", "finish", "complete", "send", "apply",
    "جمع کریں", "submit application", "final submit",
]
LOGIN_KEYWORDS  = ["login", "log in", "sign in", "signin", "لاگ ان"]
NEXT_ID_HINTS   = ["next", "continue", "proceed", "forward", "step"]
UPLOAD_KEYWORDS = ["upload", "browse", "click document", "choose file", "select file",
                   "attach", "drag", "drop file", "pick file"]

REACT_STEP_TIMEOUT  = 8
REACT_POLL_INTERVAL = 0.25
MAX_FORM_STEPS      = 15   # raised from 10


# ─────────────────────────────────────────────────────────────────────────────
# Browser setup (local: visible Chrome; server: headless Chromium via env vars)
# ─────────────────────────────────────────────────────────────────────────────

def _new_chrome(headless: bool):
    """
    AUTOMATION_HEADLESS=1   force headless (servers have no screen)
    CHROME_BIN              browser binary, e.g. /usr/bin/chromium in Docker
    CHROMEDRIVER_PATH       matching driver, e.g. /usr/bin/chromedriver
    """
    from selenium.webdriver.chrome.service import Service

    headless = headless or os.getenv("AUTOMATION_HEADLESS") == "1"
    options = Options()
    if headless:
        options.add_argument("--headless=new")
        options.add_argument("--window-size=1920,1080")
    else:
        options.add_argument("--start-maximized")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    if os.getenv("CHROME_BIN"):
        options.binary_location = os.environ["CHROME_BIN"]

    driver_path = os.getenv("CHROMEDRIVER_PATH")
    service = Service(driver_path) if driver_path else Service()
    return webdriver.Chrome(service=service, options=options)


# ─────────────────────────────────────────────────────────────────────────────
# Smart button finders
# ─────────────────────────────────────────────────────────────────────────────

def _btn_text(driver, el):
    try:
        return (driver.execute_script("return arguments[0].textContent;", el) or "").strip()
    except Exception:
        return (el.text or "").strip()


def _find_button_by_keywords(driver, keywords):
    all_btns = driver.find_elements(
        By.CSS_SELECTOR, "button, input[type='submit'], a[role='button']"
    )
    for kw in keywords:
        for el in driver.find_elements(
            By.CSS_SELECTOR,
            f"button[id*='{kw}'], button[name*='{kw}'], button[class*='{kw}'], "
            f"input[type='submit'][id*='{kw}'], a[id*='{kw}']"
        ):
            if el.is_displayed() and el.is_enabled():
                return el
    for el in all_btns:
        if not (el.is_displayed() and el.is_enabled()):
            continue
        text = _btn_text(driver, el).lower()
        if any(kw in text for kw in keywords):
            return el
    for el in all_btns:
        if not (el.is_displayed() and el.is_enabled()):
            continue
        label = (el.get_attribute("aria-label") or "").lower()
        if any(kw in label for kw in keywords):
            return el
    return None


def _find_next_button(driver):
    btn = _find_button_by_keywords(driver, NEXT_KEYWORDS)
    if btn:
        print(f"🔍 Next btn: {_btn_text(driver, btn)!r}")
        return btn
    ignore = {"back", "previous", "cancel", "reset", "واپس", "پچھلا"}
    all_btns = driver.find_elements(By.CSS_SELECTOR, "button, input[type='submit']")
    visible  = [
        el for el in all_btns
        if el.is_displayed() and el.is_enabled()
        and not any(x in _btn_text(driver, el).lower() for x in ignore)
    ]
    if visible:
        el = visible[-1]
        print(f"🔍 Next btn (last-button heuristic): {_btn_text(driver, el)!r}")
        return el
    print("⚠️  No Next button found")
    return None


def _find_submit_button(driver):
    btn = _find_button_by_keywords(driver, SUBMIT_KEYWORDS)
    if btn:
        print(f"🔍 Submit btn: {_btn_text(driver, btn)!r}")
        return btn
    all_btns = driver.find_elements(By.CSS_SELECTOR, "button, input[type='submit']")
    visible  = [e for e in all_btns if e.is_displayed() and e.is_enabled()]
    if visible:
        print(f"🔍 Submit btn (last fallback): {_btn_text(driver, visible[-1])!r}")
        return visible[-1]
    return None


def _find_login_button(driver):
    btn = _find_button_by_keywords(driver, LOGIN_KEYWORDS)
    if btn:
        print(f"🔍 Login btn: {_btn_text(driver, btn)!r}")
        return btn
    all_btns = driver.find_elements(
        By.CSS_SELECTOR, "button[type='submit'], input[type='submit']"
    )
    visible = [e for e in all_btns if e.is_displayed() and e.is_enabled()]
    if visible:
        print(f"🔍 Login btn (submit fallback): {_btn_text(driver, visible[0])!r}")
        return visible[0]
    return None


# ─────────────────────────────────────────────────────────────────────────────
# DOM CHANGE DETECTION  ← completely rewritten
# ─────────────────────────────────────────────────────────────────────────────

def _get_form_signature(driver):
    """
    Returns a stable MD5 hash of the currently visible form HTML.

    Strategy (tries in order, uses first that works):
      1. The first VISIBLE <form> element's innerHTML
      2. A React container: #root, #app, main, [role="main"]
      3. Full document body innerHTML (last resort)

    Hashing innerHTML (not just field count or URL) is reliable for
    React SPAs because React replaces the internal DOM on step change
    even when URL and field count stay the same.
    """
    try:
        # Strategy 1: visible <form>
        forms = driver.find_elements(By.TAG_NAME, "form")
        for f in forms:
            try:
                if f.is_displayed():
                    html = f.get_attribute("innerHTML") or ""
                    if len(html) > 50:
                        return hashlib.md5(html.encode("utf-8", errors="replace")).hexdigest()
            except Exception:
                continue

        # Strategy 2: React root / main content container
        for selector in ["main", "[role='main']", "#root", "#app", ".app", "[data-reactroot]"]:
            try:
                els = driver.find_elements(By.CSS_SELECTOR, selector)
                for el in els:
                    if el.is_displayed():
                        html = el.get_attribute("innerHTML") or ""
                        if len(html) > 50:
                            return hashlib.md5(html.encode("utf-8", errors="replace")).hexdigest()
            except Exception:
                continue

        # Strategy 3: full body
        body = driver.find_element(By.TAG_NAME, "body")
        html = body.get_attribute("innerHTML") or ""
        return hashlib.md5(html.encode("utf-8", errors="replace")).hexdigest()

    except Exception:
        return ""


def _wait_for_dom_change(driver, prev_signature, timeout=12):
    """
    Polls until the form signature changes from prev_signature.
    Returns True if change detected, False if timed out.

    timeout raised to 12s to handle slow React renders.
    """
    deadline = time.time() + timeout
    while time.time() < deadline:
        try:
            new_sig = _get_form_signature(driver)
            if new_sig and new_sig != prev_signature:
                # Small grace period for React to finish rendering
                time.sleep(0.6)
                _wait_for_react_hydration(driver, timeout=5)
                return True
        except Exception:
            pass
        time.sleep(0.25)
    return False


def _wait_for_react_hydration(driver, timeout=15):
    deadline = time.time() + timeout
    while time.time() < deadline:
        try:
            root   = driver.find_elements(By.CSS_SELECTOR, "#root, #app, [data-reactroot]")
            container = root[0] if root else driver.find_element(By.TAG_NAME, "body")
            inputs = container.find_elements(
                By.CSS_SELECTOR, "input:not([type='hidden']), select, textarea"
            )
            if any(el.is_displayed() for el in inputs):
                return True
        except Exception:
            pass
        time.sleep(REACT_POLL_INTERVAL)
    return False


def _is_login_page(driver):
    try:
        pwd = driver.find_elements(By.XPATH, "//input[@type='password']")
        return any(el.is_displayed() for el in pwd)
    except Exception:
        return False


# ─────────────────────────────────────────────────────────────────────────────
# FIELD EXTRACTION  ← now uses live Selenium DOM + upload detection
# ─────────────────────────────────────────────────────────────────────────────

def _extract_fields_from_page(driver, include_password=False):
    """
    PRIMARY: BeautifulSoup static parse (fast, catches most fields).
    THEN: Selenium live DOM pass to catch React-rendered file inputs
          and upload components that BS4 misses.
    """
    fields       = _extract_fields_bs4(driver, include_password)
    extra_fields = _extract_upload_fields_selenium(driver, fields)

    seen = {f["selector"] for f in fields}
    for ef in extra_fields:
        if ef["selector"] not in seen:
            fields.append(ef)
            seen.add(ef["selector"])

    return fields


def _extract_fields_bs4(driver, include_password=False):
    """Original BeautifulSoup extraction — unchanged logic."""
    soup     = BeautifulSoup(driver.page_source, "html.parser")
    elements = []

    for el in soup.find_all(["input", "select", "textarea"]):
        el_type = el.get("type", "text").lower() if el.name == "input" else el.name
        if el_type == "hidden":
            continue
        if el_type == "password" and not include_password:
            continue

        if el.get("id"):
            selector = f"#{el.get('id')}"
        elif el.get("name"):
            selector = f"[name='{el.get('name')}']"
        elif el.get("data-testid"):
            selector = f"[data-testid='{el.get('data-testid')}']"
        else:
            continue

        label = ""
        if el.get("id"):
            lbl = soup.find("label", attrs={"for": el.get("id")})
            if lbl:
                label = lbl.get_text(strip=True)
        if not label:
            label = el.get("placeholder") or el.get("aria-label") or el.get("name") or ""

        entry = {"selector": selector, "type": el_type, "label": label}
        if el_type == "file":
            entry["accept"] = el.get("accept", "")
        if el.name == "select":
            entry["options"] = [
                o.get_text(strip=True) for o in el.find_all("option")
                if o.get_text(strip=True)
            ]
        elements.append(entry)

    return elements


def _extract_upload_fields_selenium(driver, existing_fields):
    """
    Uses live Selenium DOM to find upload-related elements that BS4 misses:
      1. input[type='file'] elements (including invisible/hidden ones)
      2. Buttons/divs with upload-related text
      3. Dropzone containers
    """
    extra = []
    existing_selectors = {f["selector"] for f in existing_fields}

    # ── 1. All file inputs (including hidden ones React hides) ──────────────
    try:
        file_inputs = driver.find_elements(By.CSS_SELECTOR, "input[type='file']")
        for el in file_inputs:
            el_id   = el.get_attribute("id")
            el_name = el.get_attribute("name")
            el_test = el.get_attribute("data-testid")

            if el_id:
                selector = f"#{el_id}"
            elif el_name:
                selector = f"[name='{el_name}']"
            elif el_test:
                selector = f"[data-testid='{el_test}']"
            else:
                # Generate a unique selector using class or index
                el_class = el.get_attribute("class") or ""
                if el_class:
                    first_class = el_class.split()[0]
                    selector    = f"input.{first_class}[type='file']"
                else:
                    continue

            if selector in existing_selectors:
                continue

            # Try to find a label for context
            label = el.get_attribute("aria-label") or el.get_attribute("name") or ""
            if el_id:
                try:
                    lbl_el = driver.find_element(By.CSS_SELECTOR, f"label[for='{el_id}']")
                    label  = lbl_el.text.strip() or label
                except Exception:
                    pass

            accept = el.get_attribute("accept") or ""
            print(f"   📎 Found file input via Selenium: {selector!r} label={label!r} accept={accept!r}")
            extra.append({
                "selector": selector,
                "type":     "file",
                "label":    label,
                "accept":   accept,
            })
    except Exception as e:
        print(f"   ⚠️  Selenium file input scan error: {e}")

    # ── 2. Upload buttons / divs with upload-related text ───────────────────
    try:
        candidates = driver.find_elements(
            By.CSS_SELECTOR,
            "button, div[role='button'], label[role='button'], "
            "div[class*='upload'], div[class*='drop'], div[class*='dropzone'], "
            "label[class*='upload'], span[class*='upload']"
        )
        for el in candidates:
            try:
                text = (driver.execute_script(
                    "return arguments[0].textContent;", el) or "").strip().lower()
            except Exception:
                text = (el.text or "").strip().lower()

            if not any(kw in text for kw in UPLOAD_KEYWORDS):
                continue
            if not el.is_displayed():
                continue

            # Only include if it wraps or is associated with a file input
            # (label[for=...] pattern is the most reliable)
            for_attr = el.get_attribute("for") or ""
            if for_attr:
                selector = f"#{for_attr}"
                if selector not in existing_selectors:
                    label = el.text.strip()
                    print(f"   📎 Found upload label via Selenium: {selector!r} text={label!r}")
                    extra.append({
                        "selector": selector,
                        "type":     "file",
                        "label":    label,
                        "accept":   "",
                    })
    except Exception as e:
        print(f"   ⚠️  Selenium upload button scan error: {e}")

    # ── 3. Dropzone containers ───────────────────────────────────────────────
    try:
        dropzones = driver.find_elements(
            By.CSS_SELECTOR,
            "[data-dropzone], [class*='dropzone'], [class*='drop-zone'], "
            "[data-upload], [class*='file-upload']"
        )
        for el in dropzones:
            if not el.is_displayed():
                continue
            el_id = el.get_attribute("id")
            if not el_id:
                continue
            selector = f"#{el_id}"
            if selector in existing_selectors:
                continue
            label = el.get_attribute("aria-label") or el.text.strip()[:40] or "dropzone"
            print(f"   📎 Found dropzone via Selenium: {selector!r}")
            extra.append({
                "selector": selector,
                "type":     "file",
                "label":    label,
                "accept":   "",
            })
    except Exception as e:
        print(f"   ⚠️  Selenium dropzone scan error: {e}")

    return extra


# ─────────────────────────────────────────────────────────────────────────────
# Screenshot helpers
# ─────────────────────────────────────────────────────────────────────────────

def _uni_slug(url: str) -> str:
    try:
        parsed     = urlparse(url)
        host       = parsed.hostname or "unknown"
        port       = parsed.port or ""
        path       = parsed.path.strip("/")
        slug_parts = [host]
        if port:
            slug_parts.append(str(port))
        if path:
            slug_parts.append(path.replace("/", "-"))
        slug = "-".join(slug_parts)
        return re.sub(r"[^a-z0-9\-]+", "-", slug.lower()).strip("-")
    except Exception:
        return "unknown"


def _screenshots_dir(student_id, portal_url: str) -> Path:
    slug = _uni_slug(portal_url)
    d    = Path(settings.MEDIA_ROOT) / "screenshots" / str(student_id) / slug
    d.mkdir(parents=True, exist_ok=True)
    return d


def _take_screenshot(driver, student_id, portal_url: str, label: str) -> dict:
    d        = _screenshots_dir(student_id, portal_url)
    slug     = _uni_slug(portal_url)
    filename = f"{label}.png"
    filepath = d / filename
    try:
        driver.save_screenshot(str(filepath))
        print(f"📸 {filepath}")
    except Exception as e:
        print(f"⚠️  Screenshot failed: {e}")
        return {}
    return {
        "label":    label,
        "filename": filename,
        "url":      f"{settings.MEDIA_URL}screenshots/{student_id}/{slug}/{filename}",
    }


def _save_manifest(student_id, portal_url: str, entries: list):
    d    = _screenshots_dir(student_id, portal_url)
    path = d / "manifest.json"
    with open(path, "w") as f:
        json.dump({
            "student_id":  student_id,
            "portal":      portal_url,
            "screenshots": [e for e in entries if e],
        }, f, indent=2)


# ─────────────────────────────────────────────────────────────────────────────
# AI SERVICE
# ─────────────────────────────────────────────────────────────────────────────

class AIService:

    def __init__(self):
        api_key = getattr(settings, "GEMINI_API_KEY", None)
        if not api_key:
            raise ValueError("GEMINI_API_KEY not set in Django settings.")
        self.llm = ChatGoogleGenerativeAI(
            model="gemini-2.5-flash",
            google_api_key=api_key,
            temperature=0,
        )
        self.parser = PydanticOutputParser(pydantic_object=AutomationResponse)

    @staticmethod
    def make_app_id(student_id, url: str) -> int:
        raw = f"{student_id}:{url}"
        return int(hashlib.md5(raw.encode()).hexdigest()[:8], 16) % 999999 + 1

    # ------------------------------------------------------------------
    # Scrape entire flow: login page (if present) + all form steps
    # ------------------------------------------------------------------
    def scrape_full_flow(self, url):
        """
        Opens the URL and scrapes:
          - If a login page is detected: scrapes login fields, performs login,
            waits for the application form to appear, then scrapes all form steps.
          - If no login page: scrapes all form steps directly.

        FIX: DOM change detection now uses HTML signature hashing,
             not URL or field count. This correctly handles React SPAs.
        """
        driver = None
        pages  = []

        try:
            driver = _new_chrome(headless=True)
            driver.get(url)
            _wait_for_react_hydration(driver, timeout=15)

            # ── LOGIN PAGE ──────────────────────────────────────────────────
            if _is_login_page(driver):
                print("🔐 Login page detected during scraping")
                login_fields  = _extract_fields_from_page(driver, include_password=True)
                login_btn     = _find_login_button(driver)
                login_btn_sel = None
                if login_btn:
                    btn_id        = login_btn.get_attribute("id")
                    login_btn_sel = f"#{btn_id}" if btn_id else "LOGIN_BUTTON"

                pages.append({
                    "page_type":       "login",
                    "page_number":     0,
                    "fields":          login_fields,
                    "submit_selector": login_btn_sel or "LOGIN_BUTTON",
                })
                print(f"   Scraped {len(login_fields)} login fields")

                # Same credentials the fill step uses, so scraping and filling log in identically
                portal_email    = getattr(settings, "PORTAL_EMAIL", "")
                portal_password = getattr(settings, "PORTAL_PASSWORD", "")

                if portal_email and portal_password and login_btn:
                    try:
                        try:
                            email_el = driver.find_element(By.XPATH, "//input[@type='email']")
                        except NoSuchElementException:
                            email_el = driver.find_element(By.XPATH, "//input[@type='text']")
                        pass_el = driver.find_element(By.XPATH, "//input[@type='password']")
                        email_el.send_keys(portal_email)
                        pass_el.send_keys(portal_password)
                        driver.execute_script("arguments[0].click();", login_btn)
                        WebDriverWait(driver, 15).until(
                            EC.invisibility_of_element_located(
                                (By.XPATH, "//input[@type='password']")
                            )
                        )
                        print("✅ Scraping login succeeded — waiting for form...")
                        time.sleep(2)
                        _wait_for_react_hydration(driver, timeout=10)
                    except Exception as e:
                        print(f"⚠️  Scraping login failed: {e}")
                else:
                    print("⚠️  Credentials not set or no login button found")

            # ── APPLICATION FORM PAGES ──────────────────────────────────────
            SUBMIT_ONLY_KEYWORDS = ["submit", "finish", "complete", "send", "apply",
                                    "submit application", "final submit", "جمع کریں"]

            for step_num in range(1, MAX_FORM_STEPS + 1):
                print(f"\n🧭 Scraping application page {step_num}...")
                time.sleep(0.5)

                if _is_login_page(driver):
                    print("   Still on login page — login may have failed")
                    break

                fields = _extract_fields_from_page(driver, include_password=False)
                print(f"   {len(fields)} fields found "
                      f"({sum(1 for f in fields if f['type']=='file')} file inputs)")

                # ── STOP: 0 fields = confirmation/success page ──────────────
                if len(fields) == 0:
                    print("   ✅ No fields found — this is a confirmation/success page. Stopping.")
                    break

                # ── TAKE SIGNATURE BEFORE DECIDING WHAT TO DO ──────────────
                prev_signature = _get_form_signature(driver)

                # Check all visible buttons to decide: Next step or Submit?
                all_btns = driver.find_elements(By.CSS_SELECTOR, "button, input[type='submit']")
                visible_btns = [
                    b for b in all_btns
                    if b.is_displayed() and b.is_enabled()
                ]
                btn_texts = [_btn_text(driver, b).lower() for b in visible_btns]
                print(f"   Visible buttons: {[_btn_text(driver, b) for b in visible_btns]}")

                # A page is a SUBMIT page if:
                #   - it has a submit-like button AND
                #   - it has NO next-like button
                has_next   = any(
                    any(kw in t for kw in NEXT_KEYWORDS)
                    for t in btn_texts
                )
                has_submit = any(
                    any(kw in t for kw in SUBMIT_ONLY_KEYWORDS)
                    for t in btn_texts
                )

                next_btn   = _find_next_button(driver) if has_next else None
                submit_btn = None

                if not has_next and has_submit:
                    # This is the final page — record submit selector and stop
                    submit_btn_el = _find_submit_button(driver)
                    sid           = submit_btn_el.get_attribute("id") if submit_btn_el else None
                    submit_sel    = f"#{sid}" if sid else "SUBMIT_BUTTON"
                    pages.append({
                        "page_type":       "application",
                        "page_number":     step_num,
                        "fields":          fields,
                        "next_selector":   None,
                        "submit_selector": submit_sel,
                    })
                    print(f"   ✅ Submit page detected (btn: {submit_sel!r}) — end of form")
                    break

                # ── Regular next page ───────────────────────────────────────
                next_sel = None
                if next_btn:
                    nid      = next_btn.get_attribute("id")
                    next_sel = f"#{nid}" if nid else "NEXT_BUTTON"

                pages.append({
                    "page_type":       "application",
                    "page_number":     step_num,
                    "fields":          fields,
                    "next_selector":   next_sel,
                    "submit_selector": None,
                })

                if not next_btn:
                    print("   ✅ No Next button — end of form")
                    break

                # ── CLICK NEXT ──────────────────────────────────────────────
                try:
                    driver.execute_script(
                        "arguments[0].scrollIntoView({block:'center'});", next_btn)
                    driver.execute_script("arguments[0].click();", next_btn)
                    print("   ▶ Clicked Next — waiting for DOM signature change...")

                    changed = _wait_for_dom_change(driver, prev_signature, timeout=12)

                    if changed:
                        print(f"   ✅ DOM changed — proceeding to page {step_num + 1}")
                    else:
                        new_sig = _get_form_signature(driver)
                        if new_sig != prev_signature:
                            print(f"   ✅ DOM changed on recheck — proceeding to page {step_num + 1}")
                        else:
                            print("   ⚠️  DOM signature unchanged after 12s — treating as last step")
                            break

                except Exception as e:
                    print(f"   ❌ Error clicking Next: {e}")
                    break

            total = len([p for p in pages if p["page_type"] == "application"])
            print(f"\n✅ Scraping complete: {total} application pages total")
            return pages

        finally:
            if driver:
                driver.quit()

    # ------------------------------------------------------------------
    # Generate mapping via Gemini
    # ------------------------------------------------------------------
    def get_automation_instructions(self, target_url, student_data, app_id):
        pages = self.scrape_full_flow(target_url)
        if not pages:
            raise Exception("No pages found — check the portal URL")

        portal_email    = getattr(settings, "PORTAL_EMAIL", "")
        portal_password = getattr(settings, "PORTAL_PASSWORD", "")

        student_data_with_creds = {
            **student_data,
            "_portal_email":    portal_email,
            "_portal_password": portal_password,
        }

        system_prompt = """
You are an expert at mapping student data to multi-page university portal flows.

The pages list includes:
  - A "login" page (page_type="login") if the portal requires authentication
  - One or more "application" pages (page_type="application")

You must generate a COMPLETE automation plan that covers ALL pages in order:
  1. Fill login credentials → click login button → wait for form
  2. Fill application step 1 → click Next → ...
  3. Fill last step → submit

Return ONLY valid JSON (no markdown, no backticks). Example structure:

{{
  "application_id": <integer>,
  "url": "<target url>",
  "steps": [
    {{
      "action": "fill",
      "page_type": "login",
      "fields": [
        {{"selector": "#email",    "type": "email",    "value": "<_portal_email value>",    "confidence": 1.0}},
        {{"selector": "#password", "type": "password", "value": "<_portal_password value>", "confidence": 1.0}}
      ]
    }},
    {{
      "action": "login_click",
      "selector": "<submit_selector from login page, or LOGIN_BUTTON>",
      "wait_ms": 3000
    }},
    {{
      "action": "fill",
      "page_type": "application",
      "fields": [
        {{"selector": "#name", "type": "text", "value": "Ali Khan", "confidence": 0.95}},
        {{"selector": "#photo","type": "file", "value": "/abs/path/photo.jpg", "confidence": 0.9}}
      ]
    }},
    {{"action": "click",  "selector": "NEXT_BUTTON",   "wait_ms": 2000}},
    {{"action": "fill",   "page_type": "application", "fields": [...]}},
    {{"action": "submit", "selector": "SUBMIT_BUTTON", "wait_ms": 3000}}
  ]
}}

RULES:
1. LOGIN STEP:
   - Map "_portal_email" → the email/username input field on the login page.
   - Map "_portal_password" → the password input field on the login page.
   - Use the exact selectors from the login page fields.
   - The login click action must use "action": "login_click".

2. CLICK / SUBMIT selectors:
   - For click (Next) actions: use "NEXT_BUTTON" unless the page gave a specific next_selector.
   - For submit: use "SUBMIT_BUTTON" unless the page gave a specific submit_selector.
   - For login_click: use the submit_selector from the login page, or "LOGIN_BUTTON".
   - NEVER invent button CSS selectors.

3. FILL selectors must be the exact strings from the scraped page fields.

4. FILE FIELDS:
   photo/picture/avatar  → student.photo
   cnic/id_card          → student.cnic_image
   transcript/result     → student.transcript
   matric                → student.matric_certificate
   inter/fsc/hssc        → student.inter_certificate
   domicile              → student.domicile
   Set value="" and confidence=0.0 if no match.

5. PREFERENCE / PROGRAM CHOICE FIELDS:
   The student data contains preference1, preference2, preference3 as SHORT CODES.
   You MUST map these to the closest dropdown option on the form even if the text differs.
   Common mappings:
     BSSE  → Software Engineering / BS Software Engineering / BS (SE)
     BSCS  → Computer Science / BS Computer Science / BS (CS)
     BSIT  → Information Technology / BS IT / BS (IT)
     BECH  → Electrical Engineering / BE Electrical / BS Electrical Engineering
     BECE  → Civil Engineering / BE Civil / BS Civil Engineering
     BEME  → Mechanical Engineering / BE Mechanical
     BETE  → Telecom Engineering / Telecommunication Engineering
     BBA   → Business Administration / BBA
   If no exact match: pick the closest option available. confidence=0.8 minimum.
   NEVER leave preference2 or preference3 empty if the student data has a value.

6. confidence: 1.0=exact, 0.5=inferred, 0.0=no match.
7. Include ALL fields from ALL pages even if confidence is 0.
8. Return ONLY JSON.
"""

        prompt = ChatPromptTemplate.from_messages([
            ("system", system_prompt),
            ("human",
             "STUDENT DATA (includes _portal_email and _portal_password):\n{student_data}\n\n"
             "SCRAPED PAGES (login + application steps):\n{pages_data}\n\n"
             "URL: {url}\nAPP ID: {app_id}"),
        ])

        chain  = prompt | self.llm | self.parser
        result = chain.invoke({
            "student_data": json.dumps(student_data_with_creds, indent=2),
            "pages_data":   json.dumps(pages, indent=2),
            "url":          target_url,
            "app_id":       app_id,
        })
        return result


# ─────────────────────────────────────────────────────────────────────────────
# AUTOMATION SERVICE
# ─────────────────────────────────────────────────────────────────────────────

class AutomationService:

    # ── Normalization ──────────────────────────────────────────────────────

    def normalize_value(self, field_name, value):
        if not value:
            return value
        value    = str(value).strip()
        city_map = {
            "lahore": "Punjab", "karachi": "Sindh", "islamabad": "Islamabad",
            "peshawar": "KPK",  "quetta": "Balochistan",
        }
        if field_name and "province" in field_name.lower():
            return city_map.get(value.lower(), value)
        return value

    def normalize_course(self, value):
        if not value:
            return []
        v = str(value).lower().strip()
        m = {
            # Computer Science
            "cs":                           ["cs","computer science","bscs","bs computer science","bs (cs)"],
            "bscs":                         ["bscs","bs computer science","computer science","cs","bs (cs)"],
            "computer science":             ["computer science","bscs","cs","bs computer science","bs (cs)"],
            # Software Engineering
            "bsse":                         ["bsse","software engineering","bs software engineering","software","bs (se)"],
            "software engineering":         ["software engineering","bsse","bs software engineering","software","bs (se)"],
            # Data Science / AI / Cyber Security
            "bsds":                         ["bsds","data science","bs data science","bs (ds) data science","bs (ds)"],
            "data science":                 ["data science","bsds","bs data science","bs (ds) data science"],
            "bsai":                         ["bsai","artificial intelligence","bs artificial intelligence","bs (ai) artificial intelligence","bs (ai)"],
            "artificial intelligence":      ["artificial intelligence","bsai","bs artificial intelligence","bs (ai) artificial intelligence"],
            "bscy":                         ["bscy","cyber security","cybersecurity","bs cyber security","bs (cy) cyber security","bs (cy)"],
            # Information Technology
            "bsit":                      ["bsit","information technology","it","bs information technology","bs (it)","bs it"],
            "it":                           ["it","information technology","bsit","bs information technology","bs (it)"],
            "information technology":       ["information technology","bsit","it","bs information technology","bs (it)"],
            # Electrical Engineering
            "bech":                         ["bech","electrical engineering","bs electrical engineering","be electrical","electrical","b.e electrical","b.e. electrical"],
            "electrical engineering":       ["electrical engineering","bech","bs electrical engineering","be electrical","b.e electrical"],
            "be electrical":                ["be electrical","electrical engineering","bech","b.e electrical"],
            # Civil Engineering
            "bece":                         ["bece","civil engineering","bs civil engineering","be civil","civil","b.e civil","b.e. civil"],
            "civil engineering":            ["civil engineering","bece","bs civil engineering","be civil","b.e civil"],
            "be civil":                     ["be civil","civil engineering","bece","b.e civil"],
            # Mechanical Engineering
            "beme":                         ["beme","mechanical engineering","bs mechanical engineering","be mechanical","mechanical","b.e mechanical"],
            "mechanical engineering":       ["mechanical engineering","beme","bs mechanical engineering","be mechanical"],
            # Computer Engineering
            "bece-cpe":                     ["computer engineering","bs computer engineering","be computer","bece-cpe"],
            "computer engineering":         ["computer engineering","bs computer engineering","be computer","bece-cpe"],
            # Telecom Engineering
            "bete":                         ["bete","telecom engineering","telecommunication engineering","bs telecom","telecom"],
            "telecom engineering":          ["telecom engineering","bete","telecommunication","bs telecom"],
            # Business
            "bba":                          ["bba","business administration","business","bs business","bachelor of business"],
            "business administration":      ["business administration","bba","business","bs business"],
            "finance":                      ["finance","bba finance","business finance","bs finance"],
            # Medical
            "mbbs":                         ["mbbs","medicine","medical","bachelor of medicine"],
            "bds":                          ["bds","dentistry","dental","bachelor of dental"],
            # Other
            "nursing":                      ["nursing","bsn","bs nursing"],
            "psychology":                   ["psychology","bs psychology"],
            "sociology":                    ["sociology","bs sociology"],
            "llb":                          ["llb","law","bachelor of law","legal"],
            "law":                          ["law","llb","legal studies","legal"],
            "bba":                          ["bba","business administration","business"],
        }
        return m.get(v, [v])

    def normalize_date(self, value):
        if not value:
            return value
        fmts = [
            "%Y-%m-%d","%Y %m %d","%Y/%m/%d",
            "%d-%m-%Y","%d/%m/%Y","%d %m %Y",
            "%m/%d/%Y","%m-%d-%Y",
            "%d %b %Y","%d %B %Y","%B %d, %Y","%b %d, %Y",
        ]
        dt = None
        for fmt in fmts:
            try: dt = datetime.strptime(str(value).strip(), fmt); break
            except Exception: continue
        if not dt:
            return {"iso":value,"dmy":value,"dmy_dash":value,"dmy_slash":value,
                    "mdy":value,"long":value,"dt":None,"day":"","month":"","year":""}
        return {
            "iso":       dt.strftime("%Y-%m-%d"),
            "dmy":       dt.strftime("%d %m %Y"),
            "dmy_dash":  dt.strftime("%d-%m-%Y"),
            "dmy_slash": dt.strftime("%d/%m/%Y"),
            "mdy":       dt.strftime("%m/%d/%Y"),
            "long":      dt.strftime("%d %b %Y"),
            "dt":        dt,
            "day":       dt.strftime("%d"),
            "month":     dt.strftime("%m"),
            "year":      dt.strftime("%Y"),
        }

    # ── React helpers ──────────────────────────────────────────────────────

    def is_react_page(self, driver):
        return driver.execute_script(
            "return !!(window.__REACT_DEVTOOLS_GLOBAL_HOOK__ || "
            "document.querySelector('[data-reactroot]') || "
            "document.querySelector('#root'))"
        )

    def react_set_value(self, driver, element, value):
        driver.execute_script("""
            var el = arguments[0], val = arguments[1];
            var proto = el.tagName.toLowerCase() === 'textarea'
                ? window.HTMLTextAreaElement.prototype
                : window.HTMLInputElement.prototype;
            Object.getOwnPropertyDescriptor(proto, 'value').set.call(el, val);
            el.dispatchEvent(new Event('input',  { bubbles: true }));
            el.dispatchEvent(new Event('change', { bubbles: true }));
        """, element, value)

    # ── Date helpers ───────────────────────────────────────────────────────

    def detect_date_format(self, element):
        hint = " ".join([
            element.get_attribute("placeholder") or "",
            element.get_attribute("pattern")     or "",
            element.get_attribute("data-format") or "",
        ]).lower()
        if any(x in hint for x in ["dd-mm-yyyy","dd/mm/yyyy","dd mm yyyy"]):
            return "dmy_slash" if "/" in hint else "dmy_dash"
        if any(x in hint for x in ["mm/dd/yyyy","mm-dd-yyyy"]): return "mdy"
        if "yyyy-mm-dd" in hint: return "iso"
        return None

    def fill_date_react(self, driver, element, formats):
        input_type = (element.get_attribute("type") or "").lower()
        fmt_key    = self.detect_date_format(element)
        if input_type == "date":
            self.fill_react_native_date(driver, element, formats, fmt_key); return
        formatted = formats.get(fmt_key, formats["dmy_dash"]) if fmt_key else formats["dmy_dash"]
        self.react_set_value(driver, element, formatted); time.sleep(0.2)
        if element.get_attribute("value"): return
        if PYPERCLIP_AVAILABLE:
            try:
                pyperclip.copy(formatted)
                element.send_keys(Keys.CONTROL + "v"); time.sleep(0.3)
                if element.get_attribute("value"): return
            except Exception: pass
        driver.execute_script("arguments[0].click();", element)
        element.send_keys(Keys.CONTROL + "a"); element.send_keys(Keys.DELETE)
        for char in formatted: element.send_keys(char); time.sleep(0.04)

    def fill_react_native_date(self, driver, element, formats, fmt_key):
        self.react_set_value(driver, element, formats["iso"]); time.sleep(0.2)
        if element.get_attribute("value") == formats["iso"]: return
        driver.execute_script("arguments[0].click();", element)
        element.send_keys(formats["month"]); time.sleep(0.1)
        element.send_keys(formats["day"]);   time.sleep(0.1)
        element.send_keys(formats["year"])

    def fill_native_date(self, driver, element, formats):
        iso = formats["iso"]
        driver.execute_script("arguments[0].value = arguments[1];", element, iso)
        driver.execute_script(
            "arguments[0].dispatchEvent(new Event('input',{bubbles:true}));"
            "arguments[0].dispatchEvent(new Event('change',{bubbles:true}));", element)
        if element.get_attribute("value") != iso:
            element.clear(); element.send_keys(iso)

    def fill_custom_date(self, driver, element, formats):
        fmt_key = self.detect_date_format(element)
        if fmt_key:
            element.clear(); time.sleep(0.2)
            element.send_keys(formats.get(fmt_key, formats["dmy_dash"]))
        else:
            for key in ["dmy_dash","dmy_slash","dmy","iso","mdy"]:
                element.clear(); time.sleep(0.2)
                element.send_keys(formats.get(key,"")); time.sleep(0.3)
                if element.get_attribute("value"): return
            driver.execute_script("arguments[0].value = arguments[1];", element, formats["dmy_dash"])
            driver.execute_script(
                "arguments[0].dispatchEvent(new Event('input',{bubbles:true}));"
                "arguments[0].dispatchEvent(new Event('change',{bubbles:true}));", element)

    # ── File path resolver ─────────────────────────────────────────────────

    def resolve_file_path(self, value):
        if not value:
            raise ValueError("File path is empty")
        path = str(value).strip()
        if os.path.isabs(path) and os.path.isfile(path): return path
        media_root = getattr(settings, "MEDIA_ROOT", "")
        if media_root:
            clean = path.lstrip("/\\")
            if clean.startswith("media/") or clean.startswith("media\\"):
                clean = clean[6:]
            candidate = os.path.join(str(media_root), clean)
            if os.path.isfile(candidate): return os.path.abspath(candidate)
        base_dir = getattr(settings, "BASE_DIR", "")
        if base_dir:
            candidate = os.path.join(str(base_dir), path.lstrip("/\\"))
            if os.path.isfile(candidate): return os.path.abspath(candidate)
        abs_attempt = os.path.abspath(path)
        if os.path.isfile(abs_attempt): return abs_attempt
        raise FileNotFoundError(
            f"File not found: '{value}' — tried MEDIA_ROOT='{media_root}', BASE_DIR='{base_dir}'"
        )

    # ── wait_for_element ───────────────────────────────────────────────────

    def wait_for_element(self, driver, selector, timeout=10, clickable=False):
        if selector in ("NEXT_BUTTON", "next_button"):
            deadline = time.time() + timeout
            while time.time() < deadline:
                el = _find_next_button(driver)
                if el: return el
                time.sleep(REACT_POLL_INTERVAL)
            raise TimeoutException("No Next button found")

        if selector in ("SUBMIT_BUTTON", "submit_button"):
            deadline = time.time() + timeout
            while time.time() < deadline:
                el = _find_submit_button(driver)
                if el: return el
                time.sleep(REACT_POLL_INTERVAL)
            raise TimeoutException("No Submit button found")

        if selector in ("LOGIN_BUTTON", "login_button"):
            deadline = time.time() + timeout
            while time.time() < deadline:
                el = _find_login_button(driver)
                if el: return el
                time.sleep(REACT_POLL_INTERVAL)
            raise TimeoutException("No Login button found")

        if ":contains(" in selector:
            match = re.match(r"^(\w+)?:contains\(['\"](.+?)['\"]\)$", selector.strip())
            if match:
                tag, text = match.group(1) or "*", match.group(2).lower()
            else:
                tag  = "*"
                text = selector.split(":contains(")[1].strip("'\")")
            xpath = (
                f"//{tag}[contains("
                f"translate(normalize-space(.),"
                f"'ABCDEFGHIJKLMNOPQRSTUVWXYZ','abcdefghijklmnopqrstuvwxyz'),"
                f"'{text.lower()}')]"
            )
            wait = WebDriverWait(driver, timeout)
            cond = EC.element_to_be_clickable if clickable else EC.presence_of_element_located
            try:
                return wait.until(cond((By.XPATH, xpath)))
            except TimeoutException:
                fn = _find_login_button  if any(kw in selector.lower() for kw in LOGIN_KEYWORDS) \
                     else _find_next_button if any(kw in selector.lower() for kw in NEXT_KEYWORDS) \
                     else _find_submit_button
                el = fn(driver)
                if el: return el
                raise

        wait = WebDriverWait(driver, timeout)
        by   = By.CSS_SELECTOR
        if selector.startswith("#"):
            by, selector = By.ID, selector[1:]
        elif selector.startswith("//"):
            by = By.XPATH
        elif selector.startswith("[name="):
            by, selector = By.NAME, selector.split("'")[1]

        try:
            el_type = driver.find_element(by, selector).get_attribute("type") or ""
            if el_type == "file": clickable = False
        except Exception:
            pass

        cond = EC.element_to_be_clickable if clickable else EC.presence_of_element_located
        return wait.until(cond((by, selector)))

    # ── fill_field ─────────────────────────────────────────────────────────

    def fill_field(self, driver, element, field_type, value):
        tag        = element.tag_name.lower()
        input_type = (element.get_attribute("type") or "").lower()
        is_react   = self.is_react_page(driver)

        if field_type == "file" or input_type == "file":
            try:
                abs_path = self.resolve_file_path(value)
            except (FileNotFoundError, ValueError) as e:
                raise Exception(f"File upload failed — {e}")
            driver.execute_script("""
                arguments[0].style.display    = 'block';
                arguments[0].style.opacity    = '1';
                arguments[0].style.visibility = 'visible';
            """, element)
            time.sleep(0.2)
            element.send_keys(abs_path)
            driver.execute_script(
                "arguments[0].dispatchEvent(new Event('change',{bubbles:true}));", element)
            print(f"✅ File: {os.path.basename(abs_path)}")
            return

        if input_type == "password":
            element.clear()
            element.send_keys(str(value))
            return

        if input_type in ["checkbox", "radio"]:
            if str(value).lower() in ["true","1","yes"]:
                driver.execute_script("arguments[0].click();", element)
            return

        if field_type == "date" or input_type == "date":
            formats = self.normalize_date(value)
            if not formats.get("dt"):
                element.clear(); element.send_keys(str(value)); return
            if is_react:
                self.fill_date_react(driver, element, formats)
            elif input_type == "date":
                fmt_key = self.detect_date_format(element)
                (self.fill_custom_date if (fmt_key and fmt_key != "iso") else self.fill_native_date)(
                    driver, element, formats)
            else:
                self.fill_custom_date(driver, element, formats)
            return

        if tag == "select":
            sel     = Select(element)
            options = [o.text.strip() for o in sel.options]
            opt_low = [o.lower() for o in options]
            for target in self.normalize_course(value):
                t = target.lower().strip()
                for i, opt in enumerate(opt_low):
                    if opt == t:                           sel.select_by_visible_text(options[i]); return
                for i, opt in enumerate(opt_low):
                    if opt and opt in t:                  sel.select_by_visible_text(options[i]); return
                for i, opt in enumerate(opt_low):
                    if t and t in opt:                    sel.select_by_visible_text(options[i]); return
                for i, opt in enumerate(opt_low):
                    if set(t.split()) & set(opt.split()): sel.select_by_visible_text(options[i]); return
            raise Exception(f"Dropdown option not found for '{value}'. Available: {options}")

        if tag in ["input", "textarea"]:
            self.react_set_value(driver, element, str(value)) if is_react \
                else (element.clear() or element.send_keys(str(value)))
            return

        driver.execute_script("arguments[0].value = arguments[1];", element, value)
        driver.execute_script(
            "arguments[0].dispatchEvent(new Event('change',{bubbles:true}));", element)

    # ── Main runner ────────────────────────────────────────────────────────

    def run(self, mapping: dict) -> dict:
        """
        FIX: click step now passes prev_signature to _wait_for_dom_change
             instead of prev_count + prev_url.
        """
        url        = mapping.get("url")
        steps      = mapping.get("steps", [])
        student_id = mapping.get("application_id", 0)

        if not url:
            return {"status":"failed","message":"No URL provided","screenshots":[]}

        driver = _new_chrome(headless=False)  # visible locally, headless on servers
        driver.get(url)
        _wait_for_react_hydration(driver, timeout=15)

        completed_steps = 0
        screenshot_log  = []

        last_app_fill_idx = None
        for i, s in enumerate(steps):
            if s.get("action") == "fill" and s.get("page_type") == "application":
                last_app_fill_idx = i

        def _snap(label):
            entry = _take_screenshot(driver, student_id, url, label)
            if entry:
                screenshot_log.append(entry)

        try:
            for step_idx, step in enumerate(steps):
                action = step.get("action")

                if action == "fill":
                    page_type = step.get("page_type", "application")
                    print(f"\n📝 Fill step {step_idx} [{page_type}]")

                    # for field in step.get("fields", []):
                    #     selector   = field.get("selector")
                    #     field_type = (field.get("type") or "text").lower()
                    #     raw_value  = field.get("value")

                    #     if (raw_value is None or raw_value == "") and field_type != "file":
                    #         continue
                    #     if field_type == "file" and not raw_value:
                    #         print(f"⏭️  No file path for {selector}")
                    #         continue

                    #     value = self.normalize_value(selector, raw_value)
                    #     print(f"   🖊  [{field_type}] {selector} → {value!r}")

                    #     try:
                    #         element = self.wait_for_element(
                    #             driver, selector, clickable=(field_type != "file"))
                    #         if field_type != "file":
                    #             driver.execute_script(
                    #                 "arguments[0].scrollIntoView({block:'center'});", element)
                    #         self.fill_field(driver, element, field_type, value)
                    #         time.sleep(0.2)
                    #     except Exception as e:
                    #         print(f"   ❌ Failed {selector}: {e}")
                    #         _save_manifest(student_id, url, screenshot_log)
                    #         driver.quit()
                    #         return {
                    #             "status":"failed","message":f"Error filling {selector}",
                    #             "error":str(e),"completed_steps":completed_steps,
                    #             "screenshots":screenshot_log,
                    #         }
                    for field in step.get("fields", []):
                        selector   = field.get("selector")
                        field_type = (field.get("type") or "text").lower()
                        raw_value  = field.get("value")
                        confidence = field.get("confidence", 1.0)

                        # BLOCK: high-confidence field with empty value = mapping failure
                        # select fields with empty value are definitely wrong — stop immediately
                        if field_type == "select" and (raw_value is None or raw_value == ""):
                            msg = (
                                f"Mapping failed — field '{selector}' is a dropdown but got no value. "
                                f"The AI could not map student data to this field. "
                                f"Fix the student profile or update the preference mappings."
                            )
                            print(f"   🚫 {msg}")
                            _save_manifest(student_id, url, screenshot_log)
                            driver.quit()
                            return {
                                "status": "failed",
                                "message": msg,
                                "unmapped_field": selector,
                                "field_type": field_type,
                                "completed_steps": completed_steps,
                                "screenshots": screenshot_log,
                            }

                        # Skip truly optional empty fields (text/textarea/etc with confidence 0)
                        if (raw_value is None or raw_value == "") and field_type != "file":
                            if confidence == 0.0:
                                print(f"   ⏭️  Skipping unmapped optional field: {selector}")
                                continue
                            # Non-zero confidence but empty = warn but skip for non-critical types
                            print(f"   ⚠️  Empty value for {selector} (confidence={confidence}) — skipping")
                            continue

                        if field_type == "file" and not raw_value:
                            print(f"⏭️  No file path for {selector}")
                            continue

                        value = self.normalize_value(selector, raw_value)
                        print(f"   🖊  [{field_type}] {selector} → {value!r}")

                        try:
                            element = self.wait_for_element(
                                driver, selector, clickable=(field_type != "file"))
                            if field_type != "file":
                                driver.execute_script(
                                    "arguments[0].scrollIntoView({block:'center'});", element)
                            self.fill_field(driver, element, field_type, value)
                            time.sleep(0.2)
                        except Exception as e:
                            print(f"   ❌ Failed {selector}: {e}")
                            _save_manifest(student_id, url, screenshot_log)
                            driver.quit()
                            return {
                                "status": "failed",
                                "message": f"Error filling '{selector}': {str(e)}",
                                "unmapped_field": selector,
                                "error": str(e),
                                "completed_steps": completed_steps,
                                "screenshots": screenshot_log,
        }

                    if step_idx == last_app_fill_idx:
                        time.sleep(0.7)
                        driver.execute_script("window.scrollTo(0, 0);")
                        time.sleep(0.2)
                        _snap("before_submit")
                        print("📸 before_submit screenshot taken")

                    completed_steps += 1

                elif action == "login_click":
                    selector = step.get("selector", "LOGIN_BUTTON")
                    wait_ms  = step.get("wait_ms", 3000)
                    print(f"\n🔐 Login click (selector: {selector!r})")

                    element = None
                    try:
                        element = self.wait_for_element(driver, selector, clickable=True)
                    except Exception as e:
                        print(f"⚠️  Login button '{selector}' not found: {e}")
                        element = _find_login_button(driver)

                    if not element:
                        _save_manifest(student_id, url, screenshot_log)
                        driver.quit()
                        return {
                            "status":"failed","message":"Login button not found",
                            "completed_steps":completed_steps,"screenshots":screenshot_log,
                        }

                    driver.execute_script("arguments[0].scrollIntoView({block:'center'});", element)
                    driver.execute_script("arguments[0].click();", element)
                    print("   ▶ Clicked login — waiting for password field to disappear...")

                    try:
                        WebDriverWait(driver, 15).until(
                            EC.invisibility_of_element_located(
                                (By.XPATH, "//input[@type='password']")
                            )
                        )
                        print("   ✅ Login successful")
                        time.sleep(1.5)
                        _wait_for_react_hydration(driver, timeout=10)
                    except TimeoutException:
                        _save_manifest(student_id, url, screenshot_log)
                        driver.quit()
                        return {
                            "status":"failed",
                            "message":"Login timed out — password field never disappeared.",
                            "completed_steps":completed_steps,"screenshots":screenshot_log,
                        }

                    time.sleep(0.5)
                    driver.execute_script("window.scrollTo(0, 0);")
                    time.sleep(0.2)
                    _snap("after_login")
                    print("📸 after_login screenshot taken")
                    completed_steps += 1

                elif action == "click":
                    selector = step.get("selector", "NEXT_BUTTON")
                    wait_ms  = step.get("wait_ms", 1500)
                    print(f"\n▶  Next click (selector: {selector!r})")

                    # FIX: take signature BEFORE clicking
                    prev_signature = _get_form_signature(driver)

                    element = None
                    try:
                        element = self.wait_for_element(driver, selector, clickable=True)
                    except Exception as e:
                        print(f"⚠️  Next selector failed: {e} — trying smart finder")
                        element = _find_next_button(driver)

                    if not element:
                        _save_manifest(student_id, url, screenshot_log)
                        driver.quit()
                        return {
                            "status":"failed","message":"Next button not found",
                            "completed_steps":completed_steps,"screenshots":screenshot_log,
                        }

                    driver.execute_script("arguments[0].scrollIntoView({block:'center'});", element)
                    driver.execute_script("arguments[0].click();", element)
                    completed_steps += 1

                    # FIX: pass prev_signature (not count+url)
                    changed = _wait_for_dom_change(driver, prev_signature, timeout=12)
                    if not changed:
                        print("   ⚠️  DOM unchanged — using wait_ms fallback")
                        time.sleep(wait_ms / 1000)

                elif action == "submit":
                    selector = step.get("selector", "SUBMIT_BUTTON")
                    wait_ms  = step.get("wait_ms", 3000)

                    completed_steps += 1
                    time.sleep(0.3)
                    _snap("before_final_submit")
                    print("📸 before_final_submit screenshot taken")
                    print(f"\n✅ Submit (selector: {selector!r})")

                    element = None
                    try:
                        element = self.wait_for_element(driver, selector, clickable=True)
                    except Exception as e:
                        print(f"⚠️  Submit selector failed: {e} — trying smart finder")
                        element = _find_submit_button(driver)

                    if not element:
                        _save_manifest(student_id, url, screenshot_log)
                        driver.quit()
                        return {
                            "status":"failed","message":"Submit button not found",
                            "completed_steps":completed_steps,"screenshots":screenshot_log,
                        }

                    try:
                        driver.execute_script(
                            "arguments[0].scrollIntoView({block:'center'});", element)
                        driver.execute_script("arguments[0].click();", element)
                        time.sleep(wait_ms / 1000)
                    except Exception as e:
                        _save_manifest(student_id, url, screenshot_log)
                        driver.quit()
                        return {
                            "status":"failed","message":"Submit click failed",
                            "error":str(e),"completed_steps":completed_steps,
                            "screenshots":screenshot_log,
                        }

                    driver.execute_script("window.scrollTo(0, 0);")
                    time.sleep(0.3)
                    _snap("after_submit")
                    print("📸 after_submit screenshot taken")

                    _save_manifest(student_id, url, screenshot_log)
                    driver.quit()
                    return {
                        "status":"success","message":"Form submitted successfully",
                        "completed_steps":completed_steps + 1,"screenshots":screenshot_log,
                    }

            _save_manifest(student_id, url, screenshot_log)
            driver.quit()
            return {"status":"success","completed_steps":completed_steps,
                    "screenshots":screenshot_log}

        except Exception as e:
            try:
                _save_manifest(student_id, url, screenshot_log)
                driver.quit()
            except Exception:
                pass
            return {"status":"failed","error":str(e),"screenshots":screenshot_log}