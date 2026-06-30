import os
import sqlite3
import time
from datetime import datetime
import joblib
import numpy as np
import pandas as pd
from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field, AliasChoices

# --- INITIALISATION DE FASTAPI ---
app = FastAPI(title="E-Commerce SaaS Core Engine")

# --- CONFIGURATION DU SYSTEME DE CORS SÉCURISÉ ---
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- VARIABLES ET CONFIGURATION DES CHEMINS GLOBAUX ---

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

DB_PATH = os.path.join(BASE_DIR, "saas.db")
model_path = os.path.join(BASE_DIR, "Models", "model.pkl")  # Attention à la majuscule de 'Models'

# Variable de suivi d'activité (Heartbeat) pour le Live Tracking Engine
LAST_HEARTBEAT = 0.0

# --- CONFIGURATION DES SCHÉMAS PYDANTIC ---
class VisitorSession(BaseModel):
    Administrative: int = Field(default=0, validation_alias=AliasChoices('Administrative', 'administrative'))
    Administrative_Duration: float = Field(default=0.0, validation_alias=AliasChoices('Administrative_Duration', 'administrative_duration'))
    Informational: int = Field(default=0, validation_alias=AliasChoices('Informational', 'informational'))
    Informational_Duration: float = Field(default=0.0, validation_alias=AliasChoices('Informational_Duration', 'informational_duration'))
    ProductRelated: int = Field(default=0, validation_alias=AliasChoices('ProductRelated', 'productRelated', 'product_related'))
    ProductRelated_Duration: float = Field(default=0.0, validation_alias=AliasChoices('ProductRelated_Duration', 'productRelated_duration', 'product_related_duration'))
    BounceRates: float = Field(default=0.0, validation_alias=AliasChoices('BounceRates', 'bounceRates', 'bounce_rates'))
    ExitRates: float = Field(default=0.0, validation_alias=AliasChoices('ExitRates', 'exitRates', 'exit_rates'))
    PageValues: float = Field(default=0.0, validation_alias=AliasChoices('PageValues', 'pageValues', 'page_values'))
    SpecialDay: float = Field(default=0.0, validation_alias=AliasChoices('SpecialDay', 'specialDay', 'special_day'))
    Month: str = Field(default="May", validation_alias=AliasChoices('Month', 'month'))  # Corrigé en str
    OperatingSystems: int = Field(default=1, validation_alias=AliasChoices('OperatingSystems', 'operatingSystems', 'operating_systems'))
    Browser: int = Field(default=1, validation_alias=AliasChoices('Browser', 'browser'))
    Region: int = Field(default=1, validation_alias=AliasChoices('Region', 'region'))
    TrafficType: int = Field(default=1, validation_alias=AliasChoices('TrafficType', 'trafficType', 'traffic_type'))
    VisitorType: str = Field(default="Returning_Visitor", validation_alias=AliasChoices('VisitorType', 'visitorType', 'visitor_type'))  # Corrigé en str
    Weekend: bool = Field(default=False, validation_alias=AliasChoices('Weekend', 'weekend'))  # Booléen d'origine

class PredictionResponse(BaseModel):
    purchase_probability: float
    will_buy: bool
    confidence_level: str
    recommended_action: str
    trigger_code: str

# --- INITIALISATION BASE DE DONNÉES ---
def init_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS live_traffic (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT,
            purchase_probability REAL,
            will_buy INTEGER,
            segment TEXT,
            action_taken TEXT,
            trigger_code TEXT,
            page_values REAL,
            exit_rates REAL
        )
    """)
    conn.commit()
    conn.close()

@app.on_event("startup")
def load_ml_components():
    global pipeline_model
    init_db()
    try:
        if os.path.exists(model_path):
            pipeline_model = joblib.load(model_path)
            print("🎉 Pipeline complet chargé et Base de données initialisée avec succès !")
        else:
            print(f"❌ Fichier de modèle complet introuvables : \n -> {model_path}")
    except Exception as e:
        print(f"❌ Erreur lors du chargement : {str(e)}")

# --- ENDPOINT 1 : PRÉDICTION IA ET COMPORTEMENTALE ---
@app.post("/api/v1/predict", response_model=PredictionResponse)
async def predict_purchase_intention(session_data: VisitorSession):
    global LAST_HEARTBEAT
    
    LAST_HEARTBEAT = time.time()
    
    if pipeline_model is None:
        raise HTTPException(status_code=503, detail="Le pipeline de modèle complet est indisponible.")
    
    try:
        # 1. Reconstruction du dictionnaire de base reçu par l'API
        raw_dict = {
            "Administrative": session_data.Administrative,
            "Administrative_Duration": session_data.Administrative_Duration,
            "Informational": session_data.Informational,
            "Informational_Duration": session_data.Informational_Duration,
            "ProductRelated": session_data.ProductRelated,
            "ProductRelated_Duration": session_data.ProductRelated_Duration,
            "BounceRates": session_data.BounceRates,
            "ExitRates": session_data.ExitRates,
            "PageValues": session_data.PageValues,
            "SpecialDay": session_data.SpecialDay,
            "Month": session_data.Month,
            "OperatingSystems": session_data.OperatingSystems,
            "Browser": session_data.Browser,
            "Region": session_data.Region,
            "TrafficType": session_data.TrafficType,
            "VisitorType": session_data.VisitorType,
            "Weekend": session_data.Weekend
        }
        
        # Convertir temporairement en DataFrame pour injecter le Feature Engineering obligatoire
        df_features = pd.DataFrame([raw_dict])
        
        # 2. Injection à l'identique du Feature Engineering de la Section 07 du Notebook
        df_features['total_pages'] = df_features['Administrative'] + df_features['Informational'] + df_features['ProductRelated']
        df_features['total_duration'] = df_features['Administrative_Duration'] + df_features['Informational_Duration'] + df_features['ProductRelated_Duration']
        df_features['product_duration_ratio'] = np.where(
            df_features['total_duration'] > 0, 
            df_features['ProductRelated_Duration'] / df_features['total_duration'], 
            0.0
        )
        
        # 3. Prédiction directe via le Pipeline (Prétraitement automatique inclus)
        prediction = int(pipeline_model.predict(df_features)[0])
        probabilities = pipeline_model.predict_proba(df_features)[0]
        
        purchase_probability = float(probabilities[1]) * 100
        will_buy = bool(prediction == 1)
        
        # Attribution des règles de déclenchement marketing (Automation)
        if purchase_probability >= 75.0:
            confidence = "Très Élevée"
            action = "High-Value Target. Pas d'interruption nécessaire."
            segment = "Achat Probable"
            trigger_code = "NO_INTERRUPTION"
        elif 40.0 <= purchase_probability < 75.0:
            confidence = "Moyenne"
            action = "Hésitant. Déclencher une bannière de preuve sociale."
            segment = "Hésitant"
            trigger_code = "SHOW_SOCIAL_PROOF"
        else:
            confidence = "Faible"
            action = "Attention, Risque de Churn. Déclencher une offre de sortie."
            segment = "Faible Intention"
            trigger_code = "SHOW_EXIT_COUPON"
        
        # Enregistrement synchrone sécurisé dans SQLite
        try:
            conn = sqlite3.connect(DB_PATH, timeout=15.0)
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO live_traffic (timestamp, purchase_probability, will_buy, segment, action_taken, trigger_code, page_values, exit_rates)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                str(datetime.now().strftime("%H:%M:%S")),
                float(round(purchase_probability, 1)),
                1 if will_buy else 0,
                str(segment),
                str(action),
                str(trigger_code),
                float(session_data.PageValues),
                float(session_data.ExitRates)
            ))
            conn.commit()
            conn.close()
        except Exception as db_err:
            print(f"⚠️ Erreur d'écriture BDD : {db_err}")
        
        return PredictionResponse(
            purchase_probability=round(purchase_probability, 2),
            will_buy=will_buy,
            confidence_level=str(confidence),
            recommended_action=str(action),
            trigger_code=str(trigger_code)
        )
        
    except Exception as e:
        import traceback
        print("\n❌ --- TRACEBACK DU CRASH DU MOTEUR ---")
        traceback.print_exc()
        print("----------------------------------------\n")
        raise HTTPException(status_code=500, detail=f"Erreur interne : {str(e)}")

# --- ENDPOINT 2 : LIVE ENGINE STATUS CHECKS ---
@app.get("/api/v1/status")
async def get_tracking_engine_status():
    global LAST_HEARTBEAT
    if time.time() - LAST_HEARTBEAT < 5.0:
        return {"status": "active"}
    return {"status": "inactive"}