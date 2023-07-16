from rest_framework import serializers
from zones.models import Zone, Distribution

class DistributionSerializer(serializers.ModelSerializer):
    class Meta:#esta clase especifica el modelo a serializar
        model = Distribution
        fields = '__all__' 

class ZoneSerializer(serializers.ModelSerializer):#los datos vinculados de zones
    distributions = DistributionSerializer(many=True, read_only=True)  # Campos de distribuciones solo para lectura

    class Meta:
        model = Zone#trabajando con el modelo zona
        fields = '__all__'  # Incluye todos los campos del modelo Zone

    def create(self, validated_data):#extrae los datos de las tristibuciones asociadas a la zona
        # pedimos las distribuciones tras la validacion si hay:
        distributions_data = validated_data.pop('distributions', [])
        # crea una nueva instancia de Zone con los datos validados pero no incluye las nuevas:
        zone = Zone.objects.create(**validated_data)

        # crea cada una de las distribuciones y las asociamos con la nueva instancia de Zone:
        for distribution_data in distributions_data:
            Distribution.objects.create(zone=zone, **distribution_data)

        return zone

    def update(self, instance, validated_data):
        # actualiza los campos del modelo Zone con los datos validados:
        instance.name = validated_data.get('name', instance.name)
        instance.updated_at = validated_data.get('updated_at', instance.updated_at)
        instance.save()

        # pide las distribuciones validadas si hay:
        distributions_data = validated_data.get('distributions', [])
        distribution_ids = [item.get('id') for item in distributions_data if 'id' in item]

        # Elimina las distribuciones que no estén en la lista de lo que se recibe en los id
        instance.distributions.exclude(id__in=distribution_ids).delete()

        # Actualiza cada una de las distribuciones asociadas con la instancia de Zone
        for distribution_data in distributions_data:
            distribution_id = distribution_data.get('id')
            percentage = distribution_data.get('percentage')
            #valida el id
            if distribution_id:
                distribution = instance.distributions.filter(id=distribution_id).first()
                if distribution:
                    distribution.percentage = percentage
                    distribution.save()
            else:#si no hay id validos se devuelve la zona con su respectivo update
                Distribution.objects.create(zone=instance, percentage=percentage)

        return instance
