#!/usr/bin/env python3
"""
Simulateur de dispositifs IoT pour Mini-Usine
Supporte différents types de capteurs avec TLS MQTT
"""

import os
import sys
import json
import time
import random
import ssl
from datetime import datetime
import paho.mqtt.client as mqtt

class IoTSimulator:
    def __init__(self):
        # Configuration depuis les variables d'environnement
        self.device_id = os.getenv('DEVICE_ID', 'unknown-device')
        self.device_type = os.getenv('DEVICE_TYPE', 'generic')
        self.mqtt_broker = os.getenv('MQTT_BROKER', 'mosquitto')
        self.mqtt_port = int(os.getenv('MQTT_PORT', 8883))
        self.publish_interval = int(os.getenv('PUBLISH_INTERVAL', 5))
        
        # Certificats TLS
        self.ca_cert = os.getenv('CA_CERT', '/certs/ca.crt')
        self.client_cert = os.getenv('CLIENT_CERT', '/certs/client.crt')
        self.client_key = os.getenv('CLIENT_KEY', '/certs/client.key')
        
        # Topic MQTT
        self.topic = f"iot/plant/{self.device_type}/{self.device_id}"
        
        # Client MQTT
        self.client = None
        self.connected = False
        
        # État du dispositif
        self.state = self._initialize_state()
        
        print(f"[{self.device_id}] Initialisation du simulateur")
        print(f"  Type: {self.device_type}")
        print(f"  Broker: {self.mqtt_broker}:{self.mqtt_port}")
        print(f"  Topic: {self.topic}")
        print(f"  Intervalle: {self.publish_interval}s")
    
    def _initialize_state(self):
        """Initialise l'état selon le type de dispositif"""
        base_state = {
            'device_id': self.device_id,
            'device_type': self.device_type,
            'status': 'online'
        }
        
        if self.device_type == 'production':
            return {
                **base_state,
                'speed': 100.0,  # RPM
                'output_rate': 50.0,  # unités/min
                'downtime': 0,
                'efficiency': 95.0,
                'failures': 0
            }
        elif self.device_type == 'temperature':
            return {
                **base_state,
                'temperature': 22.0,  # Celsius
                'humidity': 45.0,  # %
                'alert_threshold': 80.0
            }
        elif self.device_type == 'pressure':
            return {
                **base_state,
                'pressure': 1.0,  # Bar
                'alert_threshold': 5.0
            }
        elif self.device_type == 'vibration':
            return {
                **base_state,
                'vibration_x': 0.0,  # mm/s
                'vibration_y': 0.0,
                'vibration_z': 0.0,
                'alert_threshold': 10.0
            }
        elif self.device_type == 'energy':
            return {
                **base_state,
                'power': 0.0,  # kW
                'energy_total': 0.0,  # kWh
                'voltage': 230.0,  # V
                'current': 0.0  # A
            }
        else:
            return base_state
    
    def _simulate_data(self):
        """Génère des données simulées selon le type"""
        timestamp = datetime.utcnow().isoformat() + 'Z'
        
        if self.device_type == 'production':
            # Simulation d'une machine de production
            # 5% de chance de panne
            if random.random() < 0.05:
                self.state['status'] = 'offline'
                self.state['downtime'] += self.publish_interval
                self.state['failures'] += 1
                self.state['speed'] = 0
                self.state['output_rate'] = 0
                self.state['efficiency'] = 0
            else:
                self.state['status'] = 'online'
                # Variation normale
                self.state['speed'] = 100 + random.uniform(-5, 5)
                self.state['output_rate'] = 50 + random.uniform(-3, 3)
                self.state['efficiency'] = 95 + random.uniform(-2, 2)
        
        elif self.device_type == 'temperature':
            # Température avec drift lent et pics occasionnels
            self.state['temperature'] += random.uniform(-0.5, 0.5)
            # 2% de chance de pic de température
            if random.random() < 0.02:
                self.state['temperature'] += random.uniform(10, 30)
            # Garder dans une plage réaliste
            self.state['temperature'] = max(15, min(100, self.state['temperature']))
            self.state['humidity'] = 45 + random.uniform(-5, 5)
        
        elif self.device_type == 'pressure':
            # Pression avec variations
            self.state['pressure'] += random.uniform(-0.1, 0.1)
            # 3% de chance de surpression
            if random.random() < 0.03:
                self.state['pressure'] += random.uniform(2, 4)
            self.state['pressure'] = max(0, min(10, self.state['pressure']))
        
        elif self.device_type == 'vibration':
            # Vibrations normales
            self.state['vibration_x'] = random.uniform(0, 2)
            self.state['vibration_y'] = random.uniform(0, 2)
            self.state['vibration_z'] = random.uniform(0, 2)
            # 4% de chance de vibrations anormales
            if random.random() < 0.04:
                axis = random.choice(['vibration_x', 'vibration_y', 'vibration_z'])
                self.state[axis] += random.uniform(8, 15)
        
        elif self.device_type == 'energy':
            # Consommation d'énergie variable
            self.state['power'] = random.uniform(5, 25)
            self.state['energy_total'] += (self.state['power'] * self.publish_interval) / 3600
            self.state['voltage'] = 230 + random.uniform(-5, 5)
            self.state['current'] = self.state['power'] / self.state['voltage'] * 1000
        
        # Créer le message
        message = {
            **self.state,
            'timestamp': timestamp
        }
        
        return message
    
    def on_connect(self, client, userdata, flags, rc):
        """Callback de connexion"""
        if rc == 0:
            self.connected = True
            print(f"[{self.device_id}] ✓ Connecté au broker MQTT avec TLS")
        else:
            print(f"[{self.device_id}] ✗ Échec de connexion, code: {rc}")
            self.connected = False
    
    def on_disconnect(self, client, userdata, rc):
        """Callback de déconnexion"""
        self.connected = False
        if rc != 0:
            print(f"[{self.device_id}] ✗ Déconnexion inattendue, code: {rc}")
    
    def on_publish(self, client, userdata, mid):
        """Callback de publication"""
        pass  # Succès silencieux
    
    def setup_mqtt(self):
        """Configure le client MQTT avec TLS"""
        try:
            # Créer le client
            self.client = mqtt.Client(client_id=self.device_id)
            
            # Configurer TLS
            self.client.tls_set(
                ca_certs=self.ca_cert,
                certfile=self.client_cert,
                keyfile=self.client_key,
                cert_reqs=ssl.CERT_REQUIRED,
                tls_version=ssl.PROTOCOL_TLSv1_2
            )
            
            # Attacher les callbacks
            self.client.on_connect = self.on_connect
            self.client.on_disconnect = self.on_disconnect
            self.client.on_publish = self.on_publish
            
            # Connexion avec retry
            max_retries = 10
            retry_delay = 5
            
            for attempt in range(max_retries):
                try:
                    print(f"[{self.device_id}] Tentative de connexion {attempt + 1}/{max_retries}...")
                    self.client.connect(self.mqtt_broker, self.mqtt_port, 60)
                    self.client.loop_start()
                    
                    # Attendre la connexion
                    wait_time = 0
                    while not self.connected and wait_time < 10:
                        time.sleep(1)
                        wait_time += 1
                    
                    if self.connected:
                        return True
                    
                except Exception as e:
                    print(f"[{self.device_id}] Erreur de connexion: {e}")
                
                if attempt < max_retries - 1:
                    print(f"[{self.device_id}] Nouvelle tentative dans {retry_delay}s...")
                    time.sleep(retry_delay)
            
            print(f"[{self.device_id}] ✗ Échec de connexion après {max_retries} tentatives")
            return False
            
        except Exception as e:
            print(f"[{self.device_id}] ✗ Erreur lors de la configuration MQTT: {e}")
            return False
    
    def run(self):
        """Boucle principale de simulation"""
        if not self.setup_mqtt():
            print(f"[{self.device_id}] Arrêt du simulateur")
            return
        
        print(f"[{self.device_id}] Démarrage de la simulation...")
        
        try:
            while True:
                if self.connected:
                    # Générer les données
                    data = self._simulate_data()
                    payload = json.dumps(data, indent=2)
                    
                    # Publier
                    result = self.client.publish(self.topic, payload, qos=1)
                    
                    if result.rc == mqtt.MQTT_ERR_SUCCESS:
                        print(f"[{self.device_id}] ✓ Données publiées sur {self.topic}")
                        if self.device_type == 'production':
                            print(f"    Status: {data['status']}, Speed: {data['speed']:.1f} RPM")
                        elif self.device_type == 'temperature':
                            print(f"    Temp: {data['temperature']:.1f}°C, Humidity: {data['humidity']:.1f}%")
                    else:
                        print(f"[{self.device_id}] ✗ Échec de publication")
                else:
                    print(f"[{self.device_id}] ⚠ Non connecté, reconnexion...")
                    self.client.reconnect()
                
                time.sleep(self.publish_interval)
                
        except KeyboardInterrupt:
            print(f"\n[{self.device_id}] Arrêt demandé par l'utilisateur")
        except Exception as e:
            print(f"[{self.device_id}] ✗ Erreur: {e}")
        finally:
            if self.client:
                self.client.loop_stop()
                self.client.disconnect()
            print(f"[{self.device_id}] Simulateur arrêté")

if __name__ == "__main__":
    simulator = IoTSimulator()
    simulator.run()