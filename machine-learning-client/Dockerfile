FROM python:3.10-slim
WORKDIR /app
RUN pip install --no-cache-dir pipenv
COPY Pipfile Pipfile.lock ./
RUN pipenv install --system --deploy
COPY . .
EXPOSE 8000
CMD ["python", "mlclient.py"]
