from django.urls import path
from deepseek_llm.views import AskQueryView


urlpatterns = [
    path('Ai/chat/', AskQueryView.as_view(), name='askquery'),
]
