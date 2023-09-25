from django.shortcuts import render
from django.db.models import Q

from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.pagination import LimitOffsetPagination
from .models import Film, Actor
from .serializers import FilmSerializer, ActorSerializer

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
