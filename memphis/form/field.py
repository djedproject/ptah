import colander
from zope import interface
from zope.component import getSiteManager

from memphis import config
from memphis.form.util import expandPrefix, OrderedDict
from memphis.form.error import Error, WidgetError
from memphis.form.interfaces import IForm, IField, IFields, IWidget, IWidgets
from memphis.form.interfaces import INPUT_MODE, DISPLAY_MODE, NOT_CHANGED


class Field(object):
    """Field implementation."""
    interface.implements(IField)

    css = ''
    widgetFactory = ''

    def __init__(self, field, name=None, prefix='', mode=None, readonly=False):
        self.typ = field.typ
        self.field = field
        if name is None:
            name = field.name
        self.name = expandPrefix(prefix) + name
        self.prefix = prefix
        self.mode = mode
        self.readonly = readonly

    def __repr__(self):
        return '<%s %r>' % (self.__class__.__name__, self.name)


class Fields(OrderedDict):
    """Fields manager"""
    interface.implements(IFields)

    def __init__(self, *args, **defaults):
        super(Fields, self).__init__()

        self.schemas = schemas = []

        fields = []
        for arg in args:
            if isinstance(arg, colander._SchemaMeta):
                arg = arg()

            if isinstance(arg, colander.SchemaNode):
                schemas.append(arg)
                for field in arg.children:
                    fields.append((field.name, field))

            elif isinstance(arg, Fields):
                schemas.extend(arg.schemas)
                for form_field in arg.values():
                    fields.append((form_field.name, form_field))

            elif isinstance(arg, Field):
                fields.append((arg.name, arg))

            else:
                raise TypeError("Unrecognized argument type", arg)

        for name, field in fields:
            if isinstance(field, Field):
                form_field = field
            else:
                customDefaults = defaults.copy()
                #if iface is not None:
                #    customDefaults['interface'] = iface
                form_field = Field(field, **customDefaults)
                name = form_field.name

            if name in self:
                raise ValueError("Duplicate name", name)

            self[name] = form_field

    def select(self, *names):
        return self.__class__(*[self[name] for name in names])

    def omit(self, *names):
        return self.__class__(
            *[item for name, item in self.items() if name not in names])


class FieldWidgets(OrderedDict):
    """Widget manager for IWidget."""
    config.adapts(IForm, interface.Interface)
    interface.implements(IWidgets)

    prefix = 'widgets.'
    mode = INPUT_MODE
    errors = ()
    hasRequiredFields = False
    setErrors = True

    def __init__(self, form, request):
        super(FieldWidgets, self).__init__()

        self.form = form
        self.request = request

    def update(self):
        content = self.content = self.form.getContent()

        # Create a unique prefix.
        prefix = expandPrefix(self.form.prefix)
        prefix += expandPrefix(self.prefix)
        request = self.request
        params = self.form.getRequestParams()
        context = self.form.getContext()

        sm = getSiteManager()

        # Walk through each field, making a widget out of it.
        for field in self.form.fields.values():
            # Step 1: Determine the mode of the widget.
            mode = self.mode
            if field.mode is not None:
                mode = field.mode
            elif field.readonly:
                mode = DISPLAY_MODE

            # Step 2: Get the widget for the given field.
            shortName = field.name

            widget = None
            factory = field.widgetFactory
            if isinstance(factory, basestring):
                widget = sm.queryMultiAdapter(
                    (field.field, field.typ, request), IWidget, name=factory)
            elif callable(factory):
                widget = factory(field.field, field.typ, request)

            if widget is None:
                raise TypeError("Can't find widget for %s"%field)

            # Step 3: Set the prefix for the widget
            widget.name = str(prefix + shortName)
            widget.id = str(prefix + shortName).replace('.', '-')

            # Step 4: Set the content
            widget.context = context
            widget.content = content

            # Step 5: Set the form
            widget.form = self.form

            # Step 6: Set some variables
            widget.params = params

            # Step 7: Set the mode of the widget
            widget.mode = mode

            # Step 8: Update the widget
            widget.update()

            # Step 9: Add the widget to the manager
            if widget.required:
                self.hasRequiredFields = True

            # Step 10:
            widget.addClass(field.css)

            widget.__parent__ = self
            widget.__name__ = shortName
            self[shortName] = widget

    def extract(self):
        data = {}
        sm = getSiteManager()
        errors = []
        errorViews = []
        context = self.form.getContext()

        for name, widget in self.items():
            if widget.mode == DISPLAY_MODE:
                continue

            value = widget.field.missing
            try:
                widget.setErrors = self.setErrors
                raw = widget.extract()
                if raw is not colander.null:
                    value = widget.field.deserialize(raw)

                if value is NOT_CHANGED:
                    value = sm.getMultiAdapter(
                        (context, field), IDataManager).query()

            except colander.Invalid, error:
                errors.append(error)

            data[widget.__name__] = value

        # validate agains top level SchemaNode
        for node in self.form.fields.schemas:
            try:
                node.deserialize(data)
            except colander.Invalid, error:
                for err in error.children:
                    errors.append(err)

                if error.msg is not None:
                    errors.append(error)

        # call form validation
        self.form.validate(data, errors)

        # prepare errors
        for error in errors:
            widget = self.get(error.node.name)

            if widget is None:
                err = Error(error, error.msg)
            else:
                err = WidgetError(error, error.msg, widget)

            if widget is not None and widget.error is not None:
                continue

            errorViews.append(err)

            if self.setErrors and widget is not None:
                widget.error = err

        if self.setErrors:
            self.errors = errorViews

        return data, errorViews
