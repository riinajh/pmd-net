FROM continuumio/miniconda3:25.3.1-1

# Set workdir
WORKDIR /app

# Copy environment.yml
COPY environment.yml .

# Create conda environment
RUN conda env create -f environment.yml

# Make RUN commands use the new env:
SHELL ["conda", "run", "-n", "pmd-net", "/bin/bash", "-c"]

# Copy project files
COPY . .

# Default command (overridden in docker-compose.yml)
CMD ["python", "src/main.py"]

