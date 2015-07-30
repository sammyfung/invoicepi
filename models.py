from django.db import models
from django.contrib.auth.models import User

class Company(models.Model):
  name = models.CharField(verbose_name='Name', max_length=100)
  description = models.TextField(verbose_name='Description', null=True, blank=True)
  address = models.TextField(verbose_name='Address', null=True, blank=True)
  country = models.CharField(verbose_name='Country', max_length=50, null=True, blank=True)
  phone = models.CharField(verbose_name='Phone', max_length=50, null=True, blank=True)
  fax = models.CharField(verbose_name='Fax', max_length=50, null=True, blank=True)
  email = models.EmailField(verbose_name='EMail', null=True, blank=True)
  website = models.URLField(verbose_name='Web Site', null=True, blank=True)
  primary_contact = models.ForeignKey(User, related_name='company_primary_contact')
  creator = models.ForeignKey(User, related_name='company_creator')

  def __unicode__(self):
    return self.name

class CompanyPerson(models.Model):
  PREFIX_CHOICES = (
    ('Mr.', 'Mr.'),
    ('Miss', 'Miss'),
    ('Ms.', 'Ms.'),
    ('Mrs.', 'Mrs.'),
    ('Dr.', 'Dr.'),
  )
  company = models.ForeignKey(Company)
  person = models.ForeignKey(User, related_name='companyperson_person')
  title = models.CharField(verbose_name='Title', max_length=50, null=True, blank=True)
  mobile = models.CharField(verbose_name='Mobile', max_length=50, null=True, blank=True)
  direct = models.CharField(verbose_name='Direct', max_length=50, null=True, blank=True)
  prefix = models.CharField(verbose_name='Prefix', max_length=4, null=True, blank=True, choices=PREFIX_CHOICES)
  creator = models.ForeignKey(User, related_name='companyperson_creator')

  def __unicode__(self):
    name = '%s %s'%(self.person.first_name, self.person.last_name)
    if name == ' ':
      return self.person.username
    else:
      return name

class DocumentType(models.Model):
  full_name = models.CharField(verbose_name='Full Name', max_length=100)
  model_name = models.CharField(verbose_name='Model Name', max_length=50, null=True, blank=True)
  code_syntax = models.CharField(verbose_name='Code Syntax', max_length=50, null=True, blank=True)
  opening = models.TextField(verbose_name='Opening Message', blank=True, null=True)
  after_table = models.TextField(verbose_name='After Table Message', blank=True, null=True)
  closing = models.TextField(verbose_name='Closing Message', blank=True, null=True)
  sender_sign = models.IntegerField(verbose_name='Sender Signature', default=1)
  receiver_sign = models.IntegerField(verbose_name='Receiver Signature', default=2)

  def __unicode__(self):
    return self.full_name

class DocumentFlow(models.Model):
  document = models.ForeignKey(DocumentType, related_name='master')
  product = models.ForeignKey(DocumentType, related_name='product')

class Document(models.Model):
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
  document_type = models.ForeignKey(DocumentType, verbose_name='Type')
  sender = models.ForeignKey(CompanyPerson, verbose_name='From', related_name='sender')
  receiver = models.ForeignKey(CompanyPerson, verbose_name='To', related_name='receiver')
  issue_date = models.DateTimeField(verbose_name='Issue Date', auto_now_add=True, editable=True)
  subject = models.CharField(verbose_name='Subject', max_length=100)
  discount = models.FloatField(verbose_name='Discount %', blank=True, null=True)
  amount = models.FloatField(verbose_name='Amount', blank=True, null=True)
  currency = models.CharField(verbose_name='Currency', max_length=3, choices=CURRENCY_CHOICES, default='HKD')
  status = models.CharField(verbose_name='Status', max_length=6, choices=STATUS_CHOICES, default='DRAFT')
  lastmodify_date = models.DateTimeField(verbose_name='Last Modfiy Date', auto_now=True)
  lastmodify_person = models.ForeignKey(User)

  def __unicode__(self):
    return "%s %s"%(self.document_type, self.pk)

class DocumentCategory(models.Model):
  document = models.ForeignKey(Document, verbose_name='Document')
  order = models.IntegerField(verbose_name='Order', default=0)
  subject = models.CharField(verbose_name='Subject', max_length=100)
  optional = models.BooleanField(verbose_name='Optional ?', default=False)
  term = models.BooleanField(verbose_name='Terms ?', default=False)

  def __unicode__(self):
    return self.subject

class DocumentItem(models.Model):
  document = models.ForeignKey(Document, verbose_name='Document')
  category = models.ForeignKey(DocumentCategory, verbose_name='Category', blank=True, null=True)
  parent = models.ForeignKey('self', verbose_name='Parent Item', blank=True, null=True)
  order = models.IntegerField(verbose_name='Order', default=0)
  subject = models.CharField(verbose_name='Subject', max_length=100)
  description = models.TextField(verbose_name='Description', blank=True, null=True)
  qty = models.IntegerField(verbose_name='Qty', default=1)
  unit_cost = models.FloatField(verbose_name='Unit Cost', default=0)
  unit_price = models.FloatField(verbose_name='Unit Price', default=0)
  waived = models.BooleanField(verbose_name='Waived ?', default=False)
  subject_only = models.BooleanField(verbose_name='Subject Only ?', default=False)

  def __unicode__(self):
    return self.subject

class Quotation(models.Model):
  document = models.ForeignKey(Document, verbose_name='Document')
  code = models.CharField(verbose_name='Quotation Code', max_length=100)

  def __unicode__(self):
    return self.code

class Invoice(models.Model):
  document = models.ForeignKey(Document, verbose_name='Document')
  code = models.CharField(verbose_name='Invoice Code', max_length=100)

  def __unicode__(self):
    return self.code

class Receipt(models.Model):
  document = models.ForeignKey(Document, verbose_name='Document')
  code = models.CharField(verbose_name='Receipt Code', max_length=100)

  def __unicode__(self):
    return self.code
