from django.conf.urls import patterns, url
from . import views

urlpatterns = patterns('',
    url(r'^$', views.entry_view, name='entry'),
    url(r'^weekly/$', views.weekly_view, name='weekly'),
    url(r'^dashboard/$', views.dashboard_view, name='dashboard'),
    url(r'^income/$', views.income_view, name='income'),
    url(r'^entry/(?P<pk>\d+)/edit/$', views.entry_edit_view, name='entry_edit'),
    url(r'^income/(?P<pk>\d+)/edit/$', views.profit_edit_view, name='profit_edit'),
    url(r'^signin/$', views.login_view, name='login'),
    url(r'^logout/$', views.logout_view, name='logout'),
    url(r'^signup/$', views.signup_view, name='signup'),
)
