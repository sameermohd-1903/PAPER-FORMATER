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
    path(
    "builder/<int:pattern_id>/preview/",
    views.paper_preview_pattern,
    name="paper_preview_pattern",
    ),
    path(
    "builder/<int:pattern_id>/print/",
    views.paper_print,
    name="paper_print",
    ),
    path(
    "builder/<int:pattern_id>/pdf/",
    views.paper_pdf,
    name="paper_pdf",
    ),
    path(
        "builder/<int:pattern_id>/section/<int:section_id>/questions/",
        views.get_section_questions_api,
        name="get_section_questions_api",
    ),
    
    path(
    'patterns/<int:pattern_id>/delete/',
    views.delete_pattern,
    name='delete_pattern'
    ),
    
    path(
        "builder/<int:pattern_id>/assign-question/",
        views.assign_section_question_api,
        name="assign_section_question_api",
    ),

]