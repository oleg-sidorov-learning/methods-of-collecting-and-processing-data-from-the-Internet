import parse_5ka


class Parse5kaCategories(parse_5ka.Parse5ka):

    def __init__(self, start_url, save_path: parse_5ka.Path, start_url_categories):
        super().__init__(start_url, save_path)
        self.start_url_categories = start_url_categories

    def run(self):
        categories = self._get_categories()
        for category in categories:
            self.params['categories'] = category['parent_group_code']
            body = self._init_body(category)
            for product in self._parse(self.start_url):
                body['products'].append(product)
            file_path = self.save_path.joinpath(f"{body['code']}.json")
            self._save(body, file_path)

    def _get_categories(self):
        response = self._get_response(self.start_url_categories)
        categories: list = response.json()
        return categories

    @staticmethod
    def _init_body(category):
        body = {
            'name': category['parent_group_name'],
            'code': category['parent_group_code'],
            'products': []
        }
        return body


if __name__ == '__main__':
    url = "https://5ka.ru/api/v2/special_offers/"
    url_categories = "https://5ka.ru/api/v2/categories/"
    categories_path = parse_5ka.get_save_path('categories')
    parser = Parse5kaCategories(url, categories_path, url_categories)
    parser.run()

