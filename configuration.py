import datetime
from google.appengine.ext import db

__author__ = 'simonhutton'


class Configuration(db.Model):
    CACHE_TIME = datetime.timedelta(minutes=5)

    _INSTANCE = None
    _INSTANCE_AGE = None

    public_stripe_key = db.StringProperty()
    private_stripe_key = db.StringProperty()
    web_debug = db.BooleanProperty()


    @classmethod
    def get_instance(cls):
        now = datetime.datetime.now()
        if not cls._INSTANCE or cls._INSTANCE_AGE + cls.CACHE_TIME < now:
            cls._INSTANCE = cls.get_or_insert('config')

            if not cls._INSTANCE.public_stripe_key:
                cls._INSTANCE.public_stripe_key = 'pk_SPjp98jtIuyUn3t6DJtvZSc5lBeqr'
                cls._INSTANCE.private_stripe_key = 'c1r52uIFDTaniTJc29tMbGGo0CGJeDtu'
                cls._INSTANCE.web_debug = True

                db.put(cls._INSTANCE)

            cls._INSTANCE_AGE = now
        return cls._INSTANCE

