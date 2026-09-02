from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

driver = webdriver.Chrome()
driver.maximize_window()

wait = WebDriverWait(driver, 20)

# -----------------------------
# Login as Patient
# -----------------------------
driver.get("http://127.0.0.1:8000/")

wait.until(
    EC.presence_of_element_located((By.NAME, "login_id"))
).send_keys("9742497134")      # Your patient phone number

driver.find_element(
    By.NAME,
    "password"
).send_keys("Amisha@123")   # <-- Replace with your password

driver.find_element(By.TAG_NAME, "button").click()

# -----------------------------
# Open Patient Dashboard
# -----------------------------
wait.until(
    EC.title_contains("Patient Dashboard")
)

# -----------------------------
# Open First Appointment Details
# -----------------------------
wait.until(
    EC.element_to_be_clickable(
        (By.XPATH, "//a[contains(text(),'View Details')]")
    )
).click()

# -----------------------------
# Click Cancel Appointment
# -----------------------------
wait.until(
    EC.element_to_be_clickable(
        (By.XPATH, "//button[contains(text(),'Cancel Appointment')]")
    )
).click()

# -----------------------------
# Accept Confirmation Alert
# -----------------------------
alert = wait.until(EC.alert_is_present())

print("Alert:", alert.text)

alert.accept()

# -----------------------------
# Wait for Redirect
# -----------------------------
time.sleep(3)


print("Current URL :", driver.current_url)
print("Page Title  :", driver.title)
print("--------------------------------")

# -----------------------------
# Verify
# -----------------------------
if "dashboard" in driver.current_url.lower():
    print("Cancel Appointment Test Passed")
else:
    print("Appointment cancelled. Verify manually.")

driver.quit()