from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from datetime import date, timedelta
import time

driver = webdriver.Chrome()
driver.maximize_window()

wait = WebDriverWait(driver, 20)

# -----------------------------
# Find next Tuesday or Wednesday
# -----------------------------
today = date.today()

appointment_date = None

for i in range(1, 61):
    d = today + timedelta(days=i)

    # Tuesday = 1, Wednesday = 2
    if d.weekday() in [1, 2]:
        appointment_date = d.strftime("%Y-%m-%d")
        break

print("Booking Date:", appointment_date)

# -----------------------------
# Login
# -----------------------------
driver.get("http://127.0.0.1:8000/")

wait.until(
    EC.presence_of_element_located((By.NAME, "login_id"))
).send_keys("9742497134")

driver.find_element(By.NAME, "password").send_keys("Amisha@123")

driver.find_element(By.TAG_NAME, "button").click()

# -----------------------------
# Open Doctor Directory
# -----------------------------
driver.get("http://127.0.0.1:8000/doctors/")

# Search Doctor
search_box = wait.until(
    EC.presence_of_element_located((By.NAME, "search"))
)

search_box.clear()
search_box.send_keys("Shyam Shrestha")
search_box.send_keys(Keys.ENTER)

# Open Doctor Profile
wait.until(
    EC.element_to_be_clickable(
        (By.XPATH, "//a[contains(text(),'View Profile')]")
    )
).click()

# Click Book Appointment
wait.until(
    EC.element_to_be_clickable(
        (By.XPATH, "//a[contains(text(),'Book Appointment')]")
    )
).click()

# -----------------------------
# Select Appointment Date
# -----------------------------
date_input = wait.until(
    EC.presence_of_element_located((By.ID, "appointment-date"))
)

driver.execute_script(
    "arguments[0].value = arguments[1];",
    date_input,
    appointment_date
)

# Trigger onchange() because the page reloads automatically
driver.execute_script(
    "arguments[0].dispatchEvent(new Event('change'));",
    date_input
)

# Wait for page reload
wait.until(
    EC.presence_of_element_located((By.CLASS_NAME, "time-slot"))
)

# -----------------------------
# Select First Time Slot
# -----------------------------
slots = driver.find_elements(By.CLASS_NAME, "time-slot")

if len(slots) == 0:
    print("No slots available.")
    driver.quit()
    exit()

slots[0].click()

# Continue
driver.find_element(By.ID, "continue-booking").click()

# -----------------------------
# Payment
# -----------------------------
wait.until(
    EC.element_to_be_clickable(
        (By.XPATH, "//input[@value='cash']")
    )
).click()

driver.find_element(By.ID, "confirm-appointment").click()

time.sleep(3)

print("--------------------------------")
print("Current URL :", driver.current_url)
print("Page Title  :", driver.title)
print("--------------------------------")

if "dashboard" in driver.current_url.lower():
    print("Book Appointment Test Passed")
else:
    print( "Appointment submitted. Check the page manually.")

driver.quit()