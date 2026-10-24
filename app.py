"""Tableau de bord Streamlit : prévision de la demande 2026.

Lancement : python3 -m streamlit run app.py
Lit outputs/prevision_2026.csv (généré par la partie 7 du notebook).
"""
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd
import streamlit as st

CSV = Path("outputs/prevision_2026.csv")
MAGASINS = Path("data/magasins.csv")

st.set_page_config(page_title="Prévision 2026", page_icon="📈", layout="wide")
st.title("📈 Prévision de la demande 2026")
st.caption("Fêtes et consommation au Sénégal · quantités prévues par jour, magasin et catégorie (plafond P90 inclus)")


@st.cache_data
def charger():
    df = pd.read_csv(CSV, parse_dates=["date"])
    noms = {}
    if MAGASINS.exists():
        m = pd.read_csv(MAGASINS)
        if {"magasin_id", "ville"} <= set(m.columns):
            noms = dict(zip(m.magasin_id, m.ville))
    df["magasin"] = df.magasin_id.map(lambda i: f"{i} · {noms[i]}" if i in noms else i)
    return df


if not CSV.exists():
    st.error(f"Fichier introuvable : {CSV}. Exécute d'abord le notebook (partie 7).")
    st.stop()

df = charger()

# Filtres
st.sidebar.header("Filtres")
categories = sorted(df.categorie.unique())
magasins = sorted(df.magasin.unique())
cat = st.sidebar.selectbox("Catégorie", categories)
mags = st.sidebar.multiselect("Points de vente", magasins, default=magasins)
d0, d1 = df.date.min().date(), df.date.max().date()
periode = st.sidebar.date_input("Période", (d0, d1), min_value=d0, max_value=d1)
if len(periode) != 2:
    st.info("Choisis une date de début et une date de fin.")
    st.stop()

masque = (
    (df.categorie == cat)
    & df.magasin.isin(mags)
    & df.date.between(pd.Timestamp(periode[0]), pd.Timestamp(periode[1]))
)
sel = df[masque]
if sel.empty:
    st.warning("Aucune donnée pour ces filtres.")
    st.stop()

# Indicateurs
c1, c2, c3 = st.columns(3)
c1.metric("Total prévu", f"{sel.prevu.sum():,.0f}".replace(",", " "))
c2.metric("Plafond P90 (somme)", f"{sel.q90.sum():,.0f}".replace(",", " "))
jour_pic = sel.groupby("date").prevu.sum().idxmax()
c3.metric("Jour de pic", jour_pic.strftime("%d/%m/%Y"))

# Courbe journalière (matplotlib : évite pyarrow, parfois bloqué par Windows)
st.subheader(f"Demande quotidienne · {cat}")
jour = sel.groupby("date")[["prevu", "q90"]].sum()
fig, ax = plt.subplots(figsize=(10, 3.8))
ax.plot(jour.index, jour.prevu, label="Prévu", color="#1f4e79")
ax.plot(jour.index, jour.q90, label="Plafond P90", color="#c55a11", alpha=0.7)
ax.set_ylabel("Quantité")
ax.legend()
fig.autofmt_xdate()
st.pyplot(fig)

# Répartition par magasin
st.subheader("Total prévu par point de vente")
par_mag = sel.groupby("magasin").prevu.sum().sort_values()
fig2, ax2 = plt.subplots(figsize=(10, 3.8))
ax2.barh(par_mag.index, par_mag.values, color="#1f4e79")
ax2.set_xlabel("Quantité prévue")
st.pyplot(fig2)

with st.expander("Voir les données"):
    st.code(sel[["date", "magasin", "categorie", "prevu", "q90"]].head(200).to_string(index=False))
    st.download_button("Télécharger (CSV)", sel.to_csv(index=False).encode("utf-8"), "prevision_filtre.csv", "text/csv")
