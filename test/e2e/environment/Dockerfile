FROM python:3.7

WORKDIR /cpmhub_mock
COPY cpmhub_mock.py /cpmhub_mock
RUN pip install --upgrade flask

ENTRYPOINT ["python3", "cpmhub_mock.py"]
