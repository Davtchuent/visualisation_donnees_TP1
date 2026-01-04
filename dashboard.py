import streamlit as st
import pandas as pd
import plotly.express as px
import matplotlib.pyplot as plt

# Set page configuration
st.set_page_config(page_title="Dashboard KPI Ventes", layout="wide")

st.title("Dashboard Analyse des Ventes")

# Load data
@st.cache_data
def load_data():
    try:
        df = pd.read_excel('data_kpi.xlsx')
        if df['Montant_Transaction'].dtype == 'object':
             # Convert to string, replace currency symbols and commas
             cleaned_series = df['Montant_Transaction'].astype(str)
             # Convert to numeric, coercing errors to NaN
             df['Montant_Transaction'] = pd.to_numeric(cleaned_series, errors='coerce')
        
        # Drop rows with invalid Montant_Transaction
        if df['Montant_Transaction'].isnull().any():
            st.warning(f"Attention : {df['Montant_Transaction'].isnull().sum()} lignes avec des montants invalides ont été ignorées.")
            df = df.dropna(subset=['Montant_Transaction'])
            
        return df
    except Exception as e:
        st.error(f"Erreur lors du chargement des données : {e}")
        return None
df = load_data()
#df = pd.read_excel('data_kpi.xlsx')
if df is not None:
    # --- 0. Data Preview ---
    st.header("Aperçu des Données")
    st.write("Voici les 5 premières lignes du fichier chargé :")
    st.dataframe(df.head())
    
    st.write("Types des colonnes :")
    st.write(df.dtypes.astype(str))

    st.markdown("---")

    # --- 1. Valeur moyenne des transactions ---
    st.header("1. Calcul de la valeur moyenne des transactions")
    
    # Optional local filter
    if st.checkbox("Filtrer par catégorie"):
        categories_q1 = st.multiselect("Sélectionner les catégories", options=df['Categorie_Produit'].unique(), default=df['Categorie_Produit'].unique())
        df_q1 = df[df['Categorie_Produit'].isin(categories_q1)]
    else:
        df_q1 = df

    avg_transaction = df_q1['Montant_Transaction'].mean()
    st.metric(label="Moyenne du montant des transactions", value=f"{avg_transaction:.2f} €")
    st.info("Calcul : Moyenne de la colonne 'Montant_Transaction'.")

    st.markdown("---")

    # --- 2. Analyse de la répartition des catégories de produits ---
    st.header("2. Analyse de la répartition des catégories de produits")
    category_counts = df['Categorie_Produit'].value_counts().reset_index()
    category_counts.columns = ['Categorie', 'Nombre_Ventes']
    
    # Calculate percentage for the text explanation
    total_sales = category_counts['Nombre_Ventes'].sum()
    category_counts['Part (%)'] = (category_counts['Nombre_Ventes'] / total_sales) * 100
    
    st.write("Part de chaque catégorie dans le total des ventes :")
    st.dataframe(category_counts)
    
    fig_cat = px.pie(category_counts, values='Nombre_Ventes', names='Categorie', title='Répartition des ventes par catégorie')
    st.plotly_chart(fig_cat, use_container_width=True)

    st.markdown("---")

    # --- 3. Taux de récurrence des clients ---
    st.header("3. Taux de récurrence des clients")
    client_counts = df['ID_Client'].value_counts()
    recurring_clients = client_counts[client_counts > 1].count()
    total_clients = client_counts.count()
    recurrence_rate = (recurring_clients / total_clients) * 100
    
    st.metric(label="Pourcentage de clients récurrents (> 1 achat)", value=f"{recurrence_rate:.2f} %")
    st.write(f"Nombre de clients récurrents : {recurring_clients} / {total_clients}")

    st.markdown("---")

    # --- 4. Taux d'utilisation des modes de paiement ---
    st.header("4. Taux d'utilisation des modes de paiement")
    payment_counts = df['Mode_Paiement'].value_counts(normalize=True).reset_index()
    payment_counts.columns = ['Mode_Paiement', 'Proportion']
    payment_counts['Proportion (%)'] = payment_counts['Proportion'] * 100
    
    st.write("Proportion d'utilisation de chaque mode de paiement :")
    st.dataframe(payment_counts[['Mode_Paiement', 'Proportion (%)']])

    fig_pay = px.bar(payment_counts, x='Mode_Paiement', y='Proportion', color='Mode_Paiement' , title="Utilisation des modes de paiement", text_auto='.1%', labels={'Proportion': 'Fréquence'})
    st.plotly_chart(fig_pay, use_container_width=True)

    st.markdown("---")     


    # --- 5. Customer Lifetime Value (CLV) moyenne ---
    st.header("5. Calcul de la Customer Lifetime Value (CLV) moyenne")
    
    # Volet 1: CLV par client
    st.subheader("Volet 1 : Calcul de la CLV par client")
    st.write("La CLV est calculée ici comme la somme des montants des transactions pour chaque client.")
    
    clv_per_client = df.groupby('ID_Client')['Montant_Transaction'].sum().reset_index()
    clv_per_client.columns = ['ID_Client', 'CLV']
    
    # Histogram to show distribution
    fig_clv = px.histogram(clv_per_client, x="CLV", nbins=20, title="Distribution de la CLV par client")
    st.plotly_chart(fig_clv, use_container_width=True)
    
    with st.expander("Voir le détail de la CLV par client (Top 10)"):
        st.dataframe(clv_per_client.sort_values(by='CLV', ascending=False).head(10))

    # Volet 2: Moyenne
    st.subheader("Volet 2 : CLV Moyenne")
    avg_clv = clv_per_client['CLV'].mean()
    
    st.metric(label="CLV Moyenne pour l'ensemble des clients", value=f"{avg_clv:.2f} €")
    st.info(f"Calcul : Moyenne des CLV calculées sur {len(clv_per_client)} clients uniques.")

    st.markdown("---")

    # --- 6. Indice de performance des catégories ---
    st.header("6. Indice de performance des catégories")
    category_revenue = df.groupby('Categorie_Produit')['Montant_Transaction'].sum().sort_values(ascending=False)
    best_category = category_revenue.idxmax()
    best_revenue = category_revenue.max()
    
    st.success(f"La catégorie ayant généré le chiffre d'affaires le plus élevé est : **{best_category}** avec **{best_revenue:.2f} €**.")
    
    st.write("Classement des catégories par chiffre d'affaires :")
    #st.bar_chart(category_revenue)
    # Création du graphique avec couleurs différentes
    fig, ax = plt.subplots()
    colors = plt.cm.tab20.colors  # Palette de couleurs

    bars = ax.bar(category_revenue.index, category_revenue.values, color=colors[:len(category_revenue)])

    ax.set_xlabel('Catégorie Produit')
    ax.set_ylabel('Chiffre d\'affaires (€)')
    ax.set_title('Chiffre d\'affaires par catégorie')

    # Affichage des valeurs au-dessus des barres
    for bar in bars:
        height = bar.get_height()
        ax.annotate(f'{height:.2f} €',
                    xy=(bar.get_x() + bar.get_width() / 2, height),
                    xytext=(0, 3),  # décalage vertical
                    textcoords="offset points",
                    ha='center', va='bottom')

    st.pyplot(fig)

else:
    st.warning("Veuillez vérifier le fichier data_kpi.xlsx")
