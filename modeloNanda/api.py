import json
from django.core.serializers.json import DjangoJSONEncoder
from tastypie.serializers import Serializer
from django.contrib.auth.models import User
from tastypie import fields
from tastypie.resources import ModelResource

from modeloNanda.models import nanda


class PrettyJSONSerializer(Serializer):
    json_indent = 2

    def to_json(self, data, options=None):
        options = options or {}
        data = self.to_simple(data, options)
        return json.dumps(data, cls=DjangoJSONEncoder,
            sort_keys=True, ensure_ascii=False, indent=self.json_indent)


class UserResource(ModelResource):
    class Meta:
        queryset = User.objects.all()
        resource_name = 'usrmodificacion'
        fields = ['username', 'first_name', 'last_name', 'last_login']
        allowed_methods = ['get']
        serializer = PrettyJSONSerializer()



class EntryResource(ModelResource):
    user = fields.ForeignKey(UserResource, 'usrmodificacion')

    class Meta:
        queryset = nanda.objects.all()
        resource_name = 'entry'
        serializer = PrettyJSONSerializer()



__author__ = 'ehebel'
