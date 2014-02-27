from django.core.paginator import EmptyPage, Paginator, InvalidPage
from django.shortcuts import render_to_response, render
from django.template import RequestContext
from efectorescas.forms import SearchForm
from efectorescas.models import concepto

def efectoresVistaImagenes(request):
    img_list = concepto.objects.filter(dominio__exact=1
    #    ,fsn__icontains='esternoclavicular derecha'
    ).order_by('fsn').all()

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
    form = SearchForm()
    examenes = []
    show_results = False
    if 'query' in request.GET and request.GET['query']:
        show_results = True
        query = request.GET['query'].strip()
        if query:
            form = SearchForm({'query': query})
            examenes = concepto.objects.filter(fsn__icontains=query,dominio=1).order_by('fsn')
    variables = RequestContext(request, {   'form': form,
                                            'modelados_imagenes': examenes,
                                            'show_results': show_results,
                                            })
#    if request.GET.has_key('ajax'):
#        return render_to_response('efectoresCAS/vista_imagenes.html', variables)
#    else:
    return  render_to_response('efectoresCAS/search_form.html', variables)
