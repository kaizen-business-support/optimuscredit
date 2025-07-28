"""
Page d'analyse avec affichage détaillé des états financiers
Grandes masses en gras selon les spécifications BCEAO
Compatible avec le main.py mis à jour
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# Import du gestionnaire de session centralisé
try:
    from session_manager import SessionManager
except ImportError:
    st.error("❌ Impossible d'importer session_manager.py")
    st.stop()

def show_detailed_analysis_page():
    """Affiche la page d'analyse détaillée avec états financiers complets"""
    
    # Vérifier la disponibilité des données
    if not SessionManager.has_analysis_data():
        show_no_analysis_error()
        return
    
    # Récupérer les données
    analysis_data = SessionManager.get_analysis_data()
    data = analysis_data['data']
    ratios = analysis_data['ratios']
    scores = analysis_data['scores']
    metadata = analysis_data['metadata']
    
    # En-tête de la page
    display_analysis_header(scores, metadata)
    
    # Onglets pour organiser l'affichage détaillé
    tab_overview, tab_bilan, tab_cr, tab_flux, tab_ratios, tab_sector = st.tabs([
        "📊 Vue d'Ensemble", 
        "🏦 Bilan Détaillé", 
        "📈 Compte de Résultat", 
        "💰 Flux de Trésorerie",
        "📉 Ratios Complets",
        "🔍 Comparaison Sectorielle"
    ])
    
    with tab_overview:
        show_analysis_overview(data, ratios, scores, metadata)
    
    with tab_bilan:
        show_detailed_balance_sheet(data)
    
    with tab_cr:
        show_detailed_income_statement(data)
    
    with tab_flux:
        show_detailed_cash_flow(data)
    
    with tab_ratios:
        show_complete_ratios_analysis(ratios, scores)
    
    with tab_sector:
        show_sectoral_comparison_detailed(ratios, metadata.get('secteur'))

def show_no_analysis_error():
    """Affiche une erreur si aucune analyse n'est disponible"""
    
    st.error("❌ Aucune analyse disponible")
    st.info("💡 Veuillez d'abord importer des données Excel ou effectuer une saisie manuelle.")
    
    col1, col2 = st.columns(2)
    
    reset_counter = SessionManager.get_reset_counter()
    
    with col1:
        input_key = f"goto_input_from_analysis_{reset_counter}"
        if st.button("📊 Saisir des Données", key=input_key, type="primary", use_container_width=True):
            SessionManager.set_current_page('unified_input')
            st.rerun()
    
    with col2:
        home_key = f"goto_home_from_analysis_{reset_counter}"
        if st.button("🏠 Accueil", key=home_key, use_container_width=True):
            SessionManager.set_current_page('home')
            st.rerun()

def display_analysis_header(scores, metadata):
    """Affiche l'en-tête de l'analyse"""
    
    st.title("📊 Analyse Financière Complète - BCEAO")
    
    # Informations générales
    col1, col2, col3 = st.columns(3)
    
    with col1:
        source = metadata.get('source', 'inconnue').replace('_', ' ').title()
        st.info(f"**Source :** {source}")
    
    with col2:
        secteur = metadata.get('secteur', '').replace('_', ' ').title()
        st.info(f"**Secteur :** {secteur}")
    
    with col3:
        date_analyse = metadata.get('date_analyse', 'Non spécifiée')
        st.info(f"**Date :** {date_analyse}")
    
    # Score global en évidence
    score_global = scores.get('global', 0)
    interpretation, color = SessionManager.get_interpretation(score_global)
    classe = SessionManager.get_financial_class(score_global)
    
    st.markdown(f"""
    <div style="text-align: center; padding: 30px; border-radius: 15px; background-color: {color}20; border: 3px solid {color}; margin: 20px 0;">
        <h1 style="color: {color}; margin: 0;">Score Global BCEAO</h1>
        <h1 style="color: {color}; margin: 15px 0; font-size: 3em;">{score_global}/100</h1>
        <h2 style="color: {color}; margin: 10px 0;">Classe {classe}</h2>
        <h3 style="color: {color}; margin: 0;">{interpretation}</h3>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("---")

def show_analysis_overview(data, ratios, scores, metadata):
    """Affiche la vue d'ensemble de l'analyse"""
    
    st.header("📊 Vue d'Ensemble de la Performance")
    
    # Scores par catégorie
    st.subheader("🎯 Scores par Catégorie BCEAO")
    
    categories_data = [
        ("💧 Liquidité", scores.get('liquidite', 0), 40, "Capacité à honorer les engagements court terme"),
        ("🏛️ Solvabilité", scores.get('solvabilite', 0), 40, "Solidité de la structure financière"),
        ("📈 Rentabilité", scores.get('rentabilite', 0), 30, "Performance économique et profitabilité"),
        ("⚡ Activité", scores.get('activite', 0), 15, "Efficacité opérationnelle et rotation"),
        ("🔧 Gestion", scores.get('gestion', 0), 15, "Qualité du management et productivité")
    ]
    
    # Affichage des scores avec barres de progression
    for label, score, max_score, description in categories_data:
        col1, col2, col3 = st.columns([2, 1, 3])
        
        with col1:
            st.markdown(f"**{label}**")
            progress = score / max_score
            st.progress(progress, text=f"{score}/{max_score} ({progress*100:.0f}%)")
        
        with col2:
            if progress >= 0.8:
                st.success("Excellent")
            elif progress >= 0.6:
                st.info("Bon")
            elif progress >= 0.4:
                st.warning("Moyen")
            else:
                st.error("Faible")
        
        with col3:
            st.caption(description)
    
    st.markdown("---")
    
    # Indicateurs financiers clés
    st.subheader("💰 Indicateurs Financiers Clés")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        ca = data.get('chiffre_affaires', 0)
        st.metric(
            "Chiffre d'Affaires", 
            f"{ca:,.0f}".replace(',', ' ') + " FCFA",
            help="Volume d'activité de l'entreprise"
        )
    
    with col2:
        rn = data.get('resultat_net', 0)
        rn_pct = (rn / ca * 100) if ca > 0 else 0
        st.metric(
            "Résultat Net", 
            f"{rn:,.0f}".replace(',', ' ') + " FCFA",
            delta=f"{rn_pct:.1f}% du CA",
            help="Bénéfice ou perte de l'exercice"
        )
    
    with col3:
        ta = data.get('total_actif', 0)
        st.metric(
            "Total Actif", 
            f"{ta:,.0f}".replace(',', ' ') + " FCFA",
            help="Total des ressources de l'entreprise"
        )
    
    with col4:
        cp = data.get('capitaux_propres', 0)
        autonomie = (cp / ta * 100) if ta > 0 else 0
        st.metric(
            "Capitaux Propres", 
            f"{cp:,.0f}".replace(',', ' ') + " FCFA",
            delta=f"{autonomie:.1f}% de l'actif",
            help="Fonds propres de l'entreprise"
        )
    
    # Ratios de performance clés
    st.subheader("📊 Ratios de Performance Clés")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        liquidite = ratios.get('ratio_liquidite_generale', 0)
        status = get_ratio_status(liquidite, 1.5, higher_is_better=True)
        st.metric("Liquidité Générale", f"{liquidite:.2f}", status)
    
    with col2:
        autonomie_ratio = ratios.get('ratio_autonomie_financiere', 0)
        status = get_ratio_status(autonomie_ratio, 30, higher_is_better=True)
        st.metric("Autonomie Financière", f"{autonomie_ratio:.1f}%", status)
    
    with col3:
        roe = ratios.get('roe', 0)
        status = get_ratio_status(roe, 10, higher_is_better=True)
        st.metric("ROE", f"{roe:.1f}%", status)
    
    with col4:
        marge_nette = ratios.get('marge_nette', 0)
        status = get_ratio_status(marge_nette, 5, higher_is_better=True)
        st.metric("Marge Nette", f"{marge_nette:.1f}%", status)
    
    # Graphique radar des performances
    st.subheader("📡 Radar de Performance")
    create_performance_radar(scores)

def show_detailed_balance_sheet(data):
    """Affiche le bilan détaillé avec grandes masses en gras"""
    
    st.header("🏦 Bilan Détaillé")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("## **ACTIF**")
        
        # Créer le DataFrame pour l'actif avec structure détaillée
        actif_data = []
        
        # IMMOBILISATIONS (Grande masse en gras)
        actif_data.append(["**IMMOBILISATIONS**", "**Montant (FCFA)**"])
        
        # Immobilisations corporelles
        if data.get('terrains', 0) > 0:
            actif_data.append(["  • Terrains", f"{data.get('terrains', 0):,.0f}"])
        if data.get('batiments', 0) > 0:
            actif_data.append(["  • Bâtiments", f"{data.get('batiments', 0):,.0f}"])
        if data.get('materiel_mobilier', 0) > 0:
            actif_data.append(["  • Matériel et mobilier", f"{data.get('materiel_mobilier', 0):,.0f}"])
        if data.get('materiel_transport', 0) > 0:
            actif_data.append(["  • Matériel de transport", f"{data.get('materiel_transport', 0):,.0f}"])
        
        # Total immobilisations en gras
        actif_data.append(["**Total Immobilisations**", f"**{data.get('immobilisations_nettes', 0):,.0f}**"])
        actif_data.append(["", ""])  # Ligne vide
        
        # ACTIF CIRCULANT (Grande masse en gras)
        actif_data.append(["**ACTIF CIRCULANT**", ""])
        
        if data.get('stocks', 0) > 0:
            actif_data.append(["  • Stocks", f"{data.get('stocks', 0):,.0f}"])
        if data.get('creances_clients', 0) > 0:
            actif_data.append(["  • Créances clients", f"{data.get('creances_clients', 0):,.0f}"])
        if data.get('autres_creances', 0) > 0:
            actif_data.append(["  • Autres créances", f"{data.get('autres_creances', 0):,.0f}"])
        
        # Total actif circulant
        actif_data.append(["**Total Actif Circulant**", f"**{data.get('total_actif_circulant', 0):,.0f}**"])
        actif_data.append(["", ""])  # Ligne vide
        
        # TRÉSORERIE ACTIF (Grande masse en gras)
        actif_data.append(["**TRÉSORERIE ACTIF**", ""])
        if data.get('banques_caisses', 0) > 0:
            actif_data.append(["  • Banques et caisses", f"{data.get('banques_caisses', 0):,.0f}"])
        if data.get('titres_placement', 0) > 0:
            actif_data.append(["  • Titres de placement", f"{data.get('titres_placement', 0):,.0f}"])
        
        actif_data.append(["**Total Trésorerie Actif**", f"**{data.get('tresorerie', 0):,.0f}**"])
        actif_data.append(["", ""])  # Ligne vide
        
        # TOTAL GÉNÉRAL ACTIF
        actif_data.append(["**TOTAL GÉNÉRAL ACTIF**", f"**{data.get('total_actif', 0):,.0f}**"])
        
        # Affichage du tableau actif
        df_actif = pd.DataFrame(actif_data, columns=["Poste", "Montant (FCFA)"])
        st.dataframe(df_actif, hide_index=True, use_container_width=True)
    
    with col2:
        st.markdown("## **PASSIF**")
        
        # Créer le DataFrame pour le passif avec structure détaillée
        passif_data = []
        
        # CAPITAUX PROPRES (Grande masse en gras)
        passif_data.append(["**CAPITAUX PROPRES**", "**Montant (FCFA)**"])
        
        if data.get('capital', 0) > 0:
            passif_data.append(["  • Capital social", f"{data.get('capital', 0):,.0f}"])
        if data.get('reserves', 0) > 0:
            passif_data.append(["  • Réserves", f"{data.get('reserves', 0):,.0f}"])
        if data.get('report_nouveau', 0) != 0:
            passif_data.append(["  • Report à nouveau", f"{data.get('report_nouveau', 0):,.0f}"])
        
        passif_data.append(["  • Résultat net", f"{data.get('resultat_net', 0):,.0f}"])
        
        # Total capitaux propres en gras
        passif_data.append(["**Total Capitaux Propres**", f"**{data.get('capitaux_propres', 0):,.0f}**"])
        passif_data.append(["", ""])  # Ligne vide
        
        # DETTES FINANCIÈRES (Grande masse en gras)
        passif_data.append(["**DETTES FINANCIÈRES**", ""])
        
        if data.get('emprunts_bancaires', 0) > 0:
            passif_data.append(["  • Emprunts bancaires", f"{data.get('emprunts_bancaires', 0):,.0f}"])
        if data.get('autres_dettes_financieres', 0) > 0:
            passif_data.append(["  • Autres dettes financières", f"{data.get('autres_dettes_financieres', 0):,.0f}"])
        
        passif_data.append(["**Total Dettes Financières**", f"**{data.get('dettes_financieres', 0):,.0f}**"])
        passif_data.append(["", ""])  # Ligne vide
        
        # DETTES COURT TERME (Grande masse en gras)
        passif_data.append(["**DETTES COURT TERME**", ""])
        
        if data.get('fournisseurs', 0) > 0:
            passif_data.append(["  • Dettes fournisseurs", f"{data.get('fournisseurs', 0):,.0f}"])
        if data.get('dettes_sociales_fiscales', 0) > 0:
            passif_data.append(["  • Dettes sociales et fiscales", f"{data.get('dettes_sociales_fiscales', 0):,.0f}"])
        if data.get('autres_dettes', 0) > 0:
            passif_data.append(["  • Autres dettes", f"{data.get('autres_dettes', 0):,.0f}"])
        
        passif_data.append(["**Total Dettes Court Terme**", f"**{data.get('dettes_court_terme', 0):,.0f}**"])
        passif_data.append(["", ""])  # Ligne vide
        
        # TRÉSORERIE PASSIF (Grande masse en gras)
        if data.get('tresorerie_passif', 0) > 0:
            passif_data.append(["**TRÉSORERIE PASSIF**", ""])
            passif_data.append(["  • Crédits de trésorerie", f"{data.get('tresorerie_passif', 0):,.0f}"])
            passif_data.append(["**Total Trésorerie Passif**", f"**{data.get('tresorerie_passif', 0):,.0f}**"])
            passif_data.append(["", ""])
        
        # TOTAL GÉNÉRAL PASSIF
        total_passif = (data.get('capitaux_propres', 0) + data.get('dettes_financieres', 0) + 
                       data.get('dettes_court_terme', 0) + data.get('tresorerie_passif', 0))
        passif_data.append(["**TOTAL GÉNÉRAL PASSIF**", f"**{total_passif:,.0f}**"])
        
        # Affichage du tableau passif
        df_passif = pd.DataFrame(passif_data, columns=["Poste", "Montant (FCFA)"])
        st.dataframe(df_passif, hide_index=True, use_container_width=True)
    
    # Vérification de l'équilibre du bilan
    st.markdown("---")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("**Total Actif**", f"{data.get('total_actif', 0):,.0f} FCFA")
    
    with col2:
        total_passif = (data.get('capitaux_propres', 0) + data.get('dettes_financieres', 0) + 
                       data.get('dettes_court_terme', 0) + data.get('tresorerie_passif', 0))
        st.metric("**Total Passif**", f"{total_passif:,.0f} FCFA")
    
    with col3:
        equilibre = abs(data.get('total_actif', 0) - total_passif)
        if equilibre < 1000:
            st.success(f"✅ **Bilan équilibré** (écart: {equilibre:,.0f})")
        else:
            st.error(f"❌ **Bilan déséquilibré** (écart: {equilibre:,.0f})")

def show_detailed_income_statement(data):
    """Affiche le compte de résultat détaillé avec grandes masses en gras"""
    
    st.header("📈 Compte de Résultat Détaillé")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("## **PRODUITS**")
        
        # Créer le DataFrame pour les produits
        produits_data = []
        
        # CHIFFRE D'AFFAIRES (Grande masse en gras)
        produits_data.append(["**CHIFFRE D'AFFAIRES**", "**Montant (FCFA)**"])
        
        if data.get('ventes_marchandises', 0) > 0:
            produits_data.append(["  • Ventes de marchandises", f"{data.get('ventes_marchandises', 0):,.0f}"])
        if data.get('ventes_produits_fabriques', 0) > 0:
            produits_data.append(["  • Ventes de produits fabriqués", f"{data.get('ventes_produits_fabriques', 0):,.0f}"])
        if data.get('travaux_services_vendus', 0) > 0:
            produits_data.append(["  • Travaux et services vendus", f"{data.get('travaux_services_vendus', 0):,.0f}"])
        
        produits_data.append(["**Total Chiffre d'Affaires**", f"**{data.get('chiffre_affaires', 0):,.0f}**"])
        produits_data.append(["", ""])  # Ligne vide
        
        # AUTRES PRODUITS
        if data.get('autres_produits', 0) > 0:
            produits_data.append(["**AUTRES PRODUITS**", ""])
            produits_data.append(["  • Autres produits d'exploitation", f"{data.get('autres_produits', 0):,.0f}"])
            produits_data.append(["", ""])
        
        # PRODUITS FINANCIERS
        if data.get('revenus_financiers', 0) > 0:
            produits_data.append(["**PRODUITS FINANCIERS**", ""])
            produits_data.append(["  • Revenus financiers", f"{data.get('revenus_financiers', 0):,.0f}"])
            produits_data.append(["**Total Produits Financiers**", f"**{data.get('revenus_financiers', 0):,.0f}**"])
            produits_data.append(["", ""])
        
        # TOTAL GÉNÉRAL PRODUITS
        total_produits = (data.get('chiffre_affaires', 0) + data.get('autres_produits', 0) + 
                         data.get('revenus_financiers', 0))
        produits_data.append(["**TOTAL GÉNÉRAL PRODUITS**", f"**{total_produits:,.0f}**"])
        
        # Affichage du tableau produits
        df_produits = pd.DataFrame(produits_data, columns=["Poste", "Montant (FCFA)"])
        st.dataframe(df_produits, hide_index=True, use_container_width=True)
    
    with col2:
        st.markdown("## **CHARGES**")
        
        # Créer le DataFrame pour les charges
        charges_data = []
        
        # CHARGES D'EXPLOITATION (Grande masse en gras)
        charges_data.append(["**CHARGES D'EXPLOITATION**", "**Montant (FCFA)**"])
        
        # Achats
        if data.get('achats_marchandises', 0) > 0:
            charges_data.append(["  • Achats de marchandises", f"{data.get('achats_marchandises', 0):,.0f}"])
        if data.get('achats_matieres_premieres', 0) > 0:
            charges_data.append(["  • Achats matières premières", f"{data.get('achats_matieres_premieres', 0):,.0f}"])
        if data.get('autres_achats', 0) > 0:
            charges_data.append(["  • Autres achats", f"{data.get('autres_achats', 0):,.0f}"])
        
        # Charges externes
        if data.get('charges_externes', 0) > 0:
            charges_data.append(["  • Charges externes", f"{data.get('charges_externes', 0):,.0f}"])
        
        # Charges de personnel
        charges_data.append(["  • Charges de personnel", f"{data.get('charges_personnel', 0):,.0f}"])
        
        # Amortissements
        if data.get('dotations_amortissements', 0) > 0:
            charges_data.append(["  • Dotations amortissements", f"{data.get('dotations_amortissements', 0):,.0f}"])
        
        charges_data.append(["**Total Charges d'Exploitation**", f"**{data.get('charges_exploitation', 0):,.0f}**"])
        charges_data.append(["", ""])  # Ligne vide
        
        # CHARGES FINANCIÈRES
        if data.get('frais_financiers', 0) > 0:
            charges_data.append(["**CHARGES FINANCIÈRES**", ""])
            charges_data.append(["  • Frais financiers", f"{data.get('frais_financiers', 0):,.0f}"])
            charges_data.append(["**Total Charges Financières**", f"**{data.get('frais_financiers', 0):,.0f}**"])
            charges_data.append(["", ""])
        
        # IMPÔTS SUR LES BÉNÉFICES
        if data.get('impots_resultat', 0) > 0:
            charges_data.append(["**IMPÔTS SUR BÉNÉFICES**", ""])
            charges_data.append(["  • Impôts sur le résultat", f"{data.get('impots_resultat', 0):,.0f}"])
            charges_data.append(["", ""])
        
        # TOTAL GÉNÉRAL CHARGES
        total_charges = (data.get('charges_exploitation', 0) + data.get('frais_financiers', 0) + 
                        data.get('impots_resultat', 0))
        charges_data.append(["**TOTAL GÉNÉRAL CHARGES**", f"**{total_charges:,.0f}**"])
        
        # Affichage du tableau charges
        df_charges = pd.DataFrame(charges_data, columns=["Poste", "Montant (FCFA)"])
        st.dataframe(df_charges, hide_index=True, use_container_width=True)
    
    # SOLDES INTERMÉDIAIRES DE GESTION
    st.markdown("---")
    st.markdown("## **SOLDES INTERMÉDIAIRES DE GESTION**")
    
    # Calculs des soldes
    valeur_ajoutee = data.get('valeur_ajoutee', 0)
    excedent_brut = data.get('excedent_brut', 0)
    resultat_exploitation = data.get('resultat_exploitation', 0)
    resultat_financier = data.get('resultat_financier', 0)
    resultat_net = data.get('resultat_net', 0)
    
    # Affichage des soldes
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("**Valeur Ajoutée**", f"{valeur_ajoutee:,.0f} FCFA",
                 delta=f"{(valeur_ajoutee/data.get('chiffre_affaires', 1)*100):.1f}% du CA" if data.get('chiffre_affaires', 0) > 0 else None)
        
        st.metric("**Excédent Brut d'Exploitation**", f"{excedent_brut:,.0f} FCFA",
                 delta=f"{(excedent_brut/data.get('chiffre_affaires', 1)*100):.1f}% du CA" if data.get('chiffre_affaires', 0) > 0 else None)
    
    with col2:
        st.metric("**Résultat d'Exploitation**", f"{resultat_exploitation:,.0f} FCFA",
                 delta=f"{(resultat_exploitation/data.get('chiffre_affaires', 1)*100):.1f}% du CA" if data.get('chiffre_affaires', 0) > 0 else None)
        
        st.metric("**Résultat Financier**", f"{resultat_financier:,.0f} FCFA")
    
    with col3:
        st.metric("**Résultat Net**", f"{resultat_net:,.0f} FCFA",
                 delta=f"{(resultat_net/data.get('chiffre_affaires', 1)*100):.1f}% du CA" if data.get('chiffre_affaires', 0) > 0 else None)
    
    # Graphique waterfall des soldes
    create_waterfall_chart(data)

def show_detailed_cash_flow(data):
    """Affiche le tableau des flux de trésorerie détaillé"""
    
    st.header("💰 Tableau des Flux de Trésorerie Détaillé")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### **Flux d'Exploitation**")
        
        # Flux opérationnels détaillés
        flux_exp_data = []
        flux_exp_data.append(["**CAPACITÉ D'AUTOFINANCEMENT**", "**Montant (FCFA)**"])
        flux_exp_data.append(["Résultat net", f"{data.get('resultat_net', 0):,.0f}"])
        flux_exp_data.append(["+ Dotations amortissements", f"{data.get('dotations_amortissements', 0):,.0f}"])
        flux_exp_data.append(["**= CAFG**", f"**{data.get('cafg', 0):,.0f}**"])
        flux_exp_data.append(["", ""])
        
        flux_exp_data.append(["**VARIATION DU BFR**", ""])
        flux_exp_data.append(["Variation du BFR", f"{data.get('variation_bfr', 0):,.0f}"])
        flux_exp_data.append(["", ""])
        
        flux_exp_data.append(["**FLUX OPÉRATIONNELS**", f"**{data.get('flux_activites_operationnelles', 0):,.0f}**"])
        
        df_flux_exp = pd.DataFrame(flux_exp_data, columns=["Élément", "Montant (FCFA)"])
        st.dataframe(df_flux_exp, hide_index=True, use_container_width=True)
        
        st.markdown("### **Flux d'Investissement**")
        
        flux_inv_data = []
        flux_inv_data.append(["**INVESTISSEMENTS**", "**Montant (FCFA)**"])
        if data.get('acquisitions_immobilisations', 0) != 0:
            flux_inv_data.append(["Acquisitions d'immobilisations", f"({abs(data.get('acquisitions_immobilisations', 0)):,.0f})"])
        if data.get('cessions_immobilisations', 0) > 0:
            flux_inv_data.append(["Cessions d'immobilisations", f"{data.get('cessions_immobilisations', 0):,.0f}"])
        
        flux_inv_data.append(["**FLUX INVESTISSEMENT**", f"**{data.get('flux_activites_investissement', 0):,.0f}**"])
        
        df_flux_inv = pd.DataFrame(flux_inv_data, columns=["Élément", "Montant (FCFA)"])
        st.dataframe(df_flux_inv, hide_index=True, use_container_width=True)
    
    with col2:
        st.markdown("### **Flux de Financement**")
        
        flux_fin_data = []
        flux_fin_data.append(["**CAPITAUX PROPRES**", "**Montant (FCFA)**"])
        if data.get('augmentation_capital', 0) > 0:
            flux_fin_data.append(["Augmentation de capital", f"{data.get('augmentation_capital', 0):,.0f}"])
        if data.get('dividendes_verses', 0) > 0:
            flux_fin_data.append(["Dividendes versés", f"({data.get('dividendes_verses', 0):,.0f})"])
        
        flux_fin_data.append(["", ""])
        
        flux_fin_data.append(["**CAPITAUX ÉTRANGERS**", ""])
        if data.get('nouveaux_emprunts', 0) > 0:
            flux_fin_data.append(["Nouveaux emprunts", f"{data.get('nouveaux_emprunts', 0):,.0f}"])
        if data.get('remboursements_emprunts', 0) > 0:
            flux_fin_data.append(["Remboursements d'emprunts", f"({data.get('remboursements_emprunts', 0):,.0f})"])
        
        flux_fin_data.append(["", ""])
        
        flux_fin_data.append(["**FLUX FINANCEMENT**", f"**{data.get('flux_activites_financement', 0):,.0f}**"])
        
        df_flux_fin = pd.DataFrame(flux_fin_data, columns=["Élément", "Montant (FCFA)"])
        st.dataframe(df_flux_fin, hide_index=True, use_container_width=True)
        
        st.markdown("### **Synthèse des Flux**")
        
        synthese_data = []
        synthese_data.append(["**ÉLÉMENTS**", "**Montant (FCFA)**"])
        synthese_data.append(["Trésorerie d'ouverture", f"{data.get('tresorerie_ouverture', 0):,.0f}"])
        synthese_data.append(["+ Flux opérationnels", f"{data.get('flux_activites_operationnelles', 0):,.0f}"])
        synthese_data.append(["+ Flux d'investissement", f"{data.get('flux_activites_investissement', 0):,.0f}"])
        synthese_data.append(["+ Flux de financement", f"{data.get('flux_activites_financement', 0):,.0f}"])
        synthese_data.append(["**= Variation trésorerie**", f"**{data.get('variation_tresorerie', 0):,.0f}**"])
        synthese_data.append(["**= Trésorerie clôture**", f"**{data.get('tresorerie_cloture', 0):,.0f}**"])
        
        df_synthese = pd.DataFrame(synthese_data, columns=["Élément", "Montant (FCFA)"])
        st.dataframe(df_synthese, hide_index=True, use_container_width=True)

def show_complete_ratios_analysis(ratios, scores):
    """Affiche l'analyse complète des ratios"""
    
    st.header("📉 Analyse Complète des Ratios")
    
    # Onglets pour organiser les ratios
    ratio_tabs = st.tabs([
        "💧 Liquidité", "🏛️ Solvabilité", "📈 Rentabilité", 
        "⚡ Activité", "🔧 Gestion"
    ])
    
    with ratio_tabs[0]:  # Liquidité
        show_liquidity_ratios(ratios, scores)
    
    with ratio_tabs[1]:  # Solvabilité
        show_solvency_ratios(ratios, scores)
    
    with ratio_tabs[2]:  # Rentabilité
        show_profitability_ratios(ratios, scores)
    
    with ratio_tabs[3]:  # Activité
        show_activity_ratios(ratios, scores)
    
    with ratio_tabs[4]:  # Gestion
        show_management_ratios(ratios, scores)

def show_liquidity_ratios(ratios, scores):
    """Affiche les ratios de liquidité détaillés"""
    
    st.subheader(f"💧 Ratios de Liquidité - Score: {scores.get('liquidite', 0)}/40")
    
    liquidity_ratios = [
        ("Liquidité Générale", "ratio_liquidite_generale", "> 1.5", "Capacité à honorer les dettes CT"),
        ("Liquidité Immédiate", "ratio_liquidite_immediate", "> 1.0", "Liquidité sans les stocks"),
        ("BFR en jours de CA", "bfr_jours_ca", "< 60 jours", "Besoin de financement d'exploitation")
    ]
    
    for label, key, norme, description in liquidity_ratios:
        if key in ratios:
            col1, col2, col3, col4 = st.columns([2, 1, 1, 3])
            
            with col1:
                st.write(f"**{label}**")
            
            with col2:
                if key == "bfr_jours_ca":
                    st.metric("Valeur", f"{ratios[key]:.0f} jours")
                else:
                    st.metric("Valeur", f"{ratios[key]:.2f}")
            
            with col3:
                if key == "bfr_jours_ca":
                    status = get_ratio_status(ratios[key], 60, higher_is_better=False)
                else:
                    threshold = {"ratio_liquidite_generale": 1.5, "ratio_liquidite_immediate": 1.0}[key]
                    status = get_ratio_status(ratios[key], threshold, higher_is_better=True)
                st.write(status)
            
            with col4:
                st.caption(description)

def show_solvency_ratios(ratios, scores):
    """Affiche les ratios de solvabilité détaillés"""
    
    st.subheader(f"🏛️ Ratios de Solvabilité - Score: {scores.get('solvabilite', 0)}/40")
    
    solvency_ratios = [
        ("Autonomie Financière", "ratio_autonomie_financiere", "> 30%", "Part des capitaux propres"),
        ("Endettement Global", "ratio_endettement", "< 65%", "Part des dettes dans le bilan"),
        ("Capacité de Remboursement", "capacite_remboursement", "< 5 ans", "Délai de remboursement")
    ]
    
    for label, key, norme, description in solvency_ratios:
        if key in ratios:
            col1, col2, col3, col4 = st.columns([2, 1, 1, 3])
            
            with col1:
                st.write(f"**{label}**")
            
            with col2:
                if "%" in norme:
                    st.metric("Valeur", f"{ratios[key]:.1f}%")
                elif "ans" in norme:
                    st.metric("Valeur", f"{ratios[key]:.1f} ans")
                else:
                    st.metric("Valeur", f"{ratios[key]:.2f}")
            
            with col3:
                if key == "ratio_autonomie_financiere":
                    status = get_ratio_status(ratios[key], 30, higher_is_better=True)
                elif key == "ratio_endettement":
                    status = get_ratio_status(ratios[key], 65, higher_is_better=False)
                elif key == "capacite_remboursement":
                    status = get_ratio_status(ratios[key], 5, higher_is_better=False)
                st.write(status)
            
            with col4:
                st.caption(description)

def show_profitability_ratios(ratios, scores):
    """Affiche les ratios de rentabilité détaillés"""
    
    st.subheader(f"📈 Ratios de Rentabilité - Score: {scores.get('rentabilite', 0)}/30")
    
    profitability_ratios = [
        ("ROE", "roe", "> 10%", "Rentabilité des capitaux propres"),
        ("ROA", "roa", "> 2%", "Rentabilité de l'actif total"),
        ("Marge Nette", "marge_nette", "> 5%", "Rentabilité du chiffre d'affaires"),
        ("Marge d'Exploitation", "marge_exploitation", "> 5%", "Rentabilité opérationnelle")
    ]
    
    for label, key, norme, description in profitability_ratios:
        if key in ratios:
            col1, col2, col3, col4 = st.columns([2, 1, 1, 3])
            
            with col1:
                st.write(f"**{label}**")
            
            with col2:
                st.metric("Valeur", f"{ratios[key]:.1f}%")
            
            with col3:
                if key == "roe":
                    status = get_ratio_status(ratios[key], 10, higher_is_better=True)
                elif key == "roa":
                    status = get_ratio_status(ratios[key], 2, higher_is_better=True)
                elif key in ["marge_nette", "marge_exploitation"]:
                    status = get_ratio_status(ratios[key], 5, higher_is_better=True)
                st.write(status)
            
            with col4:
                st.caption(description)

def show_activity_ratios(ratios, scores):
    """Affiche les ratios d'activité détaillés"""
    
    st.subheader(f"⚡ Ratios d'Activité - Score: {scores.get('activite', 0)}/15")
    
    activity_ratios = [
        ("Rotation de l'Actif", "rotation_actif", "> 1.5", "Efficacité d'utilisation des actifs"),
        ("Rotation des Stocks", "rotation_stocks", "> 6", "Vitesse d'écoulement des stocks"),
        ("Délai Recouvrement Clients", "delai_recouvrement_clients", "< 45 jours", "Temps de paiement des clients")
    ]
    
    for label, key, norme, description in activity_ratios:
        if key in ratios:
            col1, col2, col3, col4 = st.columns([2, 1, 1, 3])
            
            with col1:
                st.write(f"**{label}**")
            
            with col2:
                if "jours" in norme:
                    st.metric("Valeur", f"{ratios[key]:.0f} jours")
                else:
                    st.metric("Valeur", f"{ratios[key]:.1f}")
            
            with col3:
                if key == "rotation_actif":
                    status = get_ratio_status(ratios[key], 1.5, higher_is_better=True)
                elif key == "rotation_stocks":
                    status = get_ratio_status(ratios[key], 6, higher_is_better=True)
                elif key == "delai_recouvrement_clients":
                    status = get_ratio_status(ratios[key], 45, higher_is_better=False)
                st.write(status)
            
            with col4:
                st.caption(description)

def show_management_ratios(ratios, scores):
    """Affiche les ratios de gestion détaillés"""
    
    st.subheader(f"🔧 Ratios de Gestion - Score: {scores.get('gestion', 0)}/15")
    
    management_ratios = [
        ("Productivité Personnel", "productivite_personnel", "> 2.0", "Valeur ajoutée / Charges personnel"),
        ("Taux Charges Personnel", "taux_charges_personnel", "< 50%", "Charges personnel / Valeur ajoutée"),
        ("CAFG / CA", "ratio_cafg_ca", "> 7%", "Capacité d'autofinancement / CA")
    ]
    
    for label, key, norme, description in management_ratios:
        if key in ratios:
            col1, col2, col3, col4 = st.columns([2, 1, 1, 3])
            
            with col1:
                st.write(f"**{label}**")
            
            with col2:
                if "%" in norme:
                    st.metric("Valeur", f"{ratios[key]:.1f}%")
                else:
                    st.metric("Valeur", f"{ratios[key]:.2f}")
            
            with col3:
                if key == "productivite_personnel":
                    status = get_ratio_status(ratios[key], 2.0, higher_is_better=True)
                elif key == "taux_charges_personnel":
                    status = get_ratio_status(ratios[key], 50, higher_is_better=False)
                elif key == "ratio_cafg_ca":
                    status = get_ratio_status(ratios[key], 7, higher_is_better=True)
                st.write(status)
            
            with col4:
                st.caption(description)

def show_sectoral_comparison_detailed(ratios, secteur):
    """Affiche la comparaison sectorielle détaillée"""
    
    st.header("🔍 Comparaison Sectorielle Détaillée")
    
    if not secteur:
        st.warning("Secteur non spécifié pour la comparaison")
        return
    
    # Données sectorielles simplifiées (à remplacer par des données réelles)
    sectoral_data = {
        'industrie_manufacturiere': {
            'ratio_liquidite_generale': {'q1': 1.2, 'median': 1.8, 'q3': 2.5},
            'ratio_autonomie_financiere': {'q1': 25, 'median': 40, 'q3': 55},
            'roe': {'q1': 8, 'median': 15, 'q3': 22},
            'marge_nette': {'q1': 2, 'median': 4.5, 'q3': 8}
        },
        'commerce_detail': {
            'ratio_liquidite_generale': {'q1': 1.0, 'median': 1.5, 'q3': 2.2},
            'ratio_autonomie_financiere': {'q1': 20, 'median': 35, 'q3': 50},
            'roe': {'q1': 5, 'median': 12, 'q3': 20},
            'marge_nette': {'q1': 0.5, 'median': 2, 'q3': 4}
        },
        'services_professionnels': {
            'ratio_liquidite_generale': {'q1': 1.2, 'median': 1.7, 'q3': 2.5},
            'ratio_autonomie_financiere': {'q1': 30, 'median': 45, 'q3': 65},
            'roe': {'q1': 15, 'median': 25, 'q3': 40},
            'marge_nette': {'q1': 5, 'median': 10, 'q3': 18}
        },
        'construction_btp': {
            'ratio_liquidite_generale': {'q1': 1.2, 'median': 1.5, 'q3': 1.9},
            'ratio_autonomie_financiere': {'q1': 22, 'median': 35, 'q3': 48},
            'roe': {'q1': 8, 'median': 16, 'q3': 28},
            'marge_nette': {'q1': 1.5, 'median': 3.5, 'q3': 6}
        },
        'agriculture': {
            'ratio_liquidite_generale': {'q1': 1.1, 'median': 1.6, 'q3': 2.3},
            'ratio_autonomie_financiere': {'q1': 35, 'median': 50, 'q3': 70},
            'roe': {'q1': 2, 'median': 8, 'q3': 15},
            'marge_nette': {'q1': -5, 'median': 2, 'q3': 8}
        },
        'commerce_gros': {
            'ratio_liquidite_generale': {'q1': 1.1, 'median': 1.4, 'q3': 1.8},
            'ratio_autonomie_financiere': {'q1': 18, 'median': 30, 'q3': 45},
            'roe': {'q1': 6, 'median': 12, 'q3': 20},
            'marge_nette': {'q1': 0.5, 'median': 1.5, 'q3': 3}
        }
    }
    
    if secteur not in sectoral_data:
        st.info("Données sectorielles détaillées non disponibles pour ce secteur")
        return
    
    st.subheader(f"📊 Positionnement - {secteur.replace('_', ' ').title()}")
    
    sector_ratios = sectoral_data[secteur]
    comparison_data = []
    
    for ratio_key, benchmarks in sector_ratios.items():
        if ratio_key in ratios:
            entreprise_val = ratios[ratio_key]
            q1, median, q3 = benchmarks['q1'], benchmarks['median'], benchmarks['q3']
            
            # Déterminer le quartile
            if entreprise_val >= q3:
                quartile = "Q4 (Top 25%)"
                color = "🟢"
            elif entreprise_val >= median:
                quartile = "Q3 (50-75%)"
                color = "🟡"
            elif entreprise_val >= q1:
                quartile = "Q2 (25-50%)"
                color = "🟠"
            else:
                quartile = "Q1 (Bottom 25%)"
                color = "🔴"
            
            comparison_data.append({
                'Ratio': ratio_key.replace('_', ' ').title(),
                'Votre Valeur': f"{entreprise_val:.2f}",
                'Q1 Secteur': f"{q1:.2f}",
                'Médiane': f"{median:.2f}",
                'Q3 Secteur': f"{q3:.2f}",
                'Position': f"{color} {quartile}"
            })
    
    if comparison_data:
        df_comparison = pd.DataFrame(comparison_data)
        st.dataframe(df_comparison, hide_index=True, use_container_width=True)

def create_performance_radar(scores):
    """Crée un graphique radar des performances"""
    
    categories = ['Liquidité', 'Solvabilité', 'Rentabilité', 'Activité', 'Gestion']
    values = [
        scores.get('liquidite', 0) / 40 * 100,
        scores.get('solvabilite', 0) / 40 * 100,
        scores.get('rentabilite', 0) / 30 * 100,
        scores.get('activite', 0) / 15 * 100,
        scores.get('gestion', 0) / 15 * 100
    ]
    
    fig = go.Figure()
    
    fig.add_trace(go.Scatterpolar(
        r=values + [values[0]],
        theta=categories + [categories[0]],
        fill='toself',
        name='Performance Actuelle',
        line_color='rgb(46, 125, 50)',
        fillcolor='rgba(76, 175, 80, 0.3)'
    ))
    
    fig.add_trace(go.Scatterpolar(
        r=[100, 100, 100, 100, 100, 100],
        theta=categories + [categories[0]],
        fill='tonext',
        name='Performance Maximale',
        line_color='rgb(211, 47, 47)',
        fillcolor='rgba(244, 67, 54, 0.1)',
        line_dash='dash'
    ))
    
    fig.update_layout(
        polar=dict(
            radialaxis=dict(
                visible=True,
                range=[0, 100],
                ticktext=['0%', '25%', '50%', '75%', '100%'],
                tickvals=[0, 25, 50, 75, 100]
            )),
        showlegend=True,
        title="Radar de Performance par Catégorie BCEAO",
        height=500
    )
    
    st.plotly_chart(fig, use_container_width=True)

def create_waterfall_chart(data):
    """Crée un graphique waterfall des soldes intermédiaires"""
    
    st.subheader("📊 Formation du Résultat Net")
    
    # Calculs des soldes
    ca = data.get('chiffre_affaires', 0)
    charges_variables = (data.get('achats_marchandises', 0) + 
                        data.get('achats_matieres_premieres', 0) + 
                        data.get('autres_achats', 0))
    va = data.get('valeur_ajoutee', 0)
    charges_fixes = data.get('charges_personnel', 0)
    ebe = data.get('excedent_brut', 0)
    amortissements = data.get('dotations_amortissements', 0)
    re = data.get('resultat_exploitation', 0)
    rf = data.get('resultat_financier', 0)
    rn = data.get('resultat_net', 0)
    
    fig = go.Figure(go.Waterfall(
        name="Formation du Résultat",
        orientation="v",
        measure=["absolute", "relative", "relative", "relative", "relative", "relative", "total"],
        x=["CA", "- Charges Variables", "- Charges Personnel", "- Amortissements", "+ Résultat Financier", "- Impôts", "= Résultat Net"],
        y=[ca, -charges_variables, -charges_fixes, -amortissements, rf, -data.get('impots_resultat', 0), rn],
        connector={"line": {"color": "rgb(63, 63, 63)"}},
        text=[f"{ca:,.0f}", f"-{charges_variables:,.0f}", f"-{charges_fixes:,.0f}", 
              f"-{amortissements:,.0f}", f"{rf:+,.0f}", f"-{data.get('impots_resultat', 0):,.0f}", f"{rn:,.0f}"],
        textposition="outside"
    ))
    
    fig.update_layout(
        title="Formation du Résultat Net - Waterfall",
        height=500,
        yaxis_title="Montant (FCFA)"
    )
    
    st.plotly_chart(fig, use_container_width=True)

def get_ratio_status(value, threshold, higher_is_better=True):
    """Retourne le statut d'un ratio avec icône"""
    
    if higher_is_better:
        if value >= threshold * 1.2:
            return "🟢 Excellent"
        elif value >= threshold:
            return "🟡 Bon"
        elif value >= threshold * 0.8:
            return "🟠 Acceptable"
        else:
            return "🔴 Faible"
    else:
        if value <= threshold * 0.8:
            return "🟢 Excellent"
        elif value <= threshold:
            return "🟡 Bon"
        elif value <= threshold * 1.2:
            return "🟠 Acceptable"
        else:
            return "🔴 Faible"