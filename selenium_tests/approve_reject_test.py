from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

driver = webdriver.Chrome()
driver.maximize_window()

wait = WebDriverWait(driver, 15)

# Login as doctor
driver.get("http://127.0.0.1:8000/")

wait.until(
    EC.presence_of_element_located((By.NAME, "login_id"))
).send_keys("amisha123")

driver.find_element(By.NAME, "password").send_keys("bhatt@123")

driver.find_element(By.TAG_NAME, "button").click()

# Open Manage Today's Appointments
driver.get("http://127.0.0.1:8000/doctors/appointments/manage/")

# Click Complete on the first available appointment
wait.until(
    EC.element_to_be_clickable(
        (By.XPATH, "//a[contains(text(),'Complete')]")
    )
).click()

print("Current URL:", driver.current_url)
print("Title:", driver.title)
print("Appointment marked as Completed.")

driver.quit()