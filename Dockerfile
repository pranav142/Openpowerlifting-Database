FROM python:3.9.16

# Set the working directory in the Docker container
WORKDIR /app

# Copy the requirements.txt file into the container
COPY requirements.txt /app

# Install dependencies from requirements.txt
RUN pip install -r requirements.txt

# Copy the entire src directory into the container's /app directory
COPY src /app/src

# Copy setup.py into the container's /app directory
COPY setup.py /app

# Build the distribution packages (wheel and sdist)
RUN python setup.py bdist_wheel sdist

# Install the local package from the distribution packages
RUN pip install .

# Expose port 80 (if your application uses it)
EXPOSE 8080

# Set the command to run your application
CMD ["python", "src/server/app.py"]
