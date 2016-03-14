from django.shortcuts import render
from django.http import HttpResponse
from django.template import RequestContext, loader

from console.models import Batch

import pdb

# Create your views here.

def index(request, batch_id):
	#return HttpResponse(batch_id)
	batch = Batch.objects.get(pk=batch_id)
	template = loader.get_template('wechat/index.html')
	context = RequestContext(request, {
		'batch': batch,
	})
	return HttpResponse(template.render(context))
