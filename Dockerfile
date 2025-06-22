FROM python:3.12.0-slim

WORKDIR /bot

COPY requirements.txt .

RUN pip install -r requirements.txt

# Copy project
COPY alembic/ alembic/
COPY alembic.ini .
COPY src/ src/
COPY README.md .
COPY LICENSE .

CMD ["sh", "-c", "alembic upgrade head && python src/main.py"]