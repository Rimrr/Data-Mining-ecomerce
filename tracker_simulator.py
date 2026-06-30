import time
import random
import requests

# URL pointant vers ton API locale FastAPI
API_URL = "http://127.0.0.1:8000/api/v1/predict"

def generate_mock_session(session_type: str) -> dict:
    """Génère des profils d'utilisateurs réalistes pour le flux d'entrée."""
    if session_type == "high_intent":
        return {
            "Administrative": random.randint(2, 5),
            "Administrative_Duration": round(random.uniform(40.0, 150.0), 2),
            "Informational": random.randint(1, 3),
            "Informational_Duration": round(random.uniform(20.0, 60.0), 2),
            "ProductRelated": random.randint(15, 45),
            "ProductRelated_Duration": round(random.uniform(300.0, 1200.0), 2),
            "BounceRates": 0.0,
            "ExitRates": round(random.uniform(0.01, 0.03), 4),
            "PageValues": round(random.uniform(25.0, 85.0), 2),
            "SpecialDay": 0.0,
            "Month": "May",  # Corrigé en chaîne de caractères (str)
            "OperatingSystems": 2,
            "Browser": 2,
            "Region": 1,
            "TrafficType": 2,
            "VisitorType": "Returning_Visitor",  # Corrigé en chaîne de caractères (str)
            "Weekend": random.choice([True, False])  # Corrigé en booléen
        }
    else:
        return {
            "Administrative": random.randint(0, 1),
            "Administrative_Duration": round(random.uniform(0.0, 20.0), 2),
            "Informational": 0,
            "Informational_Duration": 0.0,
            "ProductRelated": random.randint(1, 4),
            "ProductRelated_Duration": round(random.uniform(5.0, 45.0), 2),
            "BounceRates": round(random.uniform(0.05, 0.18), 4),
            "ExitRates": round(random.uniform(0.06, 0.20), 4),
            "PageValues": 0.0,
            "SpecialDay": 0.0,
            "Month": "May",  # Corrigé en chaîne de caractères (str)
            "OperatingSystems": 1,
            "Browser": 1,
            "Region": 3,
            "TrafficType": 1,
            "VisitorType": "New_Visitor",  # Corrigé en chaîne de caractères (str)
            "Weekend": random.choice([True, False])  # Corrigé en booléen
        }

def start_clickstream_simulation():
    print("🚀 Démarrage du Simulateur de Trafic Connecté (Boucle Fermée)...")
    print("Appuyez sur CTRL+C pour arrêter le flux de données.\n" + "="*70)
    
    session_id_counter = 2000
    
    try:
        while True:
            session_id_counter += 1
            cohort = random.choice(["high_intent", "window_shopper"])
            payload = generate_mock_session(cohort)
            
            print(f"📡 [Session #{session_id_counter}] Activité détectée sur le site. Envoi des métriques à l'API...")
            
            try:
                response = requests.post(API_URL, json=payload)
                
                if response.status_code == 200:
                    data = response.json()
                    prob = data["purchase_probability"]
                    trigger = data.get("trigger_code", "UNKNOWN")
                    
                    marker = "🟢" if data["will_buy"] else "🚨"
                    print(f"   {marker} Moteur IA : Score {prob}% d'intention d'achat | Confiance : {data['confidence_level']}")
                    print(f"   📥 Code d'action intercepté par le site client : '{trigger}'")
                    
                    # 🚀 SIMULATION DE LA RÉACTION DU SCRIPT SUR LE SITE WEB
                    if trigger == "SHOW_EXIT_COUPON":
                        print("   💥 [SCRIPT INTERFACE SITE] Action exécutée -> Injection immédiate d'une Pop-up :")
                        print("      'Attendez ! Ne partez pas les mains vides. Entrez le code SAAS10 pour obtenir -10% de réduction !'")
                    elif trigger == "SHOW_SOCIAL_PROOF":
                        print("   🔥 [SCRIPT INTERFACE SITE] Action exécutée -> Injection d'un élément de Preuve Sociale :")
                        print("      'Alerte : 3 autres utilisateurs examinent actuellement ce produit. Stock limité !'")
                    elif trigger == "NO_INTERRUPTION":
                        print("   ✅ [SCRIPT INTERFACE SITE] Action exécutée -> Expérience utilisateur fluide et sans distraction.")
                        print("      Le client sait ce qu'il veut, aucun obstacle n'est ajouté sur son chemin vers le paiement.")
                    
                    print("-" * 70 + "\n")
                else:
                    print(f"   ❌ Échec de la requête. Code HTTP retourné par l'API : {response.status_code}")
                    print(f"      Détail de l'erreur : {response.text}\n")
            
            except requests.exceptions.ConnectionError:
                print("   ❌ Erreur Critique : Impossible de se connecter à l'API FastAPI. Vérifiez que uvicorn est lancé.\n")
                
            time.sleep(4)
            
    except KeyboardInterrupt:
        print("\n🛑 Simulation interrompue.")

if __name__ == "__main__":
    start_clickstream_simulation()