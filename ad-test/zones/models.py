from django.db import models



class Distribution(models.Model):
    percentage = models.IntegerField(default=0)
    zone = models.ForeignKey('Zone', on_delete=models.CASCADE, related_name='distributions', null=True)#establece la realacion

    def __str__(self):#representacion legible de los objetos distribution
        return '{} - {}%'.format(self.pk, self.percentage)

    def save(self, *args, **kwargs):#si es nuevo y no hay id debera buscar la ultima asociada a la misma zona
        if not self.pk:  # Validar si es una nueva distribución
            last_distribution = Distribution.objects.filter(zone=self.zone).order_by('-id').first()
            if last_distribution:#si se encuentra se establece el id de la neuva
                self.pk = None  # Deja que Django genere el nuevo ID automáticamente

        super(Distribution, self).save(*args, **kwargs)#guarda





class Zone(models.Model):
    name = models.CharField(max_length=200)#representa el nombre
    updated_at = models.DateTimeField(auto_now=True)#actualizacion cada que se edita y guarda

    def __str__(self):#envia la representacion del objeto
        return self.name
