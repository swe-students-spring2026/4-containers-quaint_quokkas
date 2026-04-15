FROM python:3.11-slim
WORKDIR /app
RUN pip install --no-cache-dir pipenv
COPY Pipfile ./
RUN pipenv install --system --skip-lock
ADD https://storage.googleapis.com/mediapipe-models/hand_landmarker/hand_landmarker/float16/1/hand_landmarker.task .
COPY . .
CMD ["python", "mlclient.py"]