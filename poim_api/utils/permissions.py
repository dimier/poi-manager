from rest_framework.permissions import SAFE_METHODS, BasePermission
from poim_api.utils import exceptions


class GetModelMixin:
    'Mixin к Permission, извлекающий класс модели из queryset представления'

    def _queryset(self, view):
        assert hasattr(view, 'get_queryset') \
            or getattr(view, 'queryset', None) is not None, (
            'Cannot apply {} on a view that does not set '
            '`.queryset` or have a `.get_queryset()` method.'
        ).format(self.__class__.__name__)

        if hasattr(view, 'get_queryset'):
            queryset = view.get_queryset()
            assert queryset is not None, (
                '{}.get_queryset() returned None'.format(view.__class__.__name__)
            )
            return queryset
        return view.queryset

    def _model(self, view):
        return self._queryset(view).model


class AnonRetrieveOwnerUpdate(GetModelMixin, BasePermission):
    def has_permission(self, request, view):
        if request.method in SAFE_METHODS:
            return True

        if request.method == 'POST':
            if request.user.is_authenticated and self._model(view).can_create(request.user):
                return True

            return False

        if request.method in ['PUT', 'PATCH', 'DELETE']:
            # will check for object permission
            return True

        raise exceptions.MethodNotAllowed(request.method)

    def has_object_permission(self, request, view, instance):
        if request.method in SAFE_METHODS:
            return True

        if request.method in ['PUT', 'PATCH', 'DELETE']:
            if request.user.is_authenticated and instance.can_update(request.user):
                return True

            return False

        raise exceptions.MethodNotAllowed(request.method)
