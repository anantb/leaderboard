from django.conf.urls import patterns, include, url

urlpatterns = patterns('',
	url(r'^$','server.views.home'),
	url(r'^home$', 'server.views.home'),
	url(r'^upload$', 'server.views.upload'),
	url(r'^scores$', 'server.views.scores'),
	
	

    url(r'^login', 'server.views.login'),
    url(r'^register', 'server.views.register'),
    url(r'^logout', 'server.views.logout'),
)