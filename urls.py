from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^doc/(?P<document_id>[0-9]+)/pdf$', views.show_document, {'format': 'pdf'}, name='show_document_pdf'),
    url(r'^doc/(?P<document_id>[0-9]+)/print$', views.show_document, {'format': 'print'}, name='show_document_print'),
    url(r'^doc/(?P<document_id>[0-9]+)', views.show_document, name='show_document'),
    url(r'^person/$', views.list_person, name='list_person'),
    url(r'^person/(?P<op>[a-z]+)/(?P<start_seq>[0-9]+)$', views.list_person, name='list_person'),
    url(r'^company/$', views.list_company, name='list_company'),
    url(r'^produce/(?P<document_id>[0-9]+)/(?P<flow_id>[0-9]+)$', views.produce_workflow, name='produce_workflow'),
    url(r'^logon$', views.logon_form, name='logon_form'),
    url(r'^logoff$', views.logoff_form, name='logoff_form'),
    url(r'^api/company', views.api_list_company, name='api_list_company'),
    url(r'^api/doc/(?P<document_id>[0-9]+)', views.api_show_document, name='api_show_document'),
    url(r'^api/doc', views.api_list_document, name='api_list_document'),
    url(r'^api/person', views.api_list_person, name='api_list_person'),
    url(r'^$', views.list_document, name='list_document'),
]

