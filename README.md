# E-COMMERCE LLM

## About
This is POC for AI tailored for E-Commerce needs.

There are plenty of gen AI tools showing up on the market, however I haven’t seen anything specific to E-Commerce. 
There are a few use cases that can be built on top of gen AI, to support their teams and customers. 

The ECL tool consists of a document index, that’s aligned to the E-Commerce data structures, and a set of LLM-based APIs that will allow querying it in different ways.

## Style
* Python coding style conventions: [TBD]
* Branching strategy: feature branching as per [this gentleman's speech](https://www.youtube.com/watch?v=U_IFGpJDbeU)
* PRs and Commits: we follow [Conventional Commits](https://www.conventionalcommits.org/en/v1.0.0-beta.2/) pattern.

## Local installation guide (MAC)
In a nutshell:
* Install database with pgvector extension
* Get your OpenAI key
* Run hello world!
* Have fun

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

### Enable vector extension
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

### Integrate with OpenAI
* Obtain your project [OpenAI API key](https://platform.openai.com/api-keys)
* [Store your key](https://help.openai.com/en/articles/5112595-best-practices-for-api-key-safety) in .zshrc file (replace *Your-Key* with your project API key value)
```
echo "export OPENAI_API_KEY='Your-Key'" >> ~/.zshrc
```

### Run hello world
Python code to verify OpenAI integration. Feel free to experiment with haiku, but remember about OpenAI project's cost limits, endless looping is not recommended ;-)
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