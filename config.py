import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY', 'RADMOBILE49531')
    SQLALCHEMY_TRACK_MODIFICATIONS = False

class DevelopmentConfig(Config):
    SQLALCHEMY_DATABASE_URI = 'sqlite:///development.db'

class ProductionConfig(Config):
    SQLALCHEMY_DATABASE_URI = os.environ.get('SQLALCHEMY_DATABASE_URI')

config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig
}
