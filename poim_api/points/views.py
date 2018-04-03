from django.utils.timezone import now
from rest_framework import generics, status
# from rest_framework.permissions import IsAuthenticated
from poim.points.models import Point
from poim_api.utils import exceptions
from poim_api.utils.permissions import AnonRetrieveOwnerUpdate
from poim_api.points.serializers import *
from poim_api.points.filters import PointFilter


__all__ = [
    'PointListView',
    'PointDetailView',
    'PointUndeleteView',
]


class PointListView(generics.ListCreateAPIView):
    '''
    get:
    Список точек. Аутентификация опциональна.

    post:
    Добавление точки. Аутентификация обязательна.

    Коды ответов HTTP:

    `201 Created` — успешное выполнение запроса

    `400 Bad Request` — ошибки формы

    `403 Forbidden` — у пользователя нет прав на создание объекта
    '''
    queryset = Point.objects.filter(unlisted=False).order_by('-id')
    serializer_class = PointSerializer
    permission_classes = [AnonRetrieveOwnerUpdate]
    filter_class = PointFilter

    def perform_create(self, serializer):
        assert self.request.user.is_authenticated, 'User must be authenticated.'

        instance = serializer.save(user=self.request.user)


class PointDetailView(generics.RetrieveUpdateDestroyAPIView):
    '''
    get:
    Получение точки. Аутентификация опциональна.

    Коды ответов HTTP:

    `200 OK` — успешное выполнение запроса

    `404 Not Found` — объект не сущесвует или удалён

    put:
    Обновление точки. Аутентификация обязательна. Обновить объект может только его автор или администратор.

    Коды ответов HTTP:

    `200 OK` — успешное выполнение запроса

    `400 Bad Request` — ошибки формы

    `404 Not Found` — объект не сущесвует или удалён

    `403 Forbidden` — у пользователя нет прав на изменение ресурса

    patch:
    Обновление точки. Аутентификация обязательна.

    Коды ответов HTTP аналогичны PUT.

    delete:
    Удаление точки. Аутентификация обязательна. Удалить объект может только его автор или администратор.

    Возможно восстановление после удаления, см. [/points/{id}/deleted](#points-deleted-delete).

    Коды ответов HTTP:

    `204 No Content` — успешное выполнение запроса

    `404 Not Found` — объект не сущесвует или удалён

    `403 Forbidden` — у пользователя нет прав на удаление ресурса
    '''
    queryset = Point.objects.all()
    serializer_class = PointSerializer
    permission_classes = [AnonRetrieveOwnerUpdate]

    def perform_destroy(self, instance):
        instance.date_deleted = now()
        instance.save(update_fields=['date_deleted'])


class PointUndeleteView(generics.DestroyAPIView):
    '''
    delete:
    Отмена операции удаления точки. Аутентификация обязательна.
    Восстановить объект может только его автор или администратор.

    Коды ответов HTTP:

    `204 No Content` — успешное выполнение запроса

    `404 Not Found` — объект либо не существует, либо не удалён, либо восстановлен, либо удалён окончательно
    '''
    queryset = Point.all_objects.filter(date_deleted__isnull=False)
    permission_classes = [AnonRetrieveOwnerUpdate]

    def perform_destroy(self, instance):
        if not instance.date_deleted:
            raise exceptions.NotFound()

        instance.date_deleted = None
        instance.save(update_fields=['date_deleted'])
