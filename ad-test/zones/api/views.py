from zones.api.serializers import ZoneSerializer, DistributionSerializer
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from datetime import datetime
from zones.models import Zone, Distribution

@api_view(['POST'])  # setter para editar la zona y sus distros
def edit(request):
    zone_id = request.data.get('id')
    name = request.data.get('name')
    updated_at_str = request.data.get('updated_at')
    distributions_data = request.data.get('distributions')
    new_distributions_data = request.data.get('newDistributions')

    #######################
    print('Zone ID:', zone_id)
    print('Zone Name:', name)
    print('Updated At:', updated_at_str)
    print('Distributions Data:', distributions_data)
    print('New Distributions Data:', new_distributions_data)
    ######################

    try:
        updated_at = datetime.strptime(updated_at_str, '%Y-%m-%dT%H:%M:%S.%fZ')#convierto la cadena en un objeto con datetime
    except ValueError:
        return Response('Invalid format for updated_at', status=400)

    zone = Zone.objects.filter(pk=zone_id).first()#busco la zona con su id
    if not zone:#valido que exista
        return Response('Zone not found', status=status.HTTP_400_BAD_REQUEST)

    zone.name = name
    zone.updated_at = updated_at
    zone.save()

    if distributions_data is not None and isinstance(distributions_data, list):
        for distribution_data in distributions_data:#itero las existentes y actualizo los datos
            distribution_id = distribution_data.get('id')
            percentage = distribution_data.get('percentage')

            if distribution_id:
                distribution = Distribution.objects.filter(pk=distribution_id, zone=zone).first()
                if distribution:
                    distribution.percentage = percentage
                    distribution.save()

    if new_distributions_data is not None and isinstance(new_distributions_data, list):
        for distribution_data in new_distributions_data:#itero las nuevas y creo instancias asociadas 
            percentage = distribution_data.get('percentage')
            Distribution.objects.create(zone=zone, percentage=percentage)

    # todas las distribuciones nuevamente después de guardar las nuevas y actualizar las existentes.
    all_distributions = Distribution.objects.filter(zone=zone)
    distribution_serializer = DistributionSerializer(all_distributions, many=True)

    #  diccionario con los datos a enviar 
    response_data = {
        "id": zone_id,
        "name": name,
        "distributions": distribution_serializer.data,
        "updated_at": zone.updated_at.isoformat(), 
    }

    return Response(response_data)

@api_view(['GET'])  # getter 
def get_zone(request, zone_id):
    zone = Zone.objects.filter(pk=zone_id).first()
    if not zone:
        return Response('Zone not found', status=status.HTTP_404_NOT_FOUND)
    #llamo las dist por id
    all_distributions = Distribution.objects.filter(zone=zone).order_by('id')#metodo order_by me permite consultar los id y ordenarlos como fueron creados
    distribution_serializer = DistributionSerializer(all_distributions, many=True)

    # diccionario con los datos a enviar
    response_data = {
        "id": zone_id,
        "name": zone.name,
        "distributions": distribution_serializer.data,
        "updated_at": zone.updated_at.isoformat(),
    }

    return Response(response_data)
