import streamlit as st
import pandas as pd
import plotly.express as px

# =========================
# CONFIGURATION GÉNÉRALE
# =========================
st.markdown("""
### **Analyse décisionnelle & Visualisation des données**
**Nom :** TCHUENTEU GUETCHUENG DAVID  
**Matricule :** 20U2891  
**UE :** INFO40113 – INTRODUCTION A L'INTELIGENCE ARTIFICIELLE
""")

st.set_page_config(page_title="TP1 INFO40113", layout="wide")

st.title("📊 Analyse décisionnelle – KPI des ventes")


# =========================
# CHARGEMENT DES DONNÉES
# =========================
@st.cache_data
def load_data():
    df = pd.read_excel("data_kpi.xlsx")

    # Nettoyage des montants
    df["Montant_Transaction"] = (
        df["Montant_Transaction"]
        .astype(str)
        .str.replace("XAF", "", regex=False)
        .str.replace("€", "", regex=False)
        .str.replace(" ", "", regex=False)
        .str.replace(",", ".", regex=False)
    )
    df["Montant_Transaction"] = pd.to_numeric(df["Montant_Transaction"], errors="coerce")

    df = df.dropna(subset=["Montant_Transaction"])

    return df

df = load_data()

# =========================
# APERÇU DES DONNÉES
# =========================
st.header("Aperçu des données")
st.dataframe(df.head(), use_container_width=True)

st.markdown("---")

# =========================
# 1️⃣ MOYENNE DES TRANSACTIONS
# =========================
st.header("1️⃣ Valeur moyenne des transactions")

avg_transaction = df["Montant_Transaction"].mean()
st.metric("Montant moyen des transactions", f"{avg_transaction:,.2f} XAF")

st.info("Calcul : moyenne de la colonne Montant_Transaction.")

st.markdown("---")

# =========================
# 2️⃣ RÉPARTITION DES CATÉGORIES
# =========================
st.header("2️⃣ Répartition des catégories de produits")

category_counts = (
    df["Categorie_Produit"]
    .value_counts()
    .reset_index()
)
category_counts.columns = ["Categorie", "Nombre_Ventes"]

category_counts["Part (%)"] = (
    category_counts["Nombre_Ventes"] / category_counts["Nombre_Ventes"].sum() * 100
)

st.dataframe(category_counts, use_container_width=True)

fig_cat = px.pie(
    category_counts,
    values="Nombre_Ventes",
    names="Categorie",
    title="Répartition des ventes par catégorie",
    color_discrete_sequence=px.colors.qualitative.Set2
)
st.plotly_chart(fig_cat, use_container_width=True)

st.markdown("---")

# =========================
# 3️⃣ TAUX DE RÉCURRENCE CLIENT
# =========================
st.header("3️⃣ Taux de récurrence des clients")

client_counts = df["ID_Client"].value_counts()
clients_recurrents = client_counts[client_counts > 1].count()
total_clients = client_counts.count()
taux_recurrence = (clients_recurrents / total_clients) * 100

col1, col2 = st.columns(2)
col1.metric("Clients récurrents", clients_recurrents)
col2.metric("Taux de récurrence", f"{taux_recurrence:.2f} %")

st.info("Un client est considéré récurrent s’il effectue plus d’une transaction.")

st.markdown("---")

# =========================
# 4️⃣ MODES DE PAIEMENT
# =========================
st.header("4️⃣ Utilisation des modes de paiement")

payment_counts = (
    df["Mode_Paiement"]
    .value_counts(normalize=True)
    .reset_index()
)
payment_counts.columns = ["Mode_Paiement", "Proportion"]
payment_counts["Proportion (%)"] = payment_counts["Proportion"] * 100

st.dataframe(payment_counts[["Mode_Paiement", "Proportion (%)"]], use_container_width=True)

fig_pay = px.bar(
    payment_counts,
    x="Mode_Paiement",
    y="Proportion (%)",
    color="Mode_Paiement",
    text_auto=".1f",
    title="Répartition des transactions par mode de paiement",
    color_discrete_sequence=px.colors.qualitative.Pastel
)
st.plotly_chart(fig_pay, use_container_width=True)

st.markdown("---")

# =========================
# 5️⃣ CUSTOMER LIFETIME VALUE
# =========================
st.header("5️⃣ Customer Lifetime Value (CLV) moyenne")

clv_client = (
    df.groupby("ID_Client")["Montant_Transaction"]
    .sum()
    .reset_index()
)
clv_client.columns = ["ID_Client", "CLV"]

avg_clv = clv_client["CLV"].mean()

st.metric("CLV moyenne", f"{avg_clv:,.2f} XAF")

st.subheader("Top 10 clients par CLV")
st.dataframe(
    clv_client.sort_values(by="CLV", ascending=False).head(10),
    use_container_width=True
)

st.markdown("---")

# =========================
# 6️⃣ PERFORMANCE DES CATÉGORIES
# =========================
st.header("6️⃣ Performance des catégories de produits")

category_revenue = (
    df.groupby("Categorie_Produit")["Montant_Transaction"]
    .sum()
    .reset_index()
)

fig_perf = px.bar(
    category_revenue,
    x="Categorie_Produit",
    y="Montant_Transaction",
    color="Categorie_Produit",
    title="Chiffre d'affaires par catégorie",
    text_auto=".2s",
    color_discrete_sequence=px.colors.qualitative.Set1
)
st.plotly_chart(fig_perf, use_container_width=True)

best_category = category_revenue.sort_values(
    by="Montant_Transaction",
    ascending=False
).iloc[0]

st.success(
    f"La catégorie la plus performante est **{best_category['Categorie_Produit']}** "
    f"avec un chiffre d’affaires de **{best_category['Montant_Transaction']:,.2f} XAF**."
)



# ======================================================
# ================== PARTIE 2 ==========================
# ======= CONSTRUCTION D'UN DASHBOARD INTERACTIF =======
# ======================================================

st.markdown("---")
st.title("📊 PARTIE 2 : Dashboard Interactif des Ventes")

# =========================
# CHARGEMENT DES DONNÉES
# =========================
@st.cache_data
def load_dashboard_data():
    df = pd.read_excel("data_dashboard_large.xlsx")

    # Conversion des types
    df["Date_Transaction"] = pd.to_datetime(df["Date_Transaction"], errors="coerce")

    df["Montant"] = (
        df["Montant"]
        .astype(str)
        .str.replace("€", "", regex=False)
        .str.replace("XAF", "", regex=False)
        .str.replace(" ", "", regex=False)
        .str.replace(",", ".", regex=False)
    )
    df["Montant"] = pd.to_numeric(df["Montant"], errors="coerce")

    df["Quantite"] = pd.to_numeric(df["Quantite"], errors="coerce")
    df["Satisfaction_Client"] = pd.to_numeric(df["Satisfaction_Client"], errors="coerce")

    df = df.dropna(subset=["Montant", "Date_Transaction"])

    return df

df_dash = load_dashboard_data()

# =========================
# FILTRES DYNAMIQUES
# =========================
st.sidebar.markdown("## 🔎 Filtres – Dashboard")

magasins = st.sidebar.multiselect(
    "Magasin",
    df_dash["Magasin"].unique(),
    default=df_dash["Magasin"].unique()
)

categories = st.sidebar.multiselect(
    "Catégorie de produit",
    df_dash["Categorie_Produit"].unique(),
    default=df_dash["Categorie_Produit"].unique()
)

paiements = st.sidebar.multiselect(
    "Mode de paiement",
    df_dash["Mode_Paiement"].unique(),
    default=df_dash["Mode_Paiement"].unique()
)

date_min, date_max = st.sidebar.date_input(
    "Période",
    [
        df_dash["Date_Transaction"].min().date(),
        df_dash["Date_Transaction"].max().date()
    ]
)

df_f = df_dash[
    (df_dash["Magasin"].isin(magasins)) &
    (df_dash["Categorie_Produit"].isin(categories)) &
    (df_dash["Mode_Paiement"].isin(paiements)) &
    (df_dash["Date_Transaction"].between(
        pd.to_datetime(date_min),
        pd.to_datetime(date_max)
    ))
]

if df_f.empty:
    st.warning("Aucune donnée disponible pour les filtres sélectionnés.")
    st.stop()

# =========================
# 1️⃣ VUE D’ENSEMBLE
# =========================
st.header("1️⃣ Vue d’ensemble – Indicateurs clés")

col1, col2, col3, col4 = st.columns(4)

col1.metric("💰 Total des ventes (€)", f"{df_f['Montant'].sum():,.0f}")
col2.metric("🧾 Transactions", len(df_f))
col3.metric("🛒 Montant moyen", f"{df_f['Montant'].mean():,.2f}")
col4.metric("⭐ Satisfaction moyenne", f"{df_f['Satisfaction_Client'].mean():.2f}")

ventes_jour = (
    df_f.groupby(df_f["Date_Transaction"].dt.date)["Montant"]
    .sum()
    .reset_index()
)

fig_jour = px.line(
    ventes_jour,
    x="Date_Transaction",
    y="Montant",
    title="Évolution des ventes quotidiennes",
    markers=True,
    color_discrete_sequence=px.colors.qualitative.Dark2
)
st.plotly_chart(fig_jour, use_container_width=True)

# =========================
# 2️⃣ ANALYSE PAR MAGASIN
# =========================
st.header("2️⃣ Analyse par magasin")

col1, col2 = st.columns(2)

fig_mag = px.pie(
    df_f,
    values="Montant",
    names="Magasin",
    title="Répartition des ventes par magasin",
    color_discrete_sequence=px.colors.qualitative.Set2
)
col1.plotly_chart(fig_mag, use_container_width=True)

panier_mag = df_f.groupby("Magasin")["Montant"].mean().reset_index()
fig_panier = px.bar(
    panier_mag,
    x="Magasin",
    y="Montant",
    color="Magasin",
    title="Montant moyen par transaction",
    color_discrete_sequence=px.colors.qualitative.Pastel
)
col2.plotly_chart(fig_panier, use_container_width=True)

st.subheader("Tableau récapitulatif par magasin")
st.dataframe(
    df_f.groupby("Magasin")
    .agg(
        Ventes_totales=("Montant", "sum"),
        Nombre_transactions=("Montant", "count")
    )
    .reset_index(),
    use_container_width=True
)

# =========================
# 3️⃣ CATÉGORIES DE PRODUITS
# =========================
st.header("3️⃣ Analyse des catégories de produits")

col1, col2 = st.columns(2)

quantites_cat = df_f.groupby("Categorie_Produit")["Quantite"].sum().reset_index()
fig_qte = px.bar(
    quantites_cat,
    x="Categorie_Produit",
    y="Quantite",
    color="Categorie_Produit",
    title="Quantités vendues par catégorie",
    color_discrete_sequence=px.colors.qualitative.Set3
)
col1.plotly_chart(fig_qte, use_container_width=True)

ventes_cat_mag = df_f.groupby(
    ["Categorie_Produit", "Magasin"]
)["Montant"].sum().reset_index()

fig_stack = px.bar(
    ventes_cat_mag,
    x="Categorie_Produit",
    y="Montant",
    color="Magasin",
    title="Ventes par catégorie et par magasin",
    color_discrete_sequence=px.colors.qualitative.Set1
)
col2.plotly_chart(fig_stack, use_container_width=True)

# =========================
# 4️⃣ MODES DE PAIEMENT
# =========================
st.header("4️⃣ Analyse des modes de paiement")

fig_pay = px.pie(
    df_f,
    names="Mode_Paiement",
    title="Répartition des transactions par mode de paiement",
    color_discrete_sequence=px.colors.qualitative.Pastel2
)
st.plotly_chart(fig_pay, use_container_width=True)

st.metric(
    "Mode de paiement le plus utilisé",
    df_f["Mode_Paiement"].value_counts().idxmax()
)

# =========================
# 5️⃣ SATISFACTION CLIENT
# =========================
st.header("5️⃣ Analyse de la satisfaction client")

col1, col2 = st.columns(2)

sat_mag = df_f.groupby("Magasin")["Satisfaction_Client"].mean().reset_index()
fig_sat_mag = px.bar(
    sat_mag,
    x="Magasin",
    y="Satisfaction_Client",
    color="Magasin",
    title="Satisfaction moyenne par magasin",
    color_discrete_sequence=px.colors.qualitative.Set2
)
col1.plotly_chart(fig_sat_mag, use_container_width=True)

sat_cat = df_f.groupby("Categorie_Produit")["Satisfaction_Client"].mean().reset_index()
fig_sat_cat = px.bar(
    sat_cat,
    x="Categorie_Produit",
    y="Satisfaction_Client",
    color="Categorie_Produit",
    title="Satisfaction moyenne par catégorie",
    color_discrete_sequence=px.colors.qualitative.Set1
)
col2.plotly_chart(fig_sat_cat, use_container_width=True)

fig_dist = px.histogram(
    df_f,
    x="Satisfaction_Client",
    color="Satisfaction_Client",
    nbins=5,
    title="Distribution des scores de satisfaction",
    color_discrete_sequence=px.colors.qualitative.Dark2
)
st.plotly_chart(fig_dist, use_container_width=True)


