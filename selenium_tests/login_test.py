from selenium import webdriver
from selenium.webdriver.common.by import By
import time

driver = webdriver.Chrome()

driver.maximize_window()

driver.get("http://127.0.0.1:8000/")

time.sleep(2)

driver.find_element(By.NAME, "login_id").send_keys("utsab99")  # Existing patient's phone number
driver.find_element(By.NAME, "password").send_keys("bigyan@123")

driver.find_element(By.TAG_NAME, "button").click()

time.sleep(20)


print("Login Test Passed")

print(driver.current_url)
print(driver.title)


driver.quit()