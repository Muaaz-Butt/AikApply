from time import sleep

from .services.browser import get_driver
from .services.mapping_loader import load_mapping
from .services.filler import fill_fields
from .services.navigator import click_element
from .services.submitter import submit_form
from .services.alert_handler import handle_alert
from .services.logger import save_screenshot, save_result


def run_application(mapping_file):
    """
    Executes automated form filling and submission
    based on a mapping JSON file.
    """

    # Load mapping
    mapping = load_mapping(mapping_file)

    driver = get_driver()
    errors = []
    alert_text = None

    try:
        # 1️⃣ Open dummy university form
        driver.get(mapping["url"])
        sleep(1)

        # 2️⃣ Execute steps one by one
        for step in mapping["steps"]:

            if step["action"] == "fill":
                fill_fields(driver, step["fields"], errors)

            elif step["action"] == "click":
                click_element(driver, step["selector"])

            elif step["action"] == "submit":
                # 🔹 Click submit
                submit_form(driver, step["selector"])

                # 🔹 Handle success alert
                alert_text = handle_alert(driver)

                # 🔹 Small wait to stabilize UI
                sleep(1)

                # 🔹 TAKE SCREENSHOT AFTER SUBMISSION
                save_screenshot(driver, mapping["application_id"])

    finally:
        driver.quit()

    # 3️⃣ Prepare result summary
    result = {
        "application_id": mapping["application_id"],
        "status": "submitted" if not errors else "submitted_with_errors",
        "alert_message": alert_text,
        "errors": errors
    }

    # 4️⃣ Save result JSON
    save_result(mapping["application_id"], result)

    return result
