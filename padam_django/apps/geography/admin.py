from django.contrib import admin
from django.core.exceptions import ValidationError
from django import forms

from . import models


@admin.register(models.Place)
class PlaceAdmin(admin.ModelAdmin):
    pass

@admin.register(models.BusStop)
class BusStopAdmin(admin.ModelAdmin):
    list_display = ['name', 'place']


class BusShiftStopInlineFormSet(forms.BaseInlineFormSet):
    def clean(self):
        super().clean()

        stops = [form.cleaned_data for form in self.forms if form.cleaned_data and not form.cleaned_data.get('DELETE', False)]
        if not stops:
            return

        times = [stop['scheduled_time'] for stop in stops if 'scheduled_time' in stop]
        if len(times) < 2:
            return

        departure = min(times)
        arrival = max(times)
        bus = self.instance.bus
        driver = self.instance.driver

        bus_shifts = models.BusShift.objects.filter(bus=bus)
        if self.instance.pk:
            bus_shifts = bus_shifts.exclude(pk=self.instance.pk)

        for shift in bus_shifts:
            if shift.departure_time and shift.arrival_time:
                if departure <= shift.arrival_time and arrival >= shift.departure_time:
                    raise ValidationError(f"Bus {bus.licence_plate} déjà utilisé")

        driver_shifts = models.BusShift.objects.filter(driver=driver)
        if self.instance.pk:
            driver_shifts = driver_shifts.exclude(pk=self.instance.pk)

        for shift in driver_shifts:
            if shift.departure_time and shift.arrival_time:
                if departure <= shift.arrival_time and arrival >= shift.departure_time:
                    raise ValidationError(f"Chauffeur {driver.user.username} déjà occupé")


class BusShiftStopInline(admin.TabularInline):
    model = models.BusShiftStop
    formset = BusShiftStopInlineFormSet
    fields = ['bus_stop', 'order', 'scheduled_time']


@admin.register(models.BusShift)
class BusShiftAdmin(admin.ModelAdmin):
    list_display = ['id', 'bus', 'driver', 'departure_time', 'arrival_time', 'duration']
    inlines = [BusShiftStopInline]