# Use an official Python runtime as a parent image
FROM python:3.12-slim

# update the package index and upgrading existing packages
RUN apt-get update && apt-get upgrade -y

# Install necessary build tools
RUN apt-get install -y \
    cmake \
    g++ \
    build-essential \
    tesseract-ocr \
    libtesseract-dev

# upgrade pip
RUN pip install --upgrade pip

# Set the working directory in the container
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY . /app

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

CMD ["python", "todobot.py"]