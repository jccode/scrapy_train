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
        videos = response.xpath("//video")
        url_arr = response.url.split("/")
        video_dir_url = "/".join(url_arr[:-1])
        img_dir_url = "/".join(url_arr[:-3])

        def item_parse_map_function((idx, item)):
            return self._parse_video_item(item, video_dir_url, "{}/1_{}.jpg".format(img_dir_url, str(idx+1)))

        result = map(item_parse_map_function, enumerate(videos))
        yield {'videos': result, 'poster': "{}/1_1.jpg".format(img_dir_url)}

    @staticmethod
    def _parse_video_item(selector, video_dir_url, poster_url):
        src = selector.xpath("./file/text()").extract_first().replace('\n', '')
        filename = src.split("/")[-1:][0]
        return {
            "src": "{}/{}".format(video_dir_url, filename),
            "size": selector.xpath("./size/text()").extract_first(),
            "duration": selector.xpath("./seconds/text()").extract_first(),
            "poster": poster_url,
        }
