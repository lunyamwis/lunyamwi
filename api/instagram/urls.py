from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'instagramLead', views.InstagramLeadViewSet)
router.register(r'scores', views.ScoreViewSet)
router.register(r'qualification_algorithms', views.QualificationAlgorithmViewSet)
router.register(r'schedulers', views.SchedulerViewSet)
router.register(r'lead_sources', views.LeadSourceViewSet)
router.register(r'simplehttpoperator',views.SimpleHttpOperatorViewSet)
router.register(r'workflows',views.WorkflowViewSet)
router.register(r'media',views.MediaViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('api/custom-fields/', views.CustomFieldListCreateView.as_view(), name='custom-field-list-create'),
    path('api/custom-fields/<int:pk>/', views.CustomFieldRetrieveUpdateDestroyView.as_view(), name='custom-field-detail'),
    
    path('api/custom-field-values/', views.CustomFieldValueListCreateView.as_view(), name='custom-field-value-list-create'),
    path('api/custom-field-values/<int:pk>/', views.CustomFieldValueRetrieveUpdateDestroyView.as_view(), name='custom-field-value-detail'),

    path('api/endpoints/', views.EndpointListCreateView.as_view(), name='endpoint-list-create'),
    path('api/endpoints/<int:pk>/', views.EndpointRetrieveUpdateDestroyView.as_view(), name='endpoint-detail'),

    path('api/connections/', views.ConnectionListCreateView.as_view(), name='connection-list-create'),
    path('api/connections/<int:pk>/', views.ConnectionRetrieveUpdateDestroyView.as_view(), name='connection-detail'),

    path('api/workflows/', views.WorkflowListCreateView.as_view(), name='workflow-list-create'),
    path('api/workflows/<int:pk>/', views.WorkflowRetrieveUpdateDestroyView.as_view(), name='workflow-detail'),
    path('endpoints/', views.EndpointListView.as_view(), name='endpoint_list'),
    path('endpoints/create/', views.EndpointCreateView.as_view(), name='endpoint_create'),
    path('endpoints/update/<str:pk>/', views.EndpointUpdateView.as_view(), name='endpoint_update'),
    path('endpoints/delete/<str:pk>/', views.EndpointDeleteView.as_view(), name='endpoint_delete'),
    path('workflow/list', views.WorkflowList.as_view(), name='list_workflows'),
    path('workflow/create/', views.WorkflowCreate.as_view(), name='create_workflow'),
    path('workflow/update/<str:pk>/', views.WorkflowUpdate.as_view(), name='update_workflow'),
    path('workflow/delete-operator/<str:pk>/', views.delete_httpoperator, name='delete_httpoperator'),
    path('workflow/delete-dag/<str:pk>/', views.delete_dag, name='delete_dag'),
    path('workflow/runner/<str:pk>/', views.WorkflowRunner.as_view(), name='workflow_runner'),
    path('workflow/trigger/<str:pk>/trigger', views.TriggerRun.as_view(), name='trigger_workflow'),
    path('connection/', views.ConnectionListView.as_view(), name='connection_list'),
    path('connection/create/', views.ConnectionCreateView.as_view(), name='connection_create'),
    path('connection/update/<str:pk>/', views.ConnectionUpdateView.as_view(), name='connection_update'),
    path('connection/delete/<str:pk>/', views.ConnectionDeleteView.as_view(), name='connection_delete'),
    path('custom-fields/create/', views.CustomFieldCreateView.as_view(), name='custom_field_create'),
    path('custom-fields/update/<str:pk>/', views.CustomFieldUpdateView.as_view(), name='custom_field_update'),
    path('custom-fields/delete/<str:pk>/', views.CustomFieldDeleteView.as_view(), name='custom_field_delete'),
    path('custom-fields/list/', views.CustomFieldListView.as_view(), name='custom_field_list'),
    path('endpoints/<str:endpoint_id>/custom-field/create/', views.CustomFieldValueCreateView.as_view(), name='custom_field_value_create'),
    path('displayWorkflow/', views.display_workflows,name="workflows"),
    path('generateWorkflow/', views.generate_workflow,name="create_workflowset"),
    path('scrapFollowers/', views.ScrapFollowers.as_view()),
    path('scrapGmaps/', views.ScrapGmaps.as_view()),
    path('scrapTheCut/', views.ScrapTheCut.as_view()),
    path('scrapStyleseat/',views.ScrapStyleseat.as_view()),
    path('scrapAPI/', views.ScrapAPI.as_view()),
    path('scrapURL/', views.ScrapURL.as_view()),
    path('scrapMindBodyOnline/', views.ScrapMindBodyOnline.as_view()),
    path('scrapSiteMaps/', views.ScrapSitemaps.as_view()),
    path('scrapUsers/', views.ScrapUsers.as_view()),
    path('scrapMedia/', views.ScrapMedia.as_view()),
    path('scrapInfo/', views.ScrapInfo.as_view()),
    path('insertAndEnrich/', views.InsertAndEnrich.as_view()),
    path('getMediaIds/',views.GetMediaIds.as_view()),
    path('getMediaComments/',views.GetMediaComments.as_view()),
    path('getAccounts/',views.GetAccounts.as_view()),
    path('fetchPendingInbox/',views.FetchPendingInbox.as_view()),
    path('approveRequests/',views.ApproveRequest.as_view()),
    path('sendDirectAnswer/',views.SendDirectAnswer.as_view()),
    path('qualifyingPayload/',views.PayloadQualifyingAgent.as_view()),
    path('assignmentPayload/',views.PayloadAssignmentAgent.as_view()),
    path('scrapingPayload/',views.PayloadScrappingAgent.as_view()),
    path('encPass/',views.GeneratePasswordEnc.as_view())
]