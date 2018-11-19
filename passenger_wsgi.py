import sys, os
# Virtual env's python path
INTERP = "/home/oswindsftp/socialmediaanalysis.s3platform.eu/sma2/bin/python"
#INTERP is present twice so that the new python interpreter knows the actual executable path 
if sys.executable != INTERP: os.execl(INTERP, INTERP, *sys.argv)

cwd = os.getcwd()
sys.path.append(cwd)
# Your project path here
sys.path.append(cwd + '/public/SocialMediaAnalysis/')
# Virtual env's paths
sys.path.insert(0,cwd+'/sma2/bin')
sys.path.insert(0,cwd+'/sma2/lib/python2.7/site-packages/django')
sys.path.insert(0,cwd+'/sma2/lib/python2.7/site-packages')
#Django settings file
os.environ['DJANGO_SETTINGS_MODULE'] = "SocialMediaAnalysis.settings"
from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()
