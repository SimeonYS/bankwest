import re
import scrapy
from scrapy.loader import ItemLoader
from ..items import BbankwestItem
from itemloaders.processors import TakeFirst
import json

pattern = r'(\xa0)?'

class BbankwestSpider(scrapy.Spider):
	name = 'bankwest'
	start_urls = ['https://www.bankwest.com.au/about-us/media-centre/news.article-data.json']

	def parse(self, response):
		data = json.loads(response.text)
		for index in range(len(data['articles'])):
			link = data['articles'][index]['linkURL']
			title = data['articles'][index]['title']
			date = data['articles'][index]['publishedDate'].split('T')[0]
			yield response.follow(link, self.parse_post, cb_kwargs=dict(date=date, title=title))

	def parse_post(self, response, date, title):
		content = response.xpath('//div[@class="content-wrapper "]//text()').getall()
		content = [p.strip() for p in content if p.strip()]
		content = re.sub(pattern, "",' '.join(content))

		item = ItemLoader(item=BbankwestItem(), response=response)
		item.default_output_processor = TakeFirst()

		item.add_value('title', title)
		item.add_value('link', response.url)
		item.add_value('content', content)
		item.add_value('date', date)

		yield item.load_item()
