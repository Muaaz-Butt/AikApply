# import time
# from pathlib import Path

# from django.conf import settings

# from selenium import webdriver
# from selenium.webdriver.chrome.options import Options
# from selenium.webdriver.common.by import By
# from selenium.webdriver.support.ui import Select


# class AutomationService:

#     def run(self, mapping):

#         url = mapping.get("url")
#         steps = mapping.get("steps", [])

#         # 🔥 SHOW BROWSER (for demo)
#         options = Options()
#         # options.add_argument("--headless")  # ❌ keep disabled for visibility

#         driver = webdriver.Chrome(options=options)

#         errors = []
#         completed_steps = 0
#         screenshots = []

#         # 📁 Screenshot folder
#         screenshot_dir = Path(settings.MEDIA_ROOT) / "screenshots"
#         screenshot_dir.mkdir(parents=True, exist_ok=True)

#         try:
#             driver.get(url)
#             time.sleep(2)
#             driver.maximize_window()

#             for i, step in enumerate(steps):

#                 action = step.get("action")

#                 # =========================
#                 # 🧠 FILL STEP
#                 # =========================
#                 if action == "fill":

#                     for field in step.get("fields", []):

#                         selector = field.get("selector")
#                         value = field.get("value")
#                         field_type = field.get("type")

#                         print("Filling:", selector, "| Type:", field_type, "| Value:", value)

#                         if value in [None, ""]:
#                             return {
#                                 "status": "incomplete",
#                                 "message": f"Missing value for {selector}",
#                                 "errors": [{"field": selector}],
#                                 "completed_steps": completed_steps,
#                                 "screenshots": screenshots
#                             }

#                         try:
#                             element = self.find_element(driver, selector)

#                             # 🔥 Fix disabled fields
#                             driver.execute_script(
#                                 "arguments[0].removeAttribute('disabled')",
#                                 element
#                             )

#                             # 🔥 UNIVERSAL HANDLER
#                             self.fill_field(driver, element, field_type, value)

#                         except Exception as e:
#                             errors.append({
#                                 "field": selector,
#                                 "error": str(e)
#                             })
#                             return {
#                                 "status": "failed",
#                                 "message": "Error filling form",
#                                 "errors": errors,
#                                 "completed_steps": completed_steps,
#                                 "screenshots": screenshots
#                             }

#                     completed_steps += 1

#                 # =========================
#                 # 👉 CLICK STEP
#                 # =========================
#                 elif action == "click":
#                     try:
#                         element = self.find_element(driver, step.get("selector"))
#                         driver.execute_script("arguments[0].click();", element)
#                         time.sleep(step.get("wait_ms", 2))
#                         completed_steps += 1
#                     except Exception as e:
#                         errors.append({"error": str(e)})
#                         return {
#                             "status": "failed",
#                             "message": "Click failed",
#                             "errors": errors,
#                             "completed_steps": completed_steps,
#                             "screenshots": screenshots
#                         }

#                 # =========================
#                 # 🚀 SUBMIT STEP
#                 # =========================
#                 elif action == "submit":
#                     try:
#                         element = self.find_element(driver, step.get("selector"))
#                         driver.execute_script("arguments[0].click();", element)
#                         time.sleep(3)

#                         path = self.take_screenshot(driver, screenshot_dir, "final")
#                         screenshots.append(path)

#                         return {
#                             "status": "success",
#                             "message": "Application submitted successfully",
#                             "errors": [],
#                             "completed_steps": completed_steps + 1,
#                             "screenshots": screenshots
#                         }

#                     except Exception as e:
#                         errors.append({"error": str(e)})
#                         return {
#                             "status": "failed",
#                             "message": "Submit failed",
#                             "errors": errors,
#                             "completed_steps": completed_steps,
#                             "screenshots": screenshots
#                         }

#                 # 📸 Screenshot after each step
#                 path = self.take_screenshot(driver, screenshot_dir, f"step_{i}")
#                 screenshots.append(path)

#             return {
#                 "status": "incomplete",
#                 "message": "Did not reach submit",
#                 "errors": errors,
#                 "completed_steps": completed_steps,
#                 "screenshots": screenshots
#             }

#         finally:
#             driver.quit()

#     # =========================
#     # 🔍 FIND ELEMENT
#     # =========================
#     def find_element(self, driver, selector):

#         if selector.startswith("#"):
#             return driver.find_element(By.ID, selector[1:])

#         if selector.startswith("[name="):
#             name = selector.split("'")[1]
#             return driver.find_element(By.NAME, name)

#         return driver.find_element(By.CSS_SELECTOR, selector)

#     # =========================
#     # 🧠 UNIVERSAL FIELD HANDLER
#     # =========================
#     def fill_field(self, driver, element, field_type, value):

#         tag = element.tag_name.lower()

#         # TEXT INPUTS
#         if tag == "input" and field_type in ["text", "email", "tel", "number", "date", "password"]:
#             element.clear()
#             element.send_keys(value)
#             return
#         # REACT SELECT SUPPORT
#         if field_type == "react-select":
#             driver.execute_script("arguments[0].click();", element)
#             time.sleep(1)

#             options = driver.find_elements(By.XPATH, "//*[self::div or self::li]")
#             for opt in options:
#                 if value.lower() in opt.text.lower():
#                     opt.click()
#                     return

#         # SELECT DROPDOWN
#         if tag == "select":
#             Select(element).select_by_visible_text(value)
#             return

#         # CHECKBOX
#         if field_type == "checkbox":
#             if value == "true" and not element.is_selected():
#                 element.click()
#             return

#         # RADIO
#         if field_type == "radio":
#             element.click()
#             return

#         # 🔥 REACT DROPDOWN
#         try:
#             driver.execute_script("arguments[0].click();", element)
#             time.sleep(1)

#             option = driver.find_element(
#                 By.XPATH,
#                 f"//*[text()='{value}']"
#             )

#             driver.execute_script("arguments[0].click();", option)
#             return

#         except:
#             pass

#         # 🔥 JS FALLBACK
#         driver.execute_script(
#             "arguments[0].value = arguments[1]; arguments[0].dispatchEvent(new Event('change'));",
#             element,
#             value
#         )

#     # =========================
#     # 📸 SCREENSHOT
#     # =========================
#     def take_screenshot(self, driver, folder, name):
#         path = folder / f"{name}.png"
#         driver.save_screenshot(str(path))
#         return str(path)

import time
import os
from pathlib import Path
from django.conf import settings

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select, WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


class AutomationService:

    def run(self, mapping):
        url = mapping.get("url")
        steps = mapping.get("steps", [])

        options = Options()
        # options.add_argument("--headless")  # Enable this for production

        driver = webdriver.Chrome(options=options)
        errors = []
        completed_steps = 0
        screenshots = []

        # 📁 Screenshot folder
        screenshot_dir = Path(settings.MEDIA_ROOT) / "screenshots"
        screenshot_dir.mkdir(parents=True, exist_ok=True)

        try:
            driver.get(url)
            time.sleep(2)
            driver.maximize_window()

            for i, step in enumerate(steps):
                action = step.get("action")

                # =========================
                # 🧠 FILL STEP
                # =========================
                if action == "fill":
                    for field in step.get("fields", []):
                        selector = field.get("selector")
                        value = field.get("value")
                        field_type = field.get("type", "text")

                        if value in [None, ""] and field_type != "file":
                            continue # Skip empty values unless it's a file check

                        try:
                            # Use the robust find method with Wait
                            element = self.wait_for_element(driver, selector)

                            # Remove disabled attribute via JS
                            driver.execute_script("arguments[0].removeAttribute('disabled')", element)
                            
                            # Scroll to element to ensure it's in view
                            driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", element)
                            time.sleep(0.1)

                            # Robust Fill Logic
                            self.fill_field(driver, element, field_type, value)

                        except Exception as e:
                            errors.append({"field": selector, "error": str(e)})
                            return {
                                "status": "failed",
                                "message": f"Error filling {selector}",
                                "errors": errors,
                                "completed_steps": completed_steps,
                                "screenshots": screenshots
                            }

                    completed_steps += 1

                # =========================
                # 👉 CLICK / SUBMIT STEP
                # =========================
                elif action in ["click", "submit"]:
                    try:
                        selector = step.get("selector")
                        element = self.wait_for_element(driver, selector, clickable=True)
                        
                        # JS click is more reliable for React apps
                        driver.execute_script("arguments[0].click();", element)
                        
                        time.sleep(step.get("wait_ms", 3000) / 1000)
                        
                        if action == "submit":
                            path = self.take_screenshot(driver, screenshot_dir, "final_submit")
                            screenshots.append(path)
                            return {
                                "status": "success",
                                "message": "Application processed successfully",
                                "completed_steps": completed_steps + 1,
                                "screenshots": screenshots
                            }
                        
                        completed_steps += 1
                    except Exception as e:
                        errors.append({"error": f"Action {action} failed: {str(e)}"})
                        break

                # 📸 Take screenshot after each successful step
                path = self.take_screenshot(driver, screenshot_dir, f"step_{i}")
                screenshots.append(path)

            return {
                "status": "success" if not errors else "failed",
                "completed_steps": completed_steps,
                "errors": errors,
                "screenshots": screenshots
            }

        finally:
            driver.quit()

    # =========================
    # 🔍 ROBUST FIND WITH WAIT
    # =========================
    def wait_for_element(self, driver, selector, timeout=10, clickable=False):
        wait = WebDriverWait(driver, timeout)
        by = By.CSS_SELECTOR
        
        if selector.startswith("#"):
            by = By.ID
            selector = selector[1:]
        elif selector.startswith("[name="):
            by = By.NAME
            selector = selector.split("'")[1] if "'" in selector else selector.split('"')[1]

        if clickable:
            return wait.until(EC.element_to_be_clickable((by, selector)))
        return wait.until(EC.presence_of_element_located((by, selector)))

    # =========================
    # 🧠 FIXED UNIVERSAL HANDLER
    # =========================
    def fill_field(self, driver, element, field_type, value):
        tag = element.tag_name.lower()

        # 1. FILE UPLOAD (The #photo fix)
        if field_type == "file" or tag == "input" and element.get_attribute("type") == "file":
            if value:
                # Clean path and make absolute
                clean_path = str(value).lstrip('/')
                abs_path = os.path.abspath(os.path.join(settings.BASE_DIR, clean_path))
                # CRITICAL: Never call .clear() on a file input
                element.send_keys(abs_path)
            return

        # 2. SELECT DROPDOWN
        if tag == "select":
            Select(element).select_by_visible_text(str(value))
            return

        # 3. REACT SELECT / CUSTOM DROPDOWNS
        if field_type == "react-select":
            driver.execute_script("arguments[0].click();", element)
            time.sleep(1)
            # Try to find the text option anywhere in the body
            try:
                option = driver.find_element(By.XPATH, f"//*[contains(text(), '{value}')]")
                driver.execute_script("arguments[0].click();", option)
            except:
                # Fallback to general search
                options = driver.find_elements(By.XPATH, "//*[self::div or self::li]")
                for opt in options:
                    if str(value).lower() in opt.text.lower():
                        opt.click()
                        break
            return

        # 4. CHECKBOX / RADIO
        if field_type in ["checkbox", "radio"]:
            is_checked = element.is_selected()
            should_be = str(value).lower() in ["true", "1", "yes"]
            if is_checked != should_be or field_type == "radio":
                driver.execute_script("arguments[0].click();", element)
            return

        # 5. TEXT INPUTS (Default)
        if tag == "input" or tag == "textarea":
            element.clear()
            element.send_keys(str(value))
        else:
            # Last resort JS injection for stubborn custom fields
            driver.execute_script(
                "arguments[0].value = arguments[1]; arguments[0].dispatchEvent(new Event('change'));",
                element, value
            )

    def take_screenshot(self, driver, folder, name):
        path = folder / f"{name}_{int(time.time())}.png"
        driver.save_screenshot(str(path))
        return str(path)