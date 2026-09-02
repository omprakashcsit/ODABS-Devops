from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException

driver = webdriver.Chrome()
driver.maximize_window()

wait = WebDriverWait(driver, 15)

# -------------------------
# Login as Doctor
# -------------------------
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

# -------------------------
# Open Set Availability Page
# -------------------------
driver.get("http://127.0.0.1:8000/doctors/set-availability/")

# Wait for form
wait.until(
    EC.presence_of_element_located((By.NAME, "day_of_week"))
)

# Select Monday
Select(
    driver.find_element(By.NAME, "day_of_week")
).select_by_visible_text("Monday")

# Enter times
driver.find_element(
    By.NAME,
    "start_time"
).send_keys("09:00")

driver.find_element(
    By.NAME,
    "end_time"
).send_keys("17:00")

# Apply same schedule for week (optional)
driver.find_element(
    By.NAME,
    "same_for_week"
).click()

# Continue
driver.find_element(
    By.XPATH,
    "//button[@type='submit']"
).click()

# -------------------------
# Confirm Availability (if page appears)
# -------------------------
try:
    confirm_btn = WebDriverWait(driver, 5).until(
        EC.element_to_be_clickable(
            (By.XPATH, "//button[@type='submit']")
        )
    )
    confirm_btn.click()
    print("Availability confirmed successfully.")

except TimeoutException:
    print("Confirmation page not displayed.")
    print("Current URL:", driver.current_url)
    print("Title:", driver.title)

    # Print any error shown on the page
    try:
        error = driver.find_element(By.TAG_NAME, "body").text
        print(error)
    except:
        pass

print("Current URL:", driver.current_url)
print("Title:", driver.title)

driver.quit()