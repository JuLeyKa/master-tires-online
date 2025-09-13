import streamlit as st

# Automatische Weiterleitung zur Reifen Suche
# Diese Datei erscheint nicht in der Sidebar

if __name__ == "__main__":
    # Sofort zur Reifen Suche weiterleiten
    st.switch_page("pages/01_Reifen_Suche.py")