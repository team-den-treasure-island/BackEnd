from django.apps import AppConfig


class TreasureHuntConfig(AppConfig):
    name = 'treasureHunt'

    def ready(self):
        from . import signals
