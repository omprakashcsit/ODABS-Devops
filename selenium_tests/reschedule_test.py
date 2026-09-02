from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from datetime import date, timedelta
from selenium.webdriver.support.ui import Select
import time

driver = webdriver.Chrome()
driver.maximize_window()

wait = WebDriverWait(driver, 20)

# -------------------------
# LOGIN
# -------------------------

driver.get("http://127.0.0.1:8000/")

wait.until(
    EC.presence_of_element_located((By.NAME, "login_id"))
).send_keys("9742497134")

driver.find_element(
    By.NAME,
    "password"
).send_keys("Amisha@123")

driver.find_element(By.TAG_NAME, "button").click()

# -------------------------
# OPEN UPCOMING APPOINTMENTS
# -------------------------

driver.get("http://127.0.0.1:8000/patients/appointments/upcoming/")

# -------------------------
# CLICK RESCHEDULE BUTTON
# -------------------------

wait.until(
    EC.element_to_be_clickable(
        (By.XPATH, "//a[contains(text(),'Reschedule')]")
    )
).click()

# -------------------------
# FIND NEXT TUESDAY
# -------------------------

today = date.today()

for i in range(1, 30):
    d = today + timedelta(days=i)
    if d.weekday() == 1:      # Tuesday
        new_date = d.strftime("%Y-%m-%d")
        break

# -------------------------
# SELECT DATE
# -------------------------

date_input = wait.until(
    EC.presence_of_element_located(
        (By.ID, "appointment_date")
    )
)

driver.execute_script(
    "arguments[0].value=arguments[1];",
    date_input,
    new_date
)

driver.execute_script(
    "arguments[0].dispatchEvent(new Event('change'));",
    date_input
)

# wait until page reloads
wait.until(
    EC.presence_of_element_located(
        (By.NAME, "time")
    )
)

# -------------------------
# SELECT FIRST AVAILABLE SLOT
# -------------------------

dropdown = Select(
    driver.find_element(By.NAME, "time")
)

dropdown.select_by_index(0)

# -------------------------
# CONFIRM
# -------------------------

driver.find_element(
    By.XPATH,
    "//button[contains(text(),'Confirm Reschedule')]"
).click()

time.sleep(3)

print("--------------------------------")
print("Current URL:", driver.current_url)
print("Title:", driver.title)
print("--------------------------------")

print("Reschedule Appointment Test Passed")

driver.quit()