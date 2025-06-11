# coding=utf-8
# Create your views here.
from django.template import RequestContext
from django.http import Http404, HttpResponse, HttpResponseRedirect
from django.shortcuts import render_to_response,get_object_or_404, get_list_or_404
from django.db.models import Avg, Max, Min, Q
from django.contrib.auth.decorators import login_required
from django.utils import simplejson
from django.core.urlresolvers import reverse
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import ListView, DetailView, TemplateView
from django.core.exceptions import ImproperlyConfigured, ObjectDoesNotExist, SuspiciousOperation
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.shortcuts import redirect
import django.core.exceptions
from datetime import timedelta,time,datetime,date

from decimal import Decimal

from reportlab.platypus import BaseDocTemplate, PageTemplate, Table, TableStyle, Paragraph, Spacer, Frame, PageBreak
from reportlab.lib.pagesizes import letter,landscape
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.lib.styles import ParagraphStyle

from django import forms
from django.forms import widgets
from models import *
from views import getPeopleCount,TicketView, dayRangeX

import datetime
from django.views.generic.edit import FormView

import reportlab.rl_config
reportlab.rl_config.warnOnMissingFontGlyphs = 0
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.styles import getSampleStyleSheet

from pytz import utc, timezone
from dateutil import parser
from fuzzywuzzy import fuzz
from io import BytesIO as StringIO
import csv

styles = getSampleStyleSheet()
pdfmetrics.registerFont(TTFont('Arial', '/home/django13/Arial/Arial.TTF'))
pdfmetrics.registerFont(TTFont('ArialNarrow', '/home/django13/Arial/ArialNarrow.TTF'))
pdfmetrics.registerFont(TTFont('ArialBlack', '/home/django13/Arial/ArialBlack.TTF'))



class RutaOnlyForm(forms.Form):
	ruta = forms.ChoiceField(label = "Ruta",choices = RUTA_CHOICES)
	submit_text = "Generar"
	def avls(self):
		ruta =self.cleaned_data['ruta']
		return SGAvl.objects.filter(ruta = ruta).order_by("name")

class RutaReportForm(RutaOnlyForm):
	#ruta = forms.ChoiceField(label = "Ruta",choices = RUTA_CHOICES)
	date = forms.DateField(label = "Fecha", widget = widgets.DateInput, initial = datetime.date.today())
	#submit_text = "Generar"
	#def avls(self):
	#	ruta =self.cleaned_data['ruta']
	#	return SGAvl.objects.filter(ruta = ruta).order_by("name")

	def drange(self):
		d = self.cleaned_data['date']
		d = datetime(d.year,d.month,d.day,3)
		return (d,d+timedelta(days=1))

class DateReportForm(forms.Form):
	date = forms.DateField(label = "Fecha", widget = widgets.DateInput, initial = datetime.date.today())
	submit_text = "Generar"

	def drange(self):
		d = self.cleaned_data['date']
		d = datetime(d.year,d.month,d.day,3)
		return (d,d+timedelta(days=1))

class LisReportForm(RutaReportForm):
	week = forms.BooleanField(label = "Semana completa", required=False)
	def wrange(self):
		d = self.cleaned_data['date']
		d = datetime(d.year,d.month,d.day,3)
		return (d,d+timedelta(days=7))

def findChoice(choice):
	for i in RUTA_CHOICES:
		if i[0]==int(choice):
			return i[1]
	raise ValueError
	return None

RUTA_CHOICES2 = (
	(112,"Ruta 6"),
	(115,"Ruta 31"),
	( 89,"Ruta 202"),
	(116,"Ruta 207"),
	(-1,"Ruta 400 S1"),
	(-2,"Ruta 400 S2"),
	(-3,"Ruta 400 S4"),
	)

class RutaReportForm2(RutaReportForm):
	ruta = forms.ChoiceField(label = "Ruta",choices = RUTA_CHOICES2)

from datetime import timedelta,time,datetime,date

class TicketForm(forms.Form):
	chofer = forms.CharField(label = "Nombre del Chofer", required = True, max_length = 40, min_length = 5)
	recibido = forms.IntegerField(label = "Total Liquidado", required = True)
	submit_text = "Imprimir"
	
	def clean_recibido(self):
		data = self.cleaned_data['recibido']
		if data<200:
			raise forms.ValidationError("Capture el total de liquidación correcto.")
		return data

class TicketCapture(FormView):
	template_name = "Ticket2.html"
	form_class = TicketForm
	success_url = ''
	
	@method_decorator(login_required)
	def get(self, request, *args, **kwargs):
		self.request = request
		form_class = self.get_form_class()
		form = self.get_form(form_class)
		return self.render_to_response(self.get_context_data(form=form))

	@method_decorator(login_required)
	def post(self, request, *args, **kwargs):
		self.request = request
		form_class = self.get_form_class()
		form = self.get_form(form_class)
		if form.is_valid():
			return self.form_valid(form)
		else:
			return self.form_invalid(form)

	def get_basegfevents(self,range):
		events = Event.objects.filter(imei = self.dev, date__range = range, type = 'TRACK').order_by("date")
		fences = GeoFence.objects.filter(base = self.dev.ruta)
		gf_evs=[]
		if events:
			for i in fences:
				i.where = i.fence.contains(events[0].position)
			for p in events:
				for i in fences:
					wh = i.fence.contains(p.position)
					if i.where != wh:
						i.where = wh
						if wh:
							gf_evs.append(dict(time = p.date, dir ="in"))
						else:
							gf_evs.append(dict(time = p.date, dir ="out"))
		return gf_evs

	def get_pTimes(self,gf_evs,range):
		times = []
		start = range[0]
		if gf_evs:
			#if self.dev.harness.name == u"Tarifa":
			#	start = range[0]
			#else:
			#	start = gf_evs[0]['time']
			for i in gf_evs[1:]:
				if i['time']-start > timedelta(minutes = 100):
					times.append(dict(type = "run" if i['dir'] == "in" else "stop"
									  ,start = start, end = i['time'],range = (start,i['time'])))
					start = i['time']
				elif i['time']-start < timedelta(minutes = 25) and i['dir']=="out":
					#times.append(dict(type = "stop",start = start, end = i['time']))
					start = i['time']
			if start<range[1]:
				times.append(dict(type = "tail" ,start = start, end = self.range[1],range = (start,range[1])))
		else:
			times.append(dict(type = "head" ,start = self.range[0], end = self.range[1],range = (range[0],range[1])))
			
		return times

	def get_context_data(self, **kwargs):
		try:
			self.imei = int(self.request.GET['imei'])
			self.date = datetime.strptime(self.request.GET['date'],"%Y-%m-%d")
			tm1 = datetime.strptime(self.request.GET['start'],"%H:%M")
			tm2 = datetime.strptime(self.request.GET['stop'],"%H:%M")
			start = timedelta(hours = tm1.hour, minutes = tm1.minute)
			stop = timedelta(hours = tm2.hour, minutes = tm2.minute)
			self.range = dayRangeX(self.date,start,stop)
			range= self.range
		except:
			raise
			raise django.core.exceptions.ValidationError("<h1>Invalid value</h1>")
		self.dev = get_object_or_404(SGAvl,imei = self.imei)
		if not (self.dev.owner == self.request.user or self.request.user.is_staff):
			raise Http404	
		gf_evs = self.get_basegfevents(self.range)
		rounds = self.get_pTimes(gf_evs,self.range)
		self.rounds = rounds

		#queryset
		self.cals = PsiCal.objects.filter(imei = self.dev).order_by("offpsi1")
		self.counters = []
		self.cards = Tarjetas.objects.filter(linea = self.dev.ruta, economico = self.dev.economico, date__range = self.range)
		self.object_list = self.cards
	
		# get sector 4 AVLS
		user = User.objects.get(username = "sector4")
		query = Q(owner = user)
		avls = SGAvl.objects.filter(query)
		
		range = self.range
		rounds = self.rounds

		context = kwargs
		context['Name']= self.dev.name
		context['Date']=datetime.now().strftime("%d/%m/%Y %H:%M")
		context['Economico']=self.dev.economico
		if (self.cards):
			context['Ruta']=self.cards[0].nlinea
			context['Ramal']=self.cards[0].nramal
		else:
			context['Ruta']='N/D'
			context['Ramal']='N/D'
		context['rounds'] = []
		#Totales

		context['Up']=0
		context['Down']=0
		for s in self.cals:
			s.up,s.down = getPeopleCount(s.sensor,self.range[0],self.range[1])
			context['Up']+=s.up
			context['Down']+=s.down

		upn = context['Up'] if context['Up']>context['Down'] else context['Down']
		total = len(self.cards)
		pref = total-len(self.cards.filter(tipo__in = [8,5]))
		normal = len(self.cards.filter(tipo = 5))
		nocard = upn - total - self.cals[1].up
		if nocard <0 : 
			nocard =0
		# Tarifa
		if self.dev.harness.id == 3:
			cash = nocard * 17.0
		elif self.dev.harness.id == 4:
			cash = nocard * 12.0
		else:
			cash = nocard * 12.0
		context['Preferentes']=pref
		context['Ordinarias']=normal
		context['Cash'] = cash
		context['NoCard'] = nocard

		context['Up']=0
		context['Preferentes']=0
		context['Ordinarias']=0
		context['Cash'] = 0
		context['NoCard'] = 0
		
		for dt in self.rounds:
			up=down=0
			for s in self.cals:
				s.t1,s.t2 = getPeopleCount(s.sensor,dt['range'][0],dt['range'][1])
				up+=s.t1
				down+=s.t2

			upn = up if up>down else down
			if self.dev in avls:	###
				upn = up			### Cambio sector 4 prueba
			cards = self.cards.filter(date__range = dt['range'])
			total = len(cards)
			pref = total-len(cards.filter(tipo__in = [8,5]))
			normal = len(cards.filter(tipo = 5))
			nocard = upn - total - self.cals[1].t1
			if nocard <0 : 
				nocard =0
			#tarifa
			if self.dev.harness.id == 3:
				cash = nocard * 17.0
			elif self.dev.harness.id == 4:
				cash = nocard * 12.0
			else:
				cash = nocard * 12.0			
			context['Up']+=up
			context['Preferentes']+=pref
			context['Ordinarias']+=normal
			context['Cash'] += cash
			context['NoCard'] += nocard
			#
			round = dict(
				date = dt['range'][0].strftime("%d/%m/%Y"),
				start = dt['range'][0].strftime("%H:%M"),
				stop = dt['range'][1].strftime("%H:%M"),
				up = up,
				down = down,
				total = total,
				pref = pref,
				normal = normal,
				nocard = nocard,
				cash = cash,
				real = nocard+total

			)
			context['rounds'].append(round)

		context['object_list'] = None
		context['tarjetas_list'] = None
		
		self.context = context
		return context

	def form_valid(self,form):
		chofer = form.cleaned_data['chofer']
		recibido = form.cleaned_data['recibido']
		context = self.get_context_data()

		data = simplejson.dumps(context)
	
		ticket = TicketDetails(imei = self.dev, date = datetime.now(utc), total = context['Cash'],
			chofer = chofer, recibido = recibido, ticket = data )

		ticket.save()
		d=dir(ticket)
		context['folio'] = ticket.id
		
		response = HttpResponse(content_type='application/pdf')
		filename = 'filename="Ticket.%s.%s.pdf"'%(self.dev.name,context['Date'])
		response['Content-Disposition'] = filename
		boxgrid = TableStyle([
			('GRID',(0,0),(-1,-1),0.5,colors.black),			# Whole table
			('BOX',(0,0),(-1,-1),1.5,colors.black),			# Whole table
			('BOX',(0,0),(-1,0),1.5,colors.black),			# First Row
			#('BACKGROUND',(0,0),(-1,0),colors.lightskyblue),		# First Row
			('LINEBELOW',(0,'splitlast'),(-1,'splitlast'),1.5,colors.black), # Last row of a page
			('FONT',(0,0),(-1,-1),"ArialNarrow",10,12),
			('LEFTPADDING',(0,0),(-1,-1),3),
			('RIGHTPADDING',(0,0),(-1,-1),3),
		])
		hdr = '''
<para leading="18"><font name="ArialBlack" size="14" color="magenta">Ticket Liquidación<br/>
Folio: {}</font></para>
'''
		Totales = '<para leading="18"><font name="ArialBlack" size="14" color="magenta">TOTALES</font></para>'
		#folio = "Folio: %d"%(context["folio"])
		fimp = "Fecha Imp: %s"%(context['Date'])
		hdr = hdr.format(context["folio"])
		#raise ValueError
		style=styles["Normal"]
		unidad = "Unidad: %s"%(context['Economico'])
		data_rsp = [[Paragraph(hdr,style)],[context['Name'],context['Ruta']],[fimp,0,0,unidad]]
		boxgrid.add('SPAN',(0,0),(-1,0))
		boxgrid.add('SPAN',(1,1),(3,1))
		boxgrid.add('SPAN',(0,2),(2,2))
		boxgrid.add('SPAN',(3,2),(3,2))
		boxgrid.add('LINEBELOW',(0,2),(-1,2),1.5,colors.black)
		vuelta = 1
		ramal = "Ruta: %s"%(context['Ramal'])
		for r in context['rounds']:
			v = "Vuelta: %d"%(vuelta)
			fr = "Fecha Rep: %s"%(r['date'])
			hif = "HI: %s - HF: %s"%(r['start'],r['stop'])
			sub = "Subidas: %d"%(r['nocard'])
			pref = "Tarj. Pref: %d"%(r['pref'])
			ord = "Tarj. Ord: %d"%(r['normal'])
			pas = "Pasaje: %d"%(r['real'])
			liq = "$%.2f"%(r['cash'])
			data_rsp.append([ramal,0,0,v])
			data_rsp.append([fr,0,hif])
			data_rsp.append([sub,0,pref])
			data_rsp.append([ord,0,pas])
			data_rsp.append(["Liquidación:",liq])
			boxgrid.add('SPAN',(0,vuelta*5-2),(2,vuelta*5-2))
			boxgrid.add('SPAN',(0,vuelta*5-1),(1,vuelta*5-1))
			boxgrid.add('SPAN',(2,vuelta*5-1),(3,vuelta*5-1))
			boxgrid.add('SPAN',(0,vuelta*5),(1,vuelta*5))
			boxgrid.add('SPAN',(2,vuelta*5),(3,vuelta*5))
			boxgrid.add('SPAN',(0,vuelta*5+1),(1,vuelta*5+1))
			boxgrid.add('SPAN',(2,vuelta*5+1),(3,vuelta*5+1))
			boxgrid.add('SPAN',(1,vuelta*5+2),(3,vuelta*5+2))
			boxgrid.add('ALIGN',(1,vuelta*5+2),(3,vuelta*5+2),"RIGHT")
			boxgrid.add('LINEBELOW',(0,vuelta*5+2),(-1,vuelta*5+2),1.5,colors.black)
			vuelta +=1
		data_rsp.append([Paragraph(Totales,style)])
		data_rsp.append(["Subidas","Ordinaria","Preferente","Liquidación"])
		data_rsp.append([context['NoCard'],context['Ordinarias'],context['Preferentes'],"$%.2f"%(context['Cash'])])
		boxgrid.add('SPAN',(0,vuelta*5-2),(-1,vuelta*5-2))
		boxgrid.add('ALIGN',(3,vuelta*5),(-1,vuelta*5),"RIGHT")
		data_rsp.append(["Liquidación Recibida",0,"${:,.2f}".format(recibido)])
		data_rsp.append([chofer])
		boxgrid.add('SPAN',(0,vuelta*5+1),(1,vuelta*5+1))
		boxgrid.add('SPAN',(2,vuelta*5+1),(-1,vuelta*5+1))
		boxgrid.add('ALIGN',(2,vuelta*5+1),(-1,vuelta*5+1),"RIGHT")
		boxgrid.add('SPAN',(0,vuelta*5+2),(-1,vuelta*5+2))

		t = Table(data_rsp,repeatRows=0, colWidths=(0.7*inch, 0.7*inch, 0.71*inch, 0.71*inch))
		t.setStyle(boxgrid)
		doc = BaseDocTemplate(response, pagesize=(3.15*inch,(5+5*vuelta)*19), leftMargin = 0.15*inch, rightMargin = 0.15*inch, topMargin = 0.1*inch, bottomMargin = 0.1*inch)
		frame = Frame(doc.leftMargin, doc.bottomMargin, doc.width, doc.height,id='normal')
		template = PageTemplate(id='page', frames=frame)
		doc.addPageTemplates([template])
		story = [t]
		doc.build(story)
		#raise ValueError
		return response

	
class TicketViewPdf(TicketView):
	def get(self, request, *args, **kwargs):
		try:
			self.imei = int(request.GET['imei'])
			self.date = datetime.strptime(request.GET['date'],"%Y-%m-%d")
			tm1 = datetime.strptime(request.GET['start'],"%H:%M")
			tm2 = datetime.strptime(request.GET['stop'],"%H:%M")
			start = timedelta(hours = tm1.hour, minutes = tm1.minute)
			stop = timedelta(hours = tm2.hour, minutes = tm2.minute)
			self.range = dayRangeX(self.date,start,stop)
			range= self.range
		except:
			raise
			raise django.core.exceptions.ValidationError("<h1>Invalid value</h1>")
		self.dev = get_object_or_404(SGAvl,imei = self.imei)
		if self.dev.ruta == 112 and (request.user == User.objects.get(username = "ruta400") or request.user == User.objects.get(username = "ruta140")):
			pass
		elif self.dev.name == "R202 - 06" and request.user == User.objects.get(username = "grupomg"):
			pass
		elif not (self.dev.owner == request.user or self.request.user.is_staff):
			raise Http404
		gf_evs = self.get_basegfevents(self.range)
		rounds = self.get_pTimes(gf_evs,self.range)
		self.rounds = rounds
	
		self.object_list = self.get_queryset()
		allow_empty = self.get_allow_empty()
		if not allow_empty and len(self.object_list) == 0:
			raise Http404(_(u"Empty list and '%(class_name)s.allow_empty' is False.")% {'class_name': self.__class__.__name__})
		context = self.get_context_data(object_list=self.object_list)
		
		response = HttpResponse(content_type='application/pdf')
		filename = 'filename="Ticket.%s.%s.pdf"'%(self.dev.name,context['Date'])
		response['Content-Disposition'] = filename
		boxgrid = TableStyle([
			('GRID',(0,0),(-1,-1),0.5,colors.black),			# Whole table
			('BOX',(0,0),(-1,-1),1.5,colors.black),			# Whole table
			('BOX',(0,0),(-1,0),1.5,colors.black),			# First Row
			#('BACKGROUND',(0,0),(-1,0),colors.lightskyblue),		# First Row
			('LINEBELOW',(0,'splitlast'),(-1,'splitlast'),1.5,colors.black), # Last row of a page
			('FONT',(0,0),(-1,-1),"ArialNarrow",10,12),
			('LEFTPADDING',(0,0),(-1,-1),3),
			('RIGHTPADDING',(0,0),(-1,-1),3),
		])
		hdr = '''
<para leading="18"><font name="ArialBlack" size="14" color="magenta">Ticket Liquidación<br/>
Folio: {}</font></para>
'''
		Totales = '<para leading="18"><font name="ArialBlack" size="14" color="magenta">TOTALES</font></para>'
		#folio = "Folio: %d"%(context["folio"])
		fimp = "Fecha Imp: %s"%(context['Date'])
		hdr = hdr.format(context["folio"])
		style=styles["Normal"]
		unidad = "Unidad: %s"%(context['Economico'])
		data_rsp = [[Paragraph(hdr,style)],[context['Name'],context['Ruta']],[fimp,0,0,unidad]]
		boxgrid.add('SPAN',(0,0),(-1,0))
		boxgrid.add('SPAN',(1,1),(3,1))
		boxgrid.add('SPAN',(0,2),(2,2))
		boxgrid.add('SPAN',(3,2),(3,2))
		boxgrid.add('LINEBELOW',(0,2),(-1,2),1.5,colors.black)
		vuelta = 1
		ramal = "Ruta: %s"%(context['Ramal'])
		for r in context['rounds']:
			v = "Vuelta: %d"%(vuelta)
			fr = "Fecha Rep: %s"%(r['date'])
			hif = "HI: %s - HF: %s"%(r['start'],r['stop'])
			sub = "Subidas: %d"%(r['nocard'])
			pref = "Tarj. Pref: %d"%(r['pref'])
			ord = "Tarj. Ord: %d"%(r['normal'])
			pas = "Pasaje: %d"%(r['real'])
			liq = "$%.2f"%(r['cash'])
			data_rsp.append([ramal,0,0,v])
			data_rsp.append([fr,0,hif])
			data_rsp.append([sub,0,pref])
			data_rsp.append([ord,0,pas])
			data_rsp.append(["Liquidación:",liq])
			boxgrid.add('SPAN',(0,vuelta*5-2),(2,vuelta*5-2))
			boxgrid.add('SPAN',(0,vuelta*5-1),(1,vuelta*5-1))
			boxgrid.add('SPAN',(2,vuelta*5-1),(3,vuelta*5-1))
			boxgrid.add('SPAN',(0,vuelta*5),(1,vuelta*5))
			boxgrid.add('SPAN',(2,vuelta*5),(3,vuelta*5))
			boxgrid.add('SPAN',(0,vuelta*5+1),(1,vuelta*5+1))
			boxgrid.add('SPAN',(2,vuelta*5+1),(3,vuelta*5+1))
			boxgrid.add('SPAN',(1,vuelta*5+2),(3,vuelta*5+2))
			boxgrid.add('LINEBELOW',(0,vuelta*5+2),(-1,vuelta*5+2),1.5,colors.black)
			vuelta +=1
		data_rsp.append([Paragraph(Totales,style)])
		data_rsp.append(["Subidas","Ordinaria","Preferente","Liquidación"])
		data_rsp.append([context['NoCard'],context['Ordinarias'],context['Preferentes'],"$%.2f"%(context['Cash'])])
		boxgrid.add('SPAN',(0,vuelta*5-2),(-1,vuelta*5-2))

		t = Table(data_rsp,repeatRows=0, colWidths=(0.7*inch, 0.7*inch, 0.71*inch, 0.71*inch))
		t.setStyle(boxgrid)
		doc = BaseDocTemplate(response, pagesize=(3.15*inch,(2+5*vuelta)*19.8), leftMargin = 0.15*inch, rightMargin = 0.15*inch, topMargin = 0.1*inch, bottomMargin = 0.1*inch)
		frame = Frame(doc.leftMargin, doc.bottomMargin, doc.width, doc.height,id='normal')
		template = PageTemplate(id='page', frames=frame)
		doc.addPageTemplates([template])
		story = [t]
		doc.build(story)
		#raise ValueError
		return response

class LisReport(FormView):
	template_name = "rutaForm.html"
	form_class = LisReportForm
	success_url = ''
	boxgrid = TableStyle([
		('GRID',(0,0),(-1,-1),0.5,colors.black),			# Whole table
		('BOX',(0,0),(-1,-1),1.5,colors.black),			# Whole table
		('BOX',(0,0),(-1,0),1.5,colors.black),			# First Row
		('BACKGROUND',(0,0),(-1,0),colors.lightyellow),		# First Row
		('SPAN',(0,0),(-1,0)),							# First Row
		('LINEBELOW',(0,'splitlast'),(-1,'splitlast'),1.5,colors.black), # Last row of a page
		('ALIGN',(0,0),(-1,1),'CENTER'),				# Headers
		('VALIGN',(0,2),(-1,-1),"TOP"),
		#('RIGHTPADDING',(-1,2),(-1,-1),24),
	])

	def form_valid(self,form):
		ruta = form.cleaned_data['ruta']
		dr = form.drange()
		if form.cleaned_data['week']:
			dr = form.wrange()
		dt = form.cleaned_data['date']
		avls = form.avls().filter(imei__gt = 800000000000000)
		
		response = HttpResponse(content_type='application/pdf')
		filename = 'filename="Acelerometro.%s.%04d.%02d.%02d.pdf"'%(findChoice(ruta),dt.year,dt.month,dt.day)
		response['Content-Disposition'] = filename
		data_rsp = [[filename],["Unidad", "Eventos", "Errores", "Duración Prom", "Max"]]
		for i in avls:
			lis = AccelLog.objects.filter(imei = i, date__range = dr)
			if lis:
				count = len(lis)
				peak = lis.aggregate(Max("peak"))["peak__max"]
				avg = lis.aggregate(Avg("duration"))["duration__avg"]
				error = len(lis.filter(peak__gte = 1.0))
				data_rsp.append([i.name,count,error,avg,peak])
		t = Table(data_rsp,repeatRows=2)
		t.setStyle(self.boxgrid)

		doc = BaseDocTemplate(response, pagesize=letter, leftMargin = 0.25*inch, rightMargin = 0.25*inch, topMargin = 0.25*inch, bottomMargin = 0.25*inch)
		frame = Frame(doc.leftMargin, doc.bottomMargin, doc.width, doc.height,id='normal')
		template = PageTemplate(id='page', frames=frame)
		doc.addPageTemplates([template])
		story = [t]
		doc.build(story)
		return response
	
class TicketWeeklyReport(FormView):
	template_name = "rutaForm.html"
	form_class = RutaReportForm2
	success_url = ''

	def form_valid(self,form):
		ruta = form.cleaned_data['ruta']
		dr = form.drange()
		dr = (dr[0],dr[1]+timedelta(days=6))
		dt = form.cleaned_data['date']

		#Selección por sector de la ruta 400
		har = SGHarness.objects.all()[2]
		sector1 = SGAvl.objects.filter(ruta = 96, economico__lt = 29).exclude(economico__in = (27,25)).order_by("name")
		imei1 = []
		sector2 = SGAvl.objects.filter(ruta = 96).exclude(imei__in = sector1).exclude(harness = har).order_by("name")
		sector4 = SGAvl.objects.filter(ruta = 96,harness = har).order_by("name")
		ruta = int(ruta)
		if ruta == -1:
			avls = sector1
			rname = "Ruta 400 S1"
		elif ruta == -2:
			avls = sector2
			rname = "Ruta 400 S2"
		elif ruta == -3:
			avls = sector4
			rname = "Ruta 400 S4"
		else:
			avls = SGAvl.objects.filter(ruta = ruta)
			rname = findChoice(ruta)

		tickets = TicketDetails.objects.filter(date__range = dr, imei__in = avls).order_by('imei__name','date')

		response = HttpResponse(content_type='text/csv')
		filename = 'Tickets.%s.%04d.%02d.%02d'%(rname,dt.year,dt.month,dt.day)
		response['Content-Disposition'] = 'attachment; filename="%s.csv"'%filename
		data_rsp = [[unicode(filename)],["Fecha","Ticket","Unidad","Chofer","Pasaje","Ord", "Pref","Sistema","Liq","Diferencia"]]

		data_tkt = []
		for i in tickets:
			context = simplejson.loads(i.ticket)
			fecha,hora = context["Date"].split()
			vueltas = len(context["rounds"])
			dur = fin = ini =""
			if vueltas:
				ini = context["rounds"][0]["start"]
				fin = context["rounds"][-1]["stop"]
				td = parser.parse(fin)-parser.parse(ini)
				if td <timedelta(0):
					td =+ timedelta(1)
				dur = str(td)[0:-3]
			diff = i.total-i.recibido
			chofer = i.chofer
			if diff>= 1000:
				data_tkt.append([fecha,i.id,i.imei.name,i.chofer.encode("utf8"), context['NoCard'], context['Ordinarias'], context['Preferentes'],
					float(i.total),float(i.recibido),float(diff)])
		data_str = []
		while data_tkt:
			data_str.append(data_tkt[0])
			data_tkt.pop(0)
			i=0
			while i<len(data_tkt):
				if fuzz.token_set_ratio(data_str[-1][3],data_tkt[i][3])>90:
					data_str.append(data_tkt[i])
					data_tkt.pop(i)
					continue
				i+=1
		#file = 	StringIO()
		#csvwriter = csv.writer(file,dialect="excel")
		#csvwriter.writerows(data_rsp)
		#csvwriter.writerows(data_str)
		#response.write(file.getvalue())
		csvwriter = csv.writer(response,dialect="excel")
		csvwriter.writerows(data_rsp)
		csvwriter.writerows(data_str)
		return response

class StatsDailyReport(FormView):
	template_name = "rutaForm.html"
	form_class = RutaReportForm2
	success_url = ''
	boxgrid = TableStyle([
		('GRID',(0,0),(-1,-1),0.5,colors.black),			# Whole table
		('BOX',(0,0),(-1,-1),1.5,colors.black),			# Whole table
		('BOX',(0,0),(-1,0),1.5,colors.black),			# First Row
		('BACKGROUND',(0,0),(-1,0),colors.lightyellow),		# First Row
		('SPAN',(0,0),(-1,0)),							# First Row
		('LINEBELOW',(0,'splitlast'),(-1,'splitlast'),1.5,colors.black), # Last row of a page
		('ALIGN',(0,0),(-1,1),'CENTER'),				# Headers
		('VALIGN',(0,2),(-1,-1),"TOP"),
		("ALIGN",(1,2),(-1,-1),"RIGHT"),
	])

	def form_valid(self,form):
		ruta = form.cleaned_data['ruta']
		dr = form.drange()
		dt = form.cleaned_data['date']

		#Selección por sector de la ruta 400
		har = SGHarness.objects.all()[2]
		sector1 = SGAvl.objects.filter(ruta = 96, economico__lt = 29).exclude(economico__in = (27,25)).order_by("name")
		imei1 = []
		sector2 = SGAvl.objects.filter(ruta = 96).exclude(imei__in = sector1).exclude(harness = har).order_by("name")
		sector4 = SGAvl.objects.filter(ruta = 96,harness = har).order_by("name")
		ruta = int(ruta)
		if ruta == -1:
			avls = sector1
			rname = "Ruta 400 S1"
		elif ruta == -2:
			avls = sector2
			rname = "Ruta 400 S2"
		elif ruta == -3:
			avls = sector4
			rname = "Ruta 400 S4"
		else:
			avls = SGAvl.objects.filter(ruta = ruta)
			rname = findChoice(ruta)
		response = HttpResponse(content_type='application/pdf')
		filename = 'Stats.%s.%04d.%02d.%02d'%(rname,dt.year,dt.month,dt.day)
		response['Content-Disposition'] = 'filename="%s.pdf"'%filename
		data_rsp = [[filename,"","","","",""],["Unidad","Kms","Sub. Del.", "Sub. Tra.", "Baj. Del.","Baj. Tra."]]
		for i in avls:
			st = Stats.objects.filter(name = i.name, date_start__range = dr).order_by('date_start')
			kms = sub_del = sub_tra = baj_del = baj_tra = 0
			for j in st:
				kms += j.distancia
				sub_del += j.sub_del
				sub_tra += j.sub_tra
				baj_del += j.baj_del
				baj_tra += j.baj_tra
			data_rsp.append([i.name,kms,sub_del,sub_tra,baj_del,baj_tra]);
		#raise ValueError
		t = Table(data_rsp,repeatRows=2,rowHeights = None)
		t.setStyle(self.boxgrid)

		doc = BaseDocTemplate(response, pagesize=letter, leftMargin = 0.25*inch, rightMargin = 0.25*inch, topMargin = 0.25*inch, bottomMargin = 0.25*inch)
		frame = Frame(doc.leftMargin, doc.bottomMargin, doc.width, doc.height,id='normal')
		template = PageTemplate(id='page', frames=frame)
		doc.addPageTemplates([template])
		story = [t]
		doc.build(story)
		return response
			
			
class TicketDailyReport(FormView):
	template_name = "rutaForm.html"
	form_class = RutaReportForm2
	success_url = ''
	boxgrid = TableStyle([
		('GRID',(0,0),(-1,-1),0.5,colors.black),			# Whole table
		('BOX',(0,0),(-1,-1),1.5,colors.black),			# Whole table
		('BOX',(0,0),(-1,0),1.5,colors.black),			# First Row
		('BACKGROUND',(0,0),(-1,0),colors.lightyellow),		# First Row
		('SPAN',(0,0),(-1,0)),							# First Row
		('LINEBELOW',(0,'splitlast'),(-1,'splitlast'),1.5,colors.black), # Last row of a page
		('ALIGN',(0,0),(-1,1),'CENTER'),				# Headers
		('VALIGN',(0,2),(-1,-1),"TOP"),
		("ALIGN",(4,2),(-1,-1),"RIGHT"),
		#self.boxgrid.add('SPAN',(0,-1),(7,-1))
		("SPAN",(0,-1),(7,-1))
		#('RIGHTPADDING',(-1,2),(-1,-1),24),
	])

	def form_valid(self,form):
		ruta = form.cleaned_data['ruta']
		dr = form.drange()
		dt = form.cleaned_data['date']
		
		#Selección por sector de la ruta 400
		har = SGHarness.objects.all()[2]
		sector1 = SGAvl.objects.filter(ruta = 96, economico__lt = 29).exclude(economico__in = (27,25)).order_by("name")
		imei1 = []
		sector2 = SGAvl.objects.filter(ruta = 96).exclude(imei__in = sector1).exclude(harness = har).order_by("name")
		sector4 = SGAvl.objects.filter(ruta = 96,harness = har).order_by("name")
		ruta = int(ruta)
		if ruta == -1:
			avls = sector1
			rname = "Ruta 400 S1"
		elif ruta == -2:
			avls = sector2
			rname = "Ruta 400 S2"
		elif ruta == -3:
			avls = sector4
			rname = "Ruta 400 S4"
		else:
			avls = SGAvl.objects.filter(ruta = ruta)
			rname = findChoice(ruta)
		
		tickets = TicketDetails.objects.filter(date__range = dr, imei__in = avls).order_by('imei__name','date')

		response = HttpResponse(content_type='application/pdf')
		filename = 'Tickets.%s.%04d.%02d.%02d'%(rname,dt.year,dt.month,dt.day)
		response['Content-Disposition'] = 'filename="%s.pdf"'%filename
		data_rsp = [[filename],["Ticket","Unidad","Chofer", "Hora", "Vueltas","Inicio","Fin","Duración","Pasaje","Ord", "Pref","Sistema","Liq","Diferencia"]]
		
		row = 2
		totNc = totOrd = totPref = totCash = totLiq = totDif =0
		for i in tickets:
			context = simplejson.loads(i.ticket)
			hora = context["Date"].split()[-1]
			vueltas = len(context["rounds"])
			dur = fin = ini =""
			if vueltas:
				ini = context["rounds"][0]["start"]
				fin = context["rounds"][-1]["stop"]
				td = parser.parse(fin)-parser.parse(ini)
				if td <timedelta(0):
					td =+ timedelta(1)
				dur = str(td)[0:-3]
			diff = i.total-i.recibido
			data_rsp.append([i.id,i.imei.name,i.chofer,hora,vueltas,ini,fin,dur,
				context['NoCard'], context['Ordinarias'], context['Preferentes'],
				"${:,.0f}".format(i.total),"${:,.0f}".format(i.recibido),"${:,.0f}".format(diff)])
			totNc += context['NoCard']
			totOrd += context['Ordinarias']
			totPref += context['Preferentes']
			totCash += i.total
			totLiq += i.recibido
			totDif += diff
			if diff>= 3000:
					self.boxgrid.add('BACKGROUND',(0,row),(-1,row),colors.orangered)
			elif diff>= 2000:
					self.boxgrid.add('BACKGROUND',(0,row),(-1,row),colors.yellow)
			elif diff>= 1000:
					self.boxgrid.add('BACKGROUND',(0,row),(-1,row),colors.lightyellow)
			row +=1
		data_rsp.append(["Total del día","","","","","","","",totNc,totOrd,totPref,"${:,.0f}".format(totCash),"${:,.0f}".format(totLiq),"${:,.0f}".format(totDif)])
		t = Table(data_rsp,repeatRows=2)
		t.setStyle(self.boxgrid)

		doc = BaseDocTemplate(response, pagesize=landscape(letter), leftMargin = 0.25*inch, rightMargin = 0.25*inch, topMargin = 0.25*inch, bottomMargin = 0.25*inch)
		frame = Frame(doc.leftMargin, doc.bottomMargin, doc.width, doc.height,id='normal')
		template = PageTemplate(id='page', frames=frame)
		doc.addPageTemplates([template])
		story = [t]
		doc.build(story)
		#raise ValueError
		return response
	
class TicketTotalsReport(FormView):
	template_name = "rutaForm.html"
	form_class = RutaReportForm
	success_url = ''
	boxgrid = TableStyle([
		('GRID',(0,0),(-1,-1),0.5,colors.black),			# Whole table
		('BOX',(0,0),(-1,-1),1.5,colors.black),			# Whole table
		('BOX',(0,0),(-1,0),1.5,colors.black),			# First Row
		('BACKGROUND',(0,0),(-1,0),colors.lightyellow),		# First Row
		('SPAN',(0,0),(-1,0)),							# First Row
		('LINEBELOW',(0,'splitlast'),(-1,'splitlast'),1.5,colors.black), # Last row of a page
		('ALIGN',(0,0),(-1,1),'CENTER'),				# Headers
		('VALIGN',(0,2),(-1,-1),"TOP"),
		#('RIGHTPADDING',(-1,2),(-1,-1),24),
	])

	def form_valid(self,form):
		ruta = form.cleaned_data['ruta']
		dr = form.drange()
		dt = form.cleaned_data['date']
		tickets = TicketsLog.objects.filter(date__range = dr, ruta = ruta)

		response = HttpResponse(content_type='application/pdf')
		filename = 'filename="Boletos.%s.%04d.%02d.%02d.pdf"'%(findChoice(ruta),dt.year,dt.month,dt.day)
		response['Content-Disposition'] = filename
		data_rsp = [[filename],["Fecha","Unidad", "Vtas", "Ord", "Pref", "Sub","Liq"]]

		# Get column number and headers
		filename = 'Boletos.%s.%04d.%02d.%02d.pdf'%(findChoice(ruta),dt.year,dt.month,dt.day)
		total_ord = total_pref = total_nocard = total_cash =0
		buses = {}
		for i in tickets:
			ticket = simplejson.loads(i.data)
			try:
				if ticket["Name"] in buses:
					for j in ticket['rounds']:
						add = True
						for k in buses[ticket['Name']]['rounds']:
							if j['start'] == k['start']:
								add = False
								break
						if add:
							buses[ticket["Name"]]['rounds'].append(j)
							buses[ticket["Name"]]["Date"] = ticket["Date"]
				else:
					buses[ticket['Name']] = ticket
			except KeyError,ValueError:
				raise 
				pass
		for bus, data in buses.iteritems():
			rounds = len(data['rounds'])
			date = data['Date']
			ord = pref = nocard = liq = 0
			for i in data['rounds']:
				ord += i['normal']
				pref += i['pref']
				nocard += i['nocard']
				liq += i['cash']
			data_rsp.append([date, bus, rounds, ord, pref, nocard, liq ])
			total_ord += ord
			total_pref += pref
			total_nocard += nocard
			total_cash += liq
		data_rsp.append(["Totales", "", "", total_ord, total_pref, total_nocard, total_cash])
		t = Table(data_rsp,repeatRows=2)
		t.setStyle(self.boxgrid)

		doc = BaseDocTemplate(response, pagesize=landscape(letter), leftMargin = 0.25*inch, rightMargin = 0.25*inch, topMargin = 0.25*inch, bottomMargin = 0.25*inch)
		frame = Frame(doc.leftMargin, doc.bottomMargin, doc.width, doc.height,id='normal')
		template = PageTemplate(id='page', frames=frame)
		doc.addPageTemplates([template])
		story = [t]
		doc.build(story)
		#raise ValueError
		return response

class TicketGlobalReport(FormView):
	template_name = "rutaForm.html"
	form_class = DateReportForm
	success_url = ''
	boxgrid = TableStyle([
		('GRID',(0,0),(-1,-1),0.5,colors.black),			# Whole table
		('BOX',(0,0),(-1,-1),1.5,colors.black),			# Whole table
		('BOX',(0,0),(-1,0),1.5,colors.black),			# First Row
		('BACKGROUND',(0,0),(-1,0),colors.lightyellow),		# First Row
		('SPAN',(0,0),(-1,0)),							# First Row
		('LINEBELOW',(0,'splitlast'),(-1,'splitlast'),1.5,colors.black), # Last row of a page
		('ALIGN',(0,0),(-1,1),'CENTER'),				# Headers
		('VALIGN',(0,2),(-1,-1),"TOP"),
		#('RIGHTPADDING',(-1,2),(-1,-1),24),
	])

	def form_valid(self,form):
		dr = form.drange()
		dt = form.cleaned_data['date']

		response = HttpResponse(content_type='application/pdf')
		filename = 'filename="Boletos.%s.%04d.%02d.%02d.pdf"'%("Globales",dt.year,dt.month,dt.day)
		response['Content-Disposition'] = filename

		# Get column number and headers
		filename = 'Boletos.%s.%04d.%02d.%02d.pdf'%("Globales",dt.year,dt.month,dt.day)
		data_rsp = [[filename],["Ruta", "Ord", "Pref", "Sub","Tot. Pasaje","Liq","Camiones","Ord p/c", "Pref p/c", "Liq p/c"]]

		for ruta in RUTA_CHOICES:
			tickets = TicketsLog.objects.filter(date__range = dr, ruta = ruta[0])
			total_ord = total_pref = total_nocard = total_cash =0
			buses = {}
			for i in tickets:
				ticket = simplejson.loads(i.data)
				try:
					if ticket["Name"] in buses:
						for j in ticket['rounds']:
							add = True
							for k in buses[ticket['Name']]['rounds']:
								if j['start'] == k['start']:
									add = False
									break
							if add:
								buses[ticket["Name"]]['rounds'].append(j)
								buses[ticket["Name"]]["Date"] = ticket["Date"]
					else:
						buses[ticket['Name']] = ticket
				except KeyError,ValueError:
					raise 
					pass
			for bus, data in buses.iteritems():
				rounds = len(data['rounds'])
				date = data['Date']
				ord = pref = nocard = liq = 0
				for i in data['rounds']:
					ord += i['normal']
					pref += i['pref']
					nocard += i['nocard']
					liq += i['cash']
				#data_rsp.append([date, bus, rounds, ord, pref, nocard, liq ])
				total_ord += ord
				total_pref += pref
				total_nocard += nocard
				total_cash += liq
			n = len(buses)
			if (n):
				data_rsp.append([findChoice(ruta[0]),total_ord, total_pref, total_nocard,total_ord+total_pref+total_nocard, int(total_cash), n, int(total_ord/n), int(total_pref/n), int(total_cash/n)])
			else:
				data_rsp.append([findChoice(ruta[0]),total_ord, total_pref, total_nocard,total_ord+total_pref+total_nocard, int(total_cash), n, 0, 0, 0])
		t = Table(data_rsp,repeatRows=2)
		t.setStyle(self.boxgrid)

		doc = BaseDocTemplate(response, pagesize=landscape(letter), leftMargin = 0.25*inch, rightMargin = 0.25*inch, topMargin = 0.25*inch, bottomMargin = 0.25*inch)
		frame = Frame(doc.leftMargin, doc.bottomMargin, doc.width, doc.height,id='normal')
		template = PageTemplate(id='page', frames=frame)
		doc.addPageTemplates([template])
		story = [t]
		doc.build(story)
		#raise ValueError
		return response

class TicketRuta400Report(FormView):
	template_name = "rutaForm.html"
	form_class = DateReportForm
	success_url = ''
	boxgrid = TableStyle([
		('GRID',(0,0),(-1,-1),0.5,colors.black),			# Whole table
		('BOX',(0,0),(-1,-1),1.5,colors.black),			# Whole table
		('BOX',(0,0),(-1,0),1.5,colors.black),			# First Row
		('BACKGROUND',(0,0),(-1,0),colors.lightyellow),		# First Row
		('SPAN',(0,0),(-1,0)),							# First Row
		('LINEBELOW',(0,'splitlast'),(-1,'splitlast'),1.5,colors.black), # Last row of a page
		('ALIGN',(0,0),(-1,1),'CENTER'),				# Headers
		('VALIGN',(0,2),(-1,-1),"TOP"),
		#('RIGHTPADDING',(-1,2),(-1,-1),24),
	])

	def calculate(self,buses,data_rsp,name):
		total_ord = total_pref = total_nocard = total_cash =0
		for bus, data in buses.iteritems():
			rounds = len(data['rounds'])
			date = data['Date']
			ord = pref = nocard = liq = 0
			for i in data['rounds']:
				ord += i['normal']
				pref += i['pref']
				nocard += i['nocard']
				liq += i['cash']
			#data_rsp.append([date, bus, rounds, ord, pref, nocard, liq ])
			total_ord += ord
			total_pref += pref
			total_nocard += nocard
			total_cash += liq
		n = len(buses)
		if (n):
			data_rsp.append([name,total_ord, total_pref, total_nocard,total_ord+total_pref+total_nocard, int(total_cash), n, int(total_ord/n), int(total_pref/n), int(total_cash/n)])
		else:
			data_rsp.append([name,total_ord, total_pref, total_nocard,total_ord+total_pref+total_nocard, int(total_cash), n, 0, 0, 0])
		
		
	def form_valid(self,form):
		dr = form.drange()
		dt = form.cleaned_data['date']

		response = HttpResponse(content_type='application/pdf')
		filename = 'filename="Boletos.%s.%04d.%02d.%02d.pdf"'%("Globales",dt.year,dt.month,dt.day)
		response['Content-Disposition'] = filename

		# Get column number and headers
		filename = 'Boletos.%s.%04d.%02d.%02d.pdf'%("Globales",dt.year,dt.month,dt.day)
		data_rsp = [[filename],["Ruta", "Ord", "Pref", "Sub","Tot. Pasaje","Liq","Camiones","Ord p/c", "Pref p/c", "Liq p/c"]]
		tickets = TicketsLog.objects.filter(date__range = dr, ruta__in = [112,96])
		buses1 = {}
		buses2 = {}
		buses3 = {}
		buses4 = {}
		buses = {}
		for i in tickets:
			ticket = simplejson.loads(i.data)
			try:
				if ticket["Name"] in buses:
					for j in ticket['rounds']:
						add = True
						for k in buses[ticket['Name']]['rounds']:
							if j['start'] == k['start']:
								add = False
								break
						if add:
							buses[ticket["Name"]]['rounds'].append(j)
							buses[ticket["Name"]]["Date"] = ticket["Date"]
				else:
					buses[ticket['Name']] = ticket
			except KeyError,ValueError:
				raise 
				pass
		for bus,data in buses.iteritems():
			avl = SGAvl.objects.get(name = bus)
			if avl.ruta == 112: buses3[bus] = data
			elif avl.harness.id == 3: buses4[bus] = data
			elif avl.economico <=25: buses1[bus] = data
			else: buses2[bus] = data
		self.calculate(buses1,data_rsp,"Sector 1")
		self.calculate(buses2,data_rsp,"Sector 2")
		self.calculate(buses3,data_rsp,"Sector 3 (A6)")
		self.calculate(buses4,data_rsp,"Sector 4")

		t = Table(data_rsp,repeatRows=2)
		t.setStyle(self.boxgrid)

		doc = BaseDocTemplate(response, pagesize=landscape(letter), leftMargin = 0.25*inch, rightMargin = 0.25*inch, topMargin = 0.25*inch, bottomMargin = 0.25*inch)
		frame = Frame(doc.leftMargin, doc.bottomMargin, doc.width, doc.height,id='normal')
		template = PageTemplate(id='page', frames=frame)
		doc.addPageTemplates([template])
		story = [t]
		doc.build(story)
		#raise ValueError
		return response

class TicketDifferenceReport(FormView):
	template_name = "rutaForm.html"
	form_class = RutaReportForm
	success_url = ''
	boxgrid = TableStyle([
		('GRID',(0,0),(-1,-1),0.5,colors.black),			# Whole table
		('BOX',(0,0),(-1,-1),1.5,colors.black),			# Whole table
		('BOX',(0,0),(-1,0),1.5,colors.black),			# First Row
		('BACKGROUND',(0,0),(-1,0),colors.lightyellow),		# First Row
		('SPAN',(0,0),(-1,0)),							# First Row
		('LINEBELOW',(0,'splitlast'),(-1,'splitlast'),1.5,colors.black), # Last row of a page
		('ALIGN',(0,0),(-1,1),'CENTER'),				# Headers
		('VALIGN',(0,2),(-1,-1),"TOP"),
		#('RIGHTPADDING',(-1,2),(-1,-1),24),
	])

	def form_valid(self,form):
		ruta = form.cleaned_data['ruta']
		dr = form.drange()
		dt = form.cleaned_data['date']
		
		tickets = TicketsLog.objects.filter(date__range = dr, ruta = ruta)
		response = HttpResponse(content_type='application/pdf')
		filename = 'filename="Boletos.%s.%04d.%02d.%02d.pdf"'%(findChoice(ruta),dt.year,dt.month,dt.day)
		response['Content-Disposition'] = filename

		# Get column number and headers
		filename = 'Boletos.%s.%04d.%02d.%02d.pdf'%(findChoice(ruta),dt.year,dt.month,dt.day)
		data = [[filename],["Fecha","Unidad", "Operador", "Vtas", "Ord", "Pref", "Sub","Liq", "Trans", "Efvo", "Dif"]]
		#data = []
		for i in tickets:
			ticket = simplejson.loads(i.data)
			trans = 0
			pagado =0
			chofer ="N/D"
			if "Driver" in ticket:
				try:
					driver = Driver.objects.get(id = ticket["Driver"])
					trans = int(ticket['Transfers'])
					pagado = int(ticket['Payed'])
					chofer = driver.name +" "+ driver.middle +" "+driver.last
				except KeyError:
					pass
				except Driver.DoesNotExist:
					pass
			else: 
				transbordos = 0;
				pagado =0
				chofer ="N/D"
			try:
				liq = int(ticket['Cash'])
				a = [ticket["Date"], ticket["Name"], chofer, len(ticket["rounds"]), 
					ticket["Ordinarias"], ticket['Preferentes'], ticket['NoCard'], liq, trans, pagado, liq - trans * 12 - pagado]
				if pagado >0:
					data.append(a)
			except KeyError,ValueError:
				raise 
				pass
		t = Table(data,repeatRows=2)
		t.setStyle(self.boxgrid)

		doc = BaseDocTemplate(response, pagesize=landscape(letter), leftMargin = 0.25*inch, rightMargin = 0.25*inch, topMargin = 0.25*inch, bottomMargin = 0.25*inch)
		frame = Frame(doc.leftMargin, doc.bottomMargin, doc.width, doc.height,id='normal')
		template = PageTemplate(id='page', frames=frame)
		doc.addPageTemplates([template])
		story = [t]
		doc.build(story)
		#raise ValueError
		return response

class SensorServiceReport(FormView):
	template_name = "rutaForm.html"
	form_class = RutaReportForm
	success_url = ''

	boxgrid = TableStyle([
		('GRID',(0,0),(-1,-1),0.5,colors.black),			# Whole table
		('BOX',(0,0),(-1,-1),1.5,colors.black),			# Whole table
		('BOX',(0,0),(-1,0),1.5,colors.black),			# First Row
		('BACKGROUND',(0,0),(-1,0),colors.lightyellow),		# First Row
		('SPAN',(0,0),(-1,0)),							# First Row
		('LINEBELOW',(0,'splitlast'),(-1,'splitlast'),1.5,colors.black), # Last row of a page
		('ALIGN',(0,0),(-1,1),'CENTER'),				# Headers
		('VALIGN',(0,2),(-1,-1),"TOP"),
		#('RIGHTPADDING',(-1,2),(-1,-1),24),
	])

	def form_valid(self,form):
		ruta = form.cleaned_data['ruta']
		dt = form.cleaned_data['date']
		avls = form.avls()
		if not self.request.user.is_superuser:
			avls = avls.filter(owner = self.request.user)
		response = HttpResponse(content_type='application/pdf')
		#response['Content-Disposition'] = 'attachment; filename="taskLogReport.pdf"'
		response['Content-Disposition'] = 'filename="SRV.%s.%04d.%02d.%02d.pdf"'%(findChoice(ruta),dt.year,dt.month,dt.day)

		# Get column number and headers
		heads = PsiCal.objects.filter(imei__in=avls).values_list("offpsi1","name")
		heads = heads.distinct("offpsi1").order_by("offpsi1")
		h1 = ['Camion','AVL']
		cw = [None,None]
		for i in heads:
			h1.append(i[1])
			cw.append(inch)
		h1.append("Observaciones")
		cw.append(3*inch)

		data = [['Mantenimiento de '+dt.strftime("%A %d. %B %Y")],h1]
		row = 2
		for i in avls:
			cals = PsiCal.objects.filter(imei = i).order_by("offpsi1")
			adata = [i.name,i.imei]
			#self.boxgrid.add('SPAN',(0,row),(0,row+2))
			#self.boxgrid.add('SPAN',(1,row+1),(1,row+2))
			#dummy = ['','']
			col = 2
			for j in cals:
				sid = j.sensor[2:4]+j.sensor[6:8]
				adata.append(sid)
				#dummy.append('')
				#self.boxgrid.add('SPAN',(col,row+1),(col,row+2))
				col = col+1
			#dummy.append('')
			data.append(adata)
			#data.append(dummy)
			#data.append(dummy)
			#row+=3
			row+=1
		t = Table(data,colWidths = cw,repeatRows=2)
		t.setStyle(self.boxgrid)

		doc = BaseDocTemplate(response, pagesize=letter, leftMargin = 0.25*inch, rightMargin = 0.25*inch, topMargin = 0.25*inch, bottomMargin = 0.25*inch)
		frame = Frame(doc.leftMargin, doc.bottomMargin, doc.width, doc.height,id='normal')
		template = PageTemplate(id='page', frames=frame)
		doc.addPageTemplates([template])
		story = [t]
		doc.build(story)
		#raise ValueError
		return response

class PeopleSummaryReport(FormView):
	template_name = "rutaForm.html"
	form_class = DateReportForm
	success_url = ''

	boxgrid = TableStyle([
		('GRID',(0,0),(-1,-1),1,colors.black),			# Whole table
		('BOX',(0,0),(-1,-1),2,colors.black),			# Whole table
		('BOX',(0,0),(-1,0),2,colors.black),			# First Row
		('BACKGROUND',(0,0),(-1,0),colors.lightgreen),		# First Row
		('SPAN',(0,0),(-1,0)),							# First Row
		('LINEBELOW',(0,'splitlast'),(-1,'splitlast'),2,colors.black), # Last row of a page
		('ALIGN',(0,0),(-1,2),'CENTER'),				# Headers
		('ALIGN',(0,2),(0,-1),'LEFT'),					# ID column
		('ALIGN',(1,2),(-1,-1),'RIGHT'),				# DATA columns
	])

	@method_decorator(csrf_exempt)
	def form_valid(self,form):
		dt = form.cleaned_data['date']
		drange = form.drange()
		counts=[['Dia: '+dt.strftime("%A %d. %B %Y")],["Ruta","Camiones","Subidas","Bajadas","Normal","Preferente"]]
		for i in RUTA_CHOICES:
			buses = SGAvl.objects.filter(ruta = i[0])
			up = down = normal = pref = 0
			for j in buses:
				cals = PsiCal.objects.filter(imei = j).order_by("offpsi1")
				for k in cals:
					j.up,j.down = getPeopleCount(k.sensor,drange[0],drange[1])
					if j.up > 1500:
						j.up = 0
					if j.down > 1500:
						j.down = 0
					if j.up < 0:
						j.up = 0
					if j.down < 0:
						j.down = 0
					up+=j.up
					down+=j.down
				cards = Tarjetas.objects.filter(linea = j.ruta, economico = j.economico, date__range = drange)
				total = len(cards)
				pref += total-len(cards.filter(tipo__in = [8,5]))
				normal += len(cards.filter(tipo__in = [8,5]))
			counts.append([i[1],len(buses),up,down,normal,pref])
		response = HttpResponse(content_type='application/pdf')
		#response['Content-Disposition'] = 'attachment; filename="taskLogReport.pdf"'
		response['Content-Disposition'] = 'filename="%s.%04d.%02d.%02d.pdf"'%("Resumen",dt.year,dt.month,dt.day)
		t = Table(counts,repeatRows=2)
		t.setStyle(self.boxgrid)

		doc = BaseDocTemplate(response, pagesize=letter, leftMargin = 0.25*inch, rightMargin = 0.25*inch, topMargin = 0.25*inch, bottomMargin = 0.25*inch)
		frame = Frame(doc.leftMargin, doc.bottomMargin, doc.width, doc.height,id='normal')
		template = PageTemplate(id='page', frames=frame)
		doc.addPageTemplates([template])
		story = [t]
		doc.build(story)
		return response


class PeopleCountReport(FormView):
	template_name = "rutaForm.html"
	form_class = RutaReportForm
	success_url = ''

	boxgrid = TableStyle([
		('GRID',(0,0),(-1,-1),1,colors.black),			# Whole table
		('BOX',(0,0),(-1,-1),2,colors.black),			# Whole table
		('BOX',(0,0),(-1,0),2,colors.black),			# First Row
		('BACKGROUND',(0,0),(-1,0),colors.lightgreen),		# First Row
		('SPAN',(0,0),(-1,0)),							# First Row
		('LINEBELOW',(0,'splitlast'),(-1,'splitlast'),2,colors.black), # Last row of a page
		('ALIGN',(0,0),(-1,3),'CENTER'),				# Headers
		('ALIGN',(0,3),(0,-1),'LEFT'),					# ID column
		('ALIGN',(1,3),(-1,-1),'RIGHT'),				# DATA columns
		('SPAN',(0,1),(0,2)),							# ID Header
	])

	def form_valid(self,form):
		ruta = form.cleaned_data['ruta']
		dt = form.cleaned_data['date']
		avls = form.avls()
		#if not self.request.user.is_superuser:
		#	avls = avls.filter(owner = self.request.user)
		drange = form.drange()
		response = HttpResponse(content_type='application/pdf')
		#response['Content-Disposition'] = 'attachment; filename="taskLogReport.pdf"'
		response['Content-Disposition'] = 'filename="%s.%04d.%02d.%02d.pdf"'%(findChoice(ruta),dt.year,dt.month,dt.day)

		# Get column number and headers
		heads = PsiCal.objects.filter(imei__in=avls).values_list("offpsi1","name")
		heads = heads.distinct("offpsi1").order_by("offpsi1")
		h1 = ['Camion']
		h2 = [None]
		j=1
		for i in heads:
			h1+= [i[1], None]
			h2+= ["Subidas","Bajadas"]
			self.boxgrid.add('SPAN',(j,1),(j+1,1))
			j+=2
		self.boxgrid.add('SPAN',(j,1),(j+1,1))
		self.boxgrid.add('SPAN',(-1,1),(-1,2))
		self.boxgrid.add('SPAN',(-2,1),(-2,2))
		self.boxgrid.add('SPAN',(-3,1),(-3,2))
		h1+=["Total",None,"Dif",'Tarjetas','Pasaje','%Err']
		h2+=["Subidas","Bajadas",None,None,None,None]
		data = [['Dia: '+dt.strftime("%A %d. %B %Y")],h1,h2]
		for i in avls:
			cals = PsiCal.objects.filter(imei = i).order_by("offpsi1")
			up=down= 0
			adata = [i.name]
			for j in cals:
				j.up,j.down = getPeopleCount(j.sensor,drange[0],drange[1])
				up+=j.up
				down+=j.down
				adata+=[j.up,j.down]
			if max(up,down):
				per = "{0:.2f}%".format(abs(up-down)*100.0/max(up,down))
			else:
				per = "--"
			cards = Tarjetas.objects.filter(linea = i.ruta, economico = i.economico, date__range = drange)
			ncards = len(cards)
			#adata+=[up,down,abs(up-down),ncards,max(up,down)-ncards,per]
			adata+=[up,down,up-down,ncards,max(up,down)-ncards,per]
			data.append(adata)
		t = Table(data,repeatRows=3)
		t.setStyle(self.boxgrid)

		doc = BaseDocTemplate(response, pagesize=letter, leftMargin = 0.25*inch, rightMargin = 0.25*inch, topMargin = 0.25*inch, bottomMargin = 0.25*inch)
		frame = Frame(doc.leftMargin, doc.bottomMargin, doc.width, doc.height,id='normal')
		template = PageTemplate(id='page', frames=frame)
		doc.addPageTemplates([template])
		story = [t]
		doc.build(story)
		#raise ValueError
		return response

class PeopleCountCSV(FormView):
	template_name = "rutaForm.html"
	form_class = RutaReportForm
	success_url = ''

	def form_valid(self,form):
		ruta = form.cleaned_data['ruta']
		dt = form.cleaned_data['date']
		avls = form.avls()
		#if not self.request.user.is_superuser:
		#	avls = avls.filter(owner = self.request.user)
		drange = form.drange()
		response = HttpResponse(content_type='application/text')
		#response['Content-Disposition'] = 'attachment; filename="taskLogReport.pdf"'
		response['Content-Disposition'] = 'filename="%s.%04d.%02d.%02d.txt"'%(findChoice(ruta),dt.year,dt.month,dt.day)

		# Get column number and headers
		heads = PsiCal.objects.filter(imei__in=avls).values_list("offpsi1","name")
		heads = heads.distinct("offpsi1").order_by("offpsi1")
		h1 = ['Camion']
		h2 = [None]
		j=1
		for i in heads:
			h1+= [i[1], None]
			h2+= ["Subidas","Bajadas"]
			j+=2
		h1+=["Total",None,"Dif",'Tarjetas','Pasaje','%Err']
		h2+=["Subidas","Bajadas",None,None,None,None]
		data = [['Dia: '+dt.strftime("%A %d. %B %Y")],h1,h2]
		for i in avls:
			cals = PsiCal.objects.filter(imei = i).order_by("offpsi1")
			up=down= 0
			adata = [i.name]
			for j in cals:
				j.up,j.down = getPeopleCount(j.sensor,drange[0],drange[1])
				up+=j.up
				down+=j.down
				adata+=[j.up,j.down]
			if max(up,down):
				per = "{0:.2f}%".format(abs(up-down)*100.0/max(up,down))
			else:
				per = "--"
			cards = Tarjetas.objects.filter(linea = i.ruta, economico = i.economico, date__range = drange)
			ncards = len(cards)
			#adata+=[up,down,abs(up-down),ncards,max(up,down)-ncards,per]
			adata+=[up,down,up-down,ncards,max(up,down)-ncards,per]
			data.append(adata)
		#raise ValueError
		for i in data:
			for j in i:
				response.write(j)
				response.write(',')
			response.write('\r')
		return response
		
def hms(dt):
	if dt.hour != 0:
		return dt.strftime("%H:%M:%S")
	else:
		return dt.strftime("%M:%S")

def frames2hms(frames):
	return hms(datetime.datetime(2015,1,1)+datetime.timedelta(seconds = frames/60))

class AlarmReport(FormView):
	template_name = "rutaForm.html"
	form_class = RutaReportForm
	success_url = ''

	boxgrid = TableStyle([
		('GRID',(0,0),(-1,-1),1,colors.black),			# Whole table
		('BOX',(0,0),(-1,-1),2,colors.black),			# Whole table
		('BOX',(0,0),(-1,0),2,colors.black),			# First Row
		('BACKGROUND',(0,0),(-1,0),colors.lightgreen),		# First Row
		('SPAN',(0,0),(-1,0)),							# First Row
		('LINEBELOW',(0,'splitlast'),(-1,'splitlast'),2,colors.black), # Last row of a page
		('ALIGN',(0,0),(-1,1),'CENTER'),				# Headers
		('ALIGN',(0,2),(1,-1),'LEFT'),					# ID column
		('ALIGN',(2,3),(-1,-1),'RIGHT'),				# DATA columns
	])

	def getRow(self,cksum):
		q = self.queryset.filter(cksum = cksum).order_by("duration")
		q0 = q[0]
		q1 = q[len(q)-1]
		sensor = PsiCal.objects.filter(sensor = q0.sensor)[0]

		row = [sensor.imei.name,sensor.name,cksum,
			   frames2hms(q1.duration),"{0} - {1}".format(hms(q0.date),hms(q1.date))]
		if q1.duration/60 > 60*5:
			color = colors.lightpink
		elif q1.duration/60 > 60*1:
			color = colors.yellow
		else:
			color = colors.white
		return q0.date.hour*3600+q0.date.minute*60+q0.date.second,row,color

	def form_valid(self,form):
		ruta = form.cleaned_data['ruta']
		dt = form.cleaned_data['date']
		avls = form.avls()
		#if not self.request.user.is_superuser:
		#	avls = avls.filter(owner = self.request.user)
		drange = form.drange()
		response = HttpResponse(content_type='application/pdf')
		#response['Content-Disposition'] = 'attachment; filename="taskLogReport.pdf"'
		response['Content-Disposition'] = 'filename="ALRM%s.%04d.%02d.%02d.pdf"'%(findChoice(ruta),dt.year,dt.month,dt.day)

		imeis = self.imeis = avls.values_list("imei",flat=True)
		sensors = self.sensors = PsiCal.objects.filter(imei__in = self.imeis).values_list("sensor",flat=True)
		qs = self.queryset = AlarmLog.objects.filter(sensor__in = self.sensors,date__gte = drange[0],date__lte = drange[1])
		cksums = self.cksums = self.queryset.values_list("cksum",flat=True).distinct("cksum")

		# Headers and title
		data = [['Alarmas del dia: '+dt.strftime("%A %d. %B %Y")],
			["Unidad","Sensor","ID","Duracion","Hora"]]
		rows = []
		for i in cksums:
			rows.append(self.getRow(i))
		rows = sorted(rows, key=lambda row: row[1][0]+str(row[0]))
		lineno = 1
		for i in rows:
			lineno +=1
			data.append(i[1])
			#if i[2]!= colors.white:
			#	self.boxgrid.add('BACKGROUND',(0,lineno),(-1,lineno),i[2])
		t = Table(data,repeatRows=2)
		t.setStyle(self.boxgrid)
		n = len(data)
		#raise ValueError

		doc = BaseDocTemplate(response, pagesize=letter, leftMargin = 0.25*inch, rightMargin = 0.25*inch, topMargin = 0.25*inch, bottomMargin = 0.25*inch)
		frame = Frame(doc.leftMargin, doc.bottomMargin, doc.width, doc.height,id='normal')
		template = PageTemplate(id='page', frames=frame)
		doc.addPageTemplates([template])
		story = [t]
		doc.build(story)
		return response

class SensorHellReport(FormView):
	template_name = "rutaForm.html"
	form_class = RutaOnlyForm
	success_url = ''

	boxgrid = TableStyle([
		('GRID',(0,0),(-1,-1),0.5,colors.black),			# Whole table
		('BOX',(0,0),(-1,-1),1.5,colors.black),			# Whole table
		('BOX',(0,0),(-1,0),1.5,colors.black),			# First Row
		('BOX',(0,1),(-1,1),1.5,colors.black),			# Second Row
		('BACKGROUND',(0,0),(-1,0),colors.lightyellow),		# First Row
		('SPAN',(0,0),(-1,0)),							# First Row
		('LINEBELOW',(0,'splitlast'),(-1,'splitlast'),1.5,colors.black), # Last row of a page
		('ALIGN',(0,0),(-1,1),'CENTER'),				# Headers
	])

	def form_valid(self,form):
		ruta = form.cleaned_data['ruta']
		avls = form.avls()
		if not self.request.user.is_superuser:
			avls = avls.filter(owner = self.request.user)
		response = HttpResponse(content_type='application/pdf')
		dt = datetime.date.today()
		#response['Content-Disposition'] = 'attachment; filename="taskLogReport.pdf"'
		response['Content-Disposition'] = 'filename="SENSOR.%s.%04d.%02d.%02d.pdf"'%(findChoice(ruta),dt.year,dt.month,dt.day)

		# Get column number and headers
		heads = PsiCal.objects.filter(imei__in=avls).values_list("offpsi1","name")
		heads = heads.distinct("offpsi1").order_by("offpsi1")
		h1 = ['Camion','AVL']
		cw = [None,None]
		for i in heads:
			h1.append(i[1])
			cw.append(inch)
		h1.append("Observaciones")
		cw.append(3*inch)

		data = [['Respuesta de Sensores de '+dt.strftime("%A %d. %B %Y")],["Camión","Sensor","Último reporte"]]
		hell = []
		for i in avls:
			cals = PsiCal.objects.filter(imei = i).order_by("offpsi1")
			for j in cals:
				j.avl = i
				try:
					j.latest = PsiWeightLog.objects.filter(sensor = j.sensor).latest("date")
				except:
					j.latest = None
				hell.append(j)
		for i in hell:
			if i.latest:
				td = datetime.datetime.now() - i.latest.date
				if td.days:
					status ="{0} días".format(td.days)
				else:
					hours,rem = divmod(td.seconds,3600)
					min,secs = divmod(rem,60)
					status = "{0:2}:{1:02}:{2:02}".format(hours,min,secs)
			else:
				status = "NUNCA"
			data.append([i.avl.name,i.name, status])
		t = Table(data,colWidths = cw,repeatRows=2)
		t.setStyle(self.boxgrid)

		doc = BaseDocTemplate(response, pagesize=letter, leftMargin = 0.25*inch, rightMargin = 0.25*inch, topMargin = 0.25*inch, bottomMargin = 0.25*inch)
		frame = Frame(doc.leftMargin, doc.bottomMargin, doc.width, doc.height,id='normal')
		template = PageTemplate(id='page', frames=frame)
		doc.addPageTemplates([template])
		story = [t]
		doc.build(story)
		#raise ValueError
		return response
		