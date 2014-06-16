from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.core.context_processors import csrf
from django.core.urlresolvers import reverse
from django.http import  HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.core.paginator import Paginator, EmptyPage, InvalidPage
from django.utils.decorators import method_decorator

from django.views.generic import ListView,CreateView,UpdateView,DeleteView, DetailView
from repocasos import forms
from repocasos.models import  caso


class LoggedInMixin(object):

    @method_decorator(login_required)
    def dispatch(self, *args,**kwargs):
        return super(LoggedInMixin, self).dispatch(*args,**kwargs)


class ListCaseView(ListView):

    model = caso
    template_name = 'caserepo/case_list.html'




class CreateCaseView(LoggedInMixin,CreateView):

    model = caso
    template_name = 'caserepo/edit_case.html'
    form_class = forms.CasoForm

    def get_success_url(self):
#        if 'save_next_case' in self.kwargs:
#            return reverse('case-new')
#        else:
        return reverse('case-list')


    def get_context_data(self, **kwargs):

        context = super(CreateCaseView, self).get_context_data(**kwargs)
        context['action'] = reverse('case-new')

        return context

    def form_valid(self, form):
        object = form.save(commit=False)
        object.usuario_creador_id = self.request.user.id
        object.save()
        return super(CreateCaseView, self).form_valid(form)

class UpdateCaseView(LoggedInMixin,UpdateView):

    model = caso
    template_name = 'caserepo/edit_case.html'
    form_class = forms.CasoForm

    def get_success_url(self):
        return reverse('case-list')

    def get_context_data(self, **kwargs):

        context = super(UpdateCaseView, self).get_context_data(**kwargs)
        context['action'] = reverse('case-edit',
            kwargs={'pk': self.get_object().id})

        return context

class DeleteCaseView(LoggedInMixin,DeleteView):

    model = caso
    template_name = 'caserepo/delete_case.html'

    def get_success_url(self):
        return reverse('case-list')

class CaseView(LoggedInMixin,DetailView):

    model = caso
    template_name = 'caserepo/case.html'
