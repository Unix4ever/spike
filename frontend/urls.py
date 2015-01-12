from django.conf.urls import patterns, include, url
from django.conf import settings
from django.conf.urls.static import static

from django.contrib import admin
from frontend import views
from rest_framework.urlpatterns import format_suffix_patterns

api_version = "v1"

paths = (
        ('scenarios/$', views.ScenarioList.as_view(),
            'scenario-detail'),
        ('scenarios/(?P<pk>\w+)/?$',
            views.ScenarioView.as_view(), 'scenario-detail'),

        ('scenarios/(?P<pk>\w+)/content/?$', 'get_file', 'scenario-file'),

        ('tasks/$', views.TaskList.as_view(), 'tasks-detail'),
        ('tasks/(?P<pk>[\d\w._-]+)/?$', views.TaskView.as_view(),
            'task-detail'),
)

paths = map(lambda (pattern, func, name): url(r'^%s/%s' % (api_version, pattern), func, name=name), paths) 

urlpatterns = patterns('frontend.views', *paths)

urlpatterns += patterns('',
    url(r'^api-auth/', include('rest_framework.urls', namespace='rest_framework')),
    url(r'^admin/', include(admin.site.urls))
)
