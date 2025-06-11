import sys,os,io

site = os.path.basename(os.path.dirname(__file__))
os.environ['DJANGO_SETTINGS_MODULE'] = 'sites.'+site+'.settings'
path = os.getcwd()
if path not in sys.path: sys.path.insert(0,path)

import django.core.handlers.wsgi
application = django.core.handlers.wsgi.WSGIHandler()

#f = open("/home/bcantu/test.log",'w+')
#print >> f, "sys.path = %s"%sys.path
#print >> f, "os.environ = %s"%os.environ
#f.close()
