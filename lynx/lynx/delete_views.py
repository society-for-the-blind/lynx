import logging

from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.urls import reverse_lazy
from django.views.generic import DeleteView
from .models import (Contact, Phone, IntakeNote, Authorization, ProgressReport, LessonNote, SipNote, Volunteer, SipPlan,
                     Document, Vaccine, Assignment)

logger = logging.getLogger(__name__)


class SipPlanDeleteView(LoginRequiredMixin, DeleteView):
    model = SipPlan

    def get_success_url(self):
        client_id = self.kwargs['client_id']
        return reverse_lazy('lynx:client', kwargs={'pk': client_id})


class SipNoteDeleteView(LoginRequiredMixin, DeleteView):
    model = SipNote

    def get_success_url(self):
        client_id = self.kwargs['client_id']
        return reverse_lazy('lynx:client', kwargs={'pk': client_id})


class IntakeNoteDeleteView(LoginRequiredMixin, DeleteView):
    model = IntakeNote

    def get_success_url(self):
        client_id = self.kwargs['client_id']
        return reverse_lazy('lynx:client', kwargs={'pk': client_id})


class ProgressReportDeleteView(UserPassesTestMixin, DeleteView):
    model = ProgressReport

    def test_func(self):
        return self.request.user.is_superuser

    def get_success_url(self):
        auth_id = self.kwargs['auth_id']
        return reverse_lazy('lynx:authorization_detail', kwargs={'pk': auth_id})


class AuthorizationDeleteView(UserPassesTestMixin, DeleteView):
    model = Authorization

    def test_func(self):
        return self.request.user.is_superuser

    def get_success_url(self):
        client_id = self.kwargs['client_id']
        return reverse_lazy('lynx:client', kwargs={'pk': client_id})


class ContactDeleteView(UserPassesTestMixin, DeleteView):
    model = Contact

    def test_func(self):
        return self.request.user.is_superuser

    def get_success_url(self):
        return reverse_lazy('lynx:index')


class LessonNoteDeleteView(LoginRequiredMixin, DeleteView):
    model = LessonNote

    def get_success_url(self):
        auth_id = self.kwargs['auth_id']
        return reverse_lazy('lynx:authorization_detail', kwargs={'pk': auth_id})


class VolunteerHourDeleteView(LoginRequiredMixin, DeleteView):
    model = Volunteer

    def get_success_url(self):
        return reverse_lazy('lynx:volunteer_list')


class PhoneDeleteView(LoginRequiredMixin, DeleteView):
    model = Phone

    def get_success_url(self):
        client_id = self.kwargs['client_id']
        return reverse_lazy('lynx:client', kwargs={'pk': client_id})


class VaccineDeleteView(LoginRequiredMixin, DeleteView):
    model = Vaccine

    def get_success_url(self):
        client_id = self.kwargs['client_id']
        return reverse_lazy('lynx:client', kwargs={'pk': client_id})


class AssignmentDeleteView(LoginRequiredMixin, DeleteView):
    model = Assignment

    def get_success_url(self):
        client_id = self.kwargs['client_id']
        return reverse_lazy('lynx:client', kwargs={'pk': client_id})


class DocumentDeleteView(LoginRequiredMixin, DeleteView):
    model = Document

    def get_success_url(self):
        client_id = self.kwargs['client_id']
        return reverse_lazy('lynx:client', kwargs={'pk': client_id})
