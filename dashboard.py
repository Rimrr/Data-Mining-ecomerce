import streamlit as st
import pandas as pd
import sqlite3
import os
import time
import plotly.express as px

# Mode large par défaut pour occuper l'espace intelligemment en plein écran
st.set_page_config(
    page_title="Conversion Intel v2 - Premium SaaS", 
    page_icon="📈", 
    layout="wide"
)

# --- BLOC CSS AVANCÉ CORRECTIF POUR LE PLEIN ÉCRAN ---
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght=300;400;500;600;700&display=swap');
    
    /* 1. Fixation du fond global pour l'application */
    .stApp, [data-testid="stAppViewContainer"] { 
        background-color: #05060f !important; 
        font-family: 'Inter', sans-serif; 
    }
    
    /* 2. FIX DU PLEIN ÉCRAN BLANC : Force le fond sombre et la structure pro en plein écran */
    [data-testid="stFullScreenFrame"], 
    .stFullScreenFrame, 
    div[class*="stFullScreenFrame"],
    [data-testid="stPlotlyChart"] {
        background-color: #05060f !important;
    }
    
    /* Nettoyage des bordures blanches générées par l'iframe plein écran */
    iframe {
        background-color: #05060f !important;
    }
    
    h1, h2, h3, h4 { color: #ffffff !important; font-weight: 700; }
    
    /* Cartes de KPI modernisées */
    .kpi-card {
        background: linear-gradient(135deg, #0e1126 0%, #070814 100%);
        border: 1px solid #1c2142;
        padding: 22px;
        border-radius: 12px;
        text-align: center;
        box-shadow: 0 4px 20px rgba(0,0,0,0.5);
        transition: transform 0.2s;
    }
    .kpi-card:hover { transform: translateY(-2px); border-color: #2b3366; }
    .kpi-title { color: #7689c4; font-size: 13px; text-transform: uppercase; letter-spacing: 1px; font-weight: 600; }
    .kpi-value { color: #ffffff; font-size: 36px; font-weight: 700; margin-top: 5px; }
    
    /* Badges de Segments */
    .action-badge { padding: 5px 12px; border-radius: 6px; font-size: 12px; font-weight: 600; display: inline-block; text-align: center; min-width: 120px; }
    .badge-buy { background-color: rgba(52, 211, 153, 0.12); color: #34d399; border: 1px solid rgba(52, 211, 153, 0.4); }
    .badge-hesitant { background-color: rgba(251, 191, 36, 0.12); color: #fbbf24; border: 1px solid rgba(251, 191, 36, 0.4); }
    .badge-nobuy { background-color: rgba(248, 113, 113, 0.12); color: #f87171; border: 1px solid rgba(248, 113, 113, 0.4); }

    /* Customisation des onglets */
    .stTabs [data-baseweb="tab"] { color: #7689c4 !important; font-size: 15px; font-weight: 500; }
    .stTabs [data-baseweb="tab"][aria-selected="true"] { color: #ffffff !important; border-bottom-color: #6366f1 !important; }
</style>
""", unsafe_allow_html=True)

# Définition stricte et robuste du chemin absolu de la BDD
DB_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "saas.db"))

def load_data_from_db():
    if not os.path.exists(DB_PATH):
        return pd.DataFrame()
    try:
        # Utilisation d'un timeout pour éviter les verrous de lecture/écriture avec FastAPI
        conn = sqlite3.connect(DB_PATH, timeout=10.0)
        df = pd.read_sql_query("SELECT * FROM live_traffic ORDER BY id DESC", conn)
        conn.close()
        return df
    except Exception:
        return pd.DataFrame()

# Configuration des seuils dans la session state pour garder la mémoire entre les rechargements
if "min_hot_threshold" not in st.session_state:
    st.session_state.min_hot_threshold = 75
if "min_hesitant_threshold" not in st.session_state:
    st.session_state.min_hesitant_threshold = 40

# --- ACCUEIL & EN-TÊTE ---
st.title("⚡ Conversion Intelligence Dashboard v2")
st.markdown("<p style='color: #7689c4; font-size:15px; margin-top:-10px;'>Plateforme SaaS de prédiction comportementale et d'automatisation marketing en temps réel.</p>", unsafe_allow_html=True)
st.write("---")

df = load_data_from_db()

if df.empty:
    st.warning("⏱️ En attente des données de session... Veuillez démarrer `tracker_simulator.py` pour animer l'interface.")
    # Petit bouton manuel au cas où la BDD met du temps à se créer
    if st.button("🔄 Rafraîchir manuellement"):
        st.rerun()
else:
    # --- CALCULS DES METRIQUES ---
    total_sessions = len(df)
    buyers_df = df[df['purchase_probability'] >= st.session_state.min_hot_threshold]
    hesitants_df = df[(df['purchase_probability'] >= st.session_state.min_hesitant_threshold) & (df['purchase_probability'] < st.session_state.min_hot_threshold)]
    cold_df = df[df['purchase_probability'] < st.session_state.min_hesitant_threshold]
    conv_rate = (len(buyers_df) / total_sessions) * 100 if total_sessions > 0 else 0.0

    # --- SECTION KPIs EN GRILLE LARGE ---
    kpi1, kpi2, kpi3, kpi4 = st.columns(4)
    with kpi1:
        st.markdown(f'<div class="kpi-card"><div class="kpi-title">👥 Visites Analysées</div><div class="kpi-value">{total_sessions}</div></div>', unsafe_allow_html=True)
    with kpi2:
        st.markdown(f'<div class="kpi-card"><div class="kpi-title">💰 Taux de Conversion global</div><div class="kpi-value">{conv_rate:.1f}%</div></div>', unsafe_allow_html=True)
    with kpi3:
        st.markdown(f'<div class="kpi-card"><div class="kpi-title">🔥 Clients Chauds</div><div class="kpi-value">{len(buyers_df)}</div></div>', unsafe_allow_html=True)
    with kpi4:
        st.markdown(f'<div class="kpi-card"><div class="kpi-title">⏳ Visiteurs Hésitants</div><div class="kpi-value">{len(hesitants_df)}</div></div>', unsafe_allow_html=True)

    st.write("")
    st.write("")

    # --- LES ONGLETS ---
    tab_analytics, tab_rules, tab_inspector = st.tabs([
        "📊 Graphiques & Analytics", 
        "⚙️ Règles d'Automatisation (IA)", 
        "🔍 Inspecteur de Sessions & Trafic"
    ])

    # ---------------------------------------------------------
    # ONGLET 1: GRAPHICS & ANALYTICS
    # ---------------------------------------------------------
    with tab_analytics:
        st.write("")
        col_g1, col_g2 = st.columns(2)
        
        with col_g1:
            with st.container(border=True):
                st.markdown("#### 🎯 Répartition des profils clients")
                segment_counts = pd.DataFrame({
                    'Segment': ['Achat Probable', 'Hésitant', 'Faible Intention'],
                    'Nombre': [len(buyers_df), len(hesitants_df), len(cold_df)]
                })
                fig_pie = px.pie(
                    segment_counts, names='Segment', values='Nombre',
                    color='Segment',
                    color_discrete_map={'Achat Probable':'#34d399', 'Hésitant':'#fbbf24', 'Faible Intention':'#f87171'},
                    hole=0.4
                )
                fig_pie.update_layout(template="plotly_dark", paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', margin=dict(t=20, b=20, l=10, r=10))
                st.plotly_chart(fig_pie, use_container_width=True)
            
        with col_g2:
            with st.container(border=True):
                st.markdown("#### 📊 Impact de la valeur de page (Page Values)")
                fig_scatter = px.scatter(
                    df, x='page_values', y='purchase_probability',
                    color='segment',
                    labels={'page_values': 'Valeur de la Page', 'purchase_probability': 'Probabilité %'},
                    color_discrete_map={'Achat Probable':'#34d399', 'Hésitant':'#fbbf24', 'Faible Intention':'#f87171'}
                )
                fig_scatter.update_layout(template="plotly_dark", paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', margin=dict(t=20, b=20, l=10, r=10))
                st.plotly_chart(fig_scatter, use_container_width=True)

    # ---------------------------------------------------------
    # ONGLET 2: RULES ENGINE
    # ---------------------------------------------------------
    with tab_rules:
        st.write("")
        col_slider_left, col_info_right = st.columns([4, 5])
        
        with col_slider_left:
            with st.container(border=True):
                st.markdown("#### 🛠️ Paramètres des Triggers")
                new_hot = st.slider("Seuil minimum pour Client 'Chaud' (%)", 50, 95, st.session_state.min_hot_threshold)
                new_hesitant = st.slider("Seuil minimum pour Client 'Hésitant' (%)", 10, 49, st.session_state.min_hesitant_threshold)
                
                if new_hot != st.session_state.min_hot_threshold or new_hesitant != st.session_state.min_hesitant_threshold:
                    st.session_state.min_hot_threshold = new_hot
                    st.session_state.min_hesitant_threshold = new_hesitant
                    st.toast("🎯 Seuils de l'IA mis à jour !", icon="✅")
                    time.sleep(0.3)
                    st.rerun()
                    
        with col_info_right:
            with st.container(border=True):
                st.markdown("#### 📋 Logique Métier Actuelle")
                st.markdown(f"🟢 **>= {st.session_state.min_hot_threshold}%** : Tunnel d'achat fluide (Aucune perturbation).")
                st.markdown(f"🟡 **Entre {st.session_state.min_hesitant_threshold}% et {st.session_state.min_hot_threshold}%** : Injection de preuve sociale en direct.")
                st.markdown(f"🔴 **< {st.session_state.min_hesitant_threshold}%** : Déclenchement automatique d'un coupon de réduction de sortie.")

    # ---------------------------------------------------------
    # ONGLET 3: INSPECTOR & LIVE TRAFFIC
    # ---------------------------------------------------------
    with tab_inspector:
        st.write("")
        
        f_col1, f_col2 = st.columns(2)
        with f_col1:
            segment_filter = st.selectbox("Filtrer par segment :", ["Tous les visiteurs", "Achat Probable", "Hésitant", "Faible Intention"])
        
        filtered_df = df.copy()
        if segment_filter != "Tous les visiteurs":
            filtered_df = df[df['segment'] == segment_filter]

        with f_col2:
            if not filtered_df.empty:
                session_options = [f"Session #{row['id']} ({row['purchase_probability']}% - {row['timestamp']})" for _, row in filtered_df.iterrows()]
                selected_session_str = st.selectbox("🔬 Sélectionner une session à inspecter :", session_options)
                selected_id = int(selected_session_str.split("#")[1].split(" ")[0])
                session_details = df[df['id'] == selected_id].iloc[0]

        if not filtered_df.empty:
            with st.container(border=True):
                st.markdown(f"### 🔍 Fiche Comportementale : Session #{selected_id}")
                det_c1, det_c2, det_c3 = st.columns(3)
                det_c1.metric(label="Score d'Intention", value=f"{session_details['purchase_probability']}%")
                det_c2.metric(label="Valeur de Page (PageValues)", value=f"{session_details['page_values']}")
                det_c3.metric(label="Taux de Sortie (ExitRates)", value=f"{session_details['exit_rates']}")
                st.markdown(f"👉 **Action Automatique exécutée :** `{session_details['action_taken']}`")

        st.write("")
        st.markdown("#### 📡 Journal Complet du Flux Temps Réel")
        
        with st.container():
            h_time, h_id, h_prob, h_seg, h_action = st.columns([1, 1, 1, 2, 4])
            h_time.markdown("**Heure**")
            h_id.markdown("**ID Session**")
            h_prob.markdown("**Probabilité**")
            h_seg.markdown("**Segment**")
            h_action.markdown("**Action Marketing Déclenchée**")
            st.markdown("<hr style='margin: 8px 0; border-color: #1c2142;'>", unsafe_allow_html=True)

        for _, row in filtered_df.head(15).iterrows():
            col_time, col_id, col_prob, col_seg, col_action = st.columns([1, 1, 1, 2, 4])
            
            with col_time:
                st.markdown(f"<p style='color: #7689c4; margin-top:4px;'>⏱️ {row['timestamp']}</p>", unsafe_allow_html=True)
            with col_id:
                st.markdown(f"<p style='color: #ffffff; font-weight:600; margin-top:4px;'>Session #{row['id']}</p>", unsafe_allow_html=True)
            with col_prob:
                st.markdown(f"<p style='color: #34d399; font-weight:700; margin-top:4px;'>{row['purchase_probability']}%</p>", unsafe_allow_html=True)
            with col_seg:
                if row['segment'] == "Achat Probable":
                    st.markdown(f"<span class='action-badge badge-buy'>{row['segment']}</span>", unsafe_allow_html=True)
                elif row['segment'] == "Hésitant":
                    st.markdown(f"<span class='action-badge badge-hesitant'>{row['segment']}</span>", unsafe_allow_html=True)
                else:
                    st.markdown(f"<span class='action-badge badge-nobuy'>{row['segment']}</span>", unsafe_allow_html=True)
            with col_action:
                st.markdown(f"<p style='color: #e2e8f0; font-size:14px; margin-top:4px;'>⚙️ {row['action_taken']}</p>", unsafe_allow_html=True)
            
            st.markdown("<hr style='margin: 4px 0; border-color: rgba(255,255,255,0.03);'>", unsafe_allow_html=True)

    # --- GESTION DU RAFRAÎCHISSEMENT INTELLIGENT ---
    # Un rechargement silencieux toutes les 4 secondes pour coller à la vitesse du simulateur 
    # sans bloquer les clics de l'inspecteur de l'utilisateur.
    st.write("")
    if "last_refresh" not in st.session_state:
        st.session_state.last_refresh = time.time()
        
    if time.time() - st.session_state.last_refresh > 4.0:
        st.session_state.last_refresh = time.time()
        st.rerun()