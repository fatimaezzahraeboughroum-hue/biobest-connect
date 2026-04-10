# This is a sample Python script.

# Press Maj+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.
from streamlit_autorefresh import st_autorefresh
import streamlit as st
import gspread
from datetime import datetime

# --- 1. CONFIGURATION ---
st.set_page_config(page_title="Biobest Connect", layout="centered")

st.markdown("""
    <style>
    .stApp { background-color: #f4f7f6; }
    .client-card { background-color: #ffebee; padding: 20px; border-radius: 15px; border-left: 10px solid #e57373; margin-bottom: 15px; }
    .dg-card { background-color: #e8f5e9; padding: 20px; border-radius: 15px; border-left: 10px solid #4caf50; margin-bottom: 15px; }
    .montant { color: #d32f2f; font-weight: bold; font-size: 1.2rem; }
    .alerte-tag { background-color: #fce4ec; color: #c2185b; padding: 5px 10px; border-radius: 5px; font-size: 0.9rem; font-weight: bold; border: 1px solid #f8bbd0; }
    </style>
    """, unsafe_allow_html=True)
# --- REFRESH AUTOMATIQUE ---
# interval=10000 signifie 10 000 millisecondes = 10 secondes
# key="datarefresh" est un nom interne pour Streamlit
st_autorefresh(interval=10000, key="datarefresh")

st.sidebar.info("🔄 Actualisation auto : 10s")

# --- 2. CONNEXION ---
@st.cache_resource
def connecter_google():
    try:
        gc = gspread.service_account(filename='creds.json')
        sh = gc.open_by_key("1GXK6mcAY7Fhtfj_miGBu2_xXciaFpGsUnryc4n0ln1E")
        return sh.get_worksheet(0)
    except Exception as e:
        st.error(f"Erreur de connexion : {e}")
        return None


worksheet = connecter_google()

# --- 3. AUTHENTIFICATION ---
st.sidebar.title("🔐 Accès Biobest")
profil = st.sidebar.selectbox("Rôle :", ["Choisir...", "Commercial", "Directeur Général"])
password = st.sidebar.text_input("Mot de passe :", type="password")

# --- 4. LOGIQUE ---
if worksheet:
    valeurs = worksheet.get_all_values()
    data = valeurs[1:] if len(valeurs) > 1 else []

    # --- ACCÈS COMMERCIAL ---
    if profil == "Commercial" and password == "com2026":
        st.title("📱 Espace Commercial")
        trouve = False
        for i, ligne in enumerate(data):
            statut = str(ligne[2]).strip().lower() if len(ligne) > 2 else ""
            justif = str(ligne[4]).strip() if len(ligne) > 4 else ""
            # On récupère l'alerte (Colonne D / Index 3)
            alerte = str(ligne[3]).strip() if len(ligne) > 3 else "Non spécifié"

            if "bloque" in statut and len(justif) < 2:
                trouve = True
                st.markdown(f"""
                    <div class="client-card">
                        <h3>🏢 {ligne[0]}</h3>
                        <p class="montant">💰 {ligne[1]} DH</p>
                        <p><span class="alerte-tag">⚠️ Motif : {alerte}</span></p>
                    </div>
                """, unsafe_allow_html=True)

                txt = st.text_area(f"Justification pour {ligne[0]} :", key=f"c_{i}")
                if st.button("Envoyer au DG", key=f"btn_{i}"):
                    if len(txt) > 2:
                        worksheet.update_cell(i + 2, 5, txt)
                        worksheet.update_cell(i + 2, 6, datetime.now().strftime("%H:%M"))
                        st.rerun()
        if not trouve:
            st.success("✅ Aucun dossier à justifier.")

    # --- ACCÈS DG ---
    elif profil == "Directeur Général" and password == "dg_admin":
        st.title("👨‍💼 Espace Direction")
        trouve_dg = False
        for i, ligne in enumerate(data):
            justif_com = str(ligne[4]).strip() if len(ligne) > 4 else ""
            decision_dg = str(ligne[6]).strip() if len(ligne) > 6 else ""
            # On récupère l'alerte (Colonne D / Index 3)
            alerte = str(ligne[3]).strip() if len(ligne) > 3 else "Non spécifié"

            if len(justif_com) > 2 and len(decision_dg) < 2:
                trouve_dg = True
                st.markdown(f"""
                    <div class="dg-card">
                        <h3>🏢 {ligne[0]}</h3>
                        <p>💰 {ligne[1]} DH | <span class="alerte-tag">⚠️ {alerte}</span></p>
                        <hr>
                        <p><b>📝 Justification reçue :</b><br>{justif_com}</p>
                    </div>
                """, unsafe_allow_html=True)

                c1, c2 = st.columns(2)
                if c1.button("✅ Autoriser", key=f"ok_{i}"):
                    worksheet.update_cell(i + 2, 7, "AUTORISÉ")
                    st.rerun()
                if c2.button("❌ Refuser", key=f"no_{i}"):
                    worksheet.update_cell(i + 2, 7, "REFUSÉ")
                    st.rerun()
        if not trouve_dg:
            st.info("☕ Aucun dossier à valider.")

    elif profil != "Choisir..." and password != "":
        st.sidebar.error("❌ Identifiants incorrects")