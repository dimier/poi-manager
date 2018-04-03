from django.db import models
from django.conf import settings
from django.utils.timezone import now
from django.utils.translation import gettext_lazy as _


class PointManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(date_deleted=None)


class Point(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, verbose_name=_('пользователь'))
    date_created = models.DateTimeField(_('дата создания'), default=now, db_index=True)
    unlisted = models.BooleanField(_('скрыта'), default=False, db_index=True)
    date_deleted = models.DateTimeField(_('дата удаления'), null=True, blank=True, db_index=True)

    title = models.TextField(_('название'))
    latitude = models.FloatField(db_index=True)
    longitude = models.FloatField(db_index=True)

    objects = PointManager()
    all_objects = models.Manager()

    class Meta:
        verbose_name = _('точка')
        verbose_name_plural = _('точки')

    def __str__(self):
        return self.title

    @classmethod
    def can_create(cls, user):
        if not user.is_authenticated:
            return False

        if user.is_superuser:
            return True

        # Здесь можно добавить ограничения на создание инстансов,
        # например для явного запрета определённому пользователю.

        return True

    def can_update(self, user):
        if not user.is_authenticated:
            return False

        if user.is_superuser:
            return True

        if user.is_staff and user.has_perm('points.change_point'):
            return True

        if user.id == self.user_id:
            return True

        return False
