from rest_framework import status
from rest_framework.response import Response


class CustomPostMixin:
    'Используется для произвольной модификации объектов по POST (например, изменение пароля).'

    success_status = status.HTTP_204_NO_CONTENT

    def get_object(self):
        return

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(self.get_object(), data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        return self.make_response(serializer)

    def make_response(self, serializer):
        return Response(status=self.success_status)

    def perform_create(self, serializer):
        serializer.save()
