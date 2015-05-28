# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Company',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=100, verbose_name=b'Name')),
                ('description', models.TextField(null=True, verbose_name=b'Description', blank=True)),
                ('address', models.TextField(null=True, verbose_name=b'Address', blank=True)),
                ('country', models.CharField(max_length=50, null=True, verbose_name=b'Country', blank=True)),
                ('phone', models.CharField(max_length=50, null=True, verbose_name=b'Phone', blank=True)),
                ('fax', models.CharField(max_length=50, null=True, verbose_name=b'Fax', blank=True)),
                ('email', models.EmailField(max_length=254, null=True, verbose_name=b'EMail', blank=True)),
                ('website', models.URLField(null=True, verbose_name=b'Web Site', blank=True)),
                ('primary_contact', models.ForeignKey(to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='CompanyPerson',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('title', models.CharField(max_length=50, null=True, verbose_name=b'Title', blank=True)),
                ('mobile', models.CharField(max_length=50, null=True, verbose_name=b'Mobile', blank=True)),
                ('direct', models.CharField(max_length=50, null=True, verbose_name=b'Direct', blank=True)),
                ('prefix', models.CharField(blank=True, max_length=4, null=True, verbose_name=b'Prefix', choices=[(b'Mr.', b'Mr'), (b'Miss', b'Miss'), (b'Ms.', b'Ms.'), (b'Mrs.', b'Mrs.'), (b'Dr.', b'Dr.')])),
                ('company', models.ForeignKey(to='invoicepi.Company')),
                ('person', models.ForeignKey(to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Document',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('issue_date', models.DateTimeField(auto_now_add=True, verbose_name=b'Issue Date')),
                ('subject', models.CharField(max_length=100, verbose_name=b'Subject')),
                ('discount', models.FloatField(null=True, verbose_name=b'Discount %', blank=True)),
                ('amount', models.FloatField(null=True, verbose_name=b'Amount', blank=True)),
                ('currency', models.CharField(default=b'HKD', max_length=3, verbose_name=b'Currency', choices=[(b'HKD', b'HK Dollars (HKD)'), (b'RMB', b'Chinese Yuan (RMB)'), (b'TWD', b'New Taiwan Dollars (TWD/NTD)'), (b'USD', b'US Dollars (USD)')])),
                ('status', models.CharField(default=b'DRAFT', max_length=6, verbose_name=b'Status', choices=[(b'DRAFT', b'Draft'), (b'SENT', b'Sent'), (b'SIGNED', b'Signed'), (b'RECVED', b'Received')])),
                ('lastmodify_date', models.DateTimeField(auto_now=True, verbose_name=b'Last Modfiy Date')),
            ],
        ),
        migrations.CreateModel(
            name='DocumentCategory',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('order', models.IntegerField(default=0, verbose_name=b'Order')),
                ('subject', models.CharField(max_length=100, verbose_name=b'Subject')),
                ('optional', models.BooleanField(default=False, verbose_name=b'Optional ?')),
                ('term', models.BooleanField(default=False, verbose_name=b'Terms ?')),
                ('document', models.ForeignKey(verbose_name=b'Document', to='invoicepi.Document')),
            ],
        ),
        migrations.CreateModel(
            name='DocumentFlow',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
            ],
        ),
        migrations.CreateModel(
            name='DocumentItem',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('order', models.IntegerField(default=0, verbose_name=b'Order')),
                ('subject', models.CharField(max_length=100, verbose_name=b'Subject')),
                ('description', models.TextField(null=True, verbose_name=b'Description', blank=True)),
                ('qty', models.IntegerField(default=1, verbose_name=b'Qty')),
                ('unit_cost', models.FloatField(default=0, verbose_name=b'Unit Cost')),
                ('unit_price', models.FloatField(default=0, verbose_name=b'Unit Price')),
                ('waived', models.BooleanField(default=False, verbose_name=b'Waived ?')),
                ('subject_only', models.BooleanField(default=False, verbose_name=b'Subject Only ?')),
                ('category', models.ForeignKey(verbose_name=b'Category', blank=True, to='invoicepi.DocumentCategory', null=True)),
                ('document', models.ForeignKey(verbose_name=b'Document', to='invoicepi.Document')),
                ('parent', models.ForeignKey(verbose_name=b'Parent Item', blank=True, to='invoicepi.DocumentItem', null=True)),
            ],
        ),
        migrations.CreateModel(
            name='DocumentType',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('full_name', models.CharField(max_length=100, verbose_name=b'Full Name')),
                ('model_name', models.CharField(max_length=50, null=True, verbose_name=b'Model Name', blank=True)),
                ('code_syntax', models.CharField(max_length=50, null=True, verbose_name=b'Code Syntax', blank=True)),
                ('opening', models.TextField(null=True, verbose_name=b'Opening Message', blank=True)),
                ('after_table', models.TextField(null=True, verbose_name=b'After Table Message', blank=True)),
                ('closing', models.TextField(null=True, verbose_name=b'Closing Message', blank=True)),
                ('sender_sign', models.IntegerField(default=1, verbose_name=b'Sender Signature')),
                ('receiver_sign', models.IntegerField(default=2, verbose_name=b'Receiver Signature')),
            ],
        ),
        migrations.CreateModel(
            name='Invoice',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('code', models.CharField(max_length=100, verbose_name=b'Invoice Code')),
                ('document', models.ForeignKey(verbose_name=b'Document', to='invoicepi.Document')),
            ],
        ),
        migrations.CreateModel(
            name='Quotation',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('code', models.CharField(max_length=100, verbose_name=b'Quotation Code')),
                ('document', models.ForeignKey(verbose_name=b'Document', to='invoicepi.Document')),
            ],
        ),
        migrations.CreateModel(
            name='Receipt',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('code', models.CharField(max_length=100, verbose_name=b'Receipt Code')),
                ('document', models.ForeignKey(verbose_name=b'Document', to='invoicepi.Document')),
            ],
        ),
        migrations.AddField(
            model_name='documentflow',
            name='document',
            field=models.ForeignKey(related_name='master', to='invoicepi.DocumentType'),
        ),
        migrations.AddField(
            model_name='documentflow',
            name='product',
            field=models.ForeignKey(related_name='product', to='invoicepi.DocumentType'),
        ),
        migrations.AddField(
            model_name='document',
            name='document_type',
            field=models.ForeignKey(verbose_name=b'Type', to='invoicepi.DocumentType'),
        ),
        migrations.AddField(
            model_name='document',
            name='lastmodify_person',
            field=models.ForeignKey(to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='document',
            name='receiver',
            field=models.ForeignKey(related_name='receiver', verbose_name=b'To', to='invoicepi.CompanyPerson'),
        ),
        migrations.AddField(
            model_name='document',
            name='sender',
            field=models.ForeignKey(related_name='sender', verbose_name=b'From', to='invoicepi.CompanyPerson'),
        ),
    ]
