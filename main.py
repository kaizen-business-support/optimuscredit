st.caption("Page d'accueil")

def show_basic_analysis_display():
    """Affichage basique intégré en cas d'échec de tous les autres modules"""
    
    st.title("📊 Analyse Financière - Mode Basique")
    st.info("📋 Affichage simplifié des résultats d'analyse")
    
    try:
        # Récupérer les données via SessionManager
        analysis_data = SessionManager.get_analysis_data()
        if not analysis_data:
            st.error("❌ Aucune donnée d'analyse disponible")
            return
        
        data = analysis_data.get('data', {})
        ratios = analysis_data.get('ratios', {})
        scores = analysis_data.get('scores', {})
        metadata = analysis_data.get('metadata', {})
        
        # Affichage du score global
        st.subheader("🎯 Score Global BCEAO")
        score_global = scores.get('global', 0)
        
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            if score_global >= 70:
                color = "green"
                status = "Très bonne situation"
            elif score_global >= 40:
                color = "orange" 
                status = "Situation acceptable"
            else:
                color = "red"
                status = "Situation à améliorer"
            
            st.markdown(f"""
            <div style="text-align: center; padding: 20px; border-radius: 10px; background-color: {color}20; border: 2px solid {color};">
                <h1 style="color: {color}; margin: 0;">{score_global}/100</h1>
                <p style="color: {color}; margin: 5px 0; font-weight: bold;">{status}</p>
            </div>
            """, unsafe_allow_html=True)
        
        # Scores par catégorie
        st.subheader("📈 Scores par Catégorie")
        
        col1, col2, col3, col4, col5 = st.columns(5)
        
        categories = [
            ("💧 Liquidité", scores.get('liquidite', 0), 40),
            ("🏛️ Solvabilité", scores.get('solvabilite', 0), 40),
            ("📈 Rentabilité", scores.get('rentabilite', 0), 30),
            ("⚡ Activité", scores.get('activite', 0), 15),
            ("🔧 Gestion", scores.get('gestion', 0), 15)
        ]
        
        cols = [col1, col2, col3, col4, col5]
        
        for i, (label, score, max_score) in enumerate(categories):
            with cols[i]:
                percentage = (score / max_score) * 100
                st.metric(label, f"{score}/{max_score}", f"{percentage:.0f}%")
        
        # Données financières principales
        st.subheader("💰 Données Financières Principales")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("**Bilan**")
            st.write(f"• Total Actif: {data.get('total_actif', 0):,.0f} FCFA".replace(',', ' '))
            st.write(f"• Capitaux Propres: {data.get('capitaux_propres', 0):,.0f} FCFA".replace(',', ' '))
            st.write(f"• Dettes Totales: {(data.get('dettes_financieres', 0) + data.get('dettes_court_terme', 0)):,.0f} FCFA".replace(',', ' '))
        
        with col2:
            st.markdown("**Compte de Résultat**")
            st.write(f"• Chiffre d'Affaires: {data.get('chiffre_affaires', 0):,.0f} FCFA".replace(',', ' '))
            st.write(f"• Résultat Net: {data.get('resultat_net', 0):,.0f} FCFA".replace(',', ' '))
            ca = data.get('chiffre_affaires', 1)
            marge = (data.get('resultat_net', 0) / ca * 100) if ca > 0 else 0
            st.write(f"• Marge Nette: {marge:.1f}%")
        
        # Ratios principaux
        st.subheader("📊 Ratios Principaux")
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            liquidite = ratios.get('ratio_liquidite_generale', 0)
            st.metric("Liquidité Générale", f"{liquidite:.2f}")
        
        with col2:
            autonomie = ratios.get('ratio_autonomie_financiere', 0)
            st.metric("Autonomie Financière", f"{autonomie:.1f}%")
        
        with col3:
            if st.button("🔄 Nouvelle Analyse", key=f"basic_reset_{nav_ts}", type="secondary", use_container_width=True):
                if st.session_state.get(f'basic_confirm_reset_{nav_ts}', False):
                    protected_reset()
                else:
                    st.session_state[f'basic_confirm_reset_{nav_ts}'] = True
                    st.warning("⚠️ Cliquez à nouveau pour confirmer")
        
        # Note sur le mode basique
        st.info("💡 **Mode d'affichage basique** - Pour une analyse plus détaillée, assurez-vous que les modules d'analyse avancés sont disponibles.")
        
    except Exception as e:
        st.error(f"❌ Erreur dans l'affichage basique: {e}")
        st.error("Retour à l'accueil recommandé.")
        
        if st.button("🏠 Retour Accueil", key="error_home_basic", type="primary"):
            navigate_to_page('home')
            roe = ratios.get('roe', 0)
            st.metric("ROE", f"{roe:.1f}%")
        
        with col4:
            marge_nette = ratios.get('marge_nette', 0)
            st.metric("Marge Nette", f"{marge_nette:.1f}%")
        
        # Informations sur l'analyse
        st.subheader("ℹ️ Informations sur l'Analyse")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            secteur = metadata.get('secteur', 'Non spécifié')
            st.info(f"**Secteur:** {secteur.replace('_', ' ').title()}")
        
        with col2:
            source = metadata.get('source', 'Non spécifiée')
            st.info(f"**Source:** {source}")
        
        with col3:
            date_analyse = metadata.get('date_analyse', 'Non spécifiée')
            st.info(f"**Date:** {date_analyse}")
        
        # Actions
        st.subheader("🚀 Actions Disponibles")
        
        col1, col2, col3 = st.columns(3)
        
        nav_ts = st.session_state.get('nav_timestamp', int(time.time()))
        
        with col1:
            if st.button("🏠 Retour Accueil", key=f"basic_home_{nav_ts}", type="secondary", use_container_width=True):
                navigate_to_page('home')
        
        with col2:
            if st.button("📊 Nouvelle Saisie", key=f"basic_input_{nav_ts}", type="primary", use_container_width=True):
                navigate_to_page('unified_input')
        
        with col3:
            """
Application principale OptimusCredit - Analyse Financière BCEAO
Version 2.1 ANTI-RESET - CORRECTIONS DEFINITIVES
"""

import streamlit as st
import sys
import os
import time
from datetime import datetime

# Configuration de la page DOIT être la première commande Streamlit
st.set_page_config(
    page_title="OptimusCredit - Analyse Financière BCEAO",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Ajouter le répertoire modules au path Python
sys.path.append(os.path.join(os.path.dirname(__file__), 'modules'))

# Import du gestionnaire de session centralisé
try:
    from session_manager import SessionManager, init_session, has_analysis, reset_app
except ImportError as e:
    st.error(f"❌ Impossible d'importer session_manager.py: {e}")
    st.error("Assurez-vous que session_manager.py est présent dans le répertoire racine.")
    st.stop()

def main():
    """Fonction principale de l'application"""
    
    # ÉTAPE 1: Initialiser le gestionnaire de session
    init_session()
    
    # ÉTAPE 2: Afficher l'en-tête principal
    display_main_header()
    
    # ÉTAPE 3: Gestion de la navigation dans la sidebar
    display_sidebar_navigation()
    
    # ÉTAPE 4: Affichage du contenu principal selon la page sélectionnée
    display_main_content()
    
    # ÉTAPE 5: Afficher le pied de page
    display_footer()

def display_main_header():
    """Affiche l'en-tête principal de l'application"""
    
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.markdown("""
        <div style="text-align: center; padding: 20px;">
            <h1 style="color: #1f4e79; margin-bottom: 10px;">📊 OptimusCredit</h1>
            <h3 style="color: #2e7d32; margin-top: 0;">Outil d'Analyse Financière BCEAO</h3>
            <p style="color: #666; margin-top: 10px;">Conforme aux normes prudentielles BCEAO 2024 • Version 2.1</p>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("---")

def display_sidebar_navigation():
    """Affiche la navigation complète dans la sidebar"""
    
    with st.sidebar:
        st.markdown("## 🧭 Navigation")
        
        # Vérifier l'état de l'analyse via le gestionnaire centralisé
        analysis_available = has_analysis()
        
        # Informations sur l'analyse actuelle
        if analysis_available:
            display_analysis_status_sidebar()
        else:
            st.info("ℹ️ Aucune analyse en cours")
        
        st.markdown("---")
        
        # Menu de navigation principal
        display_navigation_menu(analysis_available)
        
        st.markdown("---")
        
        # Actions rapides
        display_quick_actions(analysis_available)
        
        st.markdown("---")
        
        # Normes BCEAO
        display_bceao_norms_sidebar()

def display_analysis_status_sidebar():
    """Affiche le statut de l'analyse dans la sidebar"""
    
    try:
        score, metadata = SessionManager.get_analysis_info()
        classe = SessionManager.get_financial_class(score)
        interpretation, color = SessionManager.get_interpretation(score)
        
        st.markdown(f"""
        <div style="text-align: center; padding: 15px; border-radius: 10px; background-color: {color}20; border: 2px solid {color};">
            <h4 style="color: {color}; margin: 0;">✅ Analyse Disponible</h4>
            <h2 style="color: {color}; margin: 10px 0;">{score}/100</h2>
            <p style="color: {color}; margin: 0; font-weight: bold;">Classe {classe}</p>
            <p style="color: {color}; margin: 5px 0; font-size: 12px;">{interpretation}</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Afficher des métadonnées supplémentaires
        if metadata:
            secteur = metadata.get('secteur', 'N/A').replace('_', ' ').title()
            source = metadata.get('source', 'N/A')
            date_analyse = metadata.get('date_analyse', 'N/A')
            
            st.markdown(f"""
            **📁 Source:** {source}  
            **🏭 Secteur:** {secteur}  
            **📅 Analysé:** {date_analyse}  
            **🔢 Ratios:** {metadata.get('ratios_count', 0)}
            """)
    
    except Exception as e:
        st.error(f"Erreur affichage statut: {e}")

def display_navigation_menu(analysis_available):
    """Menu de navigation avec protection anti-reset"""
    
    # CORRECTION 1: Utiliser directement le session_state pour éviter les conflits
    current_page = st.session_state.get('current_page', 'home')
    
    # Définition des pages
    pages = {
        'home': {
            'label': '🏠 Accueil',
            'description': 'Page d\'accueil et présentation',
            'requires_analysis': False
        },
        'unified_input': {
            'label': '📊 Saisie des Données',
            'description': 'Import Excel, Saisie Manuelle ou OCR',
            'requires_analysis': False
        },
        'analysis': {
            'label': '📊 Analyse Complète',
            'description': 'Analyse détaillée et ratios',
            'requires_analysis': True
        },
        'reports': {
            'label': '📋 Rapports',
            'description': 'Génération de rapports',
            'requires_analysis': True
        }
    }
    
    # CORRECTION 2: Utiliser un timestamp statique pour éviter la régénération des clés
    if 'nav_timestamp' not in st.session_state:
        st.session_state['nav_timestamp'] = int(time.time())
    
    nav_ts = st.session_state['nav_timestamp']
    
    # Compatibilité : Rediriger les anciennes pages
    if current_page in ['excel_import', 'manual_input']:
        st.session_state['current_page'] = 'unified_input'
        current_page = 'unified_input'
    
    for page_key, page_info in pages.items():
        # Déterminer si le bouton doit être désactivé
        disabled = page_info['requires_analysis'] and not analysis_available
        
        # Déterminer le type de bouton
        if current_page == page_key:
            button_type = "primary"
        else:
            button_type = "secondary"
        
        # CORRECTION 3: Clé statique basée sur timestamp fixe
        button_key = f"nav_{page_key}_{nav_ts}"
        
        # CORRECTION 4: Utiliser callback au lieu de st.rerun() immédiat
        if st.button(
            page_info['label'], 
            key=button_key, 
            type=button_type, 
            use_container_width=True,
            disabled=disabled,
            help=page_info['description']
        ):
            if not disabled:
                # CORRECTION 5: Navigation sans st.rerun() immédiat
                navigate_to_page(page_key)
            else:
                st.warning("⚠️ Cette fonction nécessite une analyse. Importez d'abord des données.")

def navigate_to_page(page_key):
    """Navigation sécurisée vers une page"""
    
    # CORRECTION 6: Changement de page sans reset des données d'analyse
    st.session_state['current_page'] = page_key
    
    # CORRECTION 7: Utiliser query_params pour éviter les conflits de session_state
    st.query_params.page = page_key
    
    # CORRECTION 8: st.rerun() seulement après avoir sécurisé l'état
    st.rerun()

def display_quick_actions(analysis_available):
    """Actions rapides avec protection anti-reset"""
    
    st.markdown("### ⚡ Actions Rapides")
    
    # Utiliser le même timestamp statique
    nav_ts = st.session_state.get('nav_timestamp', int(time.time()))
    
    if analysis_available:
        # Actions disponibles avec analyse
        col1, col2 = st.columns(2)
        
        with col1:
            # CORRECTION 9: Callback sécurisé
            view_key = f"quick_view_{nav_ts}"
            if st.button("👁️ Voir", key=view_key, use_container_width=True):
                navigate_to_page('analysis')
        
        with col2:
            report_key = f"quick_report_{nav_ts}"
            if st.button("📄 Rapport", key=report_key, use_container_width=True):
                navigate_to_page('reports')
        
        # Bouton de réinitialisation avec confirmation
        reset_key = f"quick_reset_{nav_ts}"
        if st.button("🔄 Nouvelle Analyse", key=reset_key, type="secondary", use_container_width=True):
            confirm_key = f'confirm_reset_{nav_ts}'
            if st.session_state.get(confirm_key, False):
                # CORRECTION 10: Reset protégé
                protected_reset()
            else:
                st.session_state[confirm_key] = True
                st.warning("⚠️ Cliquez à nouveau pour confirmer")
    
    else:
        # Actions disponibles sans analyse
        input_key = f"quick_input_{nav_ts}"
        if st.button("📊 Saisir Données", key=input_key, type="primary", use_container_width=True):
            navigate_to_page('unified_input')
        
        st.caption("Import Excel, Saisie Manuelle ou OCR")

def protected_reset():
    """Reset protégé qui ne casse pas l'application"""
    
    # CORRECTION 11: Reset uniquement des données d'analyse, pas de l'état de navigation
    try:
        from session_manager import clear_analysis
        clear_analysis()
        
        # Réinitialiser seulement les timestamps pour forcer la régénération des clés
        st.session_state['nav_timestamp'] = int(time.time())
        
        # Retourner à l'accueil
        st.session_state['current_page'] = 'home'
        st.query_params.page = 'home'
        
        st.success("🔄 Application réinitialisée!")
        st.rerun()
        
    except Exception as e:
        st.error(f"Erreur lors du reset: {e}")

def display_bceao_norms_sidebar():
    """Affiche les normes BCEAO dans la sidebar"""
    
    st.markdown("### 📋 Normes BCEAO")
    
    with st.expander("🏛️ Ratios de Solvabilité"):
        st.markdown("""
        **Fonds propres de base (CET1):**
        • Minimum : 5%
        • Objectif à terme : 7%
        
        **Fonds propres Tier 1:**
        • Minimum : 6,625%
        • Objectif à terme : 8,5%
        
        **Solvabilité globale:**
        • Minimum : 8,625%
        • Objectif à terme : 11,5%
        """)
    
    with st.expander("💧 Ratios de Liquidité"):
        st.markdown("""
        **Liquidité court terme :** ≥ 75%
        **Couverture emplois MLT :** ≥ 100%
        **Transformation :** ≤ 100%
        
        *Contrôles mensuels via FODEP*
        """)
    
    with st.expander("⚖️ Division des Risques"):
        st.markdown("""
        **Division risques :** ≤ 65% des FP
        **Grands risques :** ≤ 8 fois les FP
        **Engagements apparentés :** ≤ 20%
        
        *Limite concentration débiteurs*
        """)
    
    with st.expander("📈 Qualité Portefeuille"):
        st.markdown("""
        **Créances douteuses :** Surveillance
        **Taux provisionnement :** Variable
        **Créances > 5 ans :** Passage en perte
        
        *Classification risques obligatoire*
        """)

def display_main_content():
    """Affiche le contenu principal avec gestion sécurisée"""
    
    # CORRECTION 12: Utiliser query_params comme source de vérité + fallback session_state
    current_page = st.query_params.get('page', st.session_state.get('current_page', 'home'))
    
    # S'assurer que la session_state est synchronisée
    if 'current_page' not in st.session_state or st.session_state['current_page'] != current_page:
        st.session_state['current_page'] = current_page
    
    # Compatibilité : Rediriger les anciennes pages
    if current_page in ['excel_import', 'manual_input']:
        current_page = 'unified_input'
        st.session_state['current_page'] = 'unified_input'
        st.query_params.page = 'unified_input'
    
    try:
        if current_page == 'home' or current_page is None:
            show_home_page()
        
        elif current_page == 'unified_input':
            # Charger la page unifiée
            try:
                from unified_input_page import show_unified_input_page
                show_unified_input_page()
            except ImportError:
                show_fallback_input_page()
        
        elif current_page == 'analysis':
            if has_analysis():
                try:
                    # CORRECTION 13: Essayer d'abord les pages avancées, puis fallback sécurisé
                    try:
                        from analysis_detailed import show_detailed_analysis_page
                        show_detailed_analysis_page()
                    except ImportError:
                        try:
                            from modules.pages.analysis import show_analysis_page
                            show_analysis_page()
                        except ImportError:
                            # FALLBACK SÉCURISÉ : Page d'analyse simple qui fonctionne toujours
                            try:
                                from analysis_fallback import show_fallback_analysis_page
                                show_fallback_analysis_page()
                            except ImportError:
                                # DERNIER FALLBACK : Affichage basique intégré
                                show_basic_analysis_display()
                except Exception as e:
                    st.error(f"❌ Erreur lors du chargement de l'analyse: {e}")
                    # En cas d'erreur, utiliser l'affichage basique
                    show_basic_analysis_display()
            else:
                show_no_analysis_page("analyse")
        
        elif current_page == 'reports':
            if has_analysis():
                try:
                    from modules.pages.reports import show_reports_page
                    show_reports_page()
                except ImportError as e:
                    st.error(f"❌ Page Rapports non disponible: {e}")
                    show_import_error_page("Rapports")
            else:
                show_no_analysis_page("rapports")
        
        else:
            st.error(f"❌ Page '{current_page}' non reconnue")
            show_unknown_page_error(current_page)
    
    except Exception as e:
        st.error(f"❌ Erreur lors du chargement de la page '{current_page}': {e}")
        
        # Retour sécurisé à l'accueil
        st.error("Retour automatique à l'accueil...")
        navigate_to_page('home')

def show_fallback_input_page():
    """Page de fallback si unified_input_page.py n'est pas trouvé"""
    
    st.title("📊 Saisie des Données - Mode Fallback")
    st.warning("⚠️ La page unifiée n'est pas disponible. Utilisation des pages individuelles.")
    
    col1, col2 = st.columns(2)
    
    nav_ts = st.session_state.get('nav_timestamp', int(time.time()))
    
    with col1:
        st.markdown("### 📤 Import Excel")
        st.info("Importez un fichier Excel au format BCEAO")
        
        excel_key = f"fallback_excel_{nav_ts}"
        if st.button("📤 Import Excel", key=excel_key, type="primary", use_container_width=True):
            try:
                from modules.pages.excel_import import show_excel_import_page
                show_excel_import_page()
            except ImportError:
                st.error("❌ Module excel_import non disponible")
    
    with col2:
        st.markdown("### ✏️ Saisie Manuelle")
        st.info("Saisissez vos données manuellement")
        
        manual_key = f"fallback_manual_{nav_ts}"
        if st.button("✏️ Saisie Manuelle", key=manual_key, type="secondary", use_container_width=True):
            try:
                from modules.pages.manual_input import show_manual_input_page
                show_manual_input_page()
            except ImportError:
                st.error("❌ Module manual_input non disponible")

def show_home_page():
    """Page d'accueil avec navigation anti-reset"""
    
    st.markdown("""
    ## 🏠 Bienvenue dans OptimusCredit
    
    ### L'outil d'analyse financière conforme aux normes BCEAO
    
    Analysez la santé financière de votre entreprise avec précision et obtenez des recommandations personnalisées.
    """)
    
    # Fonctionnalités principales
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        ### 🎯 Fonctionnalités Principales
        
        - **📤 Import Excel** : Compatible format BCEAO
        - **✏️ Saisie Manuelle** : Interface intuitive détaillée
        - **🤖 Import OCR** : Reconnaissance optique (V2.2)
        - **📊 Analyse Automatique** : 25+ ratios calculés
        - **🎯 Scoring BCEAO** : Notation sur 100 points
        - **📈 Graphiques Interactifs** : Visualisations dynamiques
        - **📋 Rapports Professionnels** : Export PDF
        - **🔍 Comparaison Sectorielle** : Benchmarks par industrie
        """)
    
    with col2:
        st.markdown("""
        ### 📊 Catégories d'Analyse
        
        - **💧 Liquidité (40 pts)** : Capacité de paiement CT
        - **🏛️ Solvabilité (40 pts)** : Structure financière
        - **📈 Rentabilité (30 pts)** : Performance économique
        - **⚡ Activité (15 pts)** : Efficacité opérationnelle
        - **🔧 Gestion (15 pts)** : Qualité de management
        
        **Total : 140 pts → ramené à 100**
        """)
    
    # Actions rapides avec anti-reset
    st.markdown("### 🚀 Commencer votre Analyse")
    
    col1, col2, col3 = st.columns(3)
    
    nav_ts = st.session_state.get('nav_timestamp', int(time.time()))
    
    with col1:
        # CORRECTION 14: Navigation sécurisée depuis la page d'accueil
        home_input_key = f"home_input_{nav_ts}"
        if st.button("📊 Saisir des Données", key=home_input_key, type="primary", use_container_width=True):
            navigate_to_page('unified_input')
        st.caption("Import Excel, Saisie Manuelle ou OCR")
    
    with col2:
        if has_analysis():
            # CORRECTION 15: Le bouton problématique - maintenant sécurisé
            home_analysis_key = f"home_analysis_{nav_ts}"
            if st.button("📊 Voir l'analyse actuelle", key=home_analysis_key, type="primary", use_container_width=True):
                navigate_to_page('analysis')
            st.caption("Analyse disponible")
        else:
            home_analysis_disabled_key = f"home_analysis_disabled_{nav_ts}"
            st.button("📊 Analyse", key=home_analysis_disabled_key, use_container_width=True, disabled=True)
            st.caption("Importez d'abord des données")
    
    with col3:
        if has_analysis():
            home_report_key = f"home_report_{nav_ts}"
            if st.button("📋 Générer Rapport", key=home_report_key, type="secondary", use_container_width=True):
                navigate_to_page('reports')
            st.caption("Exports disponibles")
        else:
            home_report_disabled_key = f"home_report_disabled_{nav_ts}"
            st.button("📋 Rapport", key=home_report_disabled_key, use_container_width=True, disabled=True)
            st.caption("Nécessite une analyse")
    
    # Afficher le résumé de l'analyse si disponible
    if has_analysis():
        display_analysis_summary()
    
    # Sections informatives
    display_info_sections()

def display_analysis_summary():
    """Affiche un résumé de l'analyse disponible"""
    
    st.markdown("---")
    st.markdown("### 📊 Analyse Disponible")
    
    try:
        score, metadata = SessionManager.get_analysis_info()
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Score Global", f"{score}/100")
        
        with col2:
            classe = SessionManager.get_financial_class(score)
            st.metric("Classe BCEAO", classe)
        
        with col3:
            ratios_count = metadata.get('ratios_count', 0)
            st.metric("Ratios Calculés", ratios_count)
        
        with col4:
            secteur = metadata.get('secteur', 'Non spécifié')
            st.metric("Secteur", secteur.replace('_', ' ').title())
        
        # Actions pour l'analyse disponible
        st.markdown("#### Actions Disponibles")
        col1, col2, col3 = st.columns(3)
        
        nav_ts = st.session_state.get('nav_timestamp', int(time.time()))
        
        with col1:
            # CORRECTION 16: Bouton "Consulter l'Analyse" anti-reset
            summary_view_key = f"summary_view_{nav_ts}"
            if st.button("📊 Consulter l'Analyse", key=summary_view_key, type="primary", use_container_width=True):
                navigate_to_page('analysis')
        
        with col2:
            summary_report_key = f"summary_report_{nav_ts}"
            if st.button("📋 Générer un Rapport", key=summary_report_key, type="secondary", use_container_width=True):
                navigate_to_page('reports')
        
        with col3:
            summary_reset_key = f"summary_reset_{nav_ts}"
            if st.button("🔄 Nouvelle Analyse", key=summary_reset_key, type="secondary", use_container_width=True):
                confirm_key = f'summary_confirm_reset_{nav_ts}'
                if st.session_state.get(confirm_key, False):
                    protected_reset()
                else:
                    st.session_state[confirm_key] = True
                    st.warning("⚠️ Cliquez à nouveau pour confirmer")
    
    except Exception as e:
        st.error(f"Erreur affichage résumé: {e}")

def display_info_sections():
    """Sections informatives"""
    
    st.markdown("---")
    
    with st.expander("🆕 Nouveautés Version 2.1", expanded=False):
        st.markdown("""
        ### 🚀 Améliorations Majeures
        
        - **🔒 Navigation Anti-Reset** : Plus de perte d'analyse lors de la navigation
        - **📊 Page Unifiée** : Import Excel, Saisie Manuelle et OCR en une seule interface
        - **📋 États Détaillés** : Bilan et CR avec grandes masses en gras
        - **⚡ Navigation Fluide** : Passez entre les pages sans problème
        - **🎯 Reset Contrôlé** : Seul "Nouvelle Analyse" remet à zéro
        - **📊 Graphiques Enrichis** : Visualisations plus interactives
        - **🔧 Session Manager** : Gestion d'état centralisée et robuste
        
        ### 🔧 Corrections Anti-Reset Appliquées
        
        - **Navigation sécurisée** avec `query_params` et `session_state`
        - **Clés de widgets statiques** basées sur timestamp fixe
        - **Callbacks protégés** pour éviter les reruns en cascade
        - **Reset protégé** qui préserve l'état d'analyse
        - **Import conditionnel** des modules pour éviter les erreurs
        """)
    
    with st.expander("📋 Normes BCEAO 2024", expanded=False):
        st.markdown("""
        ### 🏛️ Conformité Réglementaire
        
        Cette application respecte intégralement les normes prudentielles BCEAO :
        
        **📊 Ratios de Liquidité :**
        - Liquidité générale ≥ 1,5
        - Liquidité immédiate ≥ 1,0
        - BFR en jours de CA ≤ 90 jours
        
        **🏦 Ratios de Solvabilité :**
        - Autonomie financière ≥ 30%
        - Endettement global ≤ 65%
        - Capacité de remboursement ≤ 5 ans
        
        **💰 Ratios de Rentabilité :**
        - ROE ≥ 10%
        - ROA ≥ 2%
        - Marge nette ≥ 5%
        
        **🎯 Classes de Notation :**
        - **A+** (85-100) : Excellence financière
        - **A** (70-84) : Très bonne situation
        - **B** (55-69) : Bonne situation
        - **C** (40-54) : Situation moyenne
        - **D** (25-39) : Situation faible
        - **E** (0-24) : Situation critique
        """)

def show_no_analysis_page(page_type="analyse"):
    """Page d'erreur avec navigation sécurisée"""
    
    st.warning(f"⚠️ Aucune analyse disponible pour accéder aux {page_type}")
    st.info("💡 Veuillez d'abord saisir des données via la page unifiée.")
    
    st.markdown("### 🚀 Actions Disponibles")
    
    col1, col2 = st.columns(2)
    
    nav_ts = st.session_state.get('nav_timestamp', int(time.time()))
    
    with col1:
        goto_input_key = f"no_analysis_input_{page_type}_{nav_ts}"
        if st.button("📊 Saisir des Données", key=goto_input_key, type="primary", use_container_width=True):
            navigate_to_page('unified_input')
        st.caption("Import Excel, Saisie Manuelle ou OCR")
    
    with col2:
        goto_home_key = f"no_analysis_home_{page_type}_{nav_ts}"
        if st.button("🏠 Retour Accueil", key=goto_home_key, type="secondary", use_container_width=True):
            navigate_to_page('home')
        st.caption("Page d'accueil")

def show_import_error_page(page_name):
    """Affiche une page d'erreur pour les imports ratés"""
    
    st.error(f"❌ Impossible de charger la page {page_name}")
    
    st.markdown(f"""
    ### 🔧 Problème technique détecté
    
    La page **{page_name}** n'a pas pu être chargée. Cela peut être dû à :
    
    - 📁 Fichier manquant dans le répertoire
    - 🐍 Erreur d'import Python
    - 🔧 Module dépendant manquant
    
    ### 💡 Solutions proposées
    """)
    
    col1, col2 = st.columns(2)
    
    nav_ts = st.session_state.get('nav_timestamp', int(time.time()))
    
    with col1:
        error_home_key = f"import_error_home_{page_name}_{nav_ts}"
        if st.button("🏠 Retour Accueil", key=error_home_key, type="primary", use_container_width=True):
            navigate_to_page('home')
        st.caption("Retour sécurisé")
    
    with col2:
        error_input_key = f"import_error_input_{page_name}_{nav_ts}"
        if st.button("📊 Saisir Données", key=error_input_key, type="secondary", use_container_width=True):
            navigate_to_page('unified_input')
        st.caption("Import ou saisie")

def show_unknown_page_error(page_name):
    """Affiche une page d'erreur pour les pages inconnues"""
    
    st.error(f"❌ Page '{page_name}' non reconnue")
    
    st.markdown("""
    ### 🔧 Erreur de navigation
    
    La page demandée n'existe pas ou n'est pas configurée.
    
    ### 🚀 Actions de récupération
    """)
    
    col1, col2 = st.columns(2)
    
    nav_ts = st.session_state.get('nav_timestamp', int(time.time()))
    
    with col1:
        unknown_home_key = f"unknown_page_home_{page_name}_{nav_ts}"
        if st.button("🏠 Retour Accueil", key=unknown_home_key, type="primary", use_container_width=True):
            navigate_to_page('home')
        st.caption("Page d'accueil")
    
    with col2:
        unknown_reset_key = f"unknown_page_reset_{page_name}_{nav_ts}"
        if st.button("🔄 Réinitialiser", key=unknown_reset_key, type="secondary", use_container_width=True):
            protected_reset()
        st.caption("Reset complet")

def display_footer():
    """Affiche le pied de page de l'application"""
    
    st.markdown("---")
    
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.markdown("""
        <div style="text-align: center; padding: 20px; color: #666;">
            <p style="margin: 5px 0;">
                <strong>OptimusCredit v2.1 Anti-Reset</strong> • Outil d'Analyse Financière BCEAO
            </p>
            <p style="margin: 5px 0; font-size: 12px;">
                Conforme aux normes prudentielles BCEAO 2024 • 
            </p>
            <p style="margin: 5px 0; font-size: 10px;">
                © 2024 • Tous droits réservés • 
                <a href="mailto:contact@kaizen-corporation.com" style="color: #1f4e79;">Support Technique</a>
            </p>
        </div>
        """, unsafe_allow_html=True)

# POINT D'ENTRÉE DE L'APPLICATION
if __name__ == "__main__":
    main()
