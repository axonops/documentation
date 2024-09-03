FROM python:3.12-slim
COPY . /AxonOps.Docs/
WORKDIR /AxonOps.Docs/
RUN pip install pipenv
RUN pipenv install
EXPOSE 8000
CMD pipenv run mkdocs serve