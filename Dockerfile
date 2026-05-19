FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
RUN chmod +x /app/start.sh
EXPOSE 8501
CMD ["/bin/bash", "/app/start.sh"]
