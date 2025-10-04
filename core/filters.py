from django_filters import rest_framework as filters
from .models import Gimnasio

class GimnasioFilter(filters.FilterSet):
    precio_inscripcion = filters.RangeFilter()
    calificacion = filters.NumberFilter(field_name='calificacion', lookup_expr='gte')
    ubicacion = filters.CharFilter(field_name='ubicacion', lookup_expr='icontains')

    class Meta:
        model = Gimnasio
        fields = ['ubicacion', 'precio_inscripcion', 'calificacion']
