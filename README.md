# Mini-Usine IoT Sécurisée

Simulation d'une mini-usine industrielle IoT avec communication sécurisée TLS, monitoring en temps réel et système d'alertes.

## Table des matières

- [Vue d'ensemble](#vue-densemble)
- [Architecture](#architecture)
- [Prérequis](#prérequis)
- [Installation](#installation)
- [Configuration](#configuration)
- [Utilisation](#utilisation)
- [Tests de sécurité](#tests-de-sécurité)
- [Monitoring et alertes](#monitoring-et-alertes)
- [Dépannage](#dépannage)

## Vue d'ensemble

Ce projet simule une mini-usine industrielle connectée avec :

- **6 dispositifs IoT** simulant machines de production, capteurs de température, pression, vibration et compteur d'énergie
- **Communication sécurisée** via MQTT avec TLS 1.2
- **Pipeline de données** : MQTT → Node-RED → InfluxDB → Grafana
- **Système d'alertes** pour anomalies et seuils critiques
- **Environnement conteneurisé** avec Docker Compose

### Fonctionnalités clés

✅ **Sécurité TLS obligatoire** - Toutes les communications chiffrées  
✅ **Monitoring temps réel** - Dashboards Grafana interactifs  
✅ **Alertes automatiques** - Notifications sur événements critiques  
✅ **Scalable** - Ajout facile de nouveaux dispositifs  
✅ **Isolation** - Chaque service dans son conteneur  

## Architecture

```
┌─────────────────┐     ┌──────────────┐     ┌─────────────┐     ┌──────────────┐     ┌─────────────┐
│  IoT Devices    │────▶│   Mosquitto  │────▶│  Node-RED   │────▶│  InfluxDB    │────▶│  Grafana    │
│  (Simulateurs)  │ TLS │  MQTT Broker │ TLS │  (Pipeline) │     │ (Time-Series)│     │ (Dashboards)│
└─────────────────┘     └──────────────┘     └─────────────┘     └──────────────┘     └─────────────┘
        ↑                                              │
        │                                              ↓
        └──────────────────────────────────────[ Alertes ]
```

### Composants

| Composant | Description | Port |
|-----------|-------------|------|
| **Mosquitto** | Broker MQTT avec TLS | 8883 |
| **InfluxDB** | Base de données time-series | 8086 |
| **Node-RED** | Traitement des flux de données | 1880 |
| **Grafana** | Visualisation et alertes | 3000 |
| **IoT Simulators** | 6 dispositifs IoT simulés | - |

### Dispositifs IoT

1. **machine-1, machine-2** : Machines de production
   - Vitesse (RPM), taux de production, efficacité
   - Simulation de pannes aléatoires

2. **temp-sensor-1** : Capteur de température
   - Température, humidité
   - Alertes sur surchauffe

3. **pressure-sensor-1** : Capteur de pression
   - Pression en bars
   - Alertes sur surpression

4. **vibration-sensor-1** : Capteur de vibrations
   - Vibrations X/Y/Z
   - Détection d'anomalies

5. **energy-meter-1** : Compteur d'énergie
   - Puissance, consommation totale
   - Tension, courant

## Prérequis

- **Docker** >= 20.10
- **Docker Compose** >= 2.0
- **OpenSSL** (pour génération certificats)
- **Python 3.11+** (pour tests)
- **Ports libres** : 1880, 3000, 8086, 8883, 9001

### Vérification

```bash
docker --version
docker-compose --version
openssl version
python3 --version
```

## Installation

### 1. Cloner le projet

```bash
git clone <repository-url>
cd mini-plant
```

### 2. Structure du projet

```
mini-plant/
├── docker-compose.yml
├── mosquitto/
│   └── config/
│       └── mosquitto.conf
├── simulators/
│   ├── Dockerfile
│   ├── iot_simulator.py
│   └── requirements.txt
├── grafana/
│   └── provisioning/
│       ├── datasources/
│       │   └── datasource.yml
│       └── dashboards/
│           ├── dashboard.yml
│           └── dashboard.json
├── certs/                    # Généré automatiquement
├── scripts/
│   ├── generate-certs.sh
│   └── test-security.py
└── README.md
```

### 3. Générer les certificats TLS

```bash
chmod +x scripts/generate-certs.sh
./scripts/generate-certs.sh
```

Cela crée dans `./certs/` :
- `ca.crt` / `ca.key` : Autorité de certification
- `server.crt` / `server.key` : Certificat serveur (Mosquitto)
- `client.crt` / `client.key` : Certificat client (dispositifs IoT)

### 4. Créer le fichier de mots de passe Mosquitto

```bash
mkdir -p mosquitto/config
docker run -it --rm -v $(pwd)/mosquitto/config:/mosquitto/config eclipse-mosquitto:2.0 \
  mosquitto_passwd -c /mosquitto/config/passwd iot-user
```

Entrez un mot de passe (ex: `iot-password123`)

## Configuration

### Variables d'environnement importantes

Dans `docker-compose.yml`, vous pouvez personnaliser :

**InfluxDB**
```yaml
DOCKER_INFLUXDB_INIT_USERNAME=admin
DOCKER_INFLUXDB_INIT_PASSWORD=adminpassword123
DOCKER_INFLUXDB_INIT_ADMIN_TOKEN=my-super-secret-auth-token
```

**Grafana**
```yaml
GF_SECURITY_ADMIN_USER=admin
GF_SECURITY_ADMIN_PASSWORD=admin123
```

**Alertes email** (optionnel)
```yaml
GF_SMTP_ENABLED=true
GF_SMTP_HOST=smtp.gmail.com:587
GF_SMTP_USER=your-email@gmail.com
GF_SMTP_PASSWORD=your-app-password
```

### Configuration des simulateurs

Chaque simulateur peut être configuré via variables d'environnement :

```yaml
environment:
  - DEVICE_ID=machine-1
  - DEVICE_TYPE=production
  - PUBLISH_INTERVAL=5  # Secondes entre publications
```

## Utilisation

### Démarrage complet

```bash
# Démarrer tous les services
docker-compose up -d

# Vérifier l'état
docker-compose ps

# Voir les logs
docker-compose logs -f
```

### Démarrage par étapes

```bash
# 1. Infrastructure
docker-compose up -d mosquitto influxdb

# 2. Traitement
docker-compose up -d nodered

# 3. Visualisation
docker-compose up -d grafana

# 4. Simulateurs
docker-compose up -d iot-machine-1 iot-temp-sensor-1 iot-pressure-sensor-1
```

### Accès aux interfaces

| Service | URL | Identifiants |
|---------|-----|--------------|
| **Grafana** | http://localhost:3000 | admin / admin123 |
| **Node-RED** | http://localhost:1880 | - |
| **InfluxDB** | http://localhost:8086 | admin / adminpassword123 |

### Vérifier les données

**Dans InfluxDB :**
```bash
docker exec -it influxdb influx query 'from(bucket:"iot-data") |> range(start: -1h) |> limit(n:10)'
```

**Dans Node-RED :**
1. Ouvrir http://localhost:1880
2. Vérifier le flux "MQTT → InfluxDB Pipeline"
3. Activer les nodes debug pour voir les données

**Dans Grafana :**
1. Ouvrir http://localhost:3000
2. Dashboard "Mini-Usine IoT Dashboard"
3. Observer les métriques en temps réel

## Tests de sécurité

### Exécuter les tests automatisés

```bash
# Installer paho-mqtt
pip3 install paho-mqtt

# Lancer les tests
python3 scripts/test-security.py
```

### Tests manuels

**Test 1 : Connexion sans TLS (doit échouer)**
```bash
mosquitto_pub -h localhost -p 8883 -t test -m "hello"
# Erreur attendue
```

**Test 2 : Connexion avec TLS (doit réussir)**
```bash
mosquitto_pub -h localhost -p 8883 \
  --cafile certs/ca.crt \
  --cert certs/client.crt \
  --key certs/client.key \
  -t test -m "hello"
# Succès
```

**Test 3 : Vérifier le chiffrement**
```bash
# Capturer le trafic (nécessite tcpdump)
docker exec mosquitto tcpdump -i any -n port 8883 -X
# Le contenu doit être chiffré
```

### Résultats attendus

```
=== TESTS DE SÉCURITÉ TLS - MINI-USINE IoT ===

✓ PASS - Connexion sans TLS
      Connexion refusée comme attendu

✓ PASS - Certificats incorrects
      Connexion refusée comme attendu

✓ PASS - TLS valide
      Connexion TLS sécurisée établie avec succès

✓ PASS - Version TLS
      TLS 1.2 supporté (sécurisé)

✓ PASS - Vérification certificats
      Vérification stricte des certificats activée

Tests réussis: 5/5 (100%)
✓ TOUS LES TESTS SONT PASSÉS
```

## Monitoring et alertes

### Dashboards Grafana

Le dashboard principal affiche :

1. **Production Machines Status** : État et vitesse des machines
2. **Temperature Sensors** : Graphique températures
3. **Machine Efficiency** : Jauge d'efficacité
4. **Pressure Monitoring** : Surveillance pression
5. **Vibration Analysis** : Analyse vibrations
6. **Energy Consumption** : Consommation instantanée
7. **Machine Downtime** : Temps d'arrêt cumulé
8. **Total Energy Consumed** : Énergie totale

### Configuration des alertes

**Dans Node-RED :**
- Les alertes sont détectées dans la fonction "Check Alert Thresholds"
- Seuils configurables pour chaque type de capteur

**Dans Grafana :**

1. Aller dans un panel → Edit
2. Onglet "Alert"
3. Configurer :
   - Condition (ex: `temperature > 80`)
   - Évaluation (ex: toutes les 1m pendant 5m)
   - Notification channel

**Exemple d'alerte température :**
```
WHEN last() OF query(A, 5m, now) IS ABOVE 80
```

### Canaux de notification

**Email** (configuré dans docker-compose.yml)
```yaml
GF_SMTP_ENABLED=true
GF_SMTP_HOST=smtp.gmail.com:587
```

**Webhook** (à configurer dans Grafana)
```json
{
  "url": "https://your-webhook.com/alert",
  "method": "POST"
}
```

##  Dépannage

### Problème : Certificats TLS invalides

```bash
# Regénérer les certificats
rm -rf certs/
./scripts/generate-certs.sh

# Redémarrer les services
docker-compose restart
```

### Problème : Dispositifs IoT ne se connectent pas

```bash
# Vérifier les logs
docker-compose logs iot-machine-1

# Vérifier Mosquitto
docker-compose logs mosquitto

# Tester manuellement
docker exec -it iot-machine-1 python3 -c "import ssl; print(ssl.OPENSSL_VERSION)"
```

### Problème : Pas de données dans InfluxDB

```bash
# Vérifier Node-RED
docker-compose logs nodered

# Tester la connexion InfluxDB
docker exec -it influxdb influx ping

# Vérifier le bucket
docker exec -it influxdb influx bucket list
```

### Problème : Grafana ne se connecte pas à InfluxDB

```bash
# Vérifier le token
docker exec -it grafana cat /etc/grafana/provisioning/datasources/datasource.yml

# Tester manuellement
curl -X POST http://localhost:8086/api/v2/query \
  -H "Authorization: Token my-super-secret-auth-token" \
  -H "Content-Type: application/json"
```

### Logs utiles

```bash
# Tous les services
docker-compose logs -f

# Service spécifique
docker-compose logs -f mosquitto
docker-compose logs -f nodered
docker-compose logs -f grafana

# Dernières 100 lignes
docker-compose logs --tail=100
```

## Scalabilité

### Ajouter un nouveau dispositif

1. Dupliquer un service dans `docker-compose.yml` :

```yaml
iot-machine-3:
  build:
    context: ./simulators
    dockerfile: Dockerfile
  container_name: iot-machine-3
  environment:
    - DEVICE_ID=machine-3
    - DEVICE_TYPE=production
    - MQTT_BROKER=mosquitto
    - MQTT_PORT=8883
    - PUBLISH_INTERVAL=5
    - CA_CERT=/certs/ca.crt
    - CLIENT_CERT=/certs/client.crt
    - CLIENT_KEY=/certs/client.key
  volumes:
    - ./certs:/certs:ro
  networks:
    - iot-network
  depends_on:
    - mosquitto
  restart: unless-stopped
```

2. Démarrer le nouveau dispositif :

```bash
docker-compose up -d iot-machine-3
```

### Performances

- **Latence** : < 2 secondes bout-en-bout
- **Débit** : Testé avec 10+ dispositifs simultanés
- **Capacité** : InfluxDB peut gérer millions de points/seconde

##  Tests end-to-end

```bash
# 1. Publier un message de test
docker exec iot-machine-1 python3 -c "
import paho.mqtt.client as mqtt
import ssl
import json
import time

client = mqtt.Client('test-client')
client.tls_set(
    ca_certs='/certs/ca.crt',
    certfile='/certs/client.crt',
    keyfile='/certs/client.key'
)
client.connect('mosquitto', 8883)
client.publish('iot/plant/production/machine-1', 
    json.dumps({'temperature': 95, 'timestamp': time.time()}))
client.disconnect()
"

# 2. Vérifier dans InfluxDB
docker exec influxdb influx query '
from(bucket:"iot-data") 
  |> range(start: -5m) 
  |> filter(fn: (r) => r.device_id == "machine-1")
  |> limit(n:1)
'

# 3. Vérifier dans Grafana
# Ouvrir http://localhost:3000 et voir la valeur apparaître
```

## Commandes utiles

```bash
# Arrêter tous les services
docker-compose down

# Arrêter et supprimer les volumes
docker-compose down -v

# Reconstruire les images
docker-compose build --no-cache

# Redémarrer un service
docker-compose restart mosquitto

# Voir l'utilisation des ressources
docker stats

# Nettoyer Docker
docker system prune -a
```

##  Bonnes pratiques de sécurité

✅ **Toujours utiliser TLS** pour les communications MQTT  
✅ **Changer les mots de passe** par défaut  
✅ **Renouveler les certificats** régulièrement (avant expiration)  
✅ **Limiter les accès réseau** avec des règles firewall  
✅ **Monitorer les logs** pour détecter les anomalies  
✅ **Mettre à jour** les images Docker régulièrement  
✅ **Sauvegarder** les données InfluxDB  

##  Ressources

- [Mosquitto Documentation](https://mosquitto.org/documentation/)
- [InfluxDB Documentation](https://docs.influxdata.com/)
- [Node-RED Documentation](https://nodered.org/docs/)
- [Grafana Documentation](https://grafana.com/docs/)
- [MQTT TLS Security](https://mosquitto.org/man/mosquitto-tls-7.html)

##  Licence

Ce projet est fourni à des fins éducatives et de démonstration.

##  Contribution

Pour toute question ou amélioration, n'hésitez pas à ouvrir une issue ou une pull request.

---

**Projet Mini-Usine IoT** - Démonstration d'une infrastructure IoT industrielle sécurisée 🏭🔒