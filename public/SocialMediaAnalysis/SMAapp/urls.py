from django.conf.urls import url
from SMAapp.views import UserDetailsView, IndexView, CompareView,\
    SearchFormRedirectView, CompareFormRedirectView
from django.views.generic.base import TemplateView
from django.views.generic import RedirectView
from django.core.urlresolvers import reverse_lazy

urlpatterns = [
    url(r'^$', TemplateView.as_view(template_name="SMAapp/about.html")),
    url(r'^search-form-redirect', SearchFormRedirectView.as_view(), name='search_redirect'),
    url(r'^compare-form-redirect', CompareFormRedirectView.as_view(), name='compare_redirect'),
    url(r'^user/(?P<username>\w+)/$', UserDetailsView.as_view(), name='user_details'),
    url(r'^guide$', TemplateView.as_view(template_name="SMAapp/guide.html"), name='guide'),
    url(r'^docs', TemplateView.as_view(template_name="SMAapp/docs.html"), name='docs'),
    url(r'^about', TemplateView.as_view(template_name="SMAapp/about.html"), name='about'),
    url(r'^app$', IndexView.as_view(), name='index'),

    url(r'^compare/(?P<first_username>\w+)/(?P<second_username>\w+)/$', CompareView.as_view(), name='compare_users'),
]
