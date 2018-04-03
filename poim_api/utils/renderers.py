from rest_framework import renderers

class JSONRenderer(renderers.JSONRenderer):
    def get_indent(self, accepted_media_type, renderer_context):
        # Игнорирование задания отступов клиентом

        # If 'indent' is provided in the context, then pretty print the result.
        # E.g. If we're being called by the BrowsableAPIRenderer.
        return renderer_context.get('indent', None)
