

import autocomplete_light

from modeladorFarmacos.models import xt_pcce, xt_pc, xt_bioequivalente

class pcceForm(autocomplete_light.ModelForm):
    class Meta:
        model = xt_pcce

class bioeqForm(autocomplete_light.ModelForm):
    class Meta:
        model = xt_bioequivalente



__author__ = 'ehebel'
