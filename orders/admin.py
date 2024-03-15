from django.contrib import admin
from .models import Order

# Register your models here.
#admin.site.register(Order)


class OrderAdmin(admin.ModelAdmin):
    actions = ['upload_orders']

    def upload_orders(self, request, queryset):
        view = UploadOrderFileAdminView.as_view()
        return view(request)

admin.site.register(Order, OrderAdmin)