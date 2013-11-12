from slumber import configure

from models import Pizza, Shop
from operations import OrderPizza


configure(
    {'test': True})

configure(Pizza,
    operations_extra = [(OrderPizza, 'order')])

configure(Shop,
    properties_ro = ['web_address'])
