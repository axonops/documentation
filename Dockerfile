FROM python:3.12-slim

WORKDIR /AxonOps.Docs/

RUN apt-get update && \
    apt-get install -y \
    default-jre \
    graphviz \
    plantuml
RUN pip install pipenv

COPY Pipfile* /AxonOps.Docs/
RUN pipenv install

COPY . /AxonOps.Docs/
EXPOSE 8000
CMD ["pipenv", "run", "mkdocs", "serve"]
