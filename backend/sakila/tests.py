from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from sakila.views import FilmViewSet, ActorViewSet 
from sakila.models import Customer, Address, City, Country

# Create your tests here.
class FilmViewSetTest(APITestCase):
    def test_get_top_films(self):
        expected_films = [103, 738, 331, 382, 489]
        response = self.client.get('/films/top/')
        for i in range(len(response.data)):
            self.assertEqual(response.data[i]['film_id'], expected_films[i])

    def test_get_available_copies(self):
        expected_inventory_14 = {
                                    "copies": 0,
                                    "inventory": []
                                }
        expected_inventory_17 = {
                                    "copies": 5,
                                    "inventory": [
                                        {
                                            "inventory_id": 82,
                                            "film_id": 17,
                                            "store_id": 1,
                                            "last_update": "2006-02-15T05:09:17Z"
                                        },
                                        {
                                            "inventory_id": 83,
                                            "film_id": 17,
                                            "store_id": 1,
                                            "last_update": "2006-02-15T05:09:17Z"
                                        },
                                        {
                                            "inventory_id": 84,
                                            "film_id": 17,
                                            "store_id": 2,
                                            "last_update": "2006-02-15T05:09:17Z"
                                        },
                                        {
                                            "inventory_id": 85,
                                            "film_id": 17,
                                            "store_id": 2,
                                            "last_update": "2006-02-15T05:09:17Z"
                                        },
                                        {
                                            "inventory_id": 86,
                                            "film_id": 17,
                                            "store_id": 2,
                                            "last_update": "2006-02-15T05:09:17Z"
                                        }
                                    ]
                                }
        response14 = self.client.get('/films/14/inventory/')
        response17 = self.client.get('/films/17/inventory/')

        self.assertEqual(response14.json(), expected_inventory_14)
        self.assertEqual(response17.json(), expected_inventory_17)

class ActorViewSetTest(APITestCase):
    def test_get_top_actors(self):
        expected_actors = [107,102,198,181,23]
        response = self.client.get('/actors/top/')
        for i in range(len(response.data)):
            self.assertEqual(response.data[i]['actor_id'], expected_actors[i])

    def test_get_actor_movies(self):
        expected_films = [361, 970, 166, 1, 25]
        response = self.client.get('/actors/1/top-movies/')
        for i in range(len(response.data)):
            self.assertEqual(response.data[i]['film_id'], expected_films[i])

class CustomerViewSetTest(APITestCase):
    def setUp(self):
        cust_data = {
                        'first_name' : 'test_first',
                        'last_name' : 'test_last',
                        'email' : 'mail@test.com',
                        'store_id' : 1,
                        'active' : 1
                    }
        self.customer = Customer.objects.create(**cust_data, address=Address.objects.get(address_id=10))

    def tearDown(self):
        self.customer.delete()
        Address.objects.filter(address_id__gt=605).delete()
        City.objects.filter(city_id__gt=600).delete()
        Country.objects.filter(country_id__gt=109).delete()

    # Test that we can edit a customer's information
    def test_customer_edit(self):
        response = self.client.patch('/customers/{}/'.format(self.customer.customer_id), {'first_name' : 'New_Name'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['first_name'], 'New_Name')

    # Test that editing a customers address finds existing addresses properly
    def test_customer_edit_existing_address(self):
        #address data matching address 50
        new_addr = {
                     'address' : '46 Pjatigorsk Lane',
                     'address2' : '',
                     'postal_code' : '23616',
                     'phone' : '262076994845',
                     'district' : 'Moscow (City)',
                     'city' : {
                                'city' : 'Moscow',
                                'country' : {'country' : 'Russian Federation'}
                              }
                   } 
        response = self.client.patch('/customers/{}/'.format(self.customer.customer_id), {'address' : new_addr}, format='json')
        self.assertEqual(response.data['address']['address_id'], 50)

    # test that customer edit properly creates all of the nested fields
    def test_customer_edit_new_address(self):
        new_addr = {
                     'address' : 'test_addr',
                     'address2' : '',
                     'postal_code' : 'test_code',
                     'phone' : 'test_phone',
                     'district' : 'test_district',
                     'city' : {
                                'city' : 'test_city',
                                'country' : {'country' : 'test_country'}
                              }
                   } 
        response = self.client.patch('/customers/{}/'.format(self.customer.customer_id), {'address' : new_addr}, format='json')
        self.assertEqual(response.data['address']['address'], new_addr['address'])
        self.assertEqual(response.data['address']['city']['city'], new_addr['city']['city'])
        self.assertEqual(response.data['address']['city']['country']['country'], new_addr['city']['country']['country'])
