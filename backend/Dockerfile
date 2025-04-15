# Use an official Python runtime as a parent image
FROM python:3.11-slim

# Create a non-root user
RUN useradd -m snake

# Set the working directory to /code and change ownership
WORKDIR /code
RUN chown -R snake:snake /code

# Switch to the non-root user
USER snake

# Copy and install dependencies
COPY --chown=snake:snake ./requirements.txt /code/requirements.txt
RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt --user --no-warn-script-location

# Copy application code
COPY --chown=snake:snake ./ /code

# Ensure user-installed packages are in PATH
ENV PATH="/home/snake/.local/bin:${PATH}"

# Expose the port
EXPOSE 8000

# Set the maintainer
LABEL maintainer="Jenslee Dsouza <dsouzajenslee@gmail.com>"

# Start Uvicorn with the root path
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
