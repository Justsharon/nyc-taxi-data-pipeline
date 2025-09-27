FROM python:3.13

WORKDIR /app

RUN pip install pandas sqlalchemy pyarrow requests psycopg2-binary

COPY ny-upload-data.py ny-upload-data.py

ENTRYPOINT [ "python", "ny-upload-data.py"]
