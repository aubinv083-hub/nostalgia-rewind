FROM python:3.12.12-slim

LABEL description="Data pipeline with Streamlit interface"

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt


COPY . .


ENV DOCKER_CONTAINER=true


EXPOSE 8501


CMD ["python", "run_pipeline.py"]