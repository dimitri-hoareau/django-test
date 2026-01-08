from django.db import models


class Place(models.Model):
    name = models.CharField("Name of the place", max_length=50)

    longitude = models.DecimalField("Longitude", max_digits=9, decimal_places=6)
    latitude = models.DecimalField("Latitude", max_digits=9, decimal_places=6)

    class Meta:
        # Two places cannot be located at the same coordinates.
        unique_together = (("longitude", "latitude"), )

    def __str__(self):
        return f"Place: {self.name} (id: {self.pk})"


class BusStop(models.Model):
    name = models.CharField("Name of the bus stop", max_length=50)
    place = models.ForeignKey(Place, on_delete=models.CASCADE)

    class Meta:
        unique_together = (("name", "place"),)

    def __str__(self):
        return f"Bus stop: {self.name} (id: {self.pk})"


class BusShift(models.Model):
    """Represents a bus shift (trajet de bus)"""
    bus = models.ForeignKey('fleet.Bus', on_delete=models.CASCADE, related_name='shifts')
    driver = models.ForeignKey('fleet.Driver', on_delete=models.CASCADE, related_name='shifts')
    stops = models.ManyToManyField(BusStop, through='BusShiftStop', related_name='shifts')

    def __str__(self):
        return f"Shift {self.pk}: Bus {self.bus.licence_plate} - Driver {self.driver.user.username}"

    @property
    def departure_time(self):
        """Returns the time of the first stop"""
        first_stop = self.busshiftstop_set.first()
        return first_stop.scheduled_time if first_stop else None

    @property
    def arrival_time(self):
        """Returns the time of the last stop"""
        last_stop = self.busshiftstop_set.last()
        return last_stop.scheduled_time if last_stop else None

    @property
    def duration(self):
        """Returns the total duration of the shift"""
        if self.departure_time and self.arrival_time:
            return self.arrival_time - self.departure_time
        return None


class BusShiftStop(models.Model):
    """Represents a stop during a bus shift with order and time"""
    bus_shift = models.ForeignKey(BusShift, on_delete=models.CASCADE)
    bus_stop = models.ForeignKey(BusStop, on_delete=models.CASCADE)
    order = models.PositiveIntegerField("Stop order in the shift")
    scheduled_time = models.DateTimeField("Scheduled time at this stop")

    class Meta:
        ordering = ['order']
        unique_together = (('bus_shift', 'order'), ('bus_shift', 'bus_stop'))

    def __str__(self):
        return f"Shift {self.bus_shift.pk} - Stop {self.order}: {self.bus_stop.name} at {self.scheduled_time}"