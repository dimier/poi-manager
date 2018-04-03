from rest_framework.metadata import BaseMetadata


class EmptyMetadata(BaseMetadata):
    def determine_metadata(self, request, view):
        return
