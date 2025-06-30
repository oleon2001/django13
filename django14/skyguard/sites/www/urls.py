from django.conf.urls.defaults import patterns, include, url
from django.conf import settings
from django.conf.urls.static import static


# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

from gps.tracker.views import RealTimeView,TrackerApiView,TrackerListView,TrackerDetailView
from gps.tracker.views import GeofenceListView,GeofenceView,WeeklyReportView,PsiReportPDF,AjaxNewCoords, AjaxMsgs
from gps.tracker.views import TrackerPsiApiView, TicketApiView, TargetView
from gps.tracker.subsidio import TsheetView,CsvTSDReportView
import gps.assets.views

from gps.tracker.auth_views import TrackAndStopView
from datetime import datetime

from gps.tracker.reports import PeopleCountReport,SensorServiceReport,AlarmReport,SensorHellReport,LisReport
from gps.tracker.reports import PeopleCountCSV, PeopleSummaryReport, TicketDifferenceReport, TicketCapture
from gps.tracker.reports import TicketViewPdf ,TicketDailyReport, TicketGlobalReport, TicketRuta400Report, TicketWeeklyReport, StatsDailyReport

from gps.tracker.cfe import ConcorView

from gps.tracker.admin2 import site2

urlpatterns = patterns('',
	# Examples:
	# url(r'^$', 'gps_site.views.home', name='home'),
	# url(r'^gps_site/', include('gps_site.foo.urls')),

	# Uncomment the admin/doc line below to enable admin documentation:
	# url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

	# Uncomment the next line to enable the admin:
	(r'^$', 'gps.tracker.views.devices'),
	(r'^iridium$', 'gps.tracker.views.iridium'),
	(r'^test_devs/$', TrackerListView.as_view()),
	(r'^ptickets$', TicketViewPdf.as_view()),
	(r'^tickets$', TicketCapture.as_view()),
	(r'^tarjetas$', TargetView.as_view()),
	#(r'^tarjetas$', TicketViewPdf.as_view()),
	(r'^devices.json$', 'gps.tracker.views.devices_ajax'),
	(r'^(\d{13,15})$', 'gps.tracker.views.device'),
	(r'^(\d{13,15})/(\d{4})-(\d{2})-(\d{2})$', 'gps.tracker.views.device'),
	(r'^2/(?P<imei>\d{13,15})$', TrackerDetailView.as_view(),{'date' : None},'dev_detail'),
	(r'^2/(?P<imei>\d{13,15})/(?P<date>(\d{4})-(\d{2})-(\d{2}))$', TrackerDetailView.as_view(),{},'dev_detail2'),
	(r'^psi/(?P<imei>\d{13,15})/(?P<date>(\d{4})-(\d{2})-(\d{2}))$', PsiReportPDF.as_view(),{},'dev_psiPDF'),
	(r'^weekly01$', WeeklyReportView.as_view(),{'owner' : None},'weekly01'),
	(r'^weekly01/(?P<owner>(\w+))$', WeeklyReportView.as_view(),{},'weekly01_owner'),
	(r'^assets$', gps.assets.views.AssetView.as_view(),{},'assets'),
	(r'^glassets$', gps.assets.views.GridlessAssetView.as_view(),{},'assets'),
	(r'^fences$', GeofenceListView.as_view(),{},'fences'),
	(r'^fence/(?P<fid>\d*)$', GeofenceView.as_view(),{},'fence'),
	(r'^login$', 'django.contrib.auth.views.login',{'template_name':'index.html'}),
	(r'^logoff$', 'django.contrib.auth.views.logout',{'template_name':'logged_out.html'}),
	(r'^track/(?P<trackNo>.+)$', 'gps.tracker.auth_views.track',{}),
	(r'^newtrack$', 'gps.tracker.auth_views.newtrack',{}),
	(r'^kml$', 'gps.tracker.auth_views.getkml',{},'kml'),
	(r'^api/track$', TrackerApiView.as_view(),{},'api_track'),
#	(r'^api/psi$', TrackerPsiApiView.as_view(),{},'api_track'),
	(r'^api/newc$', AjaxNewCoords.as_view(),{},'api_newc'),
	(r'^api/msgs$', AjaxMsgs.as_view(),{},'api_newc'),
	(r'^api/tickets$', TicketApiView.as_view(),{},'api_ticket'),
	(r'^rt/(?P<pk>\d{13,15})$', RealTimeView.as_view(),{},'dev_real'),
	(r'^reports/track/(?P<imei>\d{13,15})$', TrackAndStopView.as_view(),{'date': datetime.date(datetime.now())},'rep_trackt'),
	(r'^reports/track/(?P<imei>\d{13,15})/(?P<date>(\d{4})-(\d{2})-(\d{2}))$', TrackAndStopView.as_view(),{},'rep_track'),

	(r'^rutas/conteo$', PeopleCountReport.as_view(),{},'rep_people'),
	(r'^rutas/csv$', PeopleCountCSV.as_view(),{},'rep_people'),
	(r'^rutas/mtto$', SensorServiceReport.as_view(),{},'rep_mtto'),
	(r'^rutas/alarma$', AlarmReport.as_view(),{},'rep_alarm'),
	(r'^rutas/sensor$', SensorHellReport.as_view(),{},'rep_hell'),
	(r'^rutas/summary$', PeopleSummaryReport.as_view(),{},'rep_summary'),
	(r'^rutas/tickets$', TicketDifferenceReport.as_view(),{},'rep_tickets'),
	(r'^rutas/cash$', TicketDailyReport.as_view(),{},'rep_tickets'),
	(r'^rutas/weekly$', TicketWeeklyReport.as_view(),{},'rep_tickets'),
	(r'^rutas/allcash$', TicketGlobalReport.as_view(),{},'rep_tickets'),
	(r'^rutas/400cash$', TicketRuta400Report.as_view(),{},'rep_tickets'),
	(r'^rutas/lis$', LisReport.as_view(),{},'rep_lis'),
	(r'^rutas/stats$', StatsDailyReport.as_view(),{},'rep_stats'),
	(r'^rutas/vueltas$', TsheetView.as_view(),{},'vueltas'),
	(r'^rutas/rdvueltas$', CsvTSDReportView.as_view(),{},'vueltas'),
	(r'^cfe/(?P<imei>\d{13,15})$', ConcorView.as_view(),{},'ConcorView'),
	
	url(r'^mgmt/', include(admin.site.urls)),
	url(r'^captura/', include(site2.urls)),
)
#urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
#urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

