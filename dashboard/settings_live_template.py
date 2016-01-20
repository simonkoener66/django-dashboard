import  os
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'dashboard',
        'USER': 'root',
        'PASSWORD': '',
        'HOST': '127.0.0.1',
        'PORT': '3306'
    },
    'am': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'am',
        'USER': 'root',
        'PASSWORD': '',
        'HOST': '127.0.0.1',
        'PORT': '3306'
    }
}

STATIC_ROOT = os.path.join(BASE_DIR, '../assets')

REGIONAL_DATA = {
    'North America': ['USA', 'CAN'],
    'Latin America': ['MEX', 'BRA', 'VEN'],
    'EMEA': ['GBR', 'FRA', 'SAU'],
    'APAC': ['JPN', 'KOR', 'CHN', 'AUS'],
    'Other': ['ZWE', 'HTI']
}
FORCE_SCRIPT_NAME = ''