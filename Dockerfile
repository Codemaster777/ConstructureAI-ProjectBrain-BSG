# Use official Python 3.11 image
FROM python:3.11

# Set working directory inside the container
WORKDIR /code

# Copy requirements from the Backend folder
COPY ./Backend/requirements.txt /code/requirements.txt

# Install dependencies
RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt

# Copy the Backend code into the container
COPY ./Backend /code/app

# Create necessary directories for Docs and DB
RUN mkdir -p /code/app/Docs
RUN mkdir -p /code/app/chroma_db

# GRANT PERMISSIONS: Hugging Face runs as a non-root user (user 1000)
# We must allow it to write to these folders to save the database.
RUN chmod -R 777 /code/app/Docs
RUN chmod -R 777 /code/app/chroma_db

# Set working directory to the app folder
WORKDIR /code/app

# Expose port 7860 (Hugging Face default)
EXPOSE 7860

# Start the server on port 7860
CMD ["uvicorn", "Server:App", "--host", "0.0.0.0", "--port", "7860"]