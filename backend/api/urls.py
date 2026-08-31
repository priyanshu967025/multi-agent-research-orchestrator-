from django.urls import path
from . import views

urlpatterns = [
    path("health/", views.HealthAPIView.as_view(), name="api-health"),
    path("auth/register/", views.RegisterAPIView.as_view(), name="api-register"),
    path("auth/login/", views.LoginAPIView.as_view(), name="api-login"),
    path("auth/logout/", views.LogoutAPIView.as_view(), name="api-logout"),
    path("auth/profile/", views.UserProfileAPIView.as_view(), name="api-profile"),
    path("auth/change-password/", views.ChangePasswordAPIView.as_view(), name="api-change-password"),
    path("research/execute/", views.ExecuteResearchAPIView.as_view(), name="api-execute-research"),
    path("research/jobs/", views.ResearchJobsAPIView.as_view(), name="api-research-jobs"),
    path("research/documents/", views.ResearchDocumentUploadAPIView.as_view(), name="api-research-documents"),
    path("research/sessions/", views.UserSessionsAPIView.as_view(), name="api-user-sessions"),
    path("research/sessions/<int:pk>/export/", views.ExportReportAPIView.as_view(), name="api-session-export"),
    path("research/sessions/<int:pk>/", views.SessionDetailAPIView.as_view(), name="api-session-detail"),
    path("research/stream/", views.ResearchStreamAPIView.as_view(), name="api-research-stream"),
    path("research/<int:pk>/tags/", views.ResearchTagsAPIView.as_view(), name="api-research-tags"),
    path("research/benchmark/", views.RunBenchmarkAPIView.as_view(), name="api-run-benchmark"),
    path("benchmark/history/", views.BenchmarkHistoryAPIView.as_view(), name="api-benchmark-history"),
    path("stats/", views.PlatformStatsAPIView.as_view(), name="api-platform-stats"),
    path("rag/stats/", views.RAGStatsAPIView.as_view(), name="api-rag-stats"),
    path("rag/search/", views.RAGQueryAPIView.as_view(), name="api-rag-search"),
]
