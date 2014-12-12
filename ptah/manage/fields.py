""" ptah.form fields """
import ptah
from ptah import form
from pyramid.view import view_config


@ptah.manage.module('fields')
class FieldsModule(ptah.manage.PtahModule):
    __doc__ = ('A preview and listing of all form fields in the '
      'application. This is useful to see what fields are available. '
      'You may also interact with the field to see how it works in '
      'display mode.')

    title = 'Field types'


@view_config(
    context=FieldsModule,
    renderer=ptah.layout('ptah-manage:fields.lt', 'ptah-manage'))

class FieldsView(ptah.View):
    """ Fields manage module view """

    def update(self):
        data = []

        fields = self.request.registry[form.directives.ID_FIELD]
        previews = self.request.registry[form.directives.ID_PREVIEW]

        for name, cls in fields.items():
            data.append({'name': name,
                         'doc': cls.__doc__,
                         'preview': previews.get(cls)})

        self.fields = sorted(data, key = lambda item: item['name'])
