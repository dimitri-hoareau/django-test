from django.contrib import admin

from . import models


@admin.register(models.Place)
class PlaceAdmin(admin.ModelAdmin):
    pass

@admin.register(models.BusStop)
class BusStopAdmin(admin.ModelAdmin):
    pass


class BusShiftStopInline(admin.TabularInline):
    model = models.BusShiftStop
    fields = ['bus_stop', 'order', 'scheduled_time']


@admin.register(models.BusShift)
class BusShiftAdmin(admin.ModelAdmin):
    list_display = ['id', 'bus', 'driver', 'departure_time', 'arrival_time', 'duration']
    inlines = [BusShiftStopInline]