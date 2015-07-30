from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^doc/(?P<document_id>[0-9]+)/$', views.show_document, {'docprint': False}, name='show_document'),
    url(r'^doc/(?P<document_id>[0-9]+)/pdf$', views.show_document_pdf, name='show_document_pdf'),
    url(r'^doc/(?P<document_id>[0-9]+)/print$', views.show_document, {'docprint': True}, name='show_document_print'),
    url(r'^doc/$', views.list_document, name='list_document'),
    url(r'^produce/(?P<document_id>[0-9]+)/(?P<flow_id>[0-9]+)$', views.produce_workflow, name='produce_workflow'),
]
