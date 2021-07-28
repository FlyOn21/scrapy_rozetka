import time
from pprint import pprint

from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
import scrapy


class RozetkaSpider(scrapy.Spider):
    name = 'rozetka'
    start_urls = ['http://bt.rozetka.com.ua/coffee_machines/c80164//']


    def __init__(self, name=None, **kwargs):
        super().__init__(name, **kwargs)
        self.links_dict = {}

    def parse(self, response):
        for obj in response.css("div.goods-tile__inner"):
            if (obj.css("div.goods-tile__availability::text").get()).strip() == "Нет в наличии":
                continue
            unit_url = obj.css("a.goods-tile__heading::attr(href)").get()
            # print("=======================",unit_url,"=======================")
            yield scrapy.Request(unit_url, self.unit_all_link)
            # yield self.selenium(url_all)
        button_list = (response.css('a.button::attr(href)').getall())
        button_list.pop(-1)
        next_page = button_list[-1]
        if next_page is not None:
            next_page = response.urljoin(next_page)
            yield scrapy.Request(next_page, callback=self.parse)

    def unit_all_link(self, response):
        link_titles = response.css("a.tabs__link::text").getall()
        links = response.css("a.tabs__link::attr(href)").getall()
        for link_title,link in zip(link_titles,links):
            self.links_dict[(link_title).strip()]=link
        photo_data = self.selenium_photo_urls(self.links_dict["Фото"])
        yield {
            "image_urls": photo_data,
        }
        # characteristics_data = yield scrapy.Request(url=self.links_dict["Характеристики"],callback=self.characteristics)


    def characteristics(self,response):
        characteristics = response.xpath('//main[@class="product-tabs__content"]//text()').extract()
        print(characteristics)
        yield characteristics

    def photo(self, url):
        data = self.selenium_photo_urls(url)
        yield {
            "image_urls":data,
        }
        # photos_urls = data.xpath('//*/li[@class = "product-photos__item ng-star-inserted"]/img[contains(@src)]').getall()
        # print("!!!!!1",photos_urls)

    def selenium_photo_urls(self,url):
        list_urls = []
        chrome_options = Options()
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        driver = webdriver.Chrome("/usr/lib/chromium-browser/chromedriver", chrome_options=chrome_options)
        driver.get(url)
        last_height = driver.execute_script("return document.body.scrollHeight")
        while True:
            driver.execute_script("window.scrollTo(0, window.scrollY + 200);")
            new_height = driver.execute_script("return window.scrollY + 400")
            if new_height == last_height:
                image_count = len(WebDriverWait(driver, 10).until(EC.presence_of_all_elements_located
                                                                  ((By.CLASS_NAME,
                                                                    "product-photos__picture.ng-lazyloaded"))))
                print(image_count,"!!!!!!!!!!!!!!!")
                for number in range(1, image_count + 1):
                    image_urls = driver.find_element_by_xpath(
                        f"/html/body/app-root/div/div/rz-product/div/product-tab-photo/div/div/main/"
                        f"product-gallery-list/ul/li[{number}]/img").get_attribute("src")
                    list_urls.append(image_urls)
                break
            last_height = new_height
        return list_urls

    def selenium(self, url):
        chrome_options = Options()
        chrome_options.add_argument('--headless')
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        driver = webdriver.Chrome("/usr/lib/chromium-browser/chromedriver",chrome_options=chrome_options)
        driver.get(url)
        result = {}
        try:
            button = WebDriverWait(driver, 2).until(
                EC.presence_of_element_located(
                    (By.CLASS_NAME, "button_type_link.product-about__description-toggle.ng-star-inserted")))
            button.click()
            spetification = WebDriverWait(driver, 2).until(
                EC.presence_of_element_located((By.CLASS_NAME, "product-about__description.ng-star-inserted"))).text
            result["spetification"] = spetification
        except:
            result["spetification"] = False
        try:
            price = WebDriverWait(driver, 2).until(
                EC.presence_of_element_located((By.CLASS_NAME, "product-prices__inner.ng-star-inserted"))).text
            result["price"] = price
        except:
            result["price"] = False
        finally:
            driver.quit()
        return result

if __name__ == "__main__":
    a = RozetkaSpider()
    a.selenium_photo()