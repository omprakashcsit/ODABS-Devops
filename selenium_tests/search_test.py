from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

driver = webdriver.Chrome()
driver.maximize_window()

wait = WebDriverWait(driver, 10)

driver.get("http://127.0.0.1:8000/doctors/")

# Find the search box
search_box = wait.until(
    EC.presence_of_element_located((By.NAME, "search"))
)

search_box.send_keys("Ram")
search_box.send_keys(Keys.ENTER)

# Wait until doctor cards appear
wait.until(
    EC.presence_of_element_located((By.CLASS_NAME, "doctor-card"))
)

results = driver.find_elements(By.CLASS_NAME, "doctor-card")

print("Doctors Found:", len(results))

assert len(results) > 0

print("Search Doctor Test Passed")

driver.quit()