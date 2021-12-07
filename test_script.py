

from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import os
from bs4 import BeautifulSoup
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.options import Options as FirefoxOptions
import time 



MODE = 'Seq'
total_req_seq = 3

def get_response(final_html):
    soup = BeautifulSoup(final_html, "html.parser")
    resp = soup.find('p').getText()
    return resp

def execute_process(url): 
    options = FirefoxOptions()
    options.add_argument("--headless")
    driver = webdriver.Firefox(options=options)
    
    start = time.time() 
    driver.get(url)

    driver.find_element(By.ID, "upload_proc").send_keys(os.getcwd() + '/tmp.jpg')
    button_element = driver.find_element(By.ID, 'submit_proc')
    button_element.click()

    WebDriverWait(driver, 15).until(EC.url_changes(url))
    final_html = driver.page_source
    end = time.time() 
    total_time = end - start
    return final_html, total_time 


con_req = 5
url = "http://pcvm4-3.instageni.colorado.edu:8080/"
url_list = [url] * con_req

import multiprocessing as mp
from multiprocessing import Pool

if MODE == 'Seq': 
    pool = Pool(processes=con_req)
    ret = pool.map(execute_process, url_list)
    for _, total_time in ret: 
        print(total_time)
    #print(result) 

    #print('Average Delay: %.3f'%(total_time/total_req_seq))

