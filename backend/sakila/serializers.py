from rest_framework import serializers
from .models import Film, Actor, Customer, City, Country, Address, Inventory, Rental, Store, FilmActor, FilmCategory
from django.db.models import Q

class FilmSerializer(serializers.ModelSerializer):
    language = serializers.StringRelatedField(many=False)
    original_language = serializers.StringRelatedField(many=False)
    categories = serializers.StringRelatedField(many=True)

    class Meta:
        model = Film
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

    def create(self, validated_data):
        country_name = validated_data.pop('country')
        country_instance, created = Country.objects.get_or_create(country=country_name) #get country instance and a bool saying if we created a new instance
        city_instance = City.objects.create(**validated_data, country=country_instance)
        return city_instance

class AddressSerializer(serializers.ModelSerializer):
    city = CitySerializer(many=False)

    class Meta:
        model = Address
        fields = ['address_id', 'address', 'address2', 'district', 'postal_code', 'phone', 'city']

    def create(self, validated_data):
        country_name = validated_data.pop('country')
        city_name = validated_data.pop('city')
        city_instance, created = City.objects.get_or_create(city=city_name, country=country_name)
        address_instance = Address.objects.create(**validated_data, city=city_instance)
        return address_instance

class InventorySerializer(serializers.ModelSerializer):
    #film = FilmSerializer(many=False)
    film = serializers.StringRelatedField(many=False)

    class Meta:
        model = Inventory
        fields = ['inventory_id', 'store_id', 'film']

class RentalSerializer(serializers.ModelSerializer):
    inventory = InventorySerializer(many=False, read_only=True)

    class Meta:
        model = Rental
        fields = ['rental_id','rental_date', 'customer_id', 'return_date', 'staff_id', 'inventory_id', 'inventory']

class StoreSerializer(serializers.ModelSerializer):
    class Meta:
        model = Store
        fields = ['store_id', 'manager_staff_id', 'address_id']

class CustomerSerializer(serializers.ModelSerializer):
    address = AddressSerializer(many=False) 
    rentals = RentalSerializer(source='rental_set', many=True)

    class Meta:
        model = Customer
        fields = ['customer_id', 'first_name', 'last_name', 'email', 'create_date', 'address', 'rentals'];

    def to_representation(self, instance):
        #Convert name to Title Case
        ret = super().to_representation(instance)
        ret['first_name'] = ret['first_name'].title()
        ret['last_name'] = ret['last_name'].title()
        return ret

    def create(self, validated_data):
        #get data for address
        address = validated_data.pop('address')

        
        if address['address2'] is None:
            addr2Q = Q(address2='') | Q(address2=None)
        else:
            addr2Q = Q(address2=address['address2'])

        country_instance, created = Country.objects.get_or_create(country=address['city']['country']['country'])
        city_instance, created = City.objects.get_or_create(city=address['city']['city'], country=country_instance)
        address_instance, created = Address.objects\
                                                    .filter(addr2Q)\
                                                    .get_or_create(address=address['address'], district=address['district'],\
                                                                   postal_code=address['postal_code'], phone=address['phone'],\
                                                                   city=city_instance,\
                                                                   defaults={'address2' : address['address2']})
        customer_instance = Customer.objects.create(**validated_data, address=address_instance, store_id=1, active=1)
        return customer_instance

    def update(self, instance, validated_data):
        print(validated_data)
        address_data = validated_data.pop('address', None)
        for key in validated_data:
            setattr(instance, key, validated_data.get(key))
            print(key,':',validated_data[key])
        if address_data is not None:

            if address_data['address2'] is None:
                addr2Q = Q(address2='') | Q(address2=None)
            else:
                addr2Q = Q(address2=address['address2'])

            country_instance, created = Country.objects.get_or_create(country=address_data['city']['country']['country'])
            city_instance, created = City.objects.get_or_create(city=address_data['city']['city'], country=country_instance) 
            address_instance, created = Address.objects\
                                                        .filter(addr2Q)\
                                                        .get_or_create(address=address_data['address'], district=address_data['district'],\
                                                                       postal_code=address_data['postal_code'], phone=address_data['phone'],\
                                                                       city=city_instance,\
                                                                       defaults={'address2' : address_data['address2']})
            instance.address = address_instance 
        instance.save()
        return instance
