import autocomplete_light
from models import nanda, nandaDominio

# This will generate a PersonAutocomplete class
autocomplete_light.register(nanda,
    # Just like in ModelAdmin.search_fields
    search_fields=['titulo',],
    attrs={
        # This will set the input placeholder attribute:
        'placeholder': 'titulos NANDA ?',

        # This will set the yourlabs.Autocomplete.minimumCharacters
        # options, the naming conversion is handled by jQuery
        'data-widget-minimum-characters': 1,
        },
    # This will set the data-widget-maximum-values attribute on the
    # widget container element, and will be set to
    # yourlabs.Widget.maximumValues (jQuery handles the naming
    # conversion).
#    widget_attrs={'data-widget-maximum-values', 4},
)

autocomplete_light.register(nandaDominio,
    # Just like in ModelAdmin.search_fields
    search_fields=['titulo',],

    attrs={
        # This will set the input placeholder attribute:
        'placeholder': 'titulos Dominio NANDA ?',
        # This will set the yourlabs.Autocomplete.minimumCharacters
        # options, the naming conversion is handled by jQuery
        'data-widget-minimum-characters': 1,
        },
    # This will set the data-widget-maximum-values attribute on the
    # widget container element, and will be set to
    # yourlabs.Widget.maximumValues (jQuery handles the naming
    # conversion).
    #    widget_attrs={'data-widget-maximum-values', 4},
)