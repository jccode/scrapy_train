# -*- coding: utf-8 -*-
import scrapy


class BubuSpider(scrapy.Spider):
    name = 'bubu'
    allowed_domains = ['201606mp4.11bubu.com']
    start_urls = ['http://201606mp4.11bubu.com/']

    def parse(self, response):
        index_xml_node = self._video_desc_node(response)
        if index_xml_node:
            yield response.follow(index_xml_node, callback=self.parse_video)
        else:
            links = self._dir_links(response)
            for link in links:
                yield response.follow(link, callback=self.parse)

    def _dir_links(self, selector):
        nodes = selector.xpath("//pre/text()|//pre/a[not(contains(text(), 'To Parent Directory'))]")
        dir_nodes = []
        n = len(nodes) / 2  # every 2 item in a group
        for index in range(n):
            text = nodes[2 * index].extract()
            link = nodes[2 * index + 1]
            if "<dir>" in text:
                dir_nodes.append(link)
        return dir_nodes

    def _video_desc_node(self, response):
        xml_nodes = response.xpath('//a[contains(text(),"index.xml")]')
        if len(xml_nodes) > 0:
            return xml_nodes[0]
        else:
            return None

    def _is_index_xml(self, response):
        return response.url.endswith("index.xml")

    def parse_video(self, response):
        # print 'parse video'
        videos = response.xpath("//video")
        result = map(self._parse_video_item, videos)
        # self.log(result)
        poster_url = response.url.replace("/".join(response.url.split("/")[-3:]), "1_1.jpg")
        yield {'videos': result, 'poster': poster_url}

    @staticmethod
    def _parse_video_item(selector):
        return {
            "src": selector.xpath("./file/text()").extract_first().replace('\n', ''),
            "size": selector.xpath("./size/text()").extract_first(),
            "duration": selector.xpath("./seconds/text()").extract_first(),
        }

