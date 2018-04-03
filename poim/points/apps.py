from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class PointsConfig(AppConfig):
    name = 'poim.points'
    verbose_name = _('POI')

    # def ready(self):
    #     from .signal_receivers import receiver
