from django import forms
from django_filters import rest_framework as filters


class IntegerCSVFilter(filters.BaseCSVFilter):
    field_class = forms.IntegerField


class DecimalCSVFilter(filters.BaseCSVFilter):
    field_class = forms.DecimalField
