from django.contrib import admin

# Register your models here.
from .models import Label
from .models import Icon
from .models import Warning
from .models import LabelSize
from .models import Country
from .models import Region
from .models import CompanyLogo
from .models import MadeIn
from .models import Area


class LabelAdmin(admin.ModelAdmin):
    list_display = ('part_no', 'project_name', 'creator', 'created')
    list_filter = ('created', )

class IconAdmin(admin.ModelAdmin):
    list_display = ('part_no', 'name', 'description', 'created')
    list_filter = ('created', )

class WarningAdmin(admin.ModelAdmin):
    list_display = ('part_no', 'name', 'description', 'created')
    list_filter = ('created', )

class AreaAdmin(admin.ModelAdmin):
    list_display = ('part_no', 'name', 'description')
    list_filter = ('part_no', )


admin.site.register(LabelSize)
admin.site.register(Label, LabelAdmin)
admin.site.register(Icon, IconAdmin)
admin.site.register(Warning, WarningAdmin)
admin.site.register(Country)
admin.site.register(Region)
admin.site.register(CompanyLogo)
admin.site.register(MadeIn)
admin.site.register(Area, AreaAdmin)
