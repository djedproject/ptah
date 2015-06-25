""" ptah settings """
import pytz
import logging
import sqlalchemy
import translationstring
from pyramid.events import ApplicationCreated

import ptah
from ptah import settings

_ = translationstring.TranslationStringFactory('ptah')

log = logging.getLogger('ptah')


ptah.register_settings(
    ptah.CFG_ID_PTAH,

    ptah.form.BoolField(
        'auth',
        title = _('Authentication policy'),
        description = _('Enable authentication policy.'),
        default = False),

    ptah.form.TextField(
        'secret',
        title = _('Authentication policy secret'),
        description = _('The secret (a string) used for auth_tkt '
                        'cookie signing'),
        default = '',
        tint = True),

    ptah.form.TextField(
        'hashalg',
        title = _('Authentication policy hash algorithm'),
        description = _('The hash algorithm used for auth_tkt '
                        'cookie generation'),
        default = 'sha512'),

    ptah.form.TextField(
        'manage',
        title = 'Ptah manage id',
        default = 'ptah-manage'),

    ptah.form.LinesField(
        'managers',
        title = 'Manage login',
        description = 'List of user logins with access rights to '\
                            'ptah management ui.',
        default = ()),

    ptah.form.TextField(
        'manager_role',
        title = 'Manager role',
        description = 'Specific role with access rights to ptah management ui.',
        default = ''),

    ptah.form.LinesField(
        'disable_modules',
        title = 'Hide Modules in Management UI',
        description = 'List of modules names to hide in manage ui',
        default = ()),

    ptah.form.LinesField(
        'enable_modules',
        title = 'Enable Modules in Management UI',
        description = 'List of modules names to enable in manage ui',
        default = ()),

    ptah.form.LinesField(
        'disable_models',
        title = 'Hide Models in Model Management UI',
        description = 'List of models to hide in model manage ui',
        default = ()),

    ptah.form.ChoiceField(
        'pwd_manager',
        title = 'Password manager',
        description = 'Available password managers '\
            '("plain", "ssha", "bcrypt")',
        vocabulary = ptah.form.Vocabulary(
            "plain", "ssha",),
        default = 'plain'),

    ptah.form.IntegerField(
        'pwd_min_length',
        title = 'Length',
        description = 'Password minimium length.',
        default = 5),

    ptah.form.BoolField(
        'pwd_letters_digits',
        title = 'Letters and digits',
        description = 'Use letters and digits in password.',
        default = False),

    ptah.form.BoolField(
        'pwd_letters_mixed_case',
        title = 'Letters mixed case',
        description = 'Use letters in mixed case.',
        default = False),

    ptah.form.LinesField(
        'db_skip_tables',
        title = 'Skip table creation',
        description = 'Do not create listed tables during data population.',
        default = ()),

    ptah.form.LinesField(
        'default_roles',
        title = 'Default roles',
        description = 'List of default assigned roles for all principals.',
        default = ()),

    title = _('Ptah settings'),
)


def enable_manage(cfg, name='ptah-manage', access_manager=None,
                  managers=None, manager_role=None,
                  disable_modules=None, enable_modules=None):
    """Implementation for pyramid `ptah_init_manage` directive """
    def action(cfg, name, access_manager,
               managers, manager_role, disable_modules):
        PTAH = cfg.ptah_get_settings(ptah.CFG_ID_PTAH)

        PTAH['manage'] = name
        if managers is not None:
            PTAH['managers'] = managers
        if manager_role is not None:
            PTAH['manager_role'] = manager_role
        if disable_modules is not None:
            PTAH['disable_modules'] = disable_modules
        if enable_modules is not None:
            PTAH['enable_modules'] = enable_modules

        if access_manager is None:
            access_manager = ptah.manage.PtahAccessManager(cfg.registry)

        ptah.manage.set_access_manager(access_manager, cfg.registry)

    cfg.add_route('ptah-manage', '/{0}/*traverse'.format(name),
                  factory=ptah.manage.PtahManageRoute, use_global_views=True)
    cfg.action(
        'ptah.ptah_manage', action,
        (cfg, name, access_manager,
         managers, manager_role, disable_modules), order=999999+1)


def initialize_sql(cfg, prefix='sqlalchemy.'):
    def action(cfg):
        PTAH = cfg.ptah_get_settings(ptah.CFG_ID_PTAH)
        PTAH['sqlalchemy_initialized'] = True

    cfg.include('pyramid_sqlalchemy')
    cfg.action('ptah.initalize_sql', action, (cfg,))

    # check_version
    from ptah import migrate
    cfg.add_subscriber(migrate.check_version, ApplicationCreated)


@ptah.subscriber(ApplicationCreated)
def starting(ev):
    settings.load_dbsettings()
