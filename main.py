"""
Application principale OptimusCredit - Analyse Financière BCEAO
Version 2.1 complète avec gestionnaire d'état centralisé - CORRIGÉE
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
    
    # Afficher l'en-tête principal
    display_main_header()
    
    # ÉTAPE 2: Gestion de la navigation dans la sidebar
    display_sidebar_navigation()
    
    # ÉTAPE 3: Affichage du contenu principal selon la page sélectionnée
    display_main_content()
    
    # ÉTAPE 4: Afficher le pied de page
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
    """Affiche la navigation complète dans la sidebar - VERSION CORRIGÉE"""
    
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
        
        st.markdown("---")
        
        # CORRECTION: Section debug supprimée en production
        # display_debug_section()  # COMMENTÉ

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
    """Affiche le menu de navigation principal"""
    
    # Définition des pages avec leurs propriétés
    pages = {
        'home': {
            'label': '🏠 Accueil',
            'description': 'Page d\'accueil et présentation',
            'requires_analysis': False,
            'type': 'primary'
        },
        'excel_import': {
            'label': '📤 Import Excel',
            'description': 'Importer un fichier Excel BCEAO',
            'requires_analysis': False,
            'type': 'secondary'
        },
        'manual_input': {
            'label': '✏️ Saisie Manuelle',
            'description': 'Saisie manuelle des données',
            'requires_analysis': False,
            'type': 'secondary'
        },
        'analysis': {
            'label': '📊 Analyse Complète',
            'description': 'Analyse détaillée et ratios',
            'requires_analysis': True,
            'type': 'primary'
        },
        'reports': {
            'label': '📋 Rapports',
            'description': 'Génération de rapports',
            'requires_analysis': True,
            'type': 'secondary'
        }
    }
    
    current_page = SessionManager.get_current_page()
    reset_counter = SessionManager.get_reset_counter()
    
    for page_key, page_info in pages.items():
        # Déterminer si le bouton doit être désactivé
        disabled = page_info['requires_analysis'] and not analysis_available
        
        # Déterminer le type de bouton
        if current_page == page_key:
            button_type = "primary"
        elif disabled:
            button_type = "secondary"
        else:
            button_type = page_info['type']
        
        # Créer une clé unique pour éviter les conflits
        button_key = f"nav_btn_{page_key}_{reset_counter}"
        
        # Afficher le bouton
        if st.button(
            page_info['label'], 
            key=button_key, 
            type=button_type, 
            use_container_width=True,
            disabled=disabled,
            help=page_info['description']
        ):
            if not disabled:
                SessionManager.set_current_page(page_key)
                st.rerun()
            else:
                st.warning("⚠️ Cette fonction nécessite une analyse. Importez d'abord des données.")

def display_quick_actions(analysis_available):
    """Affiche les actions rapides dans la sidebar"""
    
    st.markdown("### ⚡ Actions Rapides")
    
    reset_counter = SessionManager.get_reset_counter()
    
    if analysis_available:
        # Actions disponibles avec analyse
        col1, col2 = st.columns(2)
        
        with col1:
            view_key = f"sidebar_view_{reset_counter}"
            if st.button("👁️ Voir", key=view_key, use_container_width=True):
                SessionManager.set_current_page('analysis')
                st.rerun()
        
        with col2:
            report_key = f"sidebar_report_{reset_counter}"
            if st.button("📄 Rapport", key=report_key, use_container_width=True):
                SessionManager.set_current_page('reports')
                st.rerun()
        
        # Bouton de réinitialisation
        reset_key = f"sidebar_reset_{reset_counter}"
        if st.button("🔄 Nouvelle Analyse", key=reset_key, type="secondary", use_container_width=True):
            if st.confirm("Voulez-vous vraiment effacer l'analyse actuelle ?"):
                reset_app()
                st.success("🔄 Application réinitialisée!")
                st.rerun()
    
    else:
        # Actions disponibles sans analyse
        import_key = f"sidebar_import_{reset_counter}"
        if st.button("📤 Import Excel", key=import_key, type="primary", use_container_width=True):
            SessionManager.set_current_page('excel_import')
            st.rerun()
        
        manual_key = f"sidebar_manual_{reset_counter}"
        if st.button("✏️ Saisie Manuelle", key=manual_key, use_container_width=True):
            SessionManager.set_current_page('manual_input')
            st.rerun()

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
    """CORRIGÉ : Affiche le contenu principal selon la page sélectionnée"""
    
    current_page = SessionManager.get_current_page()
    
    try:
        if current_page == 'home' or current_page is None:
            show_home_page()
        
        elif current_page == 'excel_import':
            try:
                from modules.pages.excel_import import show_excel_import_page  # CORRECTION: chemin modules.pages
                show_excel_import_page()
            except ImportError as e:
                st.error(f"❌ Impossible de charger la page Import Excel: {e}")
                show_import_error_page("Import Excel")
        
        elif current_page == 'manual_input':
            try:
                from modules.pages.manual_input import show_manual_input_page  # CORRECTION: chemin modules.pages
                show_manual_input_page()
            except ImportError as e:
                st.error(f"❌ Impossible de charger la page Saisie Manuelle: {e}")
                show_import_error_page("Saisie Manuelle")
        
        elif current_page == 'analysis':
            if has_analysis():
                try:
                    from modules.pages.analysis import show_analysis_page  # CORRECTION: chemin modules.pages
                    show_analysis_page()
                except ImportError as e:
                    st.error(f"❌ Impossible de charger la page Analyse: {e}")
                    show_import_error_page("Analyse")
            else:
                show_no_analysis_page("analyse")
        
        elif current_page == 'reports':
            if has_analysis():
                try:
                    from modules.pages.reports import show_reports_page  # CORRECTION: chemin modules.pages
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
        
        # CORRECTION: Gestion d'erreur simplifiée
        st.error("Retour automatique à l'accueil...")
        SessionManager.set_current_page('home')
        time.sleep(1)  # CORRECTION: Attendre 1 seconde
        st.rerun()

def show_home_page():
    """Affiche la page d'accueil complète"""
    
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
        - **✏️ Saisie Manuelle** : Interface intuitive
        - **📊 Analyse Automatique** : 25+ ratios calculés
        - **🎯 Scoring BCEAO** : Notation sur 100 points
        - **📈 Graphiques Interactifs** : Visualisations dynamiques
        - **📋 Rapports Professionnels** : Export PDF
        - **🔍 Comparaison Sectorielle** : Benchmarks par industrie
        - **💡 Recommandations** : Plan d'action personnalisé
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
    
    # Actions rapides
    st.markdown("### 🚀 Commencer votre Analyse")
    
    col1, col2, col3 = st.columns(3)
    
    reset_counter = SessionManager.get_reset_counter()
    
    with col1:
        home_import_key = f"home_import_{reset_counter}"
        if st.button("📤 Importer un fichier Excel", key=home_import_key, type="primary", use_container_width=True):
            SessionManager.set_current_page('excel_import')
            st.rerun()
        st.caption("Format BCEAO standard")
    
    with col2:
        home_manual_key = f"home_manual_{reset_counter}"
        if st.button("✏️ Saisie manuelle", key=home_manual_key, type="secondary", use_container_width=True):
            SessionManager.set_current_page('manual_input')
            st.rerun()
        st.caption("Interface guidée")
    
    with col3:
        if has_analysis():
            home_analysis_key = f"home_analysis_{reset_counter}"
            if st.button("📊 Voir l'analyse actuelle", key=home_analysis_key, type="primary", use_container_width=True):
                SessionManager.set_current_page('analysis')
                st.rerun()
            st.caption("Analyse disponible")
        else:
            home_analysis_disabled_key = f"home_analysis_disabled_{reset_counter}"
            st.button("📊 Analyse", key=home_analysis_disabled_key, use_container_width=True, disabled=True)
            st.caption("Importez d'abord des données")
    
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
        
        reset_counter = SessionManager.get_reset_counter()
        
        with col1:
            home_view_key = f"home_view_{reset_counter}"
            if st.button("📊 Consulter l'Analyse", key=home_view_key, type="primary", use_container_width=True):
                SessionManager.set_current_page('analysis')
                st.rerun()
        
        with col2:
            home_report_key = f"home_report_{reset_counter}"
            if st.button("📋 Générer un Rapport", key=home_report_key, type="secondary", use_container_width=True):
                SessionManager.set_current_page('reports')
                st.rerun()
        
        with col3:
            home_reset_key = f"home_reset_{reset_counter}"
            if st.button("🔄 Nouvelle Analyse", key=home_reset_key, type="secondary", use_container_width=True):
                if st.confirm("Effacer l'analyse actuelle ?"):
                    reset_app()
                    st.success("🔄 Application réinitialisée!")
                    st.rerun()
    
    except Exception as e:
        st.error(f"Erreur affichage résumé: {e}")

def display_info_sections():
    """Affiche les sections informatives de la page d'accueil"""
    
    st.markdown("---")
    
    # Section des nouveautés
    with st.expander("🆕 Nouveautés Version 2.1", expanded=False):
        st.markdown("""
        ### 🚀 Améliorations Majeures
        
        - **🔒 Persistance Totale** : Vos fichiers ne se perdent plus lors de la navigation
        - **⚡ Navigation Fluide** : Passez entre les pages sans problème
        - **🎯 Reset Contrôlé** : Seul "Nouvelle Analyse" remet à zéro
        - **📊 Graphiques Enrichis** : Visualisations plus interactives
        - **🔧 Session Manager** : Gestion d'état centralisée et robuste
        - **🐛 Corrections** : Résolution des bugs de réinitialisation
        - **📱 Interface Améliorée** : Design plus moderne et responsive
        
        ### 🔧 Améliorations Techniques
        
        - **Anti-réinitialisation** : Protection contre la perte de données
        - **Gestionnaire d'état** : SessionManager centralisé
        - **Clés uniques** : Évite les conflits de widgets Streamlit
        - **Gestion d'erreurs** : Messages plus informatifs
        - **Performance** : Chargement plus rapide des pages
        """)
    
    # Section normes BCEAO
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
        
        **⚡ Ratios d'Activité :**
        - Rotation de l'actif ≥ 1,5
        - Rotation des stocks ≥ 6
        - Délai de recouvrement ≤ 45 jours
        
        **🎯 Classes de Notation :**
        - **A+** (85-100) : Excellence financière
        - **A** (70-84) : Très bonne situation
        - **B** (55-69) : Bonne situation
        - **C** (40-54) : Situation moyenne
        - **D** (25-39) : Situation faible
        - **E** (0-24) : Situation critique
        """)
    
    # Guide d'utilisation
    with st.expander("📖 Guide d'Utilisation Rapide", expanded=False):
        st.markdown("""
        ### 🎯 Comment utiliser OptimusCredit ?
        
        **1. 📤 Préparez vos données**
        - Fichier Excel au format BCEAO standard
        - Ou saisie manuelle via l'interface
        
        **2. 🔍 Lancez l'analyse**
        - Import automatique depuis Excel
        - Calcul instantané de 25+ ratios
        - Scoring automatique sur 100 points
        
        **3. 📊 Consultez les résultats**
        - Tableau de bord interactif
        - Graphiques de performance
        - Comparaison sectorielle
        
        **4. 📋 Générez vos rapports**
        - Synthèse exécutive
        - Rapport détaillé
        - Plan d'action personnalisé
        
        ### 💡 Conseils d'utilisation
        
        - **Données complètes** : Plus vos données sont précises, plus l'analyse sera pertinente
        - **Secteur adapté** : Choisissez le bon secteur pour une comparaison pertinente
        - **Suivi régulier** : Réalisez l'analyse trimestriellement
        - **Actions correctives** : Suivez les recommandations prioritaires
        """)
    
    # Informations techniques
    with st.expander("🔧 Spécifications Techniques", expanded=False):
        st.markdown("""
        ### 📋 Compatibilité et Prérequis
        
        **Formats supportés :**
        - Excel : .xlsx, .xls
        - Taille maximale : 200 MB
        - Encodage : UTF-8, Windows-1252
        
        **Navigateurs compatibles :**
        - Chrome 90+ (recommandé)
        - Firefox 88+
        - Safari 14+
        - Edge 90+
        
        **Sécurité et Confidentialité :**
        - ✅ Traitement 100% local
        - ✅ Aucune donnée envoyée sur internet
        - ✅ Session temporaire uniquement
        - ✅ Conforme RGPD
        
        **Performance :**
        - Analyse en 5-10 secondes
        - 25+ ratios calculés automatiquement
        - Graphiques temps réel
        - Export instantané
        
        ### 📞 Support Technique
        
        - **Email :** contact@kaizen-corporation.com
        - **Documentation :** Guide utilisateur intégré
        - **Horaires :** 9h-18h (GMT+0)
        - **Langue :** Français, Anglais
        """)

def show_no_analysis_page(page_type="analyse"):
    """Affiche une page d'erreur quand aucune analyse n'est disponible"""
    
    st.warning(f"⚠️ Aucune analyse disponible pour accéder aux {page_type}")
    st.info("💡 Veuillez d'abord importer des données Excel ou effectuer une saisie manuelle.")
    
    st.markdown("### 🚀 Actions Disponibles")
    
    col1, col2 = st.columns(2)
    
    reset_counter = SessionManager.get_reset_counter()
    
    with col1:
        goto_import_key = f"goto_import_{page_type}_{reset_counter}"
        if st.button("📤 Import Excel", key=goto_import_key, type="primary", use_container_width=True):
            SessionManager.set_current_page('excel_import')
            st.rerun()
        st.caption("Importer un fichier Excel au format BCEAO")
    
    with col2:
        goto_manual_key = f"goto_manual_{page_type}_{reset_counter}"
        if st.button("✏️ Saisie Manuelle", key=goto_manual_key, type="secondary", use_container_width=True):
            SessionManager.set_current_page('manual_input')
            st.rerun()
        st.caption("Saisir les données manuellement")

def show_import_error_page(page_name):
    """Affiche une page d'erreur pour les imports ratés"""
    
    st.error(f"❌ Impossible de charger la page {page_name}")
    
    st.markdown(f"""
    ### 🔧 Problème technique détecté
    
    La page **{page_name}** n'a pas pu être chargée. Cela peut être dû à :
    
    - 📁 Fichier manquant : `modules/pages/{page_name.lower().replace(' ', '_')}.py`
    - 🐍 Erreur d'import Python
    - 🔧 Module dépendant manquant
    
    ### 💡 Solutions proposées
    """)
    
    col1, col2 = st.columns(2)
    
    reset_counter = SessionManager.get_reset_counter()
    
    with col1:
        home_key = f"error_home_{reset_counter}"
        if st.button("🏠 Retour à l'Accueil", key=home_key, type="primary", use_container_width=True):
            SessionManager.set_current_page('home')
            st.rerun()
    
    with col2:
        reload_key = f"error_reload_{reset_counter}"
        if st.button("🔄 Recharger", key=reload_key, use_container_width=True):
            st.rerun()

def show_unknown_page_error(page_name):
    """Affiche une erreur pour une page inconnue"""
    
    st.error(f"❌ Page '{page_name}' non reconnue")
    
    st.markdown(f"""
    ### 🔍 Page inconnue détectée
    
    La page **{page_name}** n'existe pas dans l'application.
    
    ### 📋 Pages disponibles :
    - 🏠 **Accueil** : Page d'accueil et présentation
    - 📤 **Import Excel** : Importer un fichier Excel BCEAO
    - ✏️ **Saisie Manuelle** : Saisie manuelle des données
    - 📊 **Analyse Complète** : Analyse détaillée et ratios (nécessite des données)
    - 📋 **Rapports** : Génération de rapports (nécessite des données)
    """)
    
    reset_counter = SessionManager.get_reset_counter()
    
    col1, col2 = st.columns(2)
    
    with col1:
        unknown_home_key = f"unknown_home_{reset_counter}"
        if st.button("🏠 Aller à l'Accueil", key=unknown_home_key, type="primary", use_container_width=True):
            SessionManager.set_current_page('home')
            st.rerun()
    
    with col2:
        unknown_import_key = f"unknown_import_{reset_counter}"
        if st.button("📤 Commencer une Analyse", key=unknown_import_key, type="secondary", use_container_width=True):
            SessionManager.set_current_page('excel_import')
            st.rerun()

def display_footer():
    """Affiche le pied de page de l'application"""
    
    st.markdown("---")
    
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.markdown(f"""
        <div style="text-align: center; color: #666; font-size: 12px; padding: 20px;">
            <p><strong>© 2024 OptimusCredit - Analyse Financière BCEAO</strong></p>
            <p>Version 2.1 • Conforme aux normes prudentielles BCEAO 2024</p>
            <p>Développé par Kaizen Corporation • Support: contact@kaizen-corporation.com</p>
            <p><em>Dernière mise à jour: {datetime.now().strftime('%d/%m/%Y')}</em></p>
        </div>
        """, unsafe_allow_html=True)

def handle_application_error(error, context=""):
    """Gère les erreurs globales de l'application"""
    
    st.error(f"❌ Erreur Application {context}: {error}")
    
    with st.expander("🔍 Détails Techniques", expanded=False):
        import traceback
        st.code(traceback.format_exc())
    
    st.markdown("### 🔧 Actions de Récupération")
    
    col1, col2, col3 = st.columns(3)
    
    reset_counter = SessionManager.get_reset_counter()
    
    with col1:
        if st.button("🏠 Accueil", key=f"error_home_recovery_{reset_counter}"):
            SessionManager.set_current_page('home')
            st.rerun()
    
    with col2:
        if st.button("🔄 Recharger", key=f"error_reload_recovery_{reset_counter}"):
            st.rerun()
    
    with col3:
        if st.button("🧹 Reset Complet", key=f"error_reset_recovery_{reset_counter}"):
            if st.confirm("Effacer toutes les données et redémarrer ?"):
                reset_app()
                st.success("Application réinitialisée")
                st.rerun()

def check_system_requirements():
    """Vérifie les prérequis système"""
    
    requirements_ok = True
    missing_modules = []
    
    # Vérifier les modules essentiels
    essential_modules = [
        ('pandas', 'Manipulation des données'),
        ('plotly', 'Graphiques interactifs'),
        ('openpyxl', 'Lecture fichiers Excel'),
        ('datetime', 'Gestion des dates')
    ]
    
    for module_name, description in essential_modules:
        try:
            __import__(module_name)
        except ImportError:
            requirements_ok = False
            missing_modules.append((module_name, description))
    
    if not requirements_ok:
        st.error("❌ Modules Python manquants détectés")
        
        st.markdown("### 📦 Modules à installer :")
        for module, desc in missing_modules:
            st.write(f"• **{module}** : {desc}")
        
        st.code(f"pip install {' '.join([m[0] for m in missing_modules])}")
        
        st.stop()
    
    return True

def initialize_application():
    """Initialise l'application avec toutes les vérifications"""
    
    # Vérifier les prérequis système
    check_system_requirements()
    
    # Initialiser le gestionnaire de session
    init_session()
    
    # Vérifier la structure des fichiers (optionnel)
    check_file_structure()

def check_file_structure():
    """CORRIGÉ : Vérifie la structure des fichiers (version allégée)"""
    
    required_files = [
        'session_manager.py'
    ]
    
    missing_files = []
    
    for file_path in required_files:
        if not os.path.exists(file_path):
            missing_files.append(file_path)
    
    if missing_files:
        st.error("❌ Fichiers critiques manquants :")
        for file_path in missing_files:
            st.write(f"• {file_path}")
        st.stop()

# CORRECTION : Fonction pour afficher la version et les informations système (version simplifiée)
def display_system_info():
    """Affiche les informations système (version simplifiée pour la production)"""
    
    # VERSION SIMPLIFIÉE - moins de détails sensibles
    if st.sidebar.checkbox("🔧 Infos App"):
        with st.sidebar.expander("💻 Informations"):
            st.write(f"**Version :** 2.1.0")
            st.write(f"**Page :** {SessionManager.get_current_page()}")
            st.write(f"**Analyse :** {'Oui' if has_analysis() else 'Non'}")
            st.write(f"**Streamlit :** {st.__version__}")

# Point d'entrée principal de l'application
if __name__ == "__main__":
    try:
        # Initialiser l'application
        initialize_application()
        
        # CORRECTION : Afficher les informations système en mode debug (version simplifiée)
        display_system_info()
        
        # Exécuter l'application principale
        main()
        
    except KeyboardInterrupt:
        st.info("⏹️ Application interrompue par l'utilisateur")
        
    except Exception as e:
        # Gestion globale des erreurs
        handle_application_error(e, "Démarrage")
        
        # Afficher un message de récupération
        st.markdown("""
        ### 🆘 Erreur Critique
        
        Une erreur inattendue s'est produite lors du démarrage de l'application.
        
        **Solutions :**
        1. Actualisez la page (F5)
        2. Vérifiez que tous les fichiers sont présents
        3. Contactez le support technique
        
        **Support :** contact@kaizen-corporation.com
        """)
    
    finally:
        # Code de nettoyage si nécessaire
        pass