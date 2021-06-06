import scrapy
import pymongo
import re


class AutoyoulaSpider(scrapy.Spider):
    name = 'autoyoula'
    allowed_domains = ['auto.youla.ru']
    start_urls = ['https://auto.youla.ru/']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.db = pymongo.MongoClient()['parse_11'][self.name]

    def _get_follow(self, response, selector_str, callback):
        for a_link in response.css(selector_str):
            url = a_link.attrib.get("href")
            yield response.follow(url, callback=callback)

    def parse(self, response):
        yield from self._get_follow(
            response,
            ".TransportMainFilters_brandsList__2tIkv a.blackLink",
            self.brand_parse
        )

    def brand_parse(self, response):
        yield from self._get_follow(
            response,
            ".Paginator_block__2XAPy a.Paginator_button__u1e7D",
            self.brand_parse
        )
        yield from self._get_follow(
            response,
            "a.SerpSnippet_name__3F7Yu.blackLink",
            self.car_parse
        )

    def car_parse(self, response):
        title = response.css('.AdvertCard_advertTitle__1S1Ak::text').get()
        images = [image.attrib['src'] for image in response.css('figure.PhotoGallery_photo__36e_r img')]
        description = response.css('.AdvertCard_descriptionInner__KnuRi::text').get()
        characteristics = self.get_characteristics(response)
        author = self.js_decoder_autor(response)
        self.db.insert_one({
            'title': title,
            'images': images,
            'description': description,
            'url': response.url,
            'author': author,
            'characteristics': characteristics,
        })

    def get_characteristics(self, response):
        return {itm.css('.AdvertCharacteristics_elemTitle__2sK-L::text').get(): itm.css(
            '.AdvertCharacteristics_elemValue__3Vims::text').get() for itm in
                response.css('.AdvertCharacteristics_elemGroup__3ek5T')}

    def js_decoder_autor(self, response):
        script = response.xpath('//script[contains(text(), "window.transitState =")]/text()').get()
        re_str = re.compile(r"youlaId%22%2C%22([0-9|a-zA-Z]+)%22%2C%22avatar")
        result = re.findall(re_str, script)
        return f'https://youla.ru/user/{result[0]}' if result else None