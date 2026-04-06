# Use the official Python 3.12 slim image
FROM python:3.12-slim

# Set environment variables
# Prevents Python from writing .pyc files to disk
ENV PYTHONDONTWRITEBYTECODE=1
# Prevents Python from buffering stdout/stderr (makes logs visible immediately)
ENV PYTHONUNBUFFERED=1

# Set the working directory inside the container
WORKDIR /app

# Install system dependencies (sometimes required for Pillow/image processing)
RUN apt-get update \
    && apt-get install -y --no-install-recommends gcc libjpeg-dev zlib1g-dev \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install them
COPY requirements.txt /app/
RUN pip install --upgrade pip && pip install -r requirements.txt

# Copy the rest of the Django project code into the container
COPY . /app/

# Expose port 8000 for the Django server
EXPOSE 8000

# Migrations
CMD ["python", "manage.py", "migrate"]

# Install Watson search indexes
CMD ["python", "manage.py", "installwatson"]

# Linus: This is needed to build the search index for existing products in the database. 
# If you don't have any products, you can skip this step. 
# I am unsure how to selectively do this in docker, haha
# https://github.com/etianen/django-watson/wiki
CMD ["python", "manage.py", "buildwatson"]

# The default command to run when starting the container
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]