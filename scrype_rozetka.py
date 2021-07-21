import time
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
import scrapy


class Rozetka(scrapy.Spider):
    name = "rozetka"
    start_urls = ["https://bt.rozetka.com.ua/coffee_machines/c80164/", ]

    def parse(self, response):
        for obj in response.css("div.goods-tile__inner"):
            if obj.css("div.goods-tile__availability::text").get() == "Нет в наличии":
                continue
            url_all = obj.css("a.goods-tile__heading::attr(href)").get()
            yield response.follow(url_all, self.unit_all_link)
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
        characteristics = response.css("div.product-tabs__body main.product-tabs__content::text").get()
        price = response.css("div.product-carriage__price.ng-star-inserted::text").get()
        print("!!!!",characteristics,price)


    def selenium(self, url):
        driver = webdriver.Chrome()
        driver.get(url)
        try:
            button = WebDriverWait(driver, 2).until(
                EC.presence_of_element_located(
                    (By.CLASS_NAME, "button_type_link.product-about__description-toggle.ng-star-inserted")))
            button.click()
            data = WebDriverWait(driver, 2).until(
                EC.presence_of_element_located((By.CLASS_NAME, "product-about__description.ng-star-inserted")))
            result = data.text
            # time.sleep(10)
        finally:
            driver.quit()
            return result

#
# if __name__ == "__main__":
#     a = Rozetka()
#     a.selenium()
