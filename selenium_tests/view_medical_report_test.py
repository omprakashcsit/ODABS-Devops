from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

driver = webdriver.Chrome()
driver.maximize_window()

wait = WebDriverWait(driver, 15)

# -------------------------
# Login as Patient
# -------------------------
driver.get("http://127.0.0.1:8000/appointment/reports/")

wait.until(
    EC.presence_of_element_located((By.NAME, "login_id"))
).send_keys("9742497134")

driver.find_element(
    By.NAME,
    "password"
).send_keys("Amisha@123")

driver.find_element(
    By.TAG_NAME,
    "button"
).click()

# -------------------------
# Open Medical Reports page
# -------------------------
wait.until(
    EC.url_contains("dashboard")
)

driver.get("http://127.0.0.1:8000/appointment/reports/")

# -------------------------
# Verify reports page loaded
# -------------------------
wait.until(
    EC.presence_of_element_located((By.TAG_NAME, "body"))
)

print("Current URL:", driver.current_url)
print("Title:", driver.title)

assert "report" in driver.page_source.lower()

print("View Medical Reports Test Passed")

driver.quit()