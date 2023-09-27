from django.shortcuts import render
from django.db.models import Q

from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.pagination import LimitOffsetPagination
from .models import Film, Actor, Customer, Rental, Inventory, Staff
from .serializers import FilmSerializer, ActorSerializer, CustomerSerializer, RentalSerializer

# Create your views here.
class FilmViewSet(viewsets.ModelViewSet):
    serializer_class = FilmSerializer 

    @action(methods=['get'], detail=False, url_path='top', url_name='top')
    def get_top_films(self, request):
        queryset = Film.objects.raw('''
                                        SELECT F.film_id, F.title, COUNT(R.rental_id) AS rented
                                        FROM rental R
                                        INNER JOIN inventory I ON R.inventory_id = I.inventory_id
                                        INNER JOIN film F ON I.film_id = F.film_id
                                        GROUP BY F.film_id
                                        ORDER BY COUNT(R.rental_id) DESC, F.title
                                        LIMIT 5;
                                    ''')
        serializer = FilmSerializer(queryset, many=True)
        return Response(serializer.data)

    @action(methods=['get'], detail=True, url_path='inventory', url_name='inventory')
    def get_availble_copies(self, request, pk=None):
        inventory_total = Inventory.objects.filter(store_id=1).filter(film_id=pk)
        rented_out = inventory_total.filter(rental__return_date__isnull=True)
        available = inventory_total.difference(rented_out)
        return Response({'copies' : available.count(), 'inventory' : available.values()})

    def get_queryset(self):
        queryset = Film.objects.all()
        parameters = self.request.query_params
        titles = parameters.getlist('title') 
        genres = parameters.getlist('genre') 
        actors = parameters.getlist('actor') 
        if len(titles) != 0:
            queryset = queryset.filter(title__in=titles)
        if len(actors) != 0:
            print(actors)
            actorQuery = Q()
            for actor in actors:
                names = actor.split()
                fname = names[0]
                nameQuery = Q(actors__first_name=fname)
                if len(names) > 1:
                    lname = names[1]
                    nameQuery = nameQuery & Q(actors__last_name=lname)
                actorQuery = actorQuery | nameQuery
            queryset = queryset.filter(actorQuery)
        if len(genres) != 0:
            queryset = queryset.filter(categories__name__in=genres)
        return queryset 

class ActorViewSet(viewsets.ModelViewSet):
    queryset = Actor.objects.all()
    serializer_class = ActorSerializer

    @action(methods=['get'], detail=False, url_path='top', url_name='top')
    def get_top_actors(self, request):
        queryset = Actor.objects.raw('''
                                    SELECT A.actor_id, COUNT(F.title) AS movies
                                    FROM actor A
                                    INNER JOIN film_actor FA ON A.actor_id = FA.actor_id
                                    INNER JOIN film F on FA.film_id = F.film_id
                                    INNER JOIN inventory I on F.film_id = I.film_id
                                    WHERE I.store_id = 1
                                    GROUP BY A.actor_id
                                    ORDER BY movies DESC, A.last_name
                                    LIMIT 5;
                                     ''')
        serializer = ActorSerializer(queryset, many=True)
        return Response(serializer.data)

    @action(methods=['get'], detail=True, url_path='top-movies', url_name='top-movies')
    def get_actor_movies(self, request, pk=None):
        queryset = Film.objects.raw('''
                                     SELECT F.film_id, F.title, COUNT(R.rental_id) AS rented
                                    FROM rental R
                                    INNER JOIN inventory I ON R.inventory_id = I.inventory_id
                                    INNER JOIN film F ON I.film_id = F.film_id
                                    INNER JOIN film_actor FA ON FA.film_id = F.film_id
                                    INNER JOIN actor A ON FA.actor_id = A.actor_id 
                                    WHERE A.actor_id = %s
                                    GROUP BY F.film_id
                                    ORDER BY COUNT(R.rental_id) DESC, F.title
                                    LIMIT 5;
                                    ''', [pk]) 
        serializer = FilmSerializer(queryset, many=True)
        return Response(serializer.data)

class CustomerViewSet(viewsets.ModelViewSet):
    serializer_class = CustomerSerializer
    
    @action(methods=['get'], detail=True, url_path='rentals', url_name='rentals')
    def get_customer_rentals(self, request, pk=None):
        queryset = Rental.objects.filter(return_date__isnull=True)
        queryset = queryset.filter(inventory__store_id=1)
        if pk is not None:
            queryset = queryset.filter(customer_id=pk)
        serializer = RentalSerializer(queryset, many=True)
        return Response(serializer.data)

    def get_queryset(self):
        queryset = Customer.objects.all()
        queryset = queryset.filter(store_id=1)
        parameters = self.request.query_params
        fname = parameters.get('first_name')
        lname = parameters.get('last_name')
        cust_id = parameters.get('customer_id')
        if fname is not None:
            queryset = queryset.filter(first_name__istartswith=fname)
        if lname is not None:
            queryset = queryset.filter(last_name__istartswith=lname)
        if cust_id is not None:
            queryset = queryset.filter(customer_id=cust_id)
        return queryset

class RentalViewSet(viewsets.ModelViewSet):
    serializer_class = RentalSerializer

    def get_queryset(self):
        queryset = Rental.objects.all()
        return queryset

    def create(self, validated_data):
        serializer = RentalSerializer(data=self.request.data)
        inventory_id = self.request.data.pop('inventory_id')
        customer_id = self.request.data.pop('customer_id')
        staff_id = self.request.data.pop('staff_id')
        inventory_instance = Inventory.objects.filter(inventory_id=inventory_id).first()
        customer_instance = Customer.objects.filter(customer_id=customer_id).first()
        staff_instance = Staff.objects.filter(staff_id=staff_id).first()
        if not serializer.is_valid():
            print(serializer.errors)
        else:
            data = serializer.validated_data
            serializer.save(inventory=inventory_instance, customer=customer_instance, staff=staff_instance)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

