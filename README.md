# invoicepi
Web-based Quotation / Invoice / Receipt System on Django web framework.

invoicepi is a Django app developed to issue invoices, quotations, and receipts (namely invoices in the following) since Django v1, and now supports Django v4.2.

## Use Django Admin to edit

To create, modify and delete invoices, please use Django admin to do it before implementing the UI for editing.

## PDF/Print export

invoicepi can export an invoice to a PDF file for email/archive or simple HTML text for printing.

## Installation from Git

1. Git clone invoicepi to your Django project.

2. add 'invoicepi.invoicepi' to INSTALLED_APPS array of settings.py in your Django project.

3. add the following path() line to urls.py in your Django project, please do not forget to import include from django.urls.

```
    path('invoicepi/', include('invoicepi.invoicepi.urls')),
```

4. Try local test. Login and main page of invoicepi is located at [/invoicepi](http://localhost:8000/invoicepi) of your Django project, and use Django admin to modify contents.

```
http://localhost:8000/invoicepi
```