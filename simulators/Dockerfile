FROM python:3.11-slim

LABEL maintainer="Mini-Plant IoT Team"
LABEL description="IoT Device Simulator with MQTT TLS Support"

# Installer les dépendances système
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# Créer un utilisateur non-root
RUN useradd -m -u 1000 iot-user

# Répertoire de travail
WORKDIR /app

# Copier les requirements
COPY requirements.txt .

# Installer les dépendances Python
RUN pip install --no-cache-dir -r requirements.txt

# Copier le script du simulateur
COPY iot_simulator.py .

# Changer les permissions
RUN chown -R iot-user:iot-user /app

# Basculer vers l'utilisateur non-root
USER iot-user

# Commande par défaut
CMD ["python", "-u", "iot_simulator.py"]