from django.core.paginator import EmptyPage, Paginator, InvalidPage
from django.shortcuts import render_to_response, render
from django.template import RequestContext
from efectorescas.forms import SearchForm
from efectorescas.models import concepto

import re

from django.db.models import Q

def normalize_query(query_string,
                    findterms=re.compile(r'"([^"]+)"|(\S+)').findall,
                    normspace=re.compile(r'\s{2,}').sub):
    ''' Splits the query string in invidual keywords, getting rid of unecessary spaces
        and grouping quoted words together.
        Example:

        >>> normalize_query('  some random  words "with   quotes  " and   spaces')
        ['some', 'random', 'words', 'with quotes', 'and', 'spaces']

    '''
    return [normspace(' ', (t[0] or t[1]).strip()) for t in findterms(query_string)]

def get_query(query_string, search_fields):
    ''' Returns a query, that is a combination of Q objects. That combination
        aims to search keywords within a model by testing the given search fields.

    '''
    query = None # Query to search for every search term
    terms = normalize_query(query_string)
    for term in terms:
        or_query = None # Query to search for a given term in each field
        for field_name in search_fields:
            q = Q(**{"%s__icontains" % field_name: term})
            if or_query is None:
                or_query = q
            else:
                or_query = or_query | q
        if query is None:
            query = or_query
        else:
            query = query & or_query
    return query


def efectoresVistaImagenes(request):
    img_list = concepto.objects.filter(dominio__exact=1).order_by('fsn').all()

    paginator = Paginator(img_list, 100)

    try:
        page = int(request.GET.get('page','1'))
    except:
        page = 1

    try:
        imagenes = paginator.page(page)
    except(EmptyPage, InvalidPage):
        imagenes = paginator.page(paginator.num_pages)


    return render_to_response('efectoresCAS/vista_imagenes.html'
        ,{'modelados_imagenes':imagenes},
        context_instance=RequestContext(request))



def search(request):
#    form = SearchForm()
#    examenes = []
#
#    img_list = concepto.objects.filter(dominio__exact=1).order_by('fsn').all()
#    paginator = Paginator(img_list, 100)
#    try:
#        page = int(request.GET.get('page','1'))
#    except:
#        page = 1
#    try:
#        imagenes = paginator.page(page)
#    except(EmptyPage, InvalidPage):
#        imagenes = paginator.page(paginator.num_pages)
#
#    show_results = False
#    if 'query' in request.GET and request.GET['query']:
#        show_results = True
#        query = request.GET['query'].strip()
#        entry_query = get_query(query,['fsn',])
#        if entry_query:
#            form = SearchForm({'query': query})
#            examenes = concepto.objects.filter(entry_query, dominio=1).order_by('fsn')
#
#    variables = RequestContext(request, {   'form': form,
#                                            'modelados_imagenes': examenes,
#                                            'show_results': show_results,
#                                            'todos': imagenes,
#                                            })
#    if 'ajax' in request.GET:
#        return render_to_response('efectoresCAS/search_results.html', variables)
#    else:
#        return  render_to_response('efectoresCAS/search_form.html', variables)
#
    pass
