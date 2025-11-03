FROM python:3.10-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN mkdir -p instance && touch instance/pos.db instance/users.db instance/items.db instance/permissions.db

EXPOSE 5000/udp 5001/udp

CMD ["python", "app.py"]
