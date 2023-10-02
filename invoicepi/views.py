import re
from io import BytesIO
from django.shortcuts import render, Http404, redirect
from django.core.exceptions import ObjectDoesNotExist
from xhtml2pdf import pisa
from django.template.loader import get_template
from django.template import Context
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.db.models import Q
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from .models import Document, DocumentType, DocumentCategory, DocumentItem, DocumentFlow, CompanyPerson, Company


def get_document(document_id):
    # Getting document info and document code in its type syntax.
    document = Document.objects.get(id=document_id)
    document_type = DocumentType.objects.get(id=document.document_type.id)
    document.opening = document_type.opening
    document.after_table = document_type.after_table
    document.closing = document_type.closing
    document.sender_sign = document_type.sender_sign
    document.receiver_sign = document_type.receiver_sign
    try:
        document.code = document_type.model_class().objects.get(pk=document.pk).code
    except ObjectDoesNotExist:
        document.code = document.pk
    except AttributeError:
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
    if document.discount != None:
        document.lessamount = document.amount * (document.discount / 100)
        document.amount = document.amount - document.lessamount

    # Update total amount in document
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
    html  = template.render(context_dict)
    result = BytesIO()
    filename = "filename=invoicepi-%s.pdf"%code
    if context_dict['attachment']:
        filename = "attachment; %s"%filename
    pdf = pisa.CreatePDF(html, result)
    if not pdf.err:
        response = HttpResponse(result.getvalue(), content_type='application/pdf')
        response['Content-Disposition'] = filename
        return response
    return HttpResponse('We had some errors')


def show_document(request, document_id, format='default'):
    if request.user.is_authenticated:
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

        # rendering HTML / PDF
        if format == 'pdf':
            # rendering PDF
            return render_to_pdf(
                "%s-%s" % (document.document_type.model_name, document.pk),
                'invoicepi/show_document_pdf.html',
                {
                    'pagesize': 'A4',
                    'attachment': False,
                    'document': document, 'document_categories': document_categories,
                    'document_items': document_items, 'document_terms': document_terms
                }
            )
        elif format == 'print':
            templ = 'invoicepi/show_document_print.html'
        else:
            templ = 'invoicepi/show_document.html'
        return render(request, templ, {'document': document, 'document_categories': document_categories, 'document_items': document_items, 'document_terms': document_terms},)
    else:
        raise Http404("Authentication is required.")


def api_show_document(request, document_id):
    if request.user.is_authenticated:
        try:
            document = get_document(document_id)
            json_items = { 'id': document.id, 'data': [] }
            if request.user == document.sender.person or request.user == document.receiver.person:
                document_categories = get_document_category(document)
                document, document_items = get_document_items(document, document_categories)
                document = replace_variables(document)
                document_terms = get_document_terms(document)
                for i in document_categories:
                    json_item = {}
                    json_item['category_id'] = i.id
                    json_item['category_subject'] = i.subject
                    json_item['category_optional'] = i.optional
                    json_item['category_order'] = i.order
                    json_item['item'] = {}
                    for j in document_items:
                        json_subitem = {}
                        json_subitem['item_id'] = j.id
                        #json_subitem['item_parent'] = j.parent
                        json_subitem['item_subject'] = j.subject
                        #json_subitem['item_description'] = j.description
                        #json_subitem['item_qty'] = j.qty
                        #json_subitem['item_unit_cost'] = j.unit_cost
                        #json_subitem['item_unit_price'] = j.unit_price
                        #json_subitem['item_waived'] = j.waived
                        #json_subitem['item_subject_only'] = j.subject_only
                        json_item['item'].append(json_subitem)

                    json_items['data'].append(json_item)
            else:
                raise Http404("Permission is denied.")
        except Document.DoesNotExist:
            raise Http404("Document is not exist.")
        return JsonResponse(json_items)
    else:
        raise Http404("Authentication is required.")


def list_document(request):
    if request.user.is_authenticated:
        return render(request, 'invoicepi/list_document.html')
    else:
        return HttpResponseRedirect('logon')


def api_list_document(request):
    if request.user.is_authenticated:
        draw = request.POST.get('draw', 0)
        start = int(request.POST.get('start', 0))
        length = int(request.POST.get('length', 20))
        search = request.POST.get('search[value]', False)
        orders = ''
        order_column = int(request.POST.get('order[0][column]', 0))
        if request.POST.get('order[0][dir]', 'asc') == 'desc':
            prefix = '-'
        else:
            prefix = ''
        if not all and order_column > 0:
            order_column += 1
        if order_column == 0:
            orders = '%sissue_date' % prefix
        elif order_column == 1:
            orders = '%sdocument_type' % prefix
        elif order_column == 2:
            orders = '%sreceiver' % prefix
        elif order_column == 3:
            orders = '%ssubject' % prefix
        elif order_column == 4:
            orders = '%samount' % prefix
        elif order_column == 5:
            orders = '%scurrency' % prefix
        elif order_column == 6:
            orders = '%sstatus' % prefix
        search_filter = Q()
        if search:
            for i in Document().SEARCH_COLUMNS:
                search_filter |= eval("Q(%s__contains=search)" % i)
        item_list = Document.objects.filter(Q(sender__person=request.user) |
                                            Q(receiver__person=request.user)).order_by(orders)
        total = item_list.count()
        selected_list = item_list.filter(search_filter)
        json_items = { 'draw': draw, 'recordsTotal': total, \
                       'recordsFiltered': selected_list.count(), 'data': [] }
        for i in selected_list[start:start+length]:
            json_item = {}
            json_item['id'] = i.id
            json_item['document_type'] = "%s"%i.document_type
            json_item['sender'] = "%s"%i.sender
            json_item['receiver'] = "%s"%i.receiver
            json_item['issue_date'] = "%d-%02d-%02dT%02d:%02d:%06.3fZ"%\
                                      (i.issue_date.year, i.issue_date.month, i.issue_date.day, i.issue_date.hour, \
                                       i.issue_date.minute, \
                                       i.issue_date.second)
            json_item['subject'] = i.subject
            json_item['amount'] = i.amount
            json_item['currency'] = i.currency
            json_item['status'] = i.status
            json_items['data'].append(json_item)
        return JsonResponse(json_items)
    else:
        raise Http404("Authentication is required.")


def logon_form(request):
    if request.user.is_authenticated:
        return redirect('list_document')
    else:
        email = request.POST.get('inputEmail', '')
        password = request.POST.get('inputPassword', '')
        if email != '' and password != '':
            try:
                username = User.objects.get(email=email).username
            except ObjectDoesNotExist:
                return redirect('logon_form')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
            return redirect('logon_form')
        else:
            return render(request, 'invoicepi/logon_form.html')


def logoff_form(request):
    if request.user.is_authenticated:
        logout(request)
    return redirect('logon_form')


def list_person(request):
    if request.user.is_authenticated:
        return render(request, 'invoicepi/list_person.html')
    else:
        raise Http404("Authentication is required.")


def api_list_person(request):
    if request.user.is_authenticated:
        person_list = CompanyPerson.objects.filter(creator=request.user).order_by('company')
        total = person_list.count()
        json_items = { 'total': total, 'data': []}
        for person in person_list:
            json_item = {}
            json_item['id'] = person.id
            json_item['company'] = "%s"%person.company
            json_item['person'] = "%s"%person
            json_item['email'] = person.person.email
            json_item['title'] = person.title
            json_item['mobile'] = person.mobile
            json_item['direct'] = person.direct
            json_item['prefix'] = person.prefix
            json_item['creator'] = "%s"%person.creator
            json_items['data'].append(json_item)
        return JsonResponse(json_items)
    else:
        raise Http404("Authentication is required.")


def list_company(request):
    if request.user.is_authenticated:
        return render(request, 'invoicepi/list_company.html')
    else:
        return Http404("Authentication is required.")


def copy_document(request, document_id):
    if request.user.is_authenticated:
        doc = Document.objects.get(id=document_id)
        new_doc = doc.copy_new()
        return HttpResponseRedirect('/invoicepi/doc/%s' % new_doc.id)
    else:
        return Http404("Authentication is required.")



def api_list_company(request):
    if request.user.is_authenticated:
        company_list = Company.objects.filter(creator=request.user).order_by('-name')
        total = company_list.count()
        json_items = { 'total': total, 'data': [] }
        for company in company_list:
            json_item = {}
            json_item['id'] = company.id
            json_item['name'] = company.name
            json_item['description'] = company.description
            json_item['address'] = company.address
            json_item['country'] = company.country
            json_item['phone'] = company.phone
            json_item['fax'] = company.fax
            json_item['email'] = company.email
            json_item['website'] = company.website
            json_item['primary_contact'] = "%s" % company.fullname_primary_contact()
            json_item['creator'] = "%s" % company.creator
            json_items['data'].append(json_item)
        return JsonResponse(json_items)
    else:
        return Http404("Authentication is required.")


def api_show_company(request):
    if request.user.is_authenticated:
        # company = Company.objects.filter()
        pass
    else:
        return Http404("Authentication is required.")

def show_company(request, id):
    if request.user.is_authenticated:
        try:
            company = Company.objects.get(id=id)
        except Company.DoesNotExist:
            raise Http404("Company not exist.")

        templ = 'invoicepi/show_company.html'
        return render(request, templ, {'company': company},)
    else:
        raise Http404("Authentication is required.")
    
def show_person(request, id):
    if request.user.is_authenticated:
        try:
            person = CompanyPerson.objects.get(id=id)
        except Company.DoesNotExist:
            raise Http404("Company Person not exist.")

        templ = 'invoicepi/show_person.html'
        return render(request, templ, {'person': person},)
    else:
        raise Http404("Authentication is required.")