from django.urls import path
from . import views

urlpatterns = [
    path('doc/<int:document_id>/pdf', views.show_document, {'format': 'pdf'}, name='show_document_pdf'),
    path('doc/<int:document_id>/print', views.show_document, {'format': 'print'}, name='show_document_print'),
    path('doc/<int:document_id>', views.show_document, name='show_document'),
    path('person', views.list_person, name='list_person'),
    path('person/<slug:op>/<int:start_seq>', views.list_person, name='list_person'),
    path('company/', views.list_company, name='list_company'),
    path('produce/<int:document_id>/<int:flow_id>', views.produce_workflow, name='produce_workflow'),
    path('logon/', views.logon_form, name='logon_form'),
    path('logoff/', views.logoff_form, name='logoff_form'),
    path('api/company', views.api_list_company, name='api_list_company'),
    path('api/doc/<int:document_id>', views.api_show_document, name='api_show_document'),
    path('api/doc', views.api_list_document, name='api_list_document'),
    path('api/person', views.api_list_person, name='api_list_person'),
    path('', views.list_document, name='list_document'),
]

