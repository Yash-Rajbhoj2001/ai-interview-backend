from django.urls import path
from .views import get_job_descriptions, create_job_description, delete_job_description, update_job_description

urlpatterns = [

    path('', get_job_descriptions),

    path('create/', create_job_description),

    path('<int:pk>/delete/', delete_job_description),

    path('<int:pk>/update/', update_job_description),

]