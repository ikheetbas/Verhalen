from django.conf import settings # import the settings file

# TODO give this a better name, since it is not only for app_version (any more)

def app_version_number(request):
    # return the value you want as a dictionary. you may add multiple
    # values in there.
    return {'APP_VERSION_NUMBER': settings.APP_VERSION_NUMBER,
            'ENVIRONMENT': settings.ENVIRONMENT}