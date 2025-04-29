FROM python:3.12-alpine

WORKDIR /bot
COPY requirements.txt .

RUN pip install -r requirements.txt

COPY . ./

EXPOSE 8080

ENTRYPOINT ["python3", "bot.py"]
