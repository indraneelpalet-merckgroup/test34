FROM tiangolo/uvicorn-gunicorn-fastapi:python3.8-slim

WORKDIR models
COPY ./models/finetuned* ./
COPY ./models/bert-base-uncased ./bert-base-uncased
COPY ./models/bert-base-cased-squad2 ./bert-base-cased-squad2
WORKDIR ../
RUN apt-get update && apt-get -y install libgl1-mesa-glx ghostscript python-dev libxml2-dev libxslt1-dev antiword unrtf poppler-utils tesseract-ocr flac ffmpeg lame libmad0 libsox-fmt-mp3 sox libjpeg-dev swig libpulse-dev
#RUN apk update && apk upgrade && apk add mesa-gl
COPY ./requirements.txt ./requirements.txt
RUN pip install --upgrade pip &&pip install --no-cache-dir -r ./requirements.txt

COPY ./gunicorn_conf.py ./gunicorn_conf.py
COPY ./classes ./classes
COPY ./domain ./domain
COPY ./main.py ./main.py

EXPOSE 8000


#ENTRYPOINT ["sh", "-c", "python ./main.py $HEROKU_PRIVATE_IP"]
