from django.utils.translation import gettext_lazy as _
from rest_framework import fields, serializers
from rest_framework.exceptions import ValidationError
from poim.points.models import Point


__all__ = [
    'PointSerializer',
]


class PointSerializer(serializers.ModelSerializer):
    title = fields.CharField(max_length=100, label=_('Название'))
    can_edit = fields.SerializerMethodField()

    class Meta:
        model = Point
        fields = ['id', 'title', 'latitude', 'longitude', 'unlisted', 'can_edit']
        extra_kwargs = {f: {'required': True} for f in fields}
        extra_kwargs['title'].update({
            'max_length': 100,
            'style': None,
        })

    def _get_user(self):
        assert 'request' in self.context, 'request must be in context of {}'.format(type(self))
        return self.context['request'].user

    def get_can_edit(self, instance):
        user = self._get_user()
        return instance.can_update(user)
