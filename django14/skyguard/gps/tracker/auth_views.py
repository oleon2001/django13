#!/usr/bin/python
# -*- coding: utf-8 -*-

import urlparse
import gpolyencode
from datetime import datetime,timedelta
from datetime import date as dtdate
from pytz import utc, timezone

from django.conf import settings
from django.http import HttpResponse,HttpResponseRedirect,HttpResponseBadRequest
from django.shortcuts import render_to_response,get_object_or_404, get_list_or_404
from django.template import RequestContext
from django.utils.http import urlquote
from django.views.decorators.cache import never_cache
from django.views.decorators.csrf import csrf_protect,csrf_exempt

# Avoid shadowing the login() and logout() views below.
from django.contrib.auth import REDIRECT_FIELD_NAME, login as auth_login
#from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.sites.models import get_current_site

from django import forms
from django.core.urlresolvers import reverse
from django.utils import simplejson

from gps.tracker.models import *

from geopy.point import Point as gPoint
from geopy.distance import distance as geoLen

MIN_EXTENT = 1.0
def minExtents(extents):
	sw = gPoint(extents[1],extents[0])
	ne = gPoint(extents[3],extents[2])
	center = gPoint((extents[1]+extents[3])/2,(extents[0]+extents[2])/2)
	if geoLen(ne,sw).km < MIN_EXTENT:
		d = geoLen(MIN_EXTENT/2)
		ne = d.destination(center,45)
		sw = d.destination(center,225)
	return (sw.longitude, sw.latitude, ne.longitude, ne.latitude)

@csrf_exempt
@never_cache
def login(request, template_name='login.html',
          redirect_field_name=REDIRECT_FIELD_NAME,
          authentication_form=AuthenticationForm,
          current_app=None, extra_context=None):
    """
    Displays the login form and handles the login action.
    """
    redirect_to = request.REQUEST.get(redirect_field_name, '')

    if request.method == "POST":
        form = authentication_form(data=request.POST)
        if form.is_valid():
            netloc = urlparse.urlparse(redirect_to)[1]

            # Use default setting if redirect_to is empty
            if not redirect_to:
                redirect_to = settings.LOGIN_REDIRECT_URL

            # Security check -- don't allow redirection to a different
            # host.
            elif netloc and netloc != request.get_host():
                redirect_to = settings.LOGIN_REDIRECT_URL

            # Okay, security checks complete. Log the user in.
            auth_login(request, form.get_user())

            if request.session.test_cookie_worked():
                request.session.delete_test_cookie()

            return HttpResponseRedirect(redirect_to)
    else:
        form = authentication_form(request)

    request.session.set_test_cookie()

    current_site = get_current_site(request)

    context = {
        'form': form,
        redirect_field_name: redirect_to,
        'site': current_site,
        'site_name': current_site.name,
    }
    context.update(extra_context or {})
    return render_to_response(template_name, context,
                              context_instance=RequestContext(request, current_app=current_app))


class KmlForm(forms.Form):
	imei = forms.IntegerField(label = "Imei")
	day = forms.DateField(label = "Fecha")#,input_formats="%Y-%m-%d")
	start = forms.TimeField(label = "Inicio")#, input_formats ="%H:%M")
	stop = forms.TimeField(label = "Final")#, input_formats ="%H:%M")

localtz = timezone(settings.TIME_ZONE)

KML_link = """<?xml version='1.0' encoding='UTF-8'?>
<kml xmlns='http://earth.google.com/kml/2.2'>
	<Document>
		<name>Demo 3D de rastreo de vuelo</name>
		<NetworkLink>
			<name>{imei.name}</name>
			<refreshVisibility>0</refreshVisibility>
			<flyToView>1</flyToView>
			<description>
				<![CDATA[ Rastreo de trayectoria de vuelo ({date}.]]>
			</description>
			<Link>
				<href>{url}</href>
				<refreshMode>onInterval</refreshMode>
				<refreshInterval>60</refreshInterval>
			</Link>
		</NetworkLink>
	</Document>
</kml>
"""

KML_header = """<?xml version='1.0' encoding='UTF-8'?>
<kml xmlns="http://www.opengis.net/kml/2.2" xmlns:gx="http://www.google.com/kml/ext/2.2">
	<Document id="{imei.imei}">
		<name>Información de rastreo de vuelo</name>
		<Style id="s_def">
			<LineStyle>
				<color>FFFF0000</color>
				<width>4</width>
			</LineStyle>
			<PolyStyle>
				<color>66800000</color>
				<outline>0</outline>
			</PolyStyle>
		</Style>
		<LookAt>
			<longitude>{view.position.x}</longitude>
			<latitude>{view.position.y}</latitude>
			<range>4000</range>
			<heading>0</heading><tilt>0</tilt>
		</LookAt>
"""

KML_placemark0 = """		<Placemark>
			<name>Ruta {imei.name}</name>
			<styleUrl>#s_def</styleUrl>
			<LineString>
				<extrude>1</extrude>
				<tessellate>0</tessellate>
				<altitudeMode>absolute</altitudeMode>
				<coordinates>
"""
KML_placemark ="""					{0.position.x},{0.position.y},{0.altitude}
"""
KML_placemark1 ="""			</coordinates>
			</LineString>
		</Placemark>
"""

KML_tour0 = """
		<gx:Tour>
			<name>Tour 3D {imei.imei}</name>
			<LookAt>
				<longitude>{view.position.x}</longitude>
				<latitude>{view.position.y}</latitude>
				<range>50</range>
				<heading>0</heading><tilt>0</tilt>
			</LookAt>
			<gx:Playlist>
"""
KML_tour = """			<gx:FlyTo>
				<gx:duration>{0.duration}</gx:duration>
				<gx:flyToMode>smooth</gx:flyToMode>
				<Camera>
					<longitude>{0.position.x}</longitude>
					<latitude>{0.position.y}</latitude>
					<altitude>{0.altitude2}</altitude>
					<heading>{0.course}</heading>
					<tilt>60</tilt>
					<altitudeMode>absolute</altitudeMode>
				</Camera>
			</gx:FlyTo>
"""

KML_tour1 = """				<gx:Wait>
				<gx:duration>1.0</gx:duration>
				</gx:Wait>
			</gx:Playlist>
		</gx:Tour>
"""

KML_footer ="""	</Document>
</kml>
"""

@csrf_exempt
@never_cache
def getkml(request, template_name='kmldl.html'):
	if 'action' in request.GET:
		form = KmlForm(data=request.GET)
		action = request.GET['action']
		if form.is_valid():
			d = form.cleaned_data
			imei = get_object_or_404(SGAvl,imei=d['imei'])
			tstart = localtz.localize(datetime.combine(d['day'],d['start']))
			tend = localtz.localize(datetime.combine(d['day'],d['stop']))
			tracks = Event.objects.filter(imei = imei).filter(date__range = (tstart,tend)).filter(type = "TRACK").order_by('date')
			n = len(tracks)
			if (n):
				response = HttpResponse(content_type='application/vnd.google-earth.kml+xml')
				if action=='Loader':
					response['Content-Disposition'] = 'filename="{imei.name}-{day}.kml"'.format(imei=imei,day=d['day'])
					url = request.build_absolute_uri().replace('action=Loader','action=Data').replace('&','&amp;')
					response.write(KML_link.format(imei=imei,url=url,date=tstart.strftime("%Y-%m-%d %H:%M")))
				else:
					response['Content-Disposition'] = 'filename="{imei.name}-{day}-data.kml"'.format(imei=imei,day=d['day'])

					for i in range(n-1):
						td = tracks[i].date-tracks[i+1].date
						tracks[i].duration = td.seconds/30000
						tracks[i].altitude2 = tracks[i].altitude+50

					response.write(KML_header.format(imei=imei,view = tracks[n-1]))

					response.write(KML_placemark0.format(imei=imei))
					for i in tracks:
						response.write(KML_placemark.format(i))
					response.write(KML_placemark1)

					response.write(KML_tour0.format(imei=imei,view = tracks[0]))
					for i in tracks[:n-1]:
						response.write(KML_tour.format(i))
					response.write(KML_tour1)

					response.write(KML_footer)
				return response
			HttpResponseBadRequest()
		else:
			errs = form.errors
			raise ValueError(errs)
			return HttpResponseBadRequest()
	else:
		form = KmlForm()
		context = {'form': form}
		return  render_to_response(template_name, context,context_instance=RequestContext(request))

class NewTrackForm(forms.Form):
    tracking = forms.CharField(label = "Tracking No")
    #active = forms.BooleanField(label = "Activo")

    def __init__(self, user, *args, **kwargs):
        self.imeis = Device.objects.filter(owner = user)
        self.fences = GeoFence.objects.filter(owner = user)
        super(NewTrackForm, self).__init__(*args, **kwargs)
        self.fields['imei'] = forms.ModelChoiceField(queryset = self.imeis, empty_label = None, label="Equipo")
        self.fields['stopFence'] = forms.ModelChoiceField(queryset = self.fences, empty_label = None, label = "Geocerca final")
        self.fields['evFences'] = forms.ModelMultipleChoiceField(queryset = self.fences, label = "Geocercas" )


@csrf_exempt
@never_cache
def newtrack(request, template_name='newtrack.html'):
    if 'user' in request.GET:
        request.user = get_object_or_404(User,username = request.GET['user'])
    if request.method == "POST":
        form = NewTrackForm(request.user, data=request.POST)
        if form.is_valid():
            d = form.cleaned_data
            if Tracking.objects.filter(tracking = d['tracking']):
                return HttpResponseBadRequest()
            track = Tracking(tracking = d['tracking'], imei = d['imei'],
                stopFence = d['stopFence'], start = datetime.now(utc), stop = None)
            track.save()
            for i in d['evFences']:
                track.fences.add(i)
            return HttpResponseRedirect(reverse('gps.tracker.auth_views.track',kwargs = {'trackNo': track.tracking}))
        else:
            return HttpResponseBadRequest()
    else:
        form = NewTrackForm(request.user)
    context = {'form': form}
    return render_to_response(template_name, context,context_instance=RequestContext(request))

def extent2(e1,e2):
    return (min(e1[0],e2[0]),min(e1[1],e2[1]),max(e1[2],e2[2]),max(e1[3],e2[3]))

@never_cache
def track(request, trackNo, template_name='track.html'):
    track =  get_object_or_404(Tracking,tracking = trackNo)
    if track.stop:
        points = Event.objects.filter(imei = track.imei).filter(date__range = (track.start,track.stop)).filter(type__in = ["TRACK","IO_FIX"])
    else:
        points = Event.objects.filter(imei = track.imei).filter(date__gte = track.start).filter(type__in = ["TRACK","IO_FIX"])
    coords = []
    events = []
    fq = track.fences.all()
    fences = []
    extent = fq.extent()
    extent = extent2(extent, track.stopFence.fence.extent)
    for i in fq:
        if len(points):
            i.inside = i.fence.contains(points[0].position)
        fences.append(i)
    if len(points):
        track.stopFence.inside = track.stopFence.fence.contains(points[0].position)
        extent = extent2(extent,points.extent())
    if track.stopFence in fences:
        fences.remove(track.stopFence)
    fences.append(track.stopFence)
    enc = gpolyencode.GPolyEncoder()
    for i in fences:
        i.encPoly = enc.encode(i.fence.tuple[0])['points']
    for i in points:
        coords.append((i.position.x,i.position.y))
        for j in fences:
            inside = j.fence.contains(i.position)
            if inside != j.inside:
                j.inside = inside
                events.append(dict(inside = inside,point = i,fence = j, bounds = minExtents(i.position.extent)))
    if not track.stop and len(points):
        events.append(dict(inside = False,point = i, fence = None, bounds = minExtents(i.position.extent)))
    fences.remove(track.stopFence)
    encoords = enc.encode(coords)['points']
    if 'json' in request.GET:
        jevs = []
        for i in events:
            jevs.append(dict(
                date = i['point'].date.isoformat(),
                position = (i['point'].position.x, i['point'].position.y),
                inside = i['inside'],
                fence = i['fence'].name
            ))
        ctx = dict(track = track.tracking,
                   imei = track.imei.name,
                   start = track.start.isoformat(),
                   stop = None if track.stop is None else track.stop.isoformat(),
                   events = jevs
                   )
        return HttpResponse(simplejson.dumps(ctx), mimetype='application/json')
    ctx = dict(fences = fences,
               stop = track.stopFence,
               evs = events,
               tracking = track,
               extent = extent,
               coords = encoords)
    #raise ValueError
    return render_to_response(template_name, ctx,context_instance=RequestContext(request))

from pygeocoder import Geocoder
from django.views.generic import ListView, DetailView, TemplateView
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required

class TrackEv(object):
    def __init__(self,ev):
        self.sdate = ev.date
        self.edate = ev.date
        self.start = ev.position
        self.stop = ev.position
        self.km = 0
        if ev.speed>15:
            self.type = 'Recorrido'
            #s = ev.speed
            #raise ValueError
        else:
            self.type = 'Parada'

    def merge(self,tr):
        self.km += tr.km
        self.edate = tr.edate
        self.stop = tr.stop

    def addEvent(self,ev):
        edate = self.edate
        self.edate = ev.date
        self.km +=  geoLen(gPoint(self.stop.y,self.stop.x),gPoint(ev.position.y,ev.position.x)).km
        self.stop = ev.position
        if self.type == 'Recorrido':
            if ev.date-edate > timedelta(seconds = 90) or ev.speed<=15:
                if self.km<0.3:
                    self.type = 'Parada'
                    return None
                return TrackEv(ev)
        elif ev.speed > 15:
            if ev.date - self.sdate <=timedelta(seconds = 90):
                self.type = 'Recorrido'
                #dt1 = ev.date - self.sdate
                #dt1 = ev.date - edate
                #s = ev.speed
                #raise ValueError
            else:
                return TrackEv(ev)
        return None


from reportlab.platypus import BaseDocTemplate, PageTemplate, Table, TableStyle, Paragraph, Spacer, Frame, PageBreak
from reportlab.lib.pagesizes import letter,landscape
from reportlab.lib.units import inch
from reportlab.lib import colors
from pygeocoder import Geocoder

class TrackAndStopView(ListView):
    template_name = "devDetail.html"

    coder = Geocoder(api_key = 'AIzaSyC9rj3SiZbqWAqxwJ5DftckBr4UQqEl0lo')
    def dayRange(self):
        return datetime(self.date.year, self.date.month, self.date.day),datetime(self.date.year, self.date.month, self.date.day,23,59,59)

    def get_queryset(self):
        self.events = Event.objects.filter(imei = self.dev,date__range = self.dayRange(),type = 'TRACK').order_by('date')
        #try:
        #    e = self.events[0]
        #except IndexError:
        #    raise Http404
        return self.events

    @method_decorator(login_required)
    def get(self, request, *args, **kwargs):
        self.imei = kwargs.pop('imei')
        self.date = kwargs.pop('date')
        self.dev = get_object_or_404(SGAvl,imei = self.imei)
        dt = self.date
        if type(self.date)!= dtdate:
            self.date = datetime.strptime(self.date,"%Y-%m-%d")
        return super(ListView,self).get(self, request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(ListView, self).get_context_data(**kwargs)
        if context['object_list'].count():
            evs = [TrackEv(self.events[0])]
            for e in self.events[1:]:
                ed = evs[-1].addEvent(e)
                if ed:
                    evs.append(ed)
            nevs = [evs[0]]
            for i in evs[1:]:
                if i.type == nevs[-1].type:
                    nevs[-1].merge(i)
                else:
                    nevs.append(i)
            evs = nevs
        else:
            evs = []
        context['details'] = evs
        return context

    boxgrid = TableStyle([
        ('GRID',(0,0),(-1,-1),1,colors.black),
        ('BOX',(0,0),(-1,-1),2,colors.black),
        ('ALIGN',(0,0),(-1,-1),'LEFT'),
        ('SPAN',(0,0),(-1,0)),
        ('SPAN',(0,1),(-1,1))  ])

    def pos_str(self,pos):
        ps = "%.4f,%.4f"%(pos.y,pos.x)
        ad = self.coder.reverse_geocode(pos.y,pos.x)
        if ad.route:
            adl = '\n' + ad.route
            adl = adl[:50]
            if ad.street_number:
                adl = adl + ' ' + ad.street_number[:10]
        else:
            adl = ''
        return ps+adl

    def render_to_response(self,context):
        data = [['ID: %s'%self.dev.name,'','','','',''],
            ['Fecha: %s'%self.date.strftime("%x"),'','','','',''],
            [u'Tipo',u'Hora',u'Duración','Km','Inicio', 'Fin']]
        for i in context['details']:
            dt = i.edate-i.sdate
            s = dt.seconds
            h = s / 3600
            s -= h*3600
            m = s / 60
            s -= m*60
            hms = "%02d:%02d:%02d"%(h,m,s)
            ini = self.pos_str(i.start)
            if i.type == 'Recorrido':
                km = "%d Km"%i.km
                fin = self.pos_str(i.stop)
            else:
                km=''
                fin = ''
            data.append([i.type,i.sdate.strftime("%H:%M"),
                    hms,km,ini,fin])
        t = Table(data)
        t.setStyle(self.boxgrid)
        response = HttpResponse(content_type='application/pdf')
        #response['Content-Disposition'] = 'attachment; filename="taskLogReport.pdf"'
        response['Content-Disposition'] = 'filename="peso.pdf"'

        doc = BaseDocTemplate(response, pagesize=landscape(letter), leftMargin = 0.25*inch,
                              rightMargin = 0.25*inch, topMargin = 0.25*inch,
                              bottomMargin = 0.25*inch)
        frame = Frame(doc.leftMargin, doc.bottomMargin, doc.width, doc.height,
                   id='normal')
        template = PageTemplate(id='test', frames=frame)
        doc.addPageTemplates([template])
        story = [t]
        doc.build(story)
        return response


def getUserSims(u):
    return SimCard.objects.filter(avl__owner__username = u)

def getOwnerSims(u):
    return SimCard.objects.filter(avl__owner = u)

def printSims(u,func):
    print '******',u,'********'
    for i in func(u):
        print i.phone,i.iccid,i.imsi

def SimReport():
    for i in User.objects.all():
        printSims(i,getOwnerSims)

import sys
from contextlib import contextmanager
@contextmanager
def stdout_redirected(new_stdout):
    save_stdout = sys.stdout
    sys.stdout = new_stdout
    try:
        yield None
    finally:
        sys.stdout = save_stdout
