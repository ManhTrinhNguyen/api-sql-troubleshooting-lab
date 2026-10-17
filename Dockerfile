FROM python:3.11-slim
WORKDIR /lab
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY app app
COPY scripts scripts
RUN useradd --create-home lab && chown -R lab:lab /lab
USER lab
EXPOSE 8000
CMD ["sh", "-c", "python -m scripts.seed_data && uvicorn app.main:app --host 0.0.0.0 --port 8000"]
