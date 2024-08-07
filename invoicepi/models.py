from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone


class Company(models.Model):
    name = models.CharField(verbose_name='Name', max_length=100)
    description = models.TextField(verbose_name='Description', null=True, blank=True)
    address = models.TextField(verbose_name='Address', null=True, blank=True)
    country = models.CharField(verbose_name='Country', max_length=50, null=True, blank=True)
    phone = models.CharField(verbose_name='Phone', max_length=50, null=True, blank=True)
    fax = models.CharField(verbose_name='Fax', max_length=50, null=True, blank=True)
    email = models.EmailField(verbose_name='Email', null=True, blank=True)
    website = models.URLField(verbose_name='Web Site', null=True, blank=True)
    primary_contact = models.ForeignKey(User, related_name='company_primary_contact', \
                                        verbose_name='Primary Contact', on_delete=models.SET_NULL, \
                                        null=True, blank=True)
    creator = models.ForeignKey(User, related_name='company_creator', \
                                verbose_name='Creator', on_delete=models.SET_NULL, \
                                null=True, blank=True)

    def __str__(self):
        return self.name

    def fullname_primary_contact(self):
        if len(self.primary_contact.first_name) > 0 or len(self.primary_contact.last_name) > 0:
            if len(self.primary_contact.first_name) > 0 and len(self.primary_contact.last_name) > 0:
                return "%s %s"%(self.primary_contact.first_name, self.primary_contact.last_name)
            else:
                return "%s%s"%(self.primary_contact.first_name, self.primary_contact.last_name)
        else:
            return self.primary_contact.username


class CompanyPerson(models.Model):
    PREFIX_CHOICES = (
        ('Mr.', 'Mr.'),
        ('Miss', 'Miss'),
        ('Ms.', 'Ms.'),
        ('Mrs.', 'Mrs.'),
        ('Dr.', 'Dr.'),
    )
    company = models.ForeignKey(Company, verbose_name='Company', on_delete=models.CASCADE)
    person = models.ForeignKey(User, related_name='companyperson_person', \
                               verbose_name='Person', on_delete=models.CASCADE)
    title = models.CharField(verbose_name='Title', max_length=50, null=True, blank=True)
    mobile = models.CharField(verbose_name='Mobile', max_length=50, null=True, blank=True)
    direct = models.CharField(verbose_name='Direct', max_length=50, null=True, blank=True)
    prefix = models.CharField(verbose_name='Prefix', max_length=4, null=True, blank=True, choices=PREFIX_CHOICES)
    creator = models.ForeignKey(User, related_name='companyperson_creator', \
                                verbose_name='Creator', on_delete=models.SET_NULL, \
                                null=True, blank=True)

    def __str__(self):
        if len(self.person.first_name) > 0 or len(self.person.last_name) > 0:
            if len(self.person.first_name) > 0 and len(self.person.last_name) > 0:
                return "%s %s" % (self.person.first_name, self.person.last_name)
            else:
                return "%s%s" % (self.person.first_name, self.person.last_name)
        else:
            return self.person.username


class DocumentType(models.Model):
    full_name = models.CharField(verbose_name='Full Name', max_length=100)
    model_name = models.CharField(verbose_name='Model Name', max_length=50, null=True, blank=True)
    code_syntax = models.CharField(verbose_name='Code Syntax', max_length=50, null=True, blank=True)
    opening = models.TextField(verbose_name='Opening Message', blank=True, null=True)
    after_table = models.TextField(verbose_name='After Table Message', blank=True, null=True)
    closing = models.TextField(verbose_name='Closing Message', blank=True, null=True)
    sender_sign = models.IntegerField(verbose_name='Sender Signature', default=1)
    receiver_sign = models.IntegerField(verbose_name='Receiver Signature', default=2)

    def __str__(self):
        return self.full_name


class DocumentFlow(models.Model):
    document = models.ForeignKey(DocumentType, related_name='master', \
                                 verbose_name='Document', on_delete=models.CASCADE)
    product = models.ForeignKey(DocumentType, related_name='product', \
                                verbose_name='Product', on_delete=models.CASCADE)


class Document(models.Model):
    SEARCH_COLUMNS = ['id', 'document_type__full_name', 'sender__person__username', 'receiver__person__username', \
                      'issue_date', 'subject', 'status']
    CURRENCY_CHOICES = (
        ('HKD', 'HK Dollars (HKD)'),
        ('RMB', 'Chinese Yuan (RMB)'),
        ('TWD', 'New Taiwan Dollars (TWD/NTD)'),
        ('USD', 'US Dollars (USD)'),
    )
    STATUS_CHOICES = (
        ('DRAFT', 'Draft'),
        ('SENT', 'Sent'),
        ('SIGNED', 'Signed'),
        ('RECVED', 'Received'),
    )
    DEFAULT_STATUS = 'DRAFT'
    document_type = models.ForeignKey(DocumentType, verbose_name='Type', \
                                      on_delete=models.SET_NULL, \
                                      null=True, blank=True)
    code = models.CharField(verbose_name='Code', max_length=20, blank=True, null=True)
    sender = models.ForeignKey(CompanyPerson, verbose_name='From',
                               related_name='sender', on_delete=models.SET_NULL, \
                               null=True, blank=True)
    receiver = models.ForeignKey(CompanyPerson, verbose_name='To', \
                                 related_name='receiver', on_delete=models.SET_NULL, \
                                 null=True, blank=True)
    issue_date = models.DateTimeField(verbose_name='Issue Date', default=timezone.now)
    subject = models.CharField(verbose_name='Subject', max_length=100)
    discount = models.FloatField(verbose_name='Discount %', blank=True, null=True)
    amount = models.FloatField(verbose_name='Amount', blank=True, null=True)
    currency = models.CharField(verbose_name='Currency', max_length=3, choices=CURRENCY_CHOICES, default='HKD')
    status = models.CharField(verbose_name='Status', max_length=6, choices=STATUS_CHOICES, default=DEFAULT_STATUS)
    lastmodify_date = models.DateTimeField(verbose_name='Last Modify Date', auto_now=True)
    lastmodify_person = models.ForeignKey(User, verbose_name='Last Modified', \
                                          on_delete=models.SET_NULL, \
                                          null=True, blank=True)
    created_date = models.DateTimeField(verbose_name='Creation Date', auto_now_add=True)

    def __str__(self):
        return "%s %s"%(self.document_type, self.pk)

    def copy_new(self):
        categories = DocumentCategory.objects.filter(document=self)
        new_doc = self
        new_doc.id = None
        new_doc.issue_date = timezone.now()
        new_doc.status = self.DEFAULT_STATUS
        new_doc.save()
        for category in categories:
            items = DocumentItem.objects.filter(category=category)
            new_category = category.copy_new(new_doc)
            for item in items:
                item.copy_new(new_doc, new_category)
        return new_doc


class DocumentCategory(models.Model):
    document = models.ForeignKey(Document, verbose_name='Document', \
                                 on_delete=models.CASCADE)
    order = models.IntegerField(verbose_name='Order', default=0)
    subject = models.CharField(verbose_name='Subject', max_length=100)
    optional = models.BooleanField(verbose_name='Optional ?', default=False)
    term = models.BooleanField(verbose_name='Terms ?', default=False)

    def __str__(self):
        return self.subject

    def copy_new(self, new_doc):
        new_obj = self
        new_obj.id = None
        new_obj.document = new_doc
        new_obj.save()
        return new_obj


class DocumentItem(models.Model):
    document = models.ForeignKey(Document, verbose_name='Document', \
                                 on_delete=models.CASCADE)
    category = models.ForeignKey(DocumentCategory, verbose_name='Category', \
                                 on_delete=models.CASCADE, \
                                 blank=True, null=True)
    parent = models.ForeignKey('self', verbose_name='Parent Item', \
                               on_delete=models.SET_NULL, \
                               blank=True, null=True)
    order = models.IntegerField(verbose_name='Order', default=0)
    subject = models.CharField(verbose_name='Subject', max_length=100)
    description = models.TextField(verbose_name='Description', blank=True, null=True)
    qty = models.IntegerField(verbose_name='Qty', default=1)
    unit_cost = models.FloatField(verbose_name='Unit Cost', default=0)
    unit_price = models.FloatField(verbose_name='Unit Price', default=0)
    waived = models.BooleanField(verbose_name='Waived ?', default=False)
    subject_only = models.BooleanField(verbose_name='Subject Only ?', default=False)

    def __str__(self):
        return self.subject

    def copy_new(self, new_doc, new_category):
        new_obj = self
        new_obj.id = None
        new_obj.document = new_doc
        new_obj.category = new_category
        new_obj.save()
        return new_obj

