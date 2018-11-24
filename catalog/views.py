from django.shortcuts import HttpResponseRedirect
from django.urls import reverse, reverse_lazy
from django.db.models import Q
from django.views.generic import TemplateView, ListView, DetailView, RedirectView
from django.views.generic import CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin
from .models import User, Book, Reservation
from .forms import BookCreateForm, SignUpForm, UserEditForm


class SignUp(CreateView):
    form_class = SignUpForm
    success_url = reverse_lazy('login')
    template_name = 'registration/signup.html'

    def form_valid(self, form):
        form.instance.is_active = False
        return super().form_valid(form)


class UserEdit(LoginRequiredMixin, UpdateView):
    model = User
    form_class = UserEditForm
    template_name = 'catalog/user_edit.html'
    success_url = reverse_lazy('index')

    def get(self, request, *args, **kwargs):
        if request.user != User.objects.get(pk=self.kwargs['pk']):
            return HttpResponseRedirect(reverse('member_list'))
        return super(UserEdit, self).get(request, *args, **kwargs)


class AcceptNewMember(LoginRequiredMixin, RedirectView):
    pattern_name = 'index'

    def get(self, request, *args, **kwargs):
        member = User.objects.get(pk=self.kwargs['pk'])

        if request.user.is_superuser:
            member.is_active = True
            member.save()

        return HttpResponseRedirect(reverse('index'))


class DeleteMember(LoginRequiredMixin, RedirectView):
    pattern_name = 'index'

    def get(self, request, *args, **kwargs):
        member = User.objects.get(pk=self.kwargs['pk'])

        if request.user.is_superuser:
            member.delete()

        return HttpResponseRedirect(reverse('index'))


class Index(LoginRequiredMixin, TemplateView):
    template_name = 'catalog/index.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['unverified_members'] = User.objects.filter(is_active=False)
        user = User.objects.get(id=self.request.user.id)
        context['borrowed_books'] = user.books_borrowed_list()
        context['given_books'] = user.books_given_list()
        context['reservations'] = Reservation.objects.filter(book__owner=user, book__status='D', status='Z')
        context['interested_in'] = Reservation.objects.filter(member=user, status='Z')
        return context


class BookList(LoginRequiredMixin, ListView):
    template_name = 'catalog/book_list.html'
    context_object_name = 'books'

    def get_queryset(self):
        query = self.request.GET.get('q', None)
        books = Book.objects.all().exclude(status='N').exclude(owner=self.request.user)

        if query is not None:
            books = books.filter(
                Q(title__icontains=query) |
                Q(author__icontains=query) |
                Q(genre__icontains=query) |
                Q(owner__first_name__icontains=query) |
                Q(owner__last_name__icontains=query) |
                Q(owner__username__icontains=query)
            )

        return books

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        context['my_books_mark'] = False
        return context


class MyBookList(BookList):
    def get_queryset(self):
        return Book.objects.filter(owner=self.request.user)

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        context['my_books_mark'] = True
        return context


class BookDetail(LoginRequiredMixin, DetailView):
    model = Book
    template_name = 'catalog/book_detail.html'
    context_object_name = 'book'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context[''] = ''
        return context


class BookCreate(LoginRequiredMixin, CreateView):
    model = Book
    context_object_name = 'book'
    form_class = BookCreateForm
    template_name = 'catalog/book_create.html'
    success_url = reverse_lazy('my_book_list')

    def form_valid(self, form):
        form.instance.owner = self.request.user
        form.instance.status = 'D'
        return super().form_valid(form)


class BookUpdate(LoginRequiredMixin, UpdateView):
    model = Book
    form_class = BookCreateForm
    template_name = 'catalog/book_create.html'
    success_url = reverse_lazy('my_book_list')

    # wykonuje tylko przekierowanie jeżeli user to nie owner
    def get(self, request, *args, **kwargs):
        book = Book.objects.get(pk=self.kwargs['pk'])
        if request.user != book.owner:
            return HttpResponseRedirect(reverse('my_book_list'))
        return super(BookUpdate, self).get(request, *args, **kwargs)


class BookUpdateStatus(LoginRequiredMixin, RedirectView):
    pattern_name = 'book_update'

    def get(self, request, *args, **kwargs):
        book = Book.objects.get(pk=self.kwargs['pk'])
        if book.is_unavailable:
            book.status = 'D'
        elif book.is_available:
            book.status = 'N'
        book.save()
        return super(BookUpdateStatus, self).get(request, *args, **kwargs)


class BookDelete(LoginRequiredMixin, DeleteView):
    model = Book
    context_object_name = 'book'
    success_url = reverse_lazy('my_book_list')

    # wykonuje tylko przekierowanie jeżeli user to nie owner
    def get(self, request, *args, **kwargs):
        book = Book.objects.get(pk=self.kwargs['pk'])
        if request.user != book.owner:
            return HttpResponseRedirect(reverse('my_book_list'))
        return super(BookDelete, self).get(request, *args, **kwargs)


class MemberList(LoginRequiredMixin, ListView):
    model = User
    template_name = 'catalog/member_list.html'
    context_object_name = 'members'


class MemberDetail(LoginRequiredMixin, DetailView):
    model = User
    template_name = 'catalog/member_detail.html'
    context_object_name = 'member'


class ShowInterest(LoginRequiredMixin, RedirectView):
    pattern_name = 'book_detail'

    def get(self, request, *args, **kwargs):
        book = Book.objects.get(pk=self.kwargs['pk'])
        member = request.user

        if Reservation.objects.filter(book=book, member=member).exists():
            return HttpResponseRedirect(reverse('book_list'))
        else:
            reservation = Reservation(book=book, member=member, status='Z')
            reservation.save()
        return super(ShowInterest, self).get(request, *args, **kwargs)


class WithdrawInterest(LoginRequiredMixin, RedirectView):
    pattern_name = reverse_lazy('book_list')

    def get(self, request, *args, **kwargs):
        book = Book.objects.get(pk=self.kwargs['pk'])
        member = request.user
        reservation = Reservation.objects.get(book=book, member=member)

        if reservation.has_borrow_status:
            return HttpResponseRedirect(reverse('book_list'))
        else:
            reservation.delete()

        return HttpResponseRedirect(reverse('book_list'))


class BorrowBook(LoginRequiredMixin, RedirectView):
    pattern_name = reverse_lazy('book_detail')

    def get(self, request, *args, **kwargs):
        book = Book.objects.get(pk=self.kwargs['book_pk'])
        member = User.objects.get(pk=self.kwargs['member_pk'])
        reservation = Reservation.objects.get(book=book, member=member)

        book.status = 'W'
        book.save()
        reservation.status = 'W'
        reservation.save()

        return HttpResponseRedirect(reverse('book_detail', kwargs={'pk': book.pk}))


class ReturnBook(LoginRequiredMixin, RedirectView):
    pattern_name = reverse_lazy('book_list')

    def get(self, request, *args, **kwargs):
        book = Book.objects.get(pk=self.kwargs['book_pk'])
        member = User.objects.get(pk=self.kwargs['member_pk'])
        reservation = Reservation.objects.get(book=book, member=member)

        book.status = 'D'
        book.save()
        reservation.delete()

        return HttpResponseRedirect(reverse('book_detail', kwargs={'pk': book.pk}))
