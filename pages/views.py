from django.views.generic import TemplateView


class Changelog(TemplateView):
    template_name = 'CHANGELOG.html'