from distutils.core import setup

setup(
    name='django_server_conn_pool',
    packages=['django_server_conn_pool'],
    version='0.1',
    license='MIT',
    description='DB Server Connection Pooling with Django and SQL Alchemy',
    author='raju',
    author_email='ramisetty.prudhviraju@gmail.com',
    url='https://github.com/prudhviraju-011/django-server-conn-pool',
    download_url='https://github.com/prudhviraju-011/django-server-conn-pool/archive/v_01.tar.gz',
    keywords=['conn-pool'],
    classifiers=(
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ),
    install_requires=[
        'Django>2.0.0',
        'SQLAlchemy>=1.2.7',
    ]
)
