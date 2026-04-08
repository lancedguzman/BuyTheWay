from django.apps import AppConfig
from watson import search

class MarketplaceConfig(AppConfig):
    name = 'marketplace'
    def ready(self):
        products = self.get_model('Product')
        search.register(products)