from django.core.paginator import EmptyPage, Paginator, InvalidPage
from django.shortcuts import render_to_response
from django.template import RequestContext
from efectorescas.models import concepto

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