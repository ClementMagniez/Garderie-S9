from django.contrib import admin

from .models import Child, Parent, Schedule

# Register your models here.


class ScheduleInline(admin.TabularInline):
	model=Schedule	
	extra=0


class ChildInline(admin.TabularInline):
	model=Child	
	extra=0

class ChildAdmin(admin.ModelAdmin):
	inlines=[ScheduleInline]
	
class ParentAdmin(admin.ModelAdmin):
	inlines=[ChildInline]
	
admin.site.register(Child, ChildAdmin)
admin.site.register(Parent, ParentAdmin)
