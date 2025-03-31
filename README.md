# pearmonie-MLsuggestionAPI
A robust API that contains user authentication management systems integrated with a machine learning model that can suggest contents for users based on their interaction with contents.
<<<<<<< HEAD
=======

PROCEDURES FOR SETUP

1. Create a virtual environment and activate it. e.g Use command pyenv virtualenv 3.10 *name_of_env to create a virtual environment and pyenv activate **name_of_env to activate.
2. Clone the repository
3. cd into the pearmonie folder.
4. Ensuring a python==3.10.6, install all the packages in the requirements.txt file. (Use pip install -r requirements.txt)
5. run the server with python manage.py runserver
6. Start Celery with command celery -A config worker --loglevel=info > celerylogs.txt. Ensure redis has been installed. You can start redis server with command redis-server
7. You can access endpoints lists and documentation via the endpoint http://localhost:8000/api/doc
>>>>>>> df6afdf (Added feature for user registration and authentication. Added preliminary feature to allow for user subscriptions. Pre-trained Machine learning model with generated data from the database. Added feature for continous training with celery. Added installation instructions in README.md file. Integrated swagger for API documentation)
