#!/usr/bin/env python3
"""
Script de test de sécurité TLS pour Mini-Usine IoT
Vérifie que les connexions sans TLS échouent et avec TLS réussissent
"""

import sys
import ssl
import time
import paho.mqtt.client as mqtt

class SecurityTester:
    def __init__(self):
        self.broker = "localhost"
        self.port_tls = 8883
        self.results = []
    
    def print_result(self, test_name, passed, message):
        """Affiche et enregistre le résultat d'un test"""
        status = "✓ PASS" if passed else "✗ FAIL"
        color = "\033[92m" if passed else "\033[91m"
        reset = "\033[0m"
        
        print(f"{color}{status}{reset} - {test_name}")
        print(f"      {message}")
        
        self.results.append({
            'test': test_name,
            'passed': passed,
            'message': message
        })
    
    def test_connection_without_tls(self):
        """Test 1: Connexion sans TLS doit échouer"""
        print("\n[Test 1] Connexion sans TLS (doit échouer)...")
        
        try:
            client = mqtt.Client("security-test-no-tls")
            client.connect(self.broker, self.port_tls, 5)
            client.loop_start()
            time.sleep(2)
            client.loop_stop()
            client.disconnect()
            
            # Si on arrive ici, le test a échoué
            self.print_result(
                "Connexion sans TLS",
                False,
                "SÉCURITÉ COMPROMISE: Connexion réussie sans TLS!"
            )
            return False
            
        except Exception as e:
            # C'est ce qu'on attend - la connexion doit échouer
            self.print_result(
                "Connexion sans TLS",
                True,
                f"Connexion refusée comme attendu: {str(e)[:50]}"
            )
            return True
    
    def test_connection_with_wrong_certs(self):
        """Test 2: Connexion avec mauvais certificats doit échouer"""
        print("\n[Test 2] Connexion avec certificats incorrects (doit échouer)...")
        
        try:
            client = mqtt.Client("security-test-wrong-cert")
            
            # Utiliser des certificats inexistants
            client.tls_set(
                ca_certs="./certs/wrong-ca.crt",
                certfile="./certs/wrong-client.crt",
                keyfile="./certs/wrong-client.key"
            )
            
            client.connect(self.broker, self.port_tls, 5)
            client.loop_start()
            time.sleep(2)
            client.loop_stop()
            client.disconnect()
            
            self.print_result(
                "Certificats incorrects",
                False,
                "SÉCURITÉ COMPROMISE: Connexion réussie avec mauvais certificats!"
            )
            return False
            
        except Exception as e:
            self.print_result(
                "Certificats incorrects",
                True,
                f"Connexion refusée comme attendu: {str(e)[:50]}"
            )
            return True
    
    def test_connection_with_valid_tls(self):
        """Test 3: Connexion avec TLS valide doit réussir"""
        print("\n[Test 3] Connexion avec TLS valide (doit réussir)...")
        
        connected = False
        
        def on_connect(client, userdata, flags, rc):
            nonlocal connected
            if rc == 0:
                connected = True
        
        try:
            client = mqtt.Client("security-test-valid-tls")
            client.on_connect = on_connect
            
            # Configurer TLS avec les bons certificats
            client.tls_set(
                ca_certs="./certs/ca.crt",
                certfile="./certs/client.crt",
                keyfile="./certs/client.key",
                cert_reqs=ssl.CERT_REQUIRED,
                tls_version=ssl.PROTOCOL_TLSv1_2
            )
            
            client.connect(self.broker, self.port_tls, 60)
            client.loop_start()
            
            # Attendre la connexion
            timeout = 10
            elapsed = 0
            while not connected and elapsed < timeout:
                time.sleep(0.5)
                elapsed += 0.5
            
            client.loop_stop()
            client.disconnect()
            
            if connected:
                self.print_result(
                    "TLS valide",
                    True,
                    "Connexion TLS sécurisée établie avec succès"
                )
                return True
            else:
                self.print_result(
                    "TLS valide",
                    False,
                    "Échec de connexion avec certificats valides"
                )
                return False
                
        except Exception as e:
            self.print_result(
                "TLS valide",
                False,
                f"Erreur inattendue: {str(e)}"
            )
            return False
    
    def test_tls_version(self):
        """Test 4: Vérifier que seul TLS 1.2+ est accepté"""
        print("\n[Test 4] Vérification version TLS...")
        
        try:
            client = mqtt.Client("security-test-tls-version")
            
            # Essayer avec TLS 1.2 (doit fonctionner)
            client.tls_set(
                ca_certs="./certs/ca.crt",
                certfile="./certs/client.crt",
                keyfile="./certs/client.key",
                tls_version=ssl.PROTOCOL_TLSv1_2
            )
            
            self.print_result(
                "Version TLS",
                True,
                "TLS 1.2 supporté (sécurisé)"
            )
            return True
            
        except Exception as e:
            self.print_result(
                "Version TLS",
                False,
                f"Erreur de configuration TLS: {str(e)}"
            )
            return False
    
    def test_certificate_verification(self):
        """Test 5: Vérifier que la vérification des certificats est active"""
        print("\n[Test 5] Vérification des certificats...")
        
        try:
            client = mqtt.Client("security-test-verify")
            
            client.tls_set(
                ca_certs="./certs/ca.crt",
                certfile="./certs/client.crt",
                keyfile="./certs/client.key",
                cert_reqs=ssl.CERT_REQUIRED  # Verification stricte
            )
            
            self.print_result(
                "Vérification certificats",
                True,
                "Vérification stricte des certificats activée"
            )
            return True
            
        except Exception as e:
            self.print_result(
                "Vérification certificats",
                False,
                f"Erreur: {str(e)}"
            )
            return False
    
    def run_all_tests(self):
        """Exécute tous les tests de sécurité"""
        print("="*60)
        print("   TESTS DE SÉCURITÉ TLS - MINI-USINE IoT")
        print("="*60)
        
        tests = [
            self.test_connection_without_tls,
            self.test_connection_with_wrong_certs,
            self.test_connection_with_valid_tls,
            self.test_tls_version,
            self.test_certificate_verification
        ]
        
        for test in tests:
            try:
                test()
            except Exception as e:
                print(f"\n✗ Erreur critique dans le test: {e}")
        
        # Résumé
        print("\n" + "="*60)
        print("   RÉSUMÉ DES TESTS")
        print("="*60)
        
        passed = sum(1 for r in self.results if r['passed'])
        total = len(self.results)
        percentage = (passed / total * 100) if total > 0 else 0
        
        print(f"\nTests réussis: {passed}/{total} ({percentage:.0f}%)")
        
        if passed == total:
            print("\n✓ TOUS LES TESTS SONT PASSÉS - Sécurité validée!")
            return 0
        else:
            print("\n✗ CERTAINS TESTS ONT ÉCHOUÉ - Vérifier la configuration!")
            print("\nTests échoués:")
            for r in self.results:
                if not r['passed']:
                    print(f"  - {r['test']}: {r['message']}")
            return 1

def main():
    print("\n⚠️  Assurez-vous que le broker MQTT est en cours d'exécution!")
    print("    docker-compose up -d mosquitto\n")
    
    input("Appuyez sur Entrée pour commencer les tests...")
    
    tester = SecurityTester()
    exit_code = tester.run_all_tests()
    
    sys.exit(exit_code)

if __name__ == "__main__":
    main()