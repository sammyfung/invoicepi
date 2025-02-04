# invoicepi

invoicepi is a web-based Quotation / Invoice / Receipt System. It is a Django module to issue invoices, quotations and receipts.

## Features

* **Create Invoices**: use Django administration (django.contrib.admin) to create, modify and delete invoices, quotations, receipts and other document. 
* **Invoice to PDF / HTML**: click on a "Save" (PDF) or "Print" (HTML) icon on top left of document page to get its PDF file or simply HTML page. The PDF file  / HTML file can be printed or saved as a file to email it to client.
* **Other features**: Item amounts can be waived, total amount can add a discount off, item can be header only without description.

## Add "Invoices"

Hereby are steps to create an invoices in Django administration with invoicepi installed.

0. (One off) adding new document type: Add "Invoice" in "Document types".
1. Select document "Type", eg. Invoice.
2. Input the "Title" of the document, eg. Web based invoice system annual subscription service".
3. Press "Save" button to save this document to generate/get a ID for this document for creating new "Category" 

## Installation from Git

1. **Clone it**: Git clone invoicepi to your Django project.

2. **Add to Django**:
   1. Add as Installed App: add 'invoicepi.invoicepi' to INSTALLED_APPS array of settings.py in your Django project.
   2. Add to Django path: add the following path() line to urls.py in your Django project, please do not forget to import include from django.urls.

      ```
      path('invoicepi/', include('invoicepi.invoicepi.urls')),
      ```

4. **Try it**:
   1. Login and main page of invoicepi is located at [/invoicepi](http://localhost:8000/invoicepi) of your Django project, and use Django admin to modify contents.

      ```
      http://localhost:8000/invoicepi
      ```
