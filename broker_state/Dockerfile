FROM python:3.10-slim

WORKDIR /app

RUN pip install --no-cache-dir paho-mqtt

COPY broker_state.py ./

CMD ["python", "broker_state.py"]
