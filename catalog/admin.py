from django.contrib import admin
from django.contrib.auth.models import User
from .models import Book, Reservation


class ReservationInline(admin.TabularInline):
    model = Reservation
    extra = 1


@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    inlines = [ReservationInline]


@admin.register(Reservation)
class ReservationAdmin(admin.ModelAdmin):
    list_display = ['member', 'book', 'status']



