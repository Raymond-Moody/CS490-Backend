Ensure you have python and pip installed
From the project folder, run 'python -m venv venv'
Run '. venv/bin/activate' to enable the virtual environment
Run 'pip install -r requirements.txt'

Ensure that your mysql server is started
In backend/backend/settings.py, edit the DATABASES variable:
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
Change NAME to the name of your sakila database. 
Change HOST and PORT to match the host address and port number your server is running on.
Change USER and PASSWORD to match a mysql user that can access and modify the database.
For unit testing change TEST NAME to the name of a mysql database with the default sakila data.

Then run 'python backend/manage.py runserver' to start the server at http://localhost:8000.
