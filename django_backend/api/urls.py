"""
API URL Routing module.
"""

from django.urls import path
from .views import (
    RegisterView, LoginView, UserProfileView,
    StartResearchView, ResearchHistoryView,
    RunEvaluationView, EvaluationHistoryView
)

urlpatterns = [
    path('auth/register/', RegisterView.as_view(), name='auth_register'),
    path('auth/login/', LoginView.as_view(), name='auth_login'),
    path('auth/me/', UserProfileView.as_view(), name='auth_me'),
    
    path('research/start/', StartResearchView.as_view(), name='research_start'),
    path('research/history/', ResearchHistoryView.as_view(), name='research_history'),
    
    path('evaluation/run/', RunEvaluationView.as_view(), name='evaluation_run'),
    path('evaluation/history/', EvaluationHistoryView.as_view(), name='evaluation_history'),
]
