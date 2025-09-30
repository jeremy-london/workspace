FROM python:3.12-slim AS base

USER root

# Set environment variables
ENV HOME=/root \
  PYTHONPATH=/workspace \
  PYTHONDONTWRITEBYTECODE=1 \
  PYTHONUNBUFFERED=1 \
  PIP_DISABLE_PIP_VERSION_CHECK=1 \
  PIP_NO_CACHE_DIR=off \
  PIP_ROOT_USER_ACTION=ignore \
  ANONYMIZED_TELEMETRY=False

# Set default shell to Bash
SHELL ["/bin/bash", "-c"]

# Install linux tools
RUN apt-get update && apt-get install -y git

# Set up working directory
WORKDIR /workspace

# Copy the colored MOTD script for interactive shells
COPY .devcontainer/motd.sh /etc/profile.d/motd.sh

# Add MOTD to bashrc for non-login shells
RUN echo 'if [ -f /etc/profile.d/motd.sh ]; then source /etc/profile.d/motd.sh; fi' >> /etc/bash.bashrc

# Install dependencies
COPY requirements.txt requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy the preload script but DON'T run it during build
COPY .devcontainer/preload_models.py /usr/local/bin/preload_models.py

# Create an entrypoint script that downloads models on first run
COPY .devcontainer/entrypoint.sh /usr/local/bin/entrypoint.sh

ENTRYPOINT ["/usr/local/bin/entrypoint.sh"]
CMD ["sleep", "infinity"]