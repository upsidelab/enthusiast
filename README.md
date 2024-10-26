# E-COMMERCE LLM

## About
This is POC for AI tailored for E-Commerce needs.

There are plenty of gen AI tools showing up on the market, however I haven’t seen anything specific to E-Commerce. 
There are a few use cases that can be built on top of gen AI, to support their teams and customers. 

The ECL tool consists of a document index, that’s aligned to the E-Commerce data structures, and a set of LLM-based APIs that will allow querying it in different ways.

## POC Environment
* Continuous deployment github/main => render.com

## Style
* Python coding style conventions: [TBD]
* Branching strategy: feature branching as per [this gentleman's speech](https://www.youtube.com/watch?v=U_IFGpJDbeU)
* PRs and Commits: we follow [Conventional Commits](https://www.conventionalcommits.org/en/v1.0.0-beta.2/) pattern.

## Local installation guide (MAC)
In a nutshell:
* Install database with pgvector extension
* Get your OpenAI key
* Set environment variables in .zshrc file
* Run hello world!
* Have fun

### Local environment variables to be set
In ~/.zshrc file set variables used by ECL.

Note: ECL_DJANGO_ALLOWED_HOSTS is a list, below is a sample for localhost.

Provide parameters of DB you're using (you may install it locally, or use a docker container, or... sky is the limit)
```
export ECL_DB_NAME='db-name'
export ECL_DB_USER='db-user'
export ECL_DB_PASSWORD='db-pass'
export ECL_DB_HOST='127.0.0.1'
export ECL_DB_PORT='port'
export ECL_DJANGO_SECRET_KEY='your-secret-key'
export ECL_DJANGO_DEBUG='True'
export ECL_DJANGO_ALLOWED_HOSTS='["127.0.0.1"]'
# To access django templates (to be deprecated in future) set up your passwords:
export ECL_BASICAUTH_USERNAME='app-user-on-environment'
export ECL_BASICAUTH_PASSWORD='your-pass-on-environment'
```

### Setup database with pgvector extension
Components
* Install Python 3.12.6 and pip
* Install Postgres 16
* Install [pgvector](https://github.com/pgvector/pgvector)

You may also get [Docker image](https://github.com/pgvector/pgvector) with postgresql and pgvector.
Note: in below example PosgreSQL is exposed locally over the port 9432
```
docker pull pgvector/pgvector:pg16
docker run -p 127.0.0.1:9432:5432 --name ECL -e POSTGRES_PASSWORD=ecl -d b96b4bb5ce42
```

### Create ECL database
Connect with psql to your PostgreSQL server
```
Last login: Fri Sep 20 17:28:30 on ttys002
/Library/PostgreSQL/16/scripts/runpsql.sh; exit
kuba@totem ~ % /Library/PostgreSQL/16/scripts/runpsql.sh; exit
Server [localhost]: 
Database [postgres]: 
Port [5432]: 9432
Username [postgres]: 
Password for user postgres: 
psql (16.4, server 16.3 (Debian 16.3-1.pgdg120+1))
Type "help" for help.

```

Create database
```
postgres=# CREATE DATABASE ecl;
CREATE DATABASE
```

Create schema
```
ecl=# create schema ecl;
CREATE SCHEMA
```

### Enable vector extension on your database
Connect to new ecl database
```
postgres=# \connect ecl
psql (16.4, server 16.3 (Debian 16.3-1.pgdg120+1))
You are now connected to database "ecl" as user "postgres".
```
Create extension
```
ecl=# CREATE EXTENSION vector;
CREATE EXTENSION
```

If you're using **PostgreSQL** - you have to do the same also template1 database.

[PostgreSQL engine is using template1](https://www.postgresql.org/docs/current/manage-ag-templatedbs.html#MANAGE-AG-TEMPLATEDBS) when creating new databases.
When django creates new database for [unit testing](https://docs.djangoproject.com/en/5.1/topics/testing/overview/#running-tests), we need to make sure that all extensions will be created before tests run. Hence, you have to configure your PostgreSQL instance to create vector extension on each newly created database.
```
template1=# CREATE EXTENSION vector;
CREATE EXTENSION
```

### Integrate with OpenAI
* Obtain your project [OpenAI API key](https://platform.openai.com/api-keys)
* [Store your key](https://help.openai.com/en/articles/5112595-best-practices-for-api-key-safety) in .zshrc file (replace *Your-Key* with your project API key value)
  ```
  echo "export OPENAI_API_KEY='Your-Key'" >> ~/.zshrc
  ```

* Verify integration 
  
  Run below Open AI Hello World Python code. Feel free to experiment with haiku, but remember about OpenAI project's cost limits, endless looping is not recommended ;-)
  ```
  from openai import OpenAI
  client = OpenAI()
  completion = client.chat.completions.create(
      model="gpt-4o-mini",
      messages=[
          {"role": "user", "content": "write a haiku about AI."}
      ]
  )
  
  print(completion.choices[0].message)
  ```

### Install Django (Mac)
* Take a look at [Quick install guide](https://docs.djangoproject.com/en/5.1/intro/install/)
* Note: you have to install PostgreSQL first at your local environment
* Add pg_config to the PATH
* Install psycopg2
  ```
  pip3 install psycopg2
  ```
* Install django
  ```
  pip3 install django
  ```
* Run server:
Note: below example runs django at the default port.
  ```
  (venv) kuba@totem ecl % python3 ./manage.py runserver
  Watching for file changes with StatReloader
  Performing system checks...
  
  System check identified no issues (0 silenced).
  September 24, 2024 - 12:49:20
  Django version 5.1.1, using settings 'ecl.settings'
  Starting development server at http://127.0.0.1:8000/
  Quit the server with CONTROL-C.
  ```
* Verify installation: open 127.0.0.1:8000 URL in the browser. If you see Django welcome message, you are most probably well configured. Congrats.
  ```
  The install worked successfully! Congratulations!
  View release notes for Django 5.1
  ```

## If you're creating a brand-new django project and app
Below is an example how ECL app may be created.
  * Read [Writing your first Django app docs](https://docs.djangoproject.com/en/1.8/intro/tutorial01/)
  * Create folder named **server** in your main project directory, navigate to this folder
  * Create project named **pecl** (naming convention **P**roject for **ECL** app: pecl) inside **server** folder:
    
    Note: below code uses virtual environment
    ```
    python3 ../venv/bin/django-admin startproject pecl
    ```
  * A new folder named pecl should be created with the whole django content with models.py file, among the others.
  * Create application: go to pecl folder and run
    ```
    python3 ./manage.py startapp ecl 
    ```
    
# Django shell examples
## Before you start
If you want to check stuff on your local environment, [use django shell](https://docs.djangoproject.com/en/5.1/intro/tutorial02/#playing-with-the-api).

Navigate to the folder with your django project, run
```
python3 manage.py shell
```

Now you may play with the API

## Embedding calculation

```
import django, importlib, os, sys
import ecl.models as ecl_models
from openai import OpenAI

embedding_model = ecl_models.EmbeddingModel
embedding_dimension = ecl_models.EmbeddingDimension
data_set = ecl_models.DataSet
document = ecl_models.Document
embedding = ecl_models.DocumentEmbedding

my_model = embedding_model.objects.get(id=1) # My model.
my_dimension = embedding_dimension.objects.get(id=1)  # My dimension.
my_data_set = data_set.objects.get(id=1)  # My data set.
my_documents = mds.document.all()  # My data-set documents.

# Below method will reaload all embeddings calculated with my_model and provided dimensions.
my_data_set.set_content_embeddings(my_model, my_dimension)

# Below method will reaload all embeddings for: all models and all dimensions.
my_data_set.reload_all_embeddings()
```

## Similarity search
Below example shows the general flow of processing a user's question.

```
from openai import OpenAI
from ecl.models import *
from pgvector.django import CosineDistance

model = EmbeddingModel.objects.first()
dimensions = 512

question = "My internet connection doesnt work after installing an esim"

client = OpenAI()
openai_embedding = client.embeddings.create(model=model.name, dimensions=dimensions, input=question)
embedding_vector = openai_embedding.data[0].embedding

contents_with_distance = DocumentEmbedding.objects.annotate(
    distance=CosineDistance("embedding", embedding_vector)
).order_by("distance")[:12]

titles = list(map(lambda x: x.document.title, contents_with_distance))
print(titles)

result = client.chat.completions.create(model='gpt-4o', messages=[
    { 'role': 'system', 'content': 'you are a helpful assistant'},
    { 'role': 'user', 'content': f'Based on the following content delimited by three backticks ```{contents_with_distance[0].document.content}``` write a blog post that answers the question ${question} and promotes simoptions esim cards' }
])

print(result.choices[0].message.content)
```

# Troubleshooting and known issues
## Known issues
### Problem with 'vector' reported during testing on PostgreSQL instance
Problem statement:

When you [run tests](https://docs.djangoproject.com/en/5.1/topics/testing/overview/#running-tests) 
```python3 manage.py test```

error appears:
```django.db.utils.ProgrammingError: type "vector" does not exist```

Solution:
Configure template1 database. Log into template1 wwith psql, run:
```
template1=# CREATE EXTENSION vector;
CREATE EXTENSION
```
More details you'll find above, in the chapter regarding ECL database setup.

### Problem with accessing REST APIs
Problem statement: \
You run curl to check new api, for instance:
```
curl -v -X POST http://127.0.0.1:8000/api/ask/ \
-H "Content-Type: application/json" \
-H "Custom-Header: CustomValue" \
-d '{"question_message": "What is the best Product?"}'
```
...but you get...
```
HTTP/1.1 403 Forbidden
```
Solution: you need to add authorisation header with your token 
```
curl -v -X POST http://127.0.0.1:8000/api/ask/ \
-H "Content-Type: application/json" \
-H "Authorization: Token <your-token>" \
-H "Custom-Header: CustomValue" \
-d '{"question_message": "What is the best Product?"}'
```

## It may help
### Django logs
Run server in verbose mode
```
python manage.py runserver --verbosity 3
```