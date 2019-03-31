from django.db import models
from django.contrib.auth.models import User as DefaultUser


class User(DefaultUser):
    class Meta:
        proxy = True

    def count_no_of_books_owned(self):
        result = Book.objects.filter(owner=self).exclude(status='N').count()
        return result

    def books_owned_list(self):
        books = Book.objects.filter(owner=self).exclude(status='N')
        return books

    def books_borrowed_list(self):
        books = Book.objects.filter(reservation__member=self, reservation__status='W')
        return books

    def books_given_list(self):
        books = Book.objects.filter(owner=self, status='W')
        return books


class Book(models.Model):
    title = models.CharField(max_length=200)
    author = models.CharField(max_length=200)
    no_of_pages = models.PositiveIntegerField()
    genre = models.CharField(max_length=200)
    description = models.TextField()
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='owned_books')

    BORROW_STATUS = (
        ('N', 'Niedostępna'),        # reservation.status = brak
        ('D', 'Dostępna'),           # reservation.status = brak lub 'Z'
        ('W', 'Wypożyczona'),        # reservation.status = 'W'
    )
    status = models.CharField(max_length=1, choices=BORROW_STATUS, blank=True, default='D')
    members = models.ManyToManyField(User, through='Reservation', blank=True)

    def __str__(self):
        return f'{self.title} ({self.author})'

    def display_status(self):
        result = ''
        for s in self.BORROW_STATUS:
            if s[0] == self.status:
                result = f'{s[1]}'
                break
        return result

    @property
    def is_unavailable(self):
        return self.status == 'N'

    @property
    def is_available(self):
        return self.status == 'D'

    @property
    def is_borrowed(self):
        return self.status == 'W'

    def display_borrower(self):
        member = User.objects.get(reservation__book=self, reservation__status='W')
        return member

    def interested_list(self):
        members = User.objects.filter(reservation__book=self, reservation__status='Z')
        return members

    def count_interested(self):
        count = self.interested_list().count()
        return count


class Reservation(models.Model):
    member = models.ForeignKey(User, on_delete=models.CASCADE)
    book = models.ForeignKey(Book, on_delete=models.CASCADE)

    RESERVATION_STATUS = (
        ('Z', 'Zainteresowanie'),  # book.status = 'D'
        ('W', 'Wypożyczenie'),     # book.status = 'W'
    )
    status = models.CharField(max_length=1, choices=RESERVATION_STATUS, blank=True, default='Z')
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('member', 'book')

    def __str__(self):
        return f'{self.member}: {self.book}'

    @property
    def has_borrow_status(self):
        return self.status == 'W'


class MemberComment(models.Model):
    member = models.ForeignKey(User, on_delete=models.CASCADE)
    book = models.ForeignKey(Book, on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    comment_text = models.TextField()
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created']

    def __str__(self):
        return f'{self.title}'
