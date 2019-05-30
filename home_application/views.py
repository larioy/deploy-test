# -*- coding: utf-8 -*-

from common.mymako import render_mako_context
from home_application.sys_view import *
from home_application.custom_item_view import *
from home_application.module_view import *
from account.decorators import login_exempt


def home(request):
    """
    首页
    """
    # update_business()
    return render_mako_context(request, '/home_application/js_factory.html')


@login_exempt
def checkReport(request):
    return render_mako_context(request, '/home_application/report_detail.html')


def add_business_page(request):
    return render_mako_context(request, '/home_application/add_business.html')
