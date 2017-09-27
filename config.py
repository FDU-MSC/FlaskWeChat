import os


class Config:
    DEBUG = True
    SQLALCHEMY_COMMIT_ON_TEARDOWN = True
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_DATABASE_URI = "mysql+pymysql://root:" + \
        os.environ.get('DATABASE_PASSWORD') + "@" + \
        os.environ.get('DATABASE_SERVER') + "/WeChat?charset=utf8"
    MAIL_SERVER = 'smtp.exmail.qq.com'
    MAIL_PORT = 465
    MAIL_USE_TLS = False
    MAIL_USE_SSL = True
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
    FLASKY_MAIL_SUBJECT_PREFIX = '[复旦微软俱乐部]'
    FLASKY_MAIL_SENDER = "fdumstc@pentahack.com"

    @staticmethod
    def init_app(app):
        pass


config = {
    'development': Config,
    'production': Config,
    'default': Config
}
