from rest_framework import serializers
from .models import Parameter, Data, Buoy

# parameter serializer object
class ParameterSerializer(serializers.ModelSerializer):
    class Meta:
        model = Parameter
        fields = ('id', 'name', 'fullname', 'description', 'min', 'max', 'uom', 'active')


# bouy serializer object
class BuoySerializer(serializers.ModelSerializer):

    parameters = ParameterSerializer(many=True, read_only=True)

    class Meta:
        model = Buoy
        fields = ('id', 'name', 'lat', 'lon', 'img', 'parameters', 'active', 'model', 'manufacturer', 'depth')


# data serializer object
class DataSerializer(serializers.ModelSerializer):
    buoy_id = serializers.IntegerField(read_only=True, required=False)
    parameter_id = serializers.IntegerField(read_only=True, required=False)

    class Meta:
        model = Data
        fields = ('buoy_id', 'parameter_id', 'value', 'timestamp', 'errors')
