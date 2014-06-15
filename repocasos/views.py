from django.core.urlresolvers import reverse
from django.views.generic import ListView,CreateView,UpdateView,DeleteView, DetailView
from repocasos import forms
from repocasos.models import  caso


class ListCaseView(ListView):

    model = caso
    template_name = 'caserepo/case_list.html'




class CreateCaseView(CreateView):

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

class UpdateCaseView(UpdateView):

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

class DeleteCaseView(DeleteView):

    model = caso
    template_name = 'caserepo/delete_case.html'

    def get_success_url(self):
        return reverse('case-list')

class CaseView(DetailView):

    model = caso
    template_name = 'caserepo/case.html'
