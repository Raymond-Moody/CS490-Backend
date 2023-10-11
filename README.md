Ensure you have python and pip installed\
Ensure the requirements for mysqlclient are installed on your machine as described [here](https://github.com/PyMySQL/mysqlclient#install)

From the project folder, run `python -m venv venv`\
Run `. venv/bin/activate` to enable the virtual environment\
Run `pip install -r requirements.txt`

In backend/backend/settings.py, edit the DATABASES variable:
```
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'sakila',
        'USER' : 'django',
        'PASSWORD' : 'password1',
        'HOST' : 'localhost',
        'PORT' : '3306',
        'TEST': {
            'NAME': 'test_sakila',
        },
    },
}
```
Change NAME to the name of your sakila database. \
Change HOST and PORT to match the host address and port number your server is running on.\
Change USER and PASSWORD to match a mysql user that can access and modify the database.\

For unit testing change TEST NAME to the name of a mysql database with the default sakila data. This database must also be accessible by USER.\
The test database can be the same as the default database.

Ensure that your mysql server is started.\
From the mysql client, please run 'ALTER TABLE address DROP COLUMN location' for both the default and test databases. 

Run `python backend/manage.py test` to run the unit tests.\
Run `python backend/manage.py runserver` to start the server at http://localhost:8000.
