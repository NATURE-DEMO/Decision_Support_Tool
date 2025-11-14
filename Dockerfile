FROM osgeo/gdal:ubuntu-small-3.8.0

# Install Python and pip
RUN apt-get update && apt-get install -y \
    python3-pip \
    python3-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy requirements
COPY requirements.txt .

# Install Python dependencies
RUN pip3 install --no-cache-dir -r requirements.txt

# Copy application files
COPY . .

# Expose Streamlit port
EXPOSE 8501

# Health check
HEALTHCHECK CMD curl --fail http://localhost:8501/_stcore/health || exit 1

# Run Streamlit
CMD ["streamlit", "run", "Home.py", "--server.port=8501", "--server.address=0.0.0.0"]