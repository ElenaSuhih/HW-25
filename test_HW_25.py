import pytest
import hashlib
import datetime
from selenium import webdriver
from selenium.common import ElementNotInteractableException
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.common.by import By


email = "e9271727525@gmail.ru"
password = "citrus13"


def wait(driver, sec):
    return WebDriverWait(driver, sec)

@pytest.fixture(scope="session")
def get_data():
    """Возвращает в тестовый класс Web элементы: инфо_пользователя, таблицу с петами и дату для логирования"""
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument('--window-size=800,600')
    driver = webdriver.Chrome(options=chrome_options)
    driver.get("https://petfriends.skillfactory.ru/")
    driver.implicitly_wait(2)
    wait(driver, 2).until(EC.presence_of_element_located((By.CSS_SELECTOR, "button[class$='btn-success']"))).click()
    wait(driver, 2).until(EC.presence_of_element_located((By.XPATH, "//a[@href='/login']"))).click()
    input_email = wait(driver, 2).until(EC.presence_of_element_located((By.ID, 'email')))
    input_email.send_keys(email)
    input_pass = driver.find_element(By.ID, "pass")
    input_pass.send_keys(password)
    driver.find_element(By.XPATH, "//button[@type='submit']").click()
    try:
        it_a_hamburger = wait(driver, 2).\
            until(EC.presence_of_element_located((By.CSS_SELECTOR, "button[data-toggle='collapse']")))
        it_a_hamburger.click()
    except ElementNotInteractableException:
        print("\nGamburger is not found!")
        pass
    my_pets = wait(driver, 2).until(
        EC.presence_of_element_located((By.XPATH, "//a[contains(@href, '/my_pets')]")))
    my_pets.click()
    my_info = driver.find_elements(By.XPATH, "//div[contains(@class, 'left')]")
    tr_table_my_pets = driver.find_elements(By.XPATH, "//tbody//tr")
    data = datetime.datetime.now().strftime('%H_%M_%S')
    yield my_info, tr_table_my_pets, data
    driver.quit()

class TestPetFriends():

    def test_compare_my_info_and_data_my_pets(self, get_data):
        my_info, tr_table_my_pets, date = get_data
        to_list_my_info = my_info[0].text.split("\n")
        count_my_pets_in_my_info = to_list_my_info[1]
        count_my_pets_in_my_info = int(
            count_my_pets_in_my_info[count_my_pets_in_my_info.find(":") + 1:].replace(" ", ""))
        with open(f"log{date}.txt", "a") as file:
            print("="*80, file=file)
            print(f"Тест: {self.test_compare_my_info_and_data_my_pets.__name__}", file=file)
            print(f'Питомцев в инфо: {count_my_pets_in_my_info}\nв таблице: {len(tr_table_my_pets)}', file=file)
        assert count_my_pets_in_my_info == len(tr_table_my_pets)


    def test_only_half_without_photos(self, get_data):
        _, tr_table_my_pets, date = get_data
        count_with_a_foto = 0
        count_without_photos = 0
        for item in tr_table_my_pets:
            if item.find_element(By.XPATH, "th//img").get_attribute('src') == "":
                count_without_photos += 1
            else:
                count_with_a_foto += 1
        with open(f"log{date}.txt", "a") as file:
            print("="*80, file=file)
            print(f"Тест: {self.test_only_half_without_photos.__name__}", file=file)
            print(f"с фото = {count_with_a_foto}", f"без фото = {count_without_photos}", sep="\n", file=file)
        assert count_with_a_foto > count_without_photos

    def test_there_is_a_name_breed_age(self, get_data):
        _, tr_table_my_pets, date = get_data
        there_is_a_name_breed_age = True
        for i in range(len(tr_table_my_pets)):
            if not there_is_a_name_breed_age:
                break
            for j in range(1, 4):
                if tr_table_my_pets[i].find_element(By.XPATH, "td[{}]".format(j)).text == "":
                    there_is_a_name_breed_age = False
                    break
        with open(f"log{date}.txt", "a") as file:
            print("="*80, file=file)
            print(u"Тест: {}".format(self.test_there_is_a_name_breed_age.__name__), file=file)
            print(u"У всех питомцев есть имя, возраст и порода = {}".format(there_is_a_name_breed_age), file=file)

        assert there_is_a_name_breed_age

    def test_all_names_are_different(self, get_data):
        _, tr_table_my_pets, date = get_data
        all_names_are_different = True
        list_names = []
        for i in range(len(tr_table_my_pets)):
            name = tr_table_my_pets[i].find_element(By.XPATH, "td[1]").text
            if name in list_names:
                all_names_are_different = False
                break
            list_names.append(name)
        with open(f"log{date}.txt", "a") as file:
            print("="*80, file=file)
            print(f"Тест: {self.test_all_names_are_different.__name__}", file=file)
            print(f"У всех питомцев разные имена = {all_names_are_different}", file=file)
        assert all_names_are_different

    def test_there_are_no_duplicate_pets_in_the_list(self, get_data):
        _, tr_table_my_pets, date = get_data
        there_are_no_duplicate_pets_in_the_list = True
        list_data = []
        for i in range(len(tr_table_my_pets)):
            if not there_are_no_duplicate_pets_in_the_list:
                break
            string = tr_table_my_pets[i].find_element(By.XPATH, "th//img").get_attribute('src')
            for j in range(1, 4):
                string += tr_table_my_pets[i].find_element(By.XPATH, "td[{}]".format(j)).text
            hash_string = hashlib.md5(string.encode())
            hash_dig = hash_string.hexdigest()
            if hash_dig in list_data:
                there_are_no_duplicate_pets_in_the_list = False
                list_data.append(hash_dig)
                break
            list_data.append(hash_dig)
        with open(f"log{date}.txt", "a") as file:
            print("="*80, file=file)
            print(f"Тест: {self.test_there_are_no_duplicate_pets_in_the_list.__name__}", file=file)
            print(f"Нет повторяющихся питомцев. = {there_are_no_duplicate_pets_in_the_list}", file=file)
        assert there_are_no_duplicate_pets_in_the_list
