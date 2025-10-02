FROM python:3.11-slim

WORKDIR /gromit/hands

# Install dependencies
COPY requirements.txt requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Expose Flask port
EXPOSE 5000

# Default command for development
CMD ["python", "app.py"]
