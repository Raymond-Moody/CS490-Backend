from django.urls import reverse
from rest_framework.test import APITestCase
from sakila.views import FilmViewSet, ActorViewSet 

# Create your tests here.
class FilmViewSetTest(APITestCase):
    def test_get_top_films(self):
        expected_titles = ['Bucket Brotherhood', 'Rocketeer Mother', 'Forward Temple', 'Grit Clockwork', 'Juggler Hardly']
        response = self.client.get('/films/top/')
        for i in range(len(response.data)):
            #print(response.data[i]['title'], ':', expected_titles[i])
            self.assertEqual(response.data[i]['title'], expected_titles[i])

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
