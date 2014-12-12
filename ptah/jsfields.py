""" various fields """
import ptah
import datetime
import pytz
from ptah import form


@ptah.form.field('texteditor')
class TextEditorField(form.TextAreaField):
    """ TextEditor input widget. Field name is ``texteditor``.

    Extra params:

    :param width: Width of widget, default is ``400px``
    :param height: Height os widget, default is ``300px``
    """

    klass = 'texteditor-widget form-control'

    width = '400px'
    height = '300px'

    tmpl_input = "ptah:texteditor"


@ptah.form.field('date')
class JSDateField(form.DateField):
    """Date input widget with Bootstrap Datepicker. Field name is ``date``."""

    klass = 'date-widget form-control'
    value = ''

    tmpl_input = 'ptah:jsdate'

#    def to_form(self, value):
#        if value is null or value is None:
#            return null

#        if isinstance(value, datetime.datetime):
#            value = value.date()

#        if not isinstance(value, datetime.date):
#            raise Invalid(
#                _('"${val}" is not a date object'), self,
#                mapping={'val': value})

#        return value

#    def to_field(self, value):
#        if not value:
#            return None
#        try:
#            return datetime.datetime.strptime(value, '%Y-%m-%d')
#        except Exception:
#            raise Invalid(_('Invalid date'), self)


@ptah.form.field('datetime')
class JSDateTimeField(form.DateTimeField):
    """DateTime input widget with Bootstrap Datepicker.
    Field name is ``datetime``."""

    klass = 'datetime-widget form-control'
    value = ''

    #time_part = null
    #date_part = null
    #tzinfo = None

    tmpl_input = "ptah:jsdatetime"

    def to_form(self, value):
        if value is form.null or value is None or not value:
            return form.null

        if type(value) is datetime.date:  # cannot use isinstance; dt subs date
            value = datetime.datetime.combine(value, datetime.time())

        if not isinstance(value, datetime.datetime):
            raise form.Invalid(self.error_msg, self, {'val': value})

        if value.tzinfo is None:
            value = value.replace(tzinfo=self.default_tzinfo)

        return value.strftime('%Y-%m-%d %H:%M')

#    def update(self):
#        self.date_name = '%s.date' % self.name
#        self.time_name = '%s.time' % self.name

#        super(JSDateTimeField, self).update()

#        self.date_part = self.params.get(self.date_name, null)
#        self.time_part = self.params.get(self.time_name, null)

#        if self.value:
#            raw = self.value
#            self.tzinfo = raw.tzinfo
#            if self.date_part is null:
#                self.date_part = raw.strftime('%m/%d/%Y')
#            if self.time_part is null:
#                FORMAT = ptah.get_settings(
#                    ptah.CFG_ID_FORMAT, self.request.registry)
#                self.time_part = raw.strftime(FORMAT['time_short'])

#        if self.date_part is null:
#            self.date_part = ''
#        if self.time_part is null:
#            self.time_part = ''

#    def extract(self, default=null):
#        date = self.params.get(self.date_name, default)
#        if date is default:
#            return default

#        if not date:
#            return null

#        time = self.params.get(self.time_name, default)
#        if time is default:
#            return default

#        if not time:
#            return null

#        #FORMAT = ptah.get_settings(ptah.CFG_ID_FORMAT, self.request.registry)
#        try:
#            dt = datetime.datetime.strptime(
#                '%s %s' % (date, time), '%m/%d/%Y %H:%M')
#        except ValueError:
#            try:
#                dt = datetime.datetime.strptime(
#                    '%s %s' % (date, time), '%m/%d/%Y %I:%M %p')
#            except ValueError:
#                return null

#        return dt.replace(tzinfo=self.tzinfo).isoformat()
