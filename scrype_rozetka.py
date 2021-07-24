import time
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
import scrapy


class Rozetka(scrapy.Spider):
    name = "rozetka"
    start_urls = ["https://bt.rozetka.com.ua/coffee_machines/c80164/", ]

    def parse(self, response):
        for obj in response.css("div.goods-tile__inner"):
            if (obj.css("div.goods-tile__availability::text").get()).strip() == "Нет в наличии":
                continue
            url_all = obj.css("a.goods-tile__heading::attr(href)").get()
            yield scrapy.Request(url_all, self.unit_all_link)
            yield self.selenium(url_all)
        button_list = (response.css('a.button::attr(href)').getall())
        button_list.pop(-1)
        next_page = button_list[-1]
        if next_page is not None:
            next_page = response.urljoin(next_page)
            yield scrapy.Request(next_page, callback=self.parse)

    def unit_all_link(self, response):
        links_dict = {}
        link_titles = response.css("a.tabs__link::text").getall()
        links = response.css("a.tabs__link::attr(href)").getall()
        for link_title,link in zip(link_titles,links):
            links_dict[(link_title).strip()]=link
        yield scrapy.Request(url=links_dict["Характеристики"],callback=self.characteristics)

    def characteristics(self,response):
        characteristics = response.xpath('//main[@class="product-tabs__content"]//text()').extract()
        return characteristics

    def reviews(self, response):
        reviews = response.css()


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
