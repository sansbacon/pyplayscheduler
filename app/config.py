import os

class ProdConfig:
    # Database configuration
    API_TOKEN = os.environ.get('PROD_KEY_SECRET')
    WTF_CSRF_SECRET_KEY = os.environ.get('PROD_KEY_SECRET')

class DevConfig:
    # Database configuration
    API_TOKEN = os.environ.get('DEV_KEY_SECRET')
    WTF_CSRF_SECRET_KEY = os.environ.get('DEV_KEY_SECRET')

class TestConfig:
    # Database configuration
    API_TOKEN = os.environ.get('TEST_KEY_SECRET')
    WTF_CSRF_SECRET_KEY = os.environ.get('TEST_KEY_SECRET')

config = {
    'dev': DevConfig,
    'test': TestConfig,
    'prod': ProdConfig
}