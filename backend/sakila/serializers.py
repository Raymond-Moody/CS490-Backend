from rest_framework import serializers
from .models import Film, Actor

class FilmSerializer(serializers.ModelSerializer):
    language = serializers.StringRelatedField(many=False)
    original_language = serializers.StringRelatedField(many=False)
    categories = serializers.StringRelatedField(many=True)
    #actors = serializers.StringRelatedField(many=True)

    class Meta:
        model = Film
#        fields = '__all__'
        fields = ['film_id', 'title', 'description', 'release_year', 'language', 'original_language', 'rental_duration', 'rental_rate', 'length', 'replacement_cost', 'rating', 'special_features', 'last_update', 'categories']

    def to_representation(self, instance):
        #Convert title to Title Case
        ret = super().to_representation(instance)
        ret['title'] = ret['title'].title()
        return ret

class ActorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Actor
        fields = ['actor_id','first_name','last_name']

    def to_representation(self, instance):
        #Convert name to Title Case
        ret = super().to_representation(instance)
        ret['first_name'] = ret['first_name'].title()
        ret['last_name'] = ret['last_name'].title()
        return ret
