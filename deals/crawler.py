# deals/crawler.py

from selenium import webdriver
from selenium.webdriver import ActionChains
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
from .models import Game
import urllib
import time


class NoSearchResult(Exception):
    """검색 결과가 없을 때 던지는 사용자 정의 예외"""
    pass

def run_crawler(category="",count=50):
    category = urllib.parse.quote(category)
    address = f"https://store.steampowered.com/search/?sort_by=Reviews_DESC&term={category}&specials=1&category1=998&ndl=1"


    with webdriver.Chrome(service=Service(ChromeDriverManager().install())) as driver:
        driver.get(address)
        driver.implicitly_wait(10)

        # 언어 선택 - 한국어
        button = driver.find_element(By.ID, "language_pulldown")
        ActionChains(driver).click(button).perform()
        driver.implicitly_wait(10)
        button = driver.find_element(By.XPATH, '//*[@id="language_dropdown"]/div/a[4]')
        ActionChains(driver).click(button).perform()
        time.sleep(1)

        # 데이터 수집
        xpath = '//*[@id="search_resultsRows"]/a[{}]'
        try:
            driver.find_element(By.XPATH, '//*[@id="search_resultsRows"]/a[1]')
        except Exception:
            driver.quit()
            raise NoSearchResult("검색 결과가 없습니다.")
        
        for i in range(1, count + 1):
            try:
                element = driver.find_element(By.XPATH, xpath.format(i))
                title = element.find_element(By.CLASS_NAME, 'title').text
                discount_pct = element.find_element(By.CLASS_NAME, 'discount_pct').text.replace('%', '').replace('-', '').strip()
                original_price = element.find_element(By.CLASS_NAME, 'discount_original_price').text.replace('₩', '').replace(',', '').strip()
                final_price = element.find_element(By.CLASS_NAME, 'discount_final_price').text.replace('₩', '').replace(',', '').strip()
                link = element.get_attribute('href')

                # 크롤링 결과를 DB에 저장장
                Game.objects.get_or_create(
                    title=title,
                    defaults={
                        "original_price": int(original_price),
                        "discount_price": int(final_price),
                        "discount_percent": int(discount_pct),
                        "steam_link": link
                    }
                )
            except Exception as e:
                print(f"[{i}] 에러 발생:", e)
                continue