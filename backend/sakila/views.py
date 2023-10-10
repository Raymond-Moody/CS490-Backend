from django.shortcuts import render
from django.db.models import Q, Prefetch

from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.pagination import LimitOffsetPagination
from .models import Film, Actor, Customer, Rental, Inventory, Staff, Country, City, Address, Store
from .serializers import FilmSerializer, ActorSerializer, CustomerSerializer, RentalSerializer, AddressSerializer, StoreSerializer

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
        inventory_total = Inventory.objects.filter(film_id=pk)
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
    
    def get_queryset(self):
        queryset = Customer.objects.prefetch_related(Prefetch('rental_set', queryset=Rental.objects.order_by('return_date'))).all()
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

    def destroy(self, request, *args, **kwargs):
        customer = self.get_object()
        custID = customer.pk
        cust_rentals = Rental.objects.filter(customer_id=custID)
        for rental in cust_rentals:
            rental.delete()
        try:
            customer.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except:
            return Response(status=status.HTTP_404_NOT_FOUND)

class RentalViewSet(viewsets.ModelViewSet):
    serializer_class = RentalSerializer
    queryset = Rental.objects.all()

    def create(self, validated_data):
        serializer = RentalSerializer(data=self.request.data)
        inventory_id = self.request.data.pop('inventory_id')
        customer_id = self.request.data.pop('customer_id')
        staff_id = self.request.data.pop('staff_id')
        inventory_instance = Inventory.objects.filter(inventory_id=inventory_id).first()
        customer_instance = Customer.objects.filter(customer_id=customer_id).first()
        staff_instance = Staff.objects.filter(staff_id=staff_id).first()
        if not serializer.is_valid():
            print("error=",serializer.errors)
        else:
            try:
                serializer.save(inventory=inventory_instance, customer=customer_instance, staff=staff_instance)
            except Exception as e:
                if "customer_id" in e.args[1]:
                    return Response("customer_id", status=status.HTTP_400_BAD_REQUEST)
                elif "staff_id" in e.args[1]:
                    return Response("staff_id", status=status.HTTP_400_BAD_REQUEST)
                else:
                    return Response("other", status=status.HTTP_400_BAD_REQUEST)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

