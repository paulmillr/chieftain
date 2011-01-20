import api.views as api
import json
from django.http import HttpResponse
from django.core import serializers
from board.models import *

def index(request):
    return HttpResponse('pitux')

def sections(request):
    s = Section.objects.all().values()
    return HttpResponse(json.dumps(list(s)))

def categories(request):
    s = SectionGroup.objects.all().values()
    return HttpResponse(json.dumps(list(s)))