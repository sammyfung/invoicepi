from django.contrib import admin
from .models import Company, CompanyPerson, DocumentType, DocumentFlow, Document, \
    DocumentCategory, DocumentItem


class CompanyAdmin(admin.ModelAdmin):
    list_display = ('name', 'phone', 'email', 'website', 'country')


class CompanyPersonAdmin(admin.ModelAdmin):
    list_display = ('full_name', 'company', 'title', 'email', 'mobile')
  
    def full_name(self, person):
        name = '%s %s'%(person.person.first_name, person.person.last_name)
        if name == '':
            return person.person.username
        else:
            return name

    def email(self, person):
        return person.person.email


class DocumentTypeAdmin(admin.ModelAdmin):
    list_display = ('model_name', 'full_name')


class DocumentFlowAdmin(admin.ModelAdmin):
    list_display = ('document', 'product')


class DocumentItemInline(admin.StackedInline):
    model = DocumentItem


class DocumentAdmin(admin.ModelAdmin):
    list_display = ('pk', 'document_type', 'issue_date', 'receiver', 'subject', 'currency', 'amount', 'status')
    inlines = [ DocumentItemInline ]


class DocumentItemAdmin(admin.ModelAdmin):
    list_display = ('document', 'category', 'subject', 'qty', 'unit_price', 'waived')


class DocumentCategoryAdmin(admin.ModelAdmin):
    list_display = ('document', 'order', 'subject', 'optional', 'term')


admin.site.register(Company, CompanyAdmin)
admin.site.register(CompanyPerson, CompanyPersonAdmin)
admin.site.register(DocumentType, DocumentTypeAdmin)
admin.site.register(DocumentFlow, DocumentFlowAdmin)
admin.site.register(Document, DocumentAdmin)
admin.site.register(DocumentCategory, DocumentCategoryAdmin)
admin.site.register(DocumentItem, DocumentItemAdmin)

