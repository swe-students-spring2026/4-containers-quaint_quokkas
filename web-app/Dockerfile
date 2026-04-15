FROM python:3.11-slim
WORKDIR /app
RUN pip install --no-cache-dir pipenv
COPY Pipfile Pipfile.lock ./
RUN pipenv install --system
COPY . .
EXPOSE 3000
CMD ["python", "app.py"]
