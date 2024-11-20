from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import PromptViewSet, RoleViewSet, index, add, getAgent,update, detail, delete, saveResponse, generateResponse, agentSetup,fetch_logs,fetch_logs_api

router = DefaultRouter()
router.register(r"prompts", PromptViewSet, basename="prompts")
router.register(r"roles", RoleViewSet, basename="roles")

urlpatterns = [path("", include(router.urls))]

urlpatterns = [
    path('', index, name='prompt_index'),
    path('add/', add, name='add'),
    path('detail/<str:prompt_id>/', detail, name='detail'),
    path('update/<str:prompt_id>/', update, name='update'),
    path('delete/<str:prompt_id>/', delete, name='delete'),
    path('save-response/',saveResponse.as_view()),
    path("generateResponse/",generateResponse.as_view()),
    path("agentSetup/",agentSetup.as_view(),name="agentSetup"),
    path("getAgent/",getAgent.as_view()),
    path('logs/', fetch_logs, name='fetch_logs'),
    path('api/fetch-logs/', fetch_logs_api, name='fetch_logs_api'),
    path("", include(router.urls))
]
