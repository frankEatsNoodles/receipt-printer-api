# Use an official Python runtime as a parent image, using the "slim" variant for a smaller image size
FROM python:3.12-slim

# Set the working directory inside the container
WORKDIR /app

# Copy the requirements file from the host to the container's working directory
COPY requirements.txt ./

# Install any dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application source code from the host to the container
COPY . .

# Expose the port your app runs on (adjust as needed)
EXPOSE 8080

# Specify the command to run when the container starts
CMD ["python", "main.py"]