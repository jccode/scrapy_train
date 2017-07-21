# -*- coding: utf-8 -*-
import scrapy


class QuotesSpider(scrapy.Spider):
    name = 'quotes'
    allowed_domains = ['quotes.toscrape.com']
    start_urls = [
        'http://quotes.toscrape.com/page/1/',
        'http://quotes.toscrape.com/page/2/'
    ]

    def parse(self, response):
        for quote in response.css("div.quote"):
            yield {
                'text': quote.css('span.text::text').extract_first(),
                'author': quote.css('small.author::text').extract_first(),
                'tags': quote.css('div.tags a.tag::text').extract(),
            }
        next_page = response.css('li.next a::attr(href)').extract_first()
        if next_page is not None:
            yield response.follow(next_page, callback=self.parse)
            # next_page = response.urljoin(next_page)
            # yield scrapy.Request(next_page, callback=self.parse)

    def _save_to_file(self, response):
        page = response.url.split("/")[-2]
        filename = "quote-%s.html" % page
        with open(filename, 'wb') as f:
            f.write(response.body)
        self.log('Save file %s' % filename)




