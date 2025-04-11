# Use an official Python runtime as a parent image
FROM python:3.11-slim


# Set the user to snake
RUN useradd -m snake
USER snake

# Set the working directory to /app
WORKDIR /app

# Copy the requirements file
COPY --chown=snake:snake requirements.txt global_variables.py main.py ./

# Install the dependencies
RUN pip install -r requirements.txt --no-warn-script-location

# Ensure user-installed packages are in PATH
ENV PATH="/home/sherlock/.local/bin:${PATH}"

# Expose the port
EXPOSE 8000

# Set the maintainer
LABEL maintainer="Jenslee Dsouza <dsouzajenslee@gmail.com>"

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
