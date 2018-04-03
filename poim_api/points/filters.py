from django.utils.translation import gettext_lazy as _
from django_filters import rest_framework as filters
from poim.points.models import Point
from poim_api.utils import exceptions
from poim_api.utils.filters import IntegerCSVFilter, DecimalCSVFilter

# update after django-filter 2.0 release
from django_filters import STRICTNESS


class PointFilter(filters.FilterSet):
    geo = DecimalCSVFilter(method='filter_geo', help_text=_('Координаты для фильтрации в формате '
            '"latitude,longitude,distance_meters", например "59.923932,30.315181,100000".'))

    class Meta:
        model = Point
        fields = []

    def _filter_geo(self, queryset, point, distance_m):
        # 0.018 градуса с запада на восток на каждый километр радиуса (2 км с севера на юг в широтах Санкт-Петербурга)
        circle_radius = float(distance_m) * 0.018 / 1000
        # TODO переписать на Expression
        queryset = queryset.extra(where=[
                'circle(point(%s, %s), %s) @> point(latitude, longitude)',
                'earth_distance(ll_to_earth(latitude, longitude), ll_to_earth(%s, %s)) <= %s'
            ], params=[
                point[0], point[1], circle_radius,
                point[0], point[1], distance_m,
            ])
        return queryset

    def filter_geo(self, queryset, name, value):
        if len(value) != 3:
            raise exceptions.ValidationError({name: [_('Неверный формат координат.')]})

        return self._filter_geo(queryset, value[:2], value[2])
