from django.core.management.base import BaseCommand

from zones.models import Zone, Distribution


class Command(BaseCommand):#command implementa la logica
    help = 'Command to fill remaining dates'#atributo para dar descripcion de que se realiza

    def handle(self, *args, **options):#metodo de la logica principal
        self.create_zones('A', [50, 50], [])
        self.create_zones('B', [25, 25, 25, 25], [])
        self.create_zones('C', [30, 30, 40], [])
        self.create_zones('D', [15, 15, 5, 10, 55], [])

    def create_zones(self, name, percentages, new_distributions):#funcion para crear las zonas con los argumentos de post
        zone = Zone.objects.create(name=name)#instancia de zone.

        for percentage in percentages:#recorre la lista y se asocian.
            Distribution.objects.create(zone=zone, percentage=percentage)
        #ciclo para nuevas distribuciones y se asocian
        for percentage in new_distributions:
            Distribution.objects.create(zone=zone, percentage=percentage)