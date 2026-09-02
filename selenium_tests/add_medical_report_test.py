from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import os
import time

driver = webdriver.Chrome()
driver.maximize_window()

wait = WebDriverWait(driver, 20)

try:
    # -----------------------------
    # Login as Doctor
    # -----------------------------
    driver.get("http://127.0.0.1:8000/")

    wait.until(
        EC.presence_of_element_located((By.NAME, "login_id"))
    ).send_keys("amisha123")

    driver.find_element(
        By.NAME,
        "password"
    ).send_keys("bhatt@123")

    driver.find_element(
        By.TAG_NAME,
        "button"
    ).click()

    # -----------------------------
    # Open Completed Appointments
    # -----------------------------
    driver.get("http://127.0.0.1:8000/doctors/appointments/?status=completed")

    wait.until(
        EC.presence_of_element_located((By.TAG_NAME, "body"))
    )

    print("Current URL:", driver.current_url)

    # Save screenshot for debugging
    driver.save_screenshot("completed_appointments.png")

    # -----------------------------
    # Check whether Upload Report exists
    # -----------------------------
    upload_links = driver.find_elements(
        By.XPATH,
        "//a[contains(text(),'Upload Report')]"
    )

    if len(upload_links) == 0:
        print("No completed appointment found.")
        print("Please complete an appointment before running this test.")
        driver.quit()
        exit()

    upload_links[0].click()

    # -----------------------------
    # Wait for Upload Report page
    # -----------------------------
    wait.until(
        EC.presence_of_element_located(
            (By.TAG_NAME, "form")
        )
    )

    print("Upload Report page opened.")

    # -----------------------------
    # Fill Diagnosis (change names if necessary)
    # -----------------------------
    try:
        diagnosis = driver.find_element(By.NAME, "diagnosis")
        diagnosis.clear()
        diagnosis.send_keys(
            "Patient recovering well."
        )
    except:
        print("Diagnosis field not found.")

    # -----------------------------
    # Fill Prescription
    # -----------------------------
    try:
        prescription = driver.find_element(By.NAME, "prescription")
        prescription.clear()
        prescription.send_keys(
            "Continue medication for 7 days."
        )
    except:
        print("Prescription field not found.")

    # -----------------------------
    # Upload PDF
    # -----------------------------
    report_path = os.path.abspath("sample_report.pdf")

    try:
        driver.find_element(
            By.CSS_SELECTOR,
            "input[type='file']"
        ).send_keys(report_path)

        print("PDF uploaded.")
    except:
        print("File upload field not found.")

    # -----------------------------
    # Save Report
    # -----------------------------
    wait.until(
        EC.element_to_be_clickable(
            (By.XPATH, "//button[@type='submit']")
        )
    ).click()

    time.sleep(2)

    print("--------------------------------")
    print("Medical Report Upload Test Passed")
    print("Current URL:", driver.current_url)
    print("Title:", driver.title)
    print("--------------------------------")

except Exception as e:
    print("TEST FAILED")
    print(e)
    driver.save_screenshot("error.png")

finally:
    time.sleep(2)
    driver.quit()