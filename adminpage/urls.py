# -*- coding: utf-8 -*-
#



__author__ = "Epsirom"
from adminpage.views import *

from django.conf.urls import url, include
urlpatterns = [
    url(r'^login/?$', UserLogin.as_view()),
    url(r'^logout/?$', UserLogout.as_view()),
    url(r'^activity/list/?$', ActivityList.as_view()),
    url(r'^activity/delete/?$', ActivityDelete.as_view()),
    url(r'^activity/create/?$', ActivityCreate.as_view()),
    url(r'^image/upload/?$', ImageUpload.as_view()),
    url(r'^activity/detail/?$', ActivityDetail.as_view()),
    url(r'^activity/menu/?$', ActivityMenu.as_view()),
    url(r'^activity/checkin/?$', ActivityCheckin.as_view()),
]
