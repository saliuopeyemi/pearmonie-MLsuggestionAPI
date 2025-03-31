from os import sched_get_priority_max
from django.urls import path,include
from . import views
from rest_framework.routers import DefaultRouter
from drf_yasg.views import get_schema_view
from drf_yasg import openapi

router = DefaultRouter()

router.register("content",views.ContentViewSet)

schema_view = get_schema_view(
   openapi.Info(
      title="ML SUGGESTION API",
      default_version='v1',
      description="APIs for managing content suggestions.",
      terms_of_service="",
      contact=openapi.Contact(email="saliuoazeez@gmail.com"),
      license=openapi.License(name="BSD License"),
   ),
   public=True,
)


urlpatterns = [
            path("signup/",views.RegistrationView.as_view(),name="signup"),
            path("signin/",views.LoginView.as_view(),name="signin"),
            path("subscribe/",views.SubscriptionView.as_view(), name="subscribe"),
            path("retrieve/",views.InteractionView.as_view(),name="retrieve-and-interact"),
            path("recommendation/",views.PredictionView.as_view(),name="recommendation"),
            path("train/",views.TrainPredictorView.as_view(),name="Train-Predictor"),

            path("",include(router.urls)),
            path("doc/", schema_view.with_ui('swagger', cache_timeout=0), name="swagger_ui"),
        ]
