import csv
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.chrome.options import Options
from time import sleep
import yokatlasparameters
import operator


driver = webdriver.Chrome(executable_path=yokatlasparameters.chrome_driver_path)
file = open(yokatlasparameters.dosya_adi, 'w', encoding='utf-8', newline='')

writer = csv.writer(file)
writer.writerow([
    'Üniversite Adı',
    'Tür',
    'Bölüm',
    'Sıralama',
    'Kontenjan'
])

def stringToInt (sNum):
    num = ""
    for char in sNum:
        if (char != '.'):
            num += char
    return int(num)

university_list = []

for bolum in yokatlasparameters.bolumler:

    #Getting to main page to select the wanted department from the list

    driver.get('https://yokatlas.yok.gov.tr/lisans-anasayfa.php')
    lisans_sec = driver.find_element_by_id('bolum')

    options = lisans_sec.find_elements_by_tag_name('option')

    for option in options:
        bolum_adi = option.text
        if bolum_adi == bolum:
            option.click()
            break
    
    #Getting the elements of universites so that we can get the url's of them
    element_section = driver.find_element_by_xpath('/html/body/div/div[2]/div[2]/div[1]')
    all_elements = element_section.find_elements_by_class_name('panel-title')

    urls = []

    for universite_element in all_elements:
        url = universite_element.find_element_by_xpath('.//a').get_attribute('href')
        urls.append(url)

    print("Found {} {} courses".format(len(urls), bolum))


    i = 1

    #Starting to getting the data from each page

    for url in urls:

        driver.get(url)

        #Clicking the down arrows in order to load the data of quota and the last entered person's score
        driver.find_element_by_xpath('//*[@id="h1070"]/a/h4/span[1]').click()
        driver.find_element_by_xpath('//*[@id="headingEleven"]/a/h4/span[1]').click()

        arewedone = True
        
        while (arewedone):
            try:
                WebDriverWait(driver, 60).until(EC.visibility_of_element_located((By.XPATH, '//*[@id="icerik_1070"]/table')))
                WebDriverWait(driver, 60).until(EC.visibility_of_element_located((By.XPATH, '//*[@id="icerik_1000_2"]/table')))
                arewedone = false
            except TimeoutException:
                driver.refresh()
        university_last_person_score = driver.find_element_by_xpath('//*[@id="icerik_1070"]/table/tbody/tr[6]/td[2]').text
        university_quota = driver.find_element_by_xpath('//*[@id="icerik_1000_2"]/table/tbody/tr[5]/td[2]').text
        university_name = driver.find_element_by_xpath('/html/body/div[2]/div[1]/div[1]/div/h3[1]').text
        university_type = driver.find_element_by_xpath('/html/body/div[2]/div[1]/div[1]/div/h3[2]').text.strip().split(" ", 2)[-1]
        university_departmant = driver.find_element_by_xpath('/html/body/div[2]/div[1]/div[3]/div/h2').text.strip().split("-", 1)[-1].strip()

        #Some basic printing in order to see the progress of the program
        print("#{}: {} / {}".format(i, university_name, university_last_person_score))

        if ( yokatlasparameters.alt_sinir <= stringToInt(university_last_person_score) <= yokatlasparameters.ust_sinir):

            #If a university is in range then we will print it to console to know that it is worknig correctly
            print("Passed: {}".format(university_name))

            university = [
                university_name,
                university_type,
                university_departmant,
                stringToInt(university_last_person_score),
                university_quota
            ]

            university_list.append(university)
        
        i += 1

#Lastly ordering them according to last entered person's score and writing them into the csv file

print("Data Scraping Completed Succesfully and Now Writing Into CSV File")

university_list.sort(key=operator.itemgetter(3))

for university in university_list:
    writer.writerow([university[0], university[1], university[2], university[3], university[4]])

file.close()

