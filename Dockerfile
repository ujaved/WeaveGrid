FROM python:3.8
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY server/ .
ENV FLASK_APP='server'
ENV FLASK_DEBUG=1
ENV BASE_DIR='.'
CMD [ "flask", "run" ]