from rest_framework import serializers
from .models import Film, Actor, Customer, City, Country, Address, Inventory, Rental

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

class CountrySerializer(serializers.ModelSerializer):
    class Meta:
        model = Country
        fields = ['country_id', 'country']

class CitySerializer(serializers.ModelSerializer):
    country = CountrySerializer(many=False);
    class Meta:
        model = City
        fields = ['city_id', 'city', 'country']

class AddressSerializer(serializers.ModelSerializer):
    city = CitySerializer(many=False)
    class Meta:
        model = Address
        fields = ['address_id', 'address', 'address2', 'district', 'postal_code', 'phone', 'city']

class CustomerSerializer(serializers.ModelSerializer):
    address = AddressSerializer(many=False) 
    class Meta:
        model = Customer
        fields = ['customer_id', 'first_name', 'last_name', 'email', 'address'];

    def to_representation(self, instance):
        #Convert name to Title Case
        ret = super().to_representation(instance)
        ret['first_name'] = ret['first_name'].title()
        ret['last_name'] = ret['last_name'].title()
        return ret

class InventorySerializer(serializers.ModelSerializer):
    film = FilmSerializer(many=False)
    class Meta:
        model = Inventory
        fields = ['inventory_id', 'store_id', 'film']

class RentalSerializer(serializers.ModelSerializer):
    inventory = InventorySerializer(many=False, read_only=True)

    class Meta:
        model = Rental
        fields = ['rental_id','rental_date', 'customer_id', 'return_date', 'staff_id', 'inventory_id', 'inventory']
