FROM python:3.9-slim

WORKDIR /app

# Copy application files
COPY app_clean.py .
COPY templates/ templates/
COPY static/ static/

# No requirements needed - using standard library only

# Expose port
EXPOSE 8080

# Set environment variable for port
ENV PORT=8080

# Run the application
CMD ["python", "app_clean.py"]