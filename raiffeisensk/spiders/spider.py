import datetime

import scrapy

from scrapy.loader import ItemLoader
from w3lib.html import remove_tags

from ..items import RaiffeisenskItem
from itemloaders.processors import TakeFirst


class RaiffeisenskSpider(scrapy.Spider):
	name = 'raiffeisensk'
	start_urls = ['https://www.raiffeisen.sk/sk/o-banke/novinky-oznamy/']

	def parse(self, response):
		now = datetime.datetime.now().year
		for year in range(2012, now+1):
			year_url = f'https://www.raiffeisen.sk/sk/o-banke/novinky-oznamy/?year={year}'
			yield response.follow(year_url, self.parse_year)

	def parse_year(self, response):
		post_links = response.xpath('//div[@class="article"]/a/@href').getall()
		yield from response.follow_all(post_links, self.parse_post)

		next_page = response.xpath('//a[@rel="next"]/@href').getall()
		print(next_page)
		yield from response.follow_all(next_page, self.parse)

	def parse_post(self, response):
		title = response.xpath('//h1/text()').get()
		description = response.xpath('//div[@class="ly-content-body"]/div[@class="container"]//text()[normalize-space() and not(ancestor::h1 | ancestor::p[contains(@class, "smallest")])]').getall()
		description = [remove_tags(p).strip() for p in description]
		description = ' '.join(description).strip()
		date = response.xpath('//p[contains(@class, "smallest")]/text()[normalize-space()]').get()

		item = ItemLoader(item=RaiffeisenskItem(), response=response)
		item.default_output_processor = TakeFirst()
		item.add_value('title', title)
		item.add_value('description', description)
		item.add_value('date', date)

		return item.load_item()
