# Create your views here.

from django.views.generic import ListView
from gps.assets.models import *
from django.core.exceptions import ImproperlyConfigured, ObjectDoesNotExist
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from datetime import datetime
from pytz import utc, timezone
from django.conf import settings

localtz = timezone(settings.TIME_ZONE)

class AssetView(ListView):
	template_name = 'assets.html'

	@method_decorator(login_required)
	def dispatch(self, *args, **kwargs):
		return super(AssetView, self).dispatch(*args, **kwargs)

	def get_queryset(self):
		if "items" in self.request.POST:
			serials = self.request.POST["items"].split()
			objs = CarSlot.objects.filter(carSerial__in = serials)
		else:
			objs = CarSlot.objects.filter(carSerial__isnull = False).order_by('lane','number')
		return objs

	def get_context_data(self, **kwargs):
		context = super(AssetView, self).get_context_data(**kwargs)
		noDupes = None
		if "items" in self.request.POST:
			context['mTab'] = "Resultados"
			# eliminar duplicados
			noDupes = []
			for i in self.object_list:
				if len(noDupes):
					if noDupes[-1].carSerial == i.carSerial:
						noDupes[-1] = i
					else:
						noDupes.append(i)
				else:
					noDupes.append(i)
		else:
			context['mTab'] = "Inventario"
		context["total"] = len(self.object_list)
		if not context["total"]:
			context['bounds'] = CarLane.objects.all().extent()
		else:
			context['bounds'] = self.object_list.extent()
		if noDupes:
			context['object_list'] = noDupes
			context["total"] = len(context['object_list'])
		return context

	def post(self, request, *args, **kwargs):
		return super(AssetView, self).get(request,*args,**kwargs)
		#post_data = self.request.POST
		#raise ImproperlyConfigured

	def get(self, request, *args, **kwargs):
		return super(AssetView, self).get(request,*args,**kwargs)

class GridlessAssetView(AssetView):
	def get_queryset(self):
		if "items" in self.request.POST:
			serials = self.request.POST["items"].split()
			objs = []
			for i in serials:
				o = GridlessCar.objects.filter(carSerial__icontains = i)
				for r in o:
					objs.append(r)
			realSerials = []
			for i in objs:
				realSerials.append(i.carSerial)
			return GridlessCar.objects.filter(carSerial__in = realSerials,carDate__gte = datetime(2013,4,19,0,0,0,0,localtz)).order_by("carSerial","carDate")
		else:
			#objs = GridlessCar.objects.filter(carSerial__isnull = False).order_by('carSerial')
			objs = GridlessCar.objects.none()
		return objs
