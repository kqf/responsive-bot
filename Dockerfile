FROM python:3.10
WORKDIR /app

COPY . .
RUN pip install --no-cache-dir --upgrade -r ./requirements.txt
RUN pip install -e .

EXPOSE 5050
CMD ["python", "bot/main.py"]
