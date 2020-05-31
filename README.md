### Django-server-conn-pool
MySQL Connection Pooling with Django(>2.0.0) and SQLAlchemy(>=1.2.7).

Inspired from the package 'django_conn_pool' which sets up connection pool for django project using SQLAlchemy

Maintaining Single Connection pool may result in Read connections exhausting all connections.

Its necessary to maintain seperate connection pool for each server



### Usage
```
pip install django-server-conn-pool

```

settings.py

```
SQLALCHEMY_QUEUEPOOL1 = {
    'pool_size': 10,
    'max_overflow': 10,
    'timeout': 5,
    'recycle': 119,
}

SQLALCHEMY_QUEUEPOOL2 = {
    'pool_size': 15,
    'max_overflow': 10,
    'timeout': 5,
    'recycle': 119,
}
 
DATABASES = {
    'default': {
        'ENGINE': 'django_server_conn_pool.mysql',
        'HOST': '127.0.0.1',
        'NAME': 'xxx',
        'USER': 'xxx',
        'PASSWORD': 'xxx',
        'PORT': 3306,
        'QUEUE_POOL': SQLALCHEMY_QUEUEPOOL1
    },
    'slave': {
        'ENGINE': 'django_server_conn_pool.mysql',
        'HOST': '127.0.0.1',
        'NAME': 'xxx',
        'USER': 'xxx',
        'PASSWORD': 'xxx',
        'PORT': 3306,
        'QUEUE_POOL': SQLALCHEMY_QUEUEPOOL2
    }
}
```



