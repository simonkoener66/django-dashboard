"""dashboard URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.8/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Add an import:  from blog import urls as blog_urls
    2. Add a URL to urlpatterns:  url(r'^blog/', include(blog_urls))
"""
from django.conf.urls import url
from django.conf.urls.static import static
from django.conf import settings

from admin.views import *
from sales.views import *
from tools.views import *


urlpatterns = [
    url(r'^$', index, name='index'),
    url(r'^login', auth_login, name='auth_login'),
    url(r'^logout', auth_logout, name='auth_logout'),
    url(r'^reset-password', reset_password, name='reset_password'),
    url(r'^admin/api/recover', api_recover_password, name='api_recover_password'),
    url(r'^admin/users', admin_users, name='admin_users'),
    url(r'^admin/user_edit', admin_edit_user, name='admin_edit_user'),
    url(r'^admin/assign_advertisers', admin_assign_advertisers, name='admin_assign_advertisers'),
    url(r'^admin/assign_publishers', admin_assign_publishers, name='admin_assign_publishers'),

    #url(r'^sales', views.sales_commission, name='sales'),
    url(r'^sales/commission', sales_commission, name='sales_commission'),

    url(r'^tools/demand-optimization', demand_optimization, name='demand_optimization'),
    url(r'^tools/supply-optimization', supply_optimization, name='supply_optimization'),
    url(r'^api/stats/budget', api_update_budget, name='api_update_budget'),
    url(r'^api/stats_traffic/impression_avail', api_update_avail, name='api_update_avail'),
    url(r'^api/search/campaign', api_campaign_search, name='api_campaign_search'),
    url(r'^api/search/api_advertiser_search', api_advertiser_search, name='api_advertiser_search'),
    url(r'^tools/api/mail', tools_api_mail, name='tools_api_mail')
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
