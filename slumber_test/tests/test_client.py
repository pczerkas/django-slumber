from django.test import TestCase
from slumber import client
from slumber.connector import Client, DictObject
from slumber_test.models import Pizza, PizzaPrice
from mock import patch

class TestDirectoryURLs(TestCase):
    def test_get_default_url_with_made_client(self):
        client = Client()
        self.assertEqual('http://localhost:8000/slumber/', client._directory)

    def test_get_default_url_with_default_client(self):
        self.assertEqual('http://localhost:8000/slumber/', client._directory)


class TestLoads(TestCase):

    def test_applications_local(self):
        client = Client('http://localhost:8000/slumber')
        self.assertTrue(hasattr(client, 'slumber_test'))

    def test_applications_remote(self):
        def request(k, u):
            self.assertEquals(u, 'http://slumber.example.com/')
            return DictObject(status=200), '''{"apps":{}}'''
        with patch('slumber.connector.ua.Http.request', self.fail):
            client = Client('http://slumber.example.com/')
        with patch('slumber.connector.ua.Http.request', request):
            try:
                client.no_module
                self.fail("This should have given an attribute error")
            except AttributeError:
                pass

    def test_applications_with_dots_in_name(self):
        """
        dots (.) will be replaced with underscores (_) for some apps that may have dots in its name
        (i.e. django.contrib.sites)
        """
        client = Client()
        self.assertTrue(hasattr(client, 'django'), client.__dict__.keys())
        self.assertTrue(hasattr(client.django, 'contrib'), client.django.__dict__.keys())
        self.assertTrue(hasattr(client.django.contrib, 'sites'),
            (type(client.django.contrib), client.django.contrib.__dict__.keys()))
        try:
            client.django.NotAModelOrApp
            self.fail("This should have given an attribute error")
        except AttributeError:
            pass

    def test_instance_data(self):
        s = Pizza(name='S1', for_sale=True)
        s.save()
        pizza = client.slumber_test.Pizza.get(pk=s.pk)
        self.assertEqual('S1', pizza.name)
        prices = pizza.prices
        self.assertEqual(len(prices), 0)
        try:
            pizza.not_a_field
            self.fail("This should have thrown an AttributeError")
        except AttributeError:
            pass

    def test_instance_data_with_data_array(self):
        s = Pizza(name='S1', for_sale=True)
        s.save()
        for p in range(15):
            PizzaPrice(pizza=s, amount=str(p), date='2011-04-%s' % (p+1)).save()
        pizza = client.slumber_test.Pizza.get(pk=s.pk)
        self.assertEqual('S1', pizza.name)
        prices = pizza.prices
        self.assertEquals(len(prices), 15)
        first_price = prices[0]
        self.assertEquals(unicode(first_price), "PizzaPrice object")
        self.assertEquals(first_price.amount, "14")
        self.assertEquals(first_price.pizza.for_sale, True)

    def test_instance_no_pk(self):
        pizza = client.slumber_test.Pizza.get(pk=None)
        self.assertTrue(pizza is None)
