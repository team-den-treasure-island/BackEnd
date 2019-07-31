"""treasureHuntBE URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
import rest_framework
from rest_framework import routers
from treasureHunt.api import RoomViewSet, PlayerViewSet
from graphene_django.views import GraphQLView
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import authentication_classes, permission_classes, api_view
from rest_framework.settings import api_settings

# solution to use rest_framework to guard graphql
# https://github.com/graphql-python/graphene/issues/249#issuecomment-300068390
# this even uses our main settings.py configuration for authentication and permissions
# so it will be accessible via session or token
class DRFAuthenticatedGraphQLView(GraphQLView):
    def parse_body(self, request):
        if isinstance(request, rest_framework.request.Request):
            return request.data
        return super(GraphQLView, self).parse_body(request)

    @classmethod
    def as_view(cls, *args, **kwargs):
        view = super(GraphQLView, cls).as_view(*args, **kwargs)
        view = permission_classes((IsAuthenticated,))(view)
        view = authentication_classes(api_settings.DEFAULT_AUTHENTICATION_CLASSES)(view)
        view = api_view(['GET', 'POST'])(view)
        return view


router = routers.DefaultRouter()
router.register(r"rooms", RoomViewSet)
router.register(r"players", PlayerViewSet)

# router = routers.DefaultRouter()
# router.register(r"notes", PersonalNoteViewSet)
urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include(router.urls)),
    # add graphQL route with graphiql interface enabled
    # path("graphql/", GraphQLView.as_view(graphiql=True)),
    path("graphql/", DRFAuthenticatedGraphQLView.as_view(graphiql=True)),
]

  # if we need custom routes, we can add this back
  # path('', include('treasureHunt.urls')),

# authenticate graphql maybe

