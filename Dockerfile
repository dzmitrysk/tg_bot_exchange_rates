FROM python:3.9

WORKDIR /src
COPY src /src
COPY requirements.txt /src/
RUN pip install -r requirements.txt

CMD ["python", "bot.py"]