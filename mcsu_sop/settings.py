"""
Django settings for mcsu_sop project.
This is the main settings file that contains all configuration for the project.
Including security, database, static/media files, and installed apps configurations.
"""

from pathlib import Path
from datetime import timedelta
import environ
import os

env = environ.Env()

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# SECURITY WARNING: keep the secret key used in production secret!
# In production, this should be set via environment variable
SECRET_KEY = os.environ.get('DJANGO_SECRET_KEY' , 'django-insecure-f-uc^eltp31ri0j4jo!yp^9v$)7v7l4*l_+5%-rie9k21gc59h')

# SECURITY WARNING: don't run with debug turned on in production!
# Should be False in production
DEBUG = os.environ.get('DJANGO_DEBUG' , 'True') == 'True'

# Add your domain names here
ALLOWED_HOSTS = ['*']

# Application definition
# Grouped by purpose for better organization
DJANGO_APPS = [
    'jazzmin',
    'corsheaders',
    'django_celery_results',
    # Material admin configuration
    'django.contrib.admin' ,
    'django.contrib.auth' ,
    'django.contrib.contenttypes' ,
    'django.contrib.sessions' ,
    'django.contrib.messages' ,
    'django.contrib.staticfiles' ,
    "django_celery_beat",
    'django_crontab',
    'django_q',
    # 'django_cron',
    "quiz_app",
    'import_export',
    'rest_framework',
]

CRONJOBS = [
    ('*/5 * * * *', 'initiatives.cronscript.myCron'),
    
]


THIRD_PARTY_APPS = [
    'ckeditor' ,  # Rich text editor
    'ckeditor_uploader' ,  # CKEditor file upload handling
    'graphene_django',
    'django_filters',
]

# Custom project apps
PROJECT_APPS = [
    'initiatives' ,
    'monitoring' ,
    'users' ,
    'program_design' ,
    'governance' ,
    'documentation' ,
    'sustainability' ,
    'job_portal',
]

INSTALLED_APPS = DJANGO_APPS + THIRD_PARTY_APPS + PROJECT_APPS

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.security.SecurityMiddleware' ,
    'django.contrib.sessions.middleware.SessionMiddleware' ,
    'django.middleware.common.CommonMiddleware' ,
    'django.middleware.csrf.CsrfViewMiddleware' ,
    'django.contrib.auth.middleware.AuthenticationMiddleware' ,
    'django.contrib.messages.middleware.MessageMiddleware' ,
    'django.middleware.clickjacking.XFrameOptionsMiddleware' ,
]

ROOT_URLCONF = 'mcsu_sop.urls'


CORS_ALLOWED_ORIGINS = [
    "http://localhost:3000",
]

CORS_ALLOW_CREDENTIALS = True

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates' ,
        'DIRS': [BASE_DIR / 'templates'] ,  # Added templates directory
        'APP_DIRS': True ,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug' ,
                'django.template.context_processors.request' ,
                'django.contrib.auth.context_processors.auth' ,
                'django.contrib.messages.context_processors.messages' ,

            ] ,
        } ,
    } ,
]

WSGI_APPLICATION = 'mcsu_sop.wsgi.application'

# Database configuration
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3' ,
        'NAME': BASE_DIR / 'db.sqlite3' ,
        # Add these recommended settings for SQLite
        'ATOMIC_REQUESTS': True ,
        'CONN_MAX_AGE': 600 ,  # Connection persistence in seconds
    }
}

# Password validation
AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator' ,
    } ,
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator' ,
        'OPTIONS': {
            'min_length': 8 ,  # Require minimum 8 characters
        }
    } ,
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator' ,
    } ,
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator' ,
    } ,
]

# Internationalization
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

# Static files configuration
# STATIC_URL = '/static/'
# STATIC_ROOT = BASE_DIR / 'staticfiles'
# STATICFILES_DIRS = [
#     BASE_DIR / 'static'
# ]

# # Media files
# MEDIA_URL = '/media/'
# MEDIA_ROOT = BASE_DIR / 'media'

STATIC_URL = '/static/'
STATIC_ROOT='/home/gazrhktx/public_html/gazrastatic/static'
STATICFILES_DIRS = [BASE_DIR / "static"]

MEDIA_ROOT = ("/home/gazrhktx/public_html/gazramedia/media/")
MEDIA_URL = '/media/'

# Create the static directory if it doesn't exist
STATIC_DIR = BASE_DIR / 'static'
STATIC_DIR.mkdir(exist_ok=True)

# Default primary key field type
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# CKEditor configurations
CKEDITOR_UPLOAD_PATH = 'uploads/'
CKEDITOR_CONFIGS = {
    'default': {
        'toolbar': 'full' ,
        'height': 300 ,
        'width': '100%' ,
    } ,
    'basic': {
        'toolbar': [
            ['Bold' , 'Italic' , 'Underline'] ,
            ['NumberedList' , 'BulletedList' , '-' , 'Outdent' , 'Indent'] ,
            ['Link' , 'Unlink'] ,
            ['RemoveFormat' , 'Source']
        ] ,
        'height': 200 ,
        'width': '100%' ,
    } ,
    'advanced': {
        'toolbar': 'full' ,
        'height': 400 ,
        'width': '100%' ,
        'extraPlugins': ','.join([
            'uploadimage' , 'uploadfile' , 'image2' , 'clipboard' ,
            'div' , 'autolink' , 'autoembed' , 'embedsemantic' ,
            'autogrow' , 'widget' , 'lineutils' , 'dialog' ,
            'dialogui' , 'elementspath'
        ]) ,
    }
}

# Security Settings
if not DEBUG:
    # HTTPS/SSL
    SECURE_SSL_REDIRECT = True
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    SECURE_BROWSER_XSS_FILTER = True
    SECURE_CONTENT_TYPE_NOSNIFF = True
    X_FRAME_OPTIONS = 'DENY'
    SECURE_HSTS_SECONDS = 31536000  # 1 year
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_HSTS_PRELOAD = True

# Cache settings (using local memory cache)
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache' ,
        'LOCATION': 'unique-snowflake' ,
    }
}

JAZZMIN_SETTINGS = {
    # title of the window (Will default to current_admin_site.site_title if absent or None)
     "site_title": "MCSU SOP Admin",

    # Title on the login screen (19 chars max) (defaults to current_admin_site.site_header if absent or None)
    "site_header": "MCSU SOP",

    # Title on the brand (19 chars max) (defaults to current_admin_site.site_header if absent or None)
    "site_brand": "MCSU SOP",

    # Logo to use for your site, must be present in static files, used for brand on top left
    "site_logo": "images/mcsu-logo.webp",

    # Logo to use for your site, must be present in static files, used for login form logo (defaults to site_logo)
    "login_logo": "images/mcsu-logo.webp",

    # Logo to use for login form in dark theme (defaults to login_logo)
    "login_logo_dark": "images/mcsu-logo.webp",

    # CSS classes that are applied to the logo above
    "site_logo_classes": "img-circle",

    # Relative path to a favicon for your site, will default to site_logo if absent (ideally 32x32 px)
    "site_icon": "images/mcsu-logo.webp",

    # Copyright on the footer
    "copyright": "MCSU SOP Ltd",

    # List of model admins to search from the search bar, search bar omitted if excluded
    # If you want to use a single search field you dont need to use a list, you can use a simple string
    "search_model": ["auth.User", "auth.Group"],

    # Field name on user model that contains avatar ImageField/URLField/Charfield or a callable that receives the user
    "user_avatar": None,

    ############
    # Top Menu #
    ############

    # Links to put along the top menu
    "topmenu_links": [

        # Url that gets reversed (Permissions can be added)
        {"name": "Home",  "url": "admin:index", "permissions": ["auth.view_user"]},

        # external url that opens in a new window (Permissions can be added)
        {"name": "Support", "url": "https://github.com/farridav/django-jazzmin/issues", "new_window": True},

        # model admin to link to (Permissions checked against model)
        {"model": "auth.User"},

        # App with dropdown menu to all its models pages (Permissions checked against models)
        {"app": "books"},
    ],

    #############
    # User Menu #
    #############

    # Additional links to include in the user menu on the top right ("app" url type is not allowed)
    "usermenu_links": [
        {"name": "Support", "url": "https://github.com/farridav/django-jazzmin/issues", "new_window": True},
        {"model": "auth.user"}
    ],

    #############
    # Side Menu #
    #############

    # Whether to display the side menu
    "show_sidebar": True,

    # Whether to aut expand the menu
    "navigation_expanded": True,

    # Hide these apps when generating side menu e.g (auth)
    "hide_apps": [],

    # Hide these models when generating side menu (e.g auth.user)
    "hide_models": [],

    # List of apps (and/or models) to base side menu ordering off of (does not need to contain all apps/models)
    "order_with_respect_to": ["auth", "books", "books.author", "books.book"],

    # Custom icons for side menu apps/models See https://fontawesome.com/icons?d=gallery&m=free&v=5.0.0,5.0.1,5.0.10,5.0.11,5.0.12,5.0.13,5.0.2,5.0.3,5.0.4,5.0.5,5.0.6,5.0.7,5.0.8,5.0.9,5.1.0,5.1.1,5.2.0,5.3.0,5.3.1,5.4.0,5.4.1,5.4.2,5.13.0,5.12.0,5.11.2,5.11.1,5.10.0,5.9.0,5.8.2,5.8.1,5.7.2,5.7.1,5.7.0,5.6.3,5.5.0,5.4.2
    # for the full list of 5.13.0 free icon classes
    "icons": {
    # Auth Related
    "auth": "fas fa-users-cog",
    "auth.user": "fas fa-user",
    "auth.Group": "fas fa-users",

        # Initiatives Section
    "initiatives": "fas fa-lightbulb",  # Main app icon - represents ideas/initiatives
    "initiatives.initiative": "fas fa-project-diagram",  # For main initiative model
    "initiatives.brainstormingsession": "fas fa-brain",  # For brainstorming sessions
    "initiatives.communityfeedback": "fas fa-comments",  # For community feedback
    "initiatives.needsanalysis": "fas fa-search-plus",  # For needs analysis
    "initiatives.communitymapping": "fas fa-map-marked-alt",  # For community mapping
    "initiatives.task": "fas fa-tasks",  # For tasks
    "initiatives.stakeholder": "fas fa-handshake",  # For stakeholders
    "initiatives.event": "fas fa-calendar-day",  # For events
    "initiatives.feedback": "fas fa-comment-dots",  # For feedback
    "initiatives.risk": "fas fa-exclamation-circle",  # For risks
    "initiatives.kpi": "fas fa-tachometer-alt",  # For KPIs
    "initiatives.milestone": "fas fa-flag",  # For milestones
    "initiatives.budget": "fas fa-money-bill-wave",  # For budget
    "initiatives.executionlog": "fas fa-clipboard-list",

    # Monitoring App
    "monitoring": "fas fa-chart-line",  # Main app icon - represents monitoring/tracking
    "monitoring.kpimetric": "fas fa-tachometer-alt",  # For KPI metrics
    "monitoring.metricprogress": "fas fa-chart-bar",  # For metric progress tracking
    "monitoring.participantfeedback": "fas fa-comment-alt",  # For participant feedback
    "monitoring.monitoringcheckin": "fas fa-clipboard-check",  # For check-ins
    "monitoring.datacollectiontemplate": "fas fa-file-alt",  # For data collection templates
    "monitoring.monitoringreport": "fas fa-file-invoice",  # For monitoring reports
    "monitoring.employmenttracking": "fas fa-briefcase",  # For employment tracking
    "monitoring.skillassessment": "fas fa-graduation-cap",  # For skill assessment
    "monitoring.weeklyprogress": "fas fa-calendar-week",  # For weekly progress
    "monitoring.quarterlyimpactreview": "fas fa-chart-pie",  # For quarterly reviews
    "monitoring.financialtracking": "fas fa-money-bill-trend-up",

    # Reporting App
    "reporting": "fas fa-file-alt",
    "reporting.document": "fas fa-file-alt",
    "reporting.report": "fas fa-scroll",
    "reporting.analysis": "fas fa-chart-pie",
    "reporting.recommendation": "fas fa-lightbulb",

    # Users App
    "users": "fas fa-users",
    "users.profile": "fas fa-id-card",
    "users.role": "fas fa-user-tag",
    "users.permission": "fas fa-key",
    "users.department": "fas fa-building",

    # Program Design App
    "program_design": "fas fa-pencil-ruler",  # Main app icon - represents program design/planning
    "program_design.diversitymetric": "fas fa-users",  # For diversity metrics tracking
    "program_design.cocreationworkshop": "fas fa-user-friends",  # For co-creation workshops
    "program_design.inclusiontraining": "fas fa-hands-helping",  # For inclusion training
    "program_design.culturalsensitivityaudit": "fas fa-search",  # For cultural sensitivity audits
    "program_design.programfeedback": "fas fa-comment-dots",

    # Governance App
    "governance": "fas fa-landmark",  # Main app icon - represents governance/institution
    "governance.teamrole": "fas fa-users-cog",  # Team roles and responsibilities
    "governance.resourceallocation": "fas fa-hand-holding-usd",  # Resource management
    "governance.projecttimeline": "fas fa-calendar-alt",  # Project timeline tracking
    "governance.riskassessment": "fas fa-exclamation-triangle",  # Risk assessment/management
    "governance.governancebody": "fas fa-sitemap",  # Organizational structure
    "governance.governancemeeting": "fas fa-handshake",  # Meetings and discussions
    "governance.csrproposal": "fas fa-file-signature",  # CSR proposals/documents
    "governance.governancereport": "fas fa-chart-line",

    # Documentation App
    "documentation": "fas fa-folder",  # Main app icon
    "documentation.programlogbook": "fas fa-book-reader",  # For logging program activities
    "documentation.documenttemplate": "fas fa-file-invoice",  # For document templates
    "documentation.impactstory": "fas fa-star-half-alt",  # For impact stories
    "documentation.csrreport": "fas fa-file-contract",  # For CSR reports
    "documentation.progressreport": "fas fa-chart-line",  # For progress reports
    "documentation.sdgmapping": "fas fa-map-marked-alt",  # For SDG mappings
    "documentation.sdgprogress": "fas fa-chart-bar",  # For SDG progress tracking
    "documentation.reportdistribution": "fas fa-share-alt",  # For report distribution
    "documentation.documentationreview": "fas fa-clipboard-check",

    # Sustainability App
    "sustainability": "fas fa-seedling",  # Main app icon - represents sustainability/growth
    "sustainability.replicableprogram": "fas fa-copy",  # For replicable programs
    "sustainability.programreplication": "fas fa-code-branch",  # For program replications
    "sustainability.corporatepartner": "fas fa-handshake",  # For corporate partners
    "sustainability.fundingproposal": "fas fa-file-invoice-dollar",  # For funding proposals
    "sustainability.annualbudget": "fas fa-money-bill-trend-up",  # For annual budgets
    "sustainability.budgettracking": "fas fa-chart-line",  # For budget tracking
    "sustainability.franchisemodel": "fas fa-store",  # For franchise models
    "sustainability.franchiselocation": "fas fa-store-alt",  # For franchise locations
    "sustainability.product": "fas fa-box",  # For products
    "sustainability.consultingservice": "fas fa-chalkboard-teacher",  # For consulting services
    "sustainability.consultingengagement": "fas fa-user-tie",  # For consulting engagements
    "sustainability.socialenterprisemetrics": "fas fa-chart-mixed",  # For social enterprise metrics
    "sustainability.sustainabilityreport": "fas fa-file-contract",

    # Default icons for app and model levels
    "default_icon_parents": "fas fa-folder",
    "default_icon_children": "fas fa-file"
},

    # Icons that are used when one is not manually specified
    "default_icon_parents": "fas fa-chevron-circle-right",
    "default_icon_children": "fas fa-circle",

    #################
    # Related Modal #
    #################
    # Use modals instead of popups
    "related_modal_active": False,

    #############
    # UI Tweaks #
    #############
    # Relative paths to custom CSS/JS scripts (must be present in static files)
    "custom_css": None,
    "custom_js": None,
    # Whether to link font from fonts.googleapis.com (use custom_css to supply font otherwise)
    "use_google_fonts_cdn": True,
    # Whether to show the UI customizer on the sidebar
    "show_ui_builder": True,

    ###############
    # Change view #
    ###############
    # Render out the change view as a single form, or in tabs, current options are
    # - single
    # - horizontal_tabs (default)
    # - vertical_tabs
    # - collapsible
    # - carousel
    "changeform_format": "horizontal_tabs",
    # override change forms on a per modeladmin basis
    "changeform_format_overrides": {"auth.user": "collapsible", "auth.group": "vertical_tabs"},
}

# Jazzmin UI Customizer settings
JAZZMIN_UI_TWEAKS = {
    "navbar_small_text": False,
    "footer_small_text": False,
    "body_small_text": False,
    "brand_small_text": False,
    "brand_colour": False,
    "accent": "accent-purple",
    "navbar": "navbar-purple navbar-light",
    "no_navbar_border": True,
    "navbar_fixed": False,
    "layout_boxed": False,
    "footer_fixed": False,
    "sidebar_fixed": True,
    "sidebar": "sidebar-light-purple",
    "sidebar_nav_small_text": False,
    "sidebar_disable_expand": False,
    "sidebar_nav_child_indent": True,
    "sidebar_nav_compact_style": True,
    "sidebar_nav_legacy_style": False,
    "sidebar_nav_flat_style": True,
    "theme": "default",
    "dark_mode_theme": None,
    "button_classes": {
        "primary": "btn-primary",
        "secondary": "btn-secondary",
        "info": "btn-info",
        "warning": "btn-warning",
        "danger": "btn-danger",
        "success": "btn-success"
    },
    "actions_sticky_top": False,
    "custom_js": "js/custom.js",
}
JAZZMIN_SETTINGS["custom_css"] = "css/custom.css"

# Email configuration (replace with your email settings)
# EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
# EMAIL_HOST = os.environ.get("EMAIL_HOST")
# EMAIL_PORT = os.environ.get("EMAIL_PORT")
# EMAIL_HOST_USER = os.environ.get("EMAIL_HOST_USER")
# EMAIL_HOST_PASSWORD = os.environ.get("EMAIL_HOST_PASSWORD")
# EMAIL_USE_SSL = True  
# EMAIL_USE_TLS = False  
# DEFAULT_FROM_EMAIL = os.environ.get("EMAIL_HOST_USER")

# Its Work

# EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
# EMAIL_HOST = 'smtp.gmail.com'
# EMAIL_PORT = 587 
# EMAIL_USE_TLS = True
# EMAIL_USE_SSL = False
# EMAIL_HOST_USER = 'noreply.studystreak@gmail.com'  
# EMAIL_HOST_PASSWORD = 'sypowsabvnbqjhrv'
# DEFAULT_FROM_EMAIL = 'noreply.studystreak@gmail.com'

EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
# EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
EMAIL_HOST='smtpout.secureserver.net'
EMAIL_PORT = 465 
EMAIL_USE_TLS = False
EMAIL_USE_SSL = True
EMAIL_HOST_USER='support@gazra.org' 
EMAIL_HOST_PASSWORD = 'Gazra@123#'
DEFAULT_FROM_EMAIL = 'support@gazra.org'



# Logging configuration
LOGGING = {
    'version': 1 ,
    'disable_existing_loggers': False ,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {process:d} {thread:d} {message}' ,
            'style': '{' ,
        } ,
    } ,
    'handlers': {
        'file': {
            'level': 'ERROR' ,
            'class': 'logging.FileHandler' ,
            'filename': BASE_DIR / 'debug.log' ,
            'formatter': 'verbose' ,
        } ,
    } ,
    'loggers': {
        'django': {
            'handlers': ['file'] ,
            'level': 'ERROR' ,
            'propagate': True ,
        } ,
    } ,
}

# settings.py
# settings.py

# Celery Configuration
# Celery settings
CELERY_RESULT_BACKEND = 'django-db'  # Use Django database as result backend
CELERY_BROKER_URL = 'redis://localhost:6379/0'  # Redis as the broker
CELERY_ACCEPT_CONTENT = ['json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'
CELERY_TIMEZONE = 'UTC'
CELERY_BROKER_URL = 'redis://localhost:6379/0'
CELERY_RESULT_BACKEND = 'redis://localhost:6379/0'
CELERY_BROKER_CONNECTION_RETRY_ON_STARTUP = True  # Add here

Q_CLUSTER = {
    'name': 'DjangORM',
    'workers': 4,
    'timeout': 90,
    'retry': 120,
    'queue_limit': 50,
    'bulk': 10,
    'orm': 'default',
    'sync': False,
    'guard_cycle': 60  
}

# Q_CLUSTER = {
#     'retry': 60,  
#     'timeout': 30,  
#     'catch_up': False,
#     'max_attempts': 5,
#     'save_limit': 250,
# }


DATA_UPLOAD_MAX_NUMBER_FIELDS = 10000  # Increase max number of fields
FILE_UPLOAD_MAX_MEMORY_SIZE = 26214400  # Increase file upload size (25MB)