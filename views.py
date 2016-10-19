from django.shortcuts import render
from django.shortcuts import Http404
from .models import Document, DocumentType, DocumentCategory, DocumentItem, DocumentFlow, CompanyPerson, Company
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ObjectDoesNotExist
import cStringIO as StringIO
import ho.pisa as pisa
from django.template.loader import get_template
from django.template import Context
from django.http import HttpResponse
from django.db.models import Q
from django.contrib.auth.models import User
from cgi import escape
import re
from datetime import datetime


def get_document_format(document):
  doc_type = DocumentType.objects.get(pk=document.document_type.pk)
  document.opening = doc_type.opening
  document.after_table = doc_type.after_table
  document.closing = doc_type.closing
  document.sender_sign = doc_type.sender_sign
  document.receiver_sign = doc_type.receiver_sign
  return document


def get_document(document_id):
  # Getting document info and document code in its type syntax.
  document = Document.objects.get(pk=document_id)
  document = get_document_format(document)  
  document_type = ContentType.objects.get(model=document.document_type.model_name)
  try:
    document.code = document_type.model_class().objects.get(pk=document.pk).code
  except ObjectDoesNotExist:
    document.code = document.pk  
  return document


def get_document_category(document):
  # Getting categories of a document
  return DocumentCategory.objects.all().filter(document=document.pk, term=False).order_by('order')


def get_document_items(document, document_categories):
  # Getting items from each categories in a document
  # and combile category and items for output 
  document_items = []
  for category in document_categories:
    document_items += [ category ]
    parent_items = DocumentItem.objects.all().filter(document=document.pk,category=category)
    num = 0
    for item in parent_items:
      num = num + 1
      item.num = num
      document_items += [ item ]  

  # Calculating price of each items
  document.amount = 0
  for item in document_items:
    try:
      item.price = item.qty * item.unit_price
      if not item.waived and not item.category.optional:
        document.amount += item.qty * item.unit_price
    except AttributeError:
      pass

  # Calculating discount and total amount
  if document.discount > 0:
    document.lessamount = document.amount * (document.discount / 100)
    document.amount = document.amount - document.lessamount

  # 
  doc = Document.objects.get(pk=document.pk)
  doc.amount = document.amount
  doc.save()
  return (document, document_items)


def get_document_terms(document):
  # Getting terms of this document
  terms = DocumentCategory.objects.all().filter(document=document.pk, term=True).order_by('order')
  document_terms = []
  for terms_category in terms:
    document_terms += [ terms_category ]
    parent_items = DocumentItem.objects.all().filter(document=document.pk,category=terms_category)
    num = 0
    for item in parent_items:
      num = num + 1
      item.num = num
      document_terms += [ item ]
  return document_terms


def replace_variables(document):
  if document.opening != '':
    if re.search('%currency%', document.opening):
      document.opening = re.sub('%currency%', document.currency, document.opening)
    if re.search('%total_amount%', document.opening):
      document.opening = re.sub('%total_amount%', "%.2f"%document.amount, document.opening)
  if document.after_table != '':
    if re.search('%company_name%', document.after_table):
      document.after_table = re.sub('%company_name%', document.sender.company.name, document.after_table)
  return document


def render_to_pdf(code, template_src, context_dict):
  template = get_template(template_src)
  context = Context(context_dict)
  html  = template.render(context)
  result = StringIO.StringIO()
  filename = "filename=invoicepi-%s.pdf"%code
  if context['attachment']:
    filename = "attachment; %s"%filename

  #pdf = pisa.pisaDocument(StringIO.StringIO(html.encode("ISO-8859-1")), result)
  pdf = pisa.pisaDocument(StringIO.StringIO(html.encode("UTF-8")), result)
  if not pdf.err:
    response = HttpResponse(result.getvalue(), content_type='application/pdf')
    response['Content-Disposition'] = filename
    return response
  return HttpResponse('We had some errors<pre>%s</pre>' % escape(html))


def get_fullname(username):
  user = User.objects.get(username=username)
  if len(user.first_name) > 0:
    fullname = user.first_name
    if len(user.last_name) > 0:
      fullname = "%s %s"%(fullname,user.last_name)
  elif len(user.last_name) > 0:
    fullname = user.last_name
  else:
    fullname = username
  return fullname


def show_document(request, document_id, docprint=False):
  if request.user.is_authenticated(): 
    try:
      document = get_document(document_id)
      if request.user == document.sender.person or request.user == document.receiver.person:
        document_categories = get_document_category(document)
        document, document_items = get_document_items(document, document_categories)
        document = replace_variables(document)
        document_terms = get_document_terms(document)
      else:
        raise Http404("Not permitted.")
    except Document.DoesNotExist:
      raise Http404("Document not exist.")

    # rendering HTML
    if docprint:
      docprint='show_document_print.html'
    else:
      docprint='show_document.html'
    return render(request, docprint, {'document': document, 'document_categories': document_categories, 'document_items': document_items, 'document_terms': document_terms},)
  else:
    raise Http404("Authentication is required.")


def show_document_pdf(request, document_id):
  if request.user.is_authenticated():
    try:
      document = get_document(document_id)
      if request.user == document.sender.person or request.user == document.receiver.person:
        document_categories = get_document_category(document)
        document, document_items = get_document_items(document, document_categories)
        document = replace_variables(document)
        document_terms = get_document_terms(document)
      else:
        raise Http404("Not permitted.")
    except Document.DoesNotExist:
      raise Http404("Document not exist.")

    # rendering PDF
    return render_to_pdf(
      "%s-%s"%(document.document_type.model_name,document.pk),
      'show_document_pdf.html',
      {
        'pagesize':'A4',
        'attachment': False,
        'document': document, 'document_categories': document_categories, 'document_items': document_items, 'document_terms': document_terms
      }
    )
  else:
    raise Http404("Authentication is required.")


def produce_workflow(request, document_id, flow_id):
  term = request.GET.get('term', False)
  if request.user.is_authenticated():
    try: 
      source_doc = Document.objects.get(pk=document_id)
      if request.user != source_doc.sender.person and request.user != source_doc.receiver.person:
        raise Http404("Not permitted.")
    except Document.DoesNotExist:
      raise Http404("Document not exist.")

    try:
      target_type = DocumentFlow.objects.get(pk=flow_id)
      if target_type.document != source_doc.document_type: 
        raise Http404("Invalid Workflow.")
    except DocumentFlow.DoesNotExist:
      raise Http404("Workflow not exist.")

    # Creating new document
    document_category = DocumentCategory.objects.all().filter(document=source_doc)
    source_doc.pk = None
    source_doc.document_type = target_type.product
    source_doc.save()
    for category in document_category:
      if not(category.term == True and term == False):
        old_category = DocumentCategory.objects.get(pk=category.pk)
        category.pk = None
        category.document = source_doc
        category.save()
        for item in DocumentItem.objects.all().filter(document=Document.objects.get(pk=document_id), category=old_category):
          item.pk = None
          item.document = source_doc
          item.category = category
          item.save()
    return HttpResponse(source_doc.pk)
    #return HttpResponseRedirect("http://localhost:

  else:
    raise Http404("Authentication is required.")


def list_document(request, op='bf', op_date=0):
  if request.user.is_authenticated():
    item_list = Document.objects.filter(Q(sender__person=request.user) |
                                        Q(receiver__person=request.user)).order_by('-issue_date')
    total_item = item_list.count()
    start_item = 0
    first_item = 0
    if op == 'bf' and op_date > 0:
      op_date = datetime.fromtimestamp(int(op_date))
      item_list = item_list.filter(issue_date__lt = op_date)
      start_item = total_item - item_list.count()
      first_item = 0
    elif op == 'af' and op_date > 0:
      op_date = datetime.fromtimestamp(int(op_date))
      if item_list.filter(issue_date__gt = op_date).count() > 10:
        item_list = item_list.filter(issue_date__gt = op_date)
        start_item = item_list.count() - 11
        first_item = start_item
      else:
        start_item = 0
        first_item = 0
    item_per_page = 10
    if (total_item - start_item) < 10:
      item_per_page = total_item - start_item
    list_page = { 'first_date': int(item_list[first_item+item_per_page-1].issue_date.strftime("%s")),
                  'last_date': int(item_list[first_item].issue_date.strftime("%s")),
                  'total_item': total_item, 'start_item': start_item, 'item_per_page': item_per_page }
    return render(request, 'list_document.html', { 'list_page': list_page,
                                                   'item_list': item_list[first_item:first_item+item_per_page] },)
  else:
    raise Http404("Authentication is required.")


def logon_form(request):
  if request.user.is_authenticated():
    return redirect('')
  else:
    return render(request, 'logon_form.html')


def list_person(request, op='bf', start_seq=0):
  if request.user.is_authenticated():
    item_list = CompanyPerson.objects.filter(creator=request.user).order_by('company')
    for item in item_list:
      item.personname = get_fullname(item.person)
    item_per_page = 10
    total_item = item_list.count()
    start_item = 0
    if start_seq > 0:
      start_item = int(start_seq)
    print start_item
    if op == 'bf':
      start_item = start_item - item_per_page
      if start_item < 1:
        start_item = 0
    #elif op == 'af':
    #  if start_item + item_per_page >= total_item:
    #    item_per_page = total_item - start_item
    if (total_item - start_item) < 10:
      item_per_page = total_item - start_item
    print "%s %s %s"%(total_item, start_item, item_per_page)
    list_page = { 'total_item': total_item, 'start_item': start_item, 'item_per_page': item_per_page }
    return render(request, 'list_person.html', { 'list_page': list_page,
                                                 'item_list': item_list[start_item:start_item+item_per_page] },)
  else:
    raise Http404("Authentication is required.")


def list_company(request):
  if request.user.is_authenticated():
    company_list = Company.objects.filter(creator=request.user).order_by('-name')
    for company in company_list:
      company.prefix = "Mr/Ms"
      company.personname = "%s %s"%(company.primary_contact.first_name, company.primary_contact.last_name)
    return render(request, 'list_company.html', { 'company_list': company_list })
  else:
    return Http404("Authentication is required.")