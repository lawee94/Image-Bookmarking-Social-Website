from django.apps import AppConfig


class ImageConfig(AppConfig):
    name = 'image'
    verbose_name = 'Image bookmarks'

    def ready(self):
        #import signal handler
        import image.signals
