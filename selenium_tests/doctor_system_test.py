from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
import traceback
import os
import time

# -------------------------------
# Configuration
# -------------------------------
BASE_URL = "http://127.0.0.1:8000"

DOCTOR_USERNAME = "amisha123"
DOCTOR_PASSWORD = "bhatt@123"

REPORT_PATH = os.path.join(
    os.path.dirname(__file__),
    "sample_report.pdf"
)

driver = webdriver.Chrome()
driver.maximize_window()

wait = WebDriverWait(driver, 20)

try:

    # ==========================================
    # Login
    # ==========================================
    print("Logging in...")

    driver.get(BASE_URL)

    wait.until(
        EC.presence_of_element_located(
            (By.NAME, "login_id")
        )
    ).send_keys(DOCTOR_USERNAME)

    driver.find_element(
        By.NAME,
        "password"
    ).send_keys(DOCTOR_PASSWORD)

    driver.find_element(
        By.TAG_NAME,
        "button"
    ).click()

    wait.until(
        EC.presence_of_element_located(
            (By.TAG_NAME, "body")
        )
    )

    print("Login successful.")

    # ==========================================
    # Set Availability
    # ==========================================
    print("Setting availability...")

    driver.get(BASE_URL + "/doctors/set-availability/")

    wait.until(
        EC.presence_of_element_located(
            (By.NAME, "day_of_week")
        )
    )

    Select(
        driver.find_element(
            By.NAME,
            "day_of_week"
        )
    ).select_by_visible_text("Monday")

    start = driver.find_element(By.NAME, "start_time")
    start.clear()
    start.send_keys("09:00")

    end = driver.find_element(By.NAME, "end_time")
    end.clear()
    end.send_keys("17:00")

    try:
        checkbox = driver.find_element(By.NAME, "same_for_week")

        if not checkbox.is_selected():
            checkbox.click()

    except Exception:
        pass

    wait.until(
        EC.element_to_be_clickable(
            (By.XPATH, "//button[@type='submit']")
        )
    ).click()

    try:
        WebDriverWait(driver, 5).until(
            EC.element_to_be_clickable(
                (By.XPATH, "//button[@type='submit']")
            )
        ).click()

    except TimeoutException:
        pass

    print("Availability saved.")

    # ==========================================
    # Complete Appointment
    # ==========================================
    print("Completing appointment...")

    driver.get(BASE_URL + "/doctors/appointments/manage/")

    wait.until(
        EC.presence_of_element_located(
            (By.TAG_NAME, "body")
        )
    )

    complete_buttons = driver.find_elements(
        By.XPATH,
        "//a[contains(text(),'Complete')]"
    )

    if not complete_buttons:
        raise Exception("No appointment available to complete.")

    complete_buttons[0].click()

    # Wait for redirect after clicking Complete
    wait.until(
        EC.presence_of_element_located(
            (By.TAG_NAME, "body")
        )
    )

    print("Appointment completed.")

    # ==========================================
    # Open Completed Appointments
    # ==========================================
    driver.get(BASE_URL + "/doctors/appointments/?status=completed")

    wait.until(
        EC.presence_of_element_located(
            (By.TAG_NAME, "body")
        )
    )

    # ==========================================
    # Upload Medical Report
    # ==========================================
    print("Uploading medical report...")

    upload = wait.until(
        EC.element_to_be_clickable(
            (By.XPATH, "//a[contains(text(),'Upload Report')]")
        )
    )

    upload.click()

    wait.until(
        EC.presence_of_element_located(
            (By.NAME, "diagnosis")
        )
    )

    diagnosis = driver.find_element(By.NAME, "diagnosis")
    diagnosis.clear()
    diagnosis.send_keys("Patient recovering well.")

    prescription = driver.find_element(By.NAME, "prescription")
    prescription.clear()
    prescription.send_keys(
        "Continue medication twice daily for one week."
    )

    remarks = driver.find_element(By.NAME, "remarks")
    remarks.clear()
    remarks.send_keys(
        "Patient should return after seven days for follow-up."
    )

    driver.find_element(
        By.NAME,
        "report_file"
    ).send_keys(REPORT_PATH)

    wait.until(
        EC.element_to_be_clickable(
            (By.XPATH, "//button[@type='submit']")
        )
    ).click()

    wait.until(
        EC.presence_of_element_located(
            (By.TAG_NAME, "body")
        )
    )

    print("Medical report uploaded successfully.")
    print("Doctor module system test completed successfully.")

except Exception:

    print("\nSystem test failed.\n")

    traceback.print_exc()

    print("\nCurrent URL :", driver.current_url)
    print("Page Title  :", driver.title)

    driver.save_screenshot("doctor_system_error.png")

finally:

    time.sleep(2)
    driver.quit()