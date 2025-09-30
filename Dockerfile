# Use slim Python image
FROM python:3.11-slim

# Set working directory inside container
WORKDIR /gromit

# Install dependencies
COPY requirements.txt requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy app code
COPY . .

# Run the app
CMD ["python", "app.py"]

