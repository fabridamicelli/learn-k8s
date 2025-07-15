FROM python:3.13-slim

WORKDIR /app

RUN pip install uv
COPY requirements.txt /app/
RUN uv venv
RUN uv pip install --no-cache-dir -r requirements.txt

COPY app.py /app/

# Expose the Streamlit default port
EXPOSE 8501

CMD ["uv", "run", "streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]
