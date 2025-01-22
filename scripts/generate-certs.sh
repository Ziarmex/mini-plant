#!/bin/bash

# Script de génération des certificats TLS pour la mini-usine IoT
# Utilise OpenSSL pour créer une CA, des certificats serveur et client

set -e

CERTS_DIR="./certs"
DAYS_VALID=3650

echo "=== Génération des certificats TLS pour Mini-Usine IoT ==="

# Créer le répertoire des certificats
mkdir -p "$CERTS_DIR"
cd "$CERTS_DIR"

# 1. Générer la clé privée de la CA (Certificate Authority)
echo "[1/7] Génération de la clé privée CA..."
openssl genrsa -out ca.key 4096

# 2. Générer le certificat CA auto-signé
echo "[2/7] Génération du certificat CA..."
openssl req -new -x509 -days $DAYS_VALID -key ca.key -out ca.crt \
    -subj "/C=FR/ST=Setif/L=Setif/O=MiniPlant-IoT/OU=Security/CN=Mini-Plant-CA"

# 3. Générer la clé privée du serveur (Mosquitto)
echo "[3/7] Génération de la clé privée serveur..."
openssl genrsa -out server.key 2048

# 4. Créer une demande de certificat pour le serveur
echo "[4/7] Création de la demande de certificat serveur..."
openssl req -new -key server.key -out server.csr \
    -subj "/C=FR/ST=Setif/L=Setif/O=MiniPlant-IoT/OU=MQTT/CN=mosquitto"

# 5. Signer le certificat serveur avec la CA
echo "[5/7] Signature du certificat serveur..."
openssl x509 -req -in server.csr -CA ca.crt -CAkey ca.key \
    -CAcreateserial -out server.crt -days $DAYS_VALID

# 6. Générer la clé privée du client
echo "[6/7] Génération de la clé privée client..."
openssl genrsa -out client.key 2048

# 7. Créer et signer le certificat client
echo "[7/7] Création et signature du certificat client..."
openssl req -new -key client.key -out client.csr \
    -subj "/C=FR/ST=Setif/L=Setif/O=MiniPlant-IoT/OU=IoT-Devices/CN=iot-client"

openssl x509 -req -in client.csr -CA ca.crt -CAkey ca.key \
    -CAcreateserial -out client.crt -days $DAYS_VALID

# Nettoyer les fichiers temporaires
rm -f *.csr *.srl

# Définir les permissions appropriées
chmod 644 *.crt
chmod 600 *.key

echo ""
echo "=== Certificats générés avec succès ! ==="
echo ""
echo "Fichiers créés dans $CERTS_DIR:"
ls -lh
echo ""
echo "CA Certificate: ca.crt"
echo "Server Certificate: server.crt"
echo "Server Key: server.key"
echo "Client Certificate: client.crt"
echo "Client Key: client.key"
echo ""
echo "Validité: $DAYS_VALID jours (environ 10 ans)"
echo ""
echo "Pour vérifier les certificats:"
echo "  openssl x509 -in ca.crt -text -noout"
echo "  openssl x509 -in server.crt -text -noout"
echo "  openssl x509 -in client.crt -text -noout"