from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

driver = webdriver.Chrome()
driver.maximize_window()

# Open the registration page

driver.get("http://127.0.0.1:8000/patients/register/")

print(driver.current_url)
# print(driver.title)
# print(driver.page_source[:500])

wait = WebDriverWait(driver, 10)

# Fill the registration form
wait.until(EC.presence_of_element_located((By.NAME, "name"))).send_keys("Selenium Test")

driver.find_element(By.NAME, "phone").send_keys("9812343628")

driver.find_element(By.NAME, "email").send_keys("seleniumtest223@gmail.com")

driver.find_element(By.NAME, "address").send_keys("Kathmandu")

driver.find_element(By.NAME, "dob").send_keys("01-01-2002")

driver.find_element(By.NAME, "gender").send_keys("F")

driver.find_element(By.NAME, "password").send_keys("Test@123")

driver.find_element(By.NAME, "confirm_password").send_keys("Test@123")

# Click Register
driver.find_element(By.TAG_NAME, "button").click()

# Wait for page to load after submission
wait.until(lambda d: d.current_url != "http://127.0.0.1:8000/register/")

print("Current URL:", driver.current_url)
assert "dashboard" in driver.current_url.lower()
print("Registration Test Passed")
# print("Title:", driver.title)

driver.quit()