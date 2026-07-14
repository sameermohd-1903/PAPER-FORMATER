from django.urls import path
from . import views

app_name = 'papers'

urlpatterns = [

    path('', views.home, name='home'),

    path('patterns/', views.pattern_list, name='pattern_list'),

    path('create-pattern/', views.create_pattern, name='create_pattern'),

    path('generate/<int:pattern_id>/', views.generate_paper, name='generate_paper'),

    path('preview/<int:paper_id>/', views.paper_preview, name='paper_preview'),

    path('download/<int:paper_id>/<str:format_type>/', views.download_paper, name='download_paper'),

    path('generated-papers/', views.generated_papers_list, name='generated_papers'),

    path(
        "builder/<int:pattern_id>/",
        views.pattern_builder,
        name="pattern_builder"
    ),

    path(
        "builder/<int:pattern_id>/save/",
        views.save_pattern_rows,
        name="save_pattern_rows"
    ),

    path(
        "builder/<int:pattern_id>/rows/",
        views.load_pattern_rows,
        name="load_pattern_rows"
    ),

]