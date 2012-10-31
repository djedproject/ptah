""" base view class with access to various api's """
import logging
from pyramid.decorator import reify
from pyramid.compat import escape
from pyramid_layer import render, tmpl_filter

import ptah
from ptah.formatter import format

log = logging.getLogger('ptah.view')


class View(object):
    """ Base view """

    __name__ = ''
    __parent__ = None

    format = format

    def __init__(self, context, request):
        self.context = context
        self.request = request
        self.__parent__ = context

    @reify
    def application_url(self):
        url = self.request.application_url
        if url.endswith('/'):
            url = url[:-1]
        return url

    def update(self):
        return {}

    def __call__(self):
        result = self.update()
        if result is None:
            result = {}

        return result


def add_message(request, msg, type='info'):
    """ Add status message

    Predefined message types

    * info

    * success

    * warning

    * error

    """
    request.session.flash(render_message(request, msg, type), 'status')


def render_message(request, msg, type='info'):
    """ Render message, return html """
    if ':' not in type:
        type = 'ptah-message:%s'%type
    return render(request, type, msg)


def render_messages(request):
    """ Render previously added messages """
    return ''.join(request.session.pop_flash('status'))


@tmpl_filter('ptah-message:error')
def error_message(context, request):
    if isinstance(context, Exception):
        context = '%s: %s'%(
            context.__class__.__name__, escape(str(context), True))

    return {'context': context}


class MasterLayout(View):

    @reify
    def user(self):
        userid = ptah.auth_service.get_userid()
        return ptah.resolve(userid)

    @reify
    def manage_url(self):
        return ptah.manage.get_manage_url(self.request)

    @reify
    def actions(self):
        return []
