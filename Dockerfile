FROM python:3.9-slim

WORKDIR /app

# Install system dependencies (if needed)
RUN apt-get update && apt-get install -y --no-install-recommends gcc

# Copy Chrome package and install it
# The .deb file must exist in the build context
# COPY chrome_114_amd64.deb /tmp/
# RUN apt-get update && apt-get install -y /tmp/chrome_114_amd64.deb && rm /tmp/chrome_114_amd64.deb

# Copy requirements and install dependencies
COPY requirements.txt .
RUN pip install -r requirements.txt

# Copy the rest of your code
COPY . .

EXPOSE 5000

# Use uvicorn to run FastAPI app
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "5000"]