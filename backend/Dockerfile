# Use an official Python runtime as a parent image
FROM python:3.11.10-bookworm

# Set the working directory to /app
WORKDIR /app

# Copy the requirements file
COPY requirements.txt main.py ./

# Install the dependencies
RUN pip install -r requirements.txt

# Expose the port
EXPOSE 8000

# Set the maintainer
LABEL maintainer="Jenslee Dsouza <dsouzajenslee@gmail.com>"

# Run the command to start the application
CMD ["python", "main.py"]