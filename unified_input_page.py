"""
Page Unifiée de Saisie des Données - OptimusCredit
Import Excel, Saisie Manuelle et OCR en une seule interface
Version avec tests de navigation intégrés
"""

import streamlit as st
import tempfile
import os
import time
from datetime import datetime

# Import du gestionnaire de session centralisé
try:
    from session_manager import SessionManager, store_analysis, has_analysis, reset_app
except ImportError:
    st.error("❌ Impossible d'importer session_manager.py")
    st.stop()

def show_unified_input_page():
    """Affiche la page unifiée de saisie des données"""
    
    st.title("📊 Méthode de Saisie des Données")
    st.markdown("*Sélectionnez votre méthode de saisie préférée*")
    st.markdown("---")
    
    # Initialisation des variables de session
    initialize_session_variables()
    
    # Gestion du message de reset
    handle_reset_message()
    
    # Sélection de la méthode
    method = display_method_selection()
    
    # Affichage selon la méthode sélectionnée
    if method == "excel":
        display_excel_import_section()
    elif method == "manual":
        display_manual_input_section()
    elif method == "ocr":
        display_ocr_section()

def initialize_session_variables():
    """Initialise les variables de session nécessaires"""
    
    session_vars = [
        'file_uploaded', 'file_content', 'file_name', 'analysis_running',
        'analysis_completed', 'show_sectoral', 'show_charts', 'manual_data_entered'
    ]
    
    for var in session_vars:
        if var not in st.session_state:
            st.session_state[var] = False
    
    # Variables spécifiques
    if 'secteur_selected' not in st.session_state:
        st.session_state['secteur_selected'] = 'commerce_detail'

def handle_reset_message():
    """Gère l'affichage du message de reset"""
    
    if st.session_state.get('complete_reset', False):
        st.success("🔄 Application complètement réinitialisée! Vous pouvez maintenant saisir de nouvelles données.")
        st.session_state['file_uploaded'] = False
        st.session_state['file_content'] = None
        st.session_state['file_name'] = None
        st.session_state['analysis_running'] = False
        st.session_state['analysis_completed'] = False
        st.session_state['manual_data_entered'] = False
        del st.session_state['complete_reset']
        st.rerun()

def display_method_selection():
    """Affiche la sélection de méthode de saisie"""
    
    st.subheader("🔧 Méthode de Saisie des Données")
    
    method_options = {
        "excel": "📤 Import Excel",
        "manual": "✏️ Saisie Manuelle", 
        "ocr": "📷 Import OCR"
    }
    
    # Radio buttons pour la sélection
    selected_method = st.radio(
        "Sélectionnez votre méthode de saisie :",
        options=list(method_options.keys()),
        format_func=lambda x: method_options[x],
        horizontal=True,
        key="method_selection"
    )
    
    return selected_method

def display_excel_import_section():
    """Section d'import Excel complète"""
    
    st.markdown("---")
    st.subheader("📤 Import de Fichier Excel")
    
    # Vérifier si une analyse existe déjà
    if has_analysis():
        display_existing_analysis_section()
        return
    
    # Vérifier si un fichier est déjà uploadé
    if st.session_state.get('file_uploaded', False):
        display_uploaded_file_section()
    else:
        display_file_upload_section()

def display_existing_analysis_section():
    """Affiche la section pour une analyse existante"""
    
    # Récupérer les informations d'analyse
    try:
        score, metadata = SessionManager.get_analysis_info()
        source = metadata.get('source', 'Source inconnue')
        filename = metadata.get('fichier_nom', 'Fichier inconnu')
        secteur = metadata.get('secteur', 'Non spécifié')
        
        st.warning(f"⚠️ **Analyse existante détectée** (Source: {source}, Score: {score}/100)")
        
        with st.expander("📋 Détails de l'analyse actuelle", expanded=True):
            col1, col2 = st.columns(2)
            
            with col1:
                st.write(f"**📁 Fichier :** {filename}")
                st.write(f"**🏭 Secteur :** {secteur.replace('_', ' ').title()}")
            
            with col2:
                st.write(f"**📊 Score :** {score}/100")
                st.write(f"**📅 Date :** {metadata.get('date_analyse', 'N/A')}")
        
        # Actions disponibles
        st.markdown("### 🚀 Actions Disponibles")
        
        col1, col2, col3 = st.columns(3)
        
        # Générer une clé unique basée sur le timestamp
        reset_counter = SessionManager.get_reset_counter()
        
        with col1:
            # BOUTON ORIGINAL qui ne fonctionne pas
            if st.button("📊 Voir l'Analyse", 
                        key=f"view_analysis_original_{reset_counter}", 
                        type="primary", 
                        use_container_width=True):
                navigate_to_page('analysis')
        
        with col2:
            if st.button("🆕 Nouvelle Analyse", 
                        key=f"new_analysis_{reset_counter}", 
                        type="secondary", 
                        use_container_width=True):
                if st.session_state.get(f'confirm_reset_{reset_counter}', False):
                    reset_app()
                    st.rerun()
                else:
                    st.session_state[f'confirm_reset_{reset_counter}'] = True
                    st.warning("⚠️ Cliquez à nouveau pour confirmer")
        
        with col3:
            if st.button("🏠 Accueil", 
                        key=f"go_home_{reset_counter}", 
                        type="secondary", 
                        use_container_width=True):
                navigate_to_page('home')
        
        # 🧪 SECTION TEST DE NAVIGATION
        st.markdown("---")
        st.markdown("### 🧪 Test de Navigation - Boutons Debug")
        st.info("💡 Ces boutons testent différentes méthodes de navigation pour identifier le problème")
        
        # CALLBACK sécurisé pour la navigation
        def navigate_to_analysis_callback():
            """Callback sécurisé pour navigation vers analyse"""
            st.session_state['current_page'] = 'analysis'
            try:
                st.query_params.page = 'analysis'
            except:
                pass
        
        col1, col2 = st.columns(2)
        
        with col1:
            # BOUTON TEST avec callback
            if st.button("🧪 TEST - Voir l'Analyse (Callback)", 
                        key=f"test_analysis_callback_{reset_counter}", 
                        type="primary", 
                        on_click=navigate_to_analysis_callback,
                        use_container_width=True):
                st.success("✅ Callback exécuté - Navigation en cours...")
        
        with col2:
            # BOUTON TEST avec logique conditionnelle
            if st.button("🧪 TEST - Voir l'Analyse (If)", 
                        key=f"test_analysis_if_{reset_counter}", 
                        type="secondary", 
                        use_container_width=True):
                st.success("✅ Bouton cliqué - Navigation manuelle...")
                st.session_state['current_page'] = 'analysis'
                try:
                    st.query_params.page = 'analysis'
                except:
                    pass
                st.rerun()
        
        # Debug des variables de navigation
        with st.expander("🔍 Debug Navigation", expanded=False):
            st.write(f"**current_page:** {st.session_state.get('current_page', 'Non défini')}")
            try:
                query_page = st.query_params.get('page', 'Non défini')
                st.write(f"**query_params.page:** {query_page}")
            except Exception as e:
                st.write(f"**query_params error:** {e}")
            
            st.write(f"**has_analysis():** {has_analysis()}")
            st.write(f"**nav_timestamp:** {st.session_state.get('nav_timestamp', 'Non défini')}")
            st.write(f"**reset_counter:** {reset_counter}")
        
        # Options d'affichage rapide
        display_quick_analysis_options()
        
    except Exception as e:
        st.error(f"❌ Erreur lors de l'affichage de l'analyse existante: {e}")

def display_file_upload_section():
    """Affiche la section d'upload de fichier"""
    
    st.markdown("### 📁 Sélection du Fichier Excel")
    
    # Instructions
    with st.expander("💡 Instructions d'utilisation", expanded=False):
        st.markdown("""
        **Format requis :**
        - Extension : `.xlsx` ou `.xls`
        - Feuilles obligatoires : `Bilan`, `CR` (Compte de Résultat)
        - Feuille optionnelle : `TFT` (Tableau des Flux de Trésorerie)
        
        **Procédure :**
        1. Uploadez votre fichier Excel au format BCEAO
        2. Sélectionnez votre secteur d'activité
        3. Lancez l'analyse automatique
        """)
    
    # Upload du fichier
    reset_counter = SessionManager.get_reset_counter()
    uploader_key = f"file_uploader_{reset_counter}"
    
    uploaded_file = st.file_uploader(
        "Sélectionnez votre fichier Excel",
        type=['xlsx', 'xls'],
        help="Le fichier doit contenir les feuilles : Bilan, CR (Compte de Résultat)",
        key=uploader_key
    )
    
    if uploaded_file is not None:
        # Stocker le fichier en session state
        st.session_state['file_content'] = uploaded_file.getbuffer()
        st.session_state['file_name'] = uploaded_file.name
        st.session_state['file_uploaded'] = True
        st.rerun()

def display_uploaded_file_section():
    """Affiche la section avec fichier uploadé"""
    
    st.markdown("### 📁 Fichier Sélectionné")
    
    filename = st.session_state.get('file_name', 'Fichier inconnu')
    file_size = len(st.session_state.get('file_content', b'')) / 1024
    
    with st.expander("📋 Détails du fichier", expanded=True):
        col1, col2 = st.columns(2)
        
        with col1:
            st.write(f"**📄 Nom :** {filename}")
            st.write(f"**📊 Taille :** {file_size:.1f} KB")
        
        with col2:
            st.write(f"**📅 Uploadé :** {datetime.now().strftime('%H:%M:%S')}")
            st.success("✅ Fichier prêt pour l'analyse")
    
    # Sélection du secteur
    st.markdown("### 🏭 Secteur d'Activité")
    
    secteur_options = {
        "industrie_manufacturiere": "Industrie Manufacturière",
        "commerce_detail": "Commerce de Détail",
        "services_professionnels": "Services Professionnels",
        "construction_btp": "Construction / BTP",
        "agriculture": "Agriculture",
        "commerce_gros": "Commerce de Gros"
    }
    
    secteur = st.selectbox(
        "Sélectionnez votre secteur d'activité :",
        options=list(secteur_options.keys()),
        format_func=lambda x: secteur_options[x],
        key="secteur_selection"
    )
    
    # Bouton d'analyse
    st.markdown("### 🚀 Lancement de l'Analyse")
    
    if not st.session_state.get('analysis_running', False):
        if st.button("🔍 Analyser le Fichier", 
                    key="analyze_file_btn", 
                    type="primary", 
                    use_container_width=True):
            st.session_state['analysis_running'] = True
            analyze_uploaded_file(
                st.session_state['file_content'],
                st.session_state['file_name'],
                secteur
            )
    else:
        st.info("🔄 Analyse en cours... Veuillez patienter.")
        # Simuler une barre de progression
        progress_bar = st.progress(0)
        for i in range(100):
            time.sleep(0.01)
            progress_bar.progress(i + 1)

def analyze_uploaded_file(file_content, filename, secteur):
    """Analyse le fichier uploadé"""
    
    with st.spinner("📊 Extraction et analyse des données en cours..."):
        temp_file_path = None
        
        try:
            # Créer un fichier temporaire
            with tempfile.NamedTemporaryFile(delete=False, suffix='.xlsx') as tmp_file:
                tmp_file.write(file_content)
                temp_file_path = tmp_file.name
            
            # Importer l'analyseur
            try:
                from modules.core.analyzer import FinancialAnalyzer
            except ImportError as e:
                st.error(f"❌ Impossible d'importer FinancialAnalyzer: {e}")
                st.session_state['analysis_running'] = False
                return
            
            # Analyser le fichier
            analyzer = FinancialAnalyzer()
            data = analyzer.load_excel_template(temp_file_path)
            
            if data is None:
                st.error("❌ Erreur lors du chargement du fichier Excel")
                st.error("Vérifiez que le fichier contient les feuilles 'Bilan' et 'CR'")
                st.session_state['analysis_running'] = False
                return
            
            # Calculer les ratios et scores
            ratios = analyzer.calculate_ratios(data)
            scores = analyzer.calculate_score(ratios, secteur)
            
            # Stocker les résultats
            metadata = {
                'secteur': secteur,
                'fichier_nom': filename,
                'source': 'excel_import_unified'
            }
            
            store_analysis(data, ratios, scores, metadata)
            
            # Mettre à jour l'état
            st.session_state['analysis_running'] = False
            st.session_state['analysis_completed'] = True
            st.session_state['analysis_just_completed'] = True
            
            st.success("✅ Analyse terminée avec succès!")
            st.balloons()
            st.rerun()
            
        except Exception as e:
            st.error(f"❌ Erreur lors de l'analyse: {str(e)}")
            st.session_state['analysis_running'] = False
            
        finally:
            # Nettoyer le fichier temporaire
            if temp_file_path and os.path.exists(temp_file_path):
                try:
                    os.unlink(temp_file_path)
                except:
                    pass

def display_manual_input_section():
    """Section de saisie manuelle"""
    
    st.markdown("---")
    st.subheader("✏️ Saisie Manuelle des Données")
    
    st.info("🚧 **Fonctionnalité en développement**")
    st.markdown("""
    La saisie manuelle détaillée sera disponible dans la version 2.2.
    
    **Fonctionnalités prévues :**
    - 📊 Saisie du bilan par onglets
    - 📈 Saisie du compte de résultat
    - 💰 Saisie des flux de trésorerie
    - ✅ Validation automatique des équilibres
    - 🎯 Calcul en temps réel des ratios
    """)
    
    # Bouton temporaire pour accéder à l'ancienne page
    if st.button("📝 Accéder à la Saisie Manuelle (Version Bêta)", 
                key="manual_input_beta", 
                type="secondary"):
        try:
            from modules.pages.manual_input import show_manual_input_page
            show_manual_input_page()
        except ImportError:
            st.error("❌ Module de saisie manuelle non disponible")

def display_ocr_section():
    """Section d'import OCR"""
    
    st.markdown("---")
    st.subheader("📷 Import par Reconnaissance Optique (OCR)")
    
    st.info("🚧 **Fonctionnalité en développement**")
    st.markdown("""
    L'import par OCR sera disponible dans la version 2.2.
    
    **Fonctionnalités prévues :**
    - 📷 Upload d'images ou PDF scannés
    - 🤖 Reconnaissance automatique des chiffres
    - ✏️ Interface de correction manuelle
    - 📊 Conversion automatique en format Excel
    - 🎯 Intégration avec l'analyse automatique
    """)
    
    # Démonstration visuelle
    with st.expander("👁️ Aperçu de la fonctionnalité OCR", expanded=False):
        st.markdown("""
        **Étapes de traitement OCR :**
        
        1. **📷 Upload** : Image ou PDF du document financier
        2. **🔍 Détection** : Identification des zones de texte et chiffres
        3. **🤖 Reconnaissance** : Extraction automatique des données
        4. **✏️ Validation** : Interface de correction des erreurs
        5. **📊 Conversion** : Génération du modèle Excel BCEAO
        6. **🎯 Analyse** : Lancement automatique de l'analyse
        """)

def display_quick_analysis_options():
    """Affiche les options d'affichage rapide de l'analyse"""
    
    st.markdown("### ⚡ Aperçu Rapide")
    
    col1, col2 = st.columns(2)
    
    reset_counter = SessionManager.get_reset_counter()
    
    with col1:
        if st.button("📊 Comparaison Sectorielle", 
                    key=f"toggle_sectoral_{reset_counter}", 
                    use_container_width=True):
            st.session_state['show_sectoral'] = not st.session_state.get('show_sectoral', False)
    
    with col2:
        if st.button("📈 Graphiques Rapides", 
                    key=f"toggle_charts_{reset_counter}", 
                    use_container_width=True):
            st.session_state['show_charts'] = not st.session_state.get('show_charts', False)
    
    # Affichage conditionnel
    if st.session_state.get('show_sectoral', False):
        display_sectoral_comparison()
    
    if st.session_state.get('show_charts', False):
        display_quick_charts()

def display_sectoral_comparison():
    """Affiche la comparaison sectorielle rapide"""
    
    st.markdown("#### 🔄 Comparaison Sectorielle")
    
    try:
        analysis_data = SessionManager.get_analysis_data()
        if not analysis_data:
            st.warning("Aucune donnée d'analyse disponible")
            return
        
        ratios = analysis_data['ratios']
        secteur = analysis_data['metadata'].get('secteur', '')
        
        # Données sectorielles simplifiées (exemple)
        sectoral_data = {
            'commerce_detail': {
                'liquidite_generale': {'median': 1.5, 'q3': 2.2},
                'autonomie_financiere': {'median': 35, 'q3': 50},
                'roe': {'median': 12, 'q3': 20}
            },
            'commerce_gros': {
                'liquidite_generale': {'median': 1.4, 'q3': 1.8},
                'autonomie_financiere': {'median': 30, 'q3': 45},
                'roe': {'median': 10, 'q3': 18}
            }
            # Ajouter d'autres secteurs...
        }
        
        if secteur in sectoral_data:
            benchmarks = sectoral_data[secteur]
            
            comparison_data = []
            
            # Comparaison des ratios clés
            key_ratios = {
                'ratio_liquidite_generale': 'Liquidité Générale',
                'ratio_autonomie_financiere': 'Autonomie Financière (%)',
                'roe': 'ROE (%)'
            }
            
            for ratio_key, ratio_name in key_ratios.items():
                if ratio_key in ratios:
                    entreprise_val = ratios[ratio_key]
                    
                    # Déterminer la benchmark key
                    benchmark_key = ratio_key.replace('ratio_', '')
                    if benchmark_key in benchmarks:
                        benchmark = benchmarks[benchmark_key]
                        median_val = benchmark['median']
                        q3_val = benchmark['q3']
                        
                        # Position relative
                        if entreprise_val >= q3_val:
                            position = "🟢 Top 25%"
                        elif entreprise_val >= median_val:
                            position = "🟡 Au-dessus médiane"
                        else:
                            position = "🟠 Sous médiane"
                        
                        comparison_data.append({
                            'Ratio': ratio_name,
                            'Votre Valeur': f"{entreprise_val:.2f}",
                            'Médiane Secteur': f"{median_val:.2f}",
                            'Position': position
                        })
            
            if comparison_data:
                import pandas as pd
                df = pd.DataFrame(comparison_data)
                st.dataframe(df, hide_index=True, use_container_width=True)
            else:
                st.info("Données de comparaison non disponibles")
        else:
            st.info(f"Données sectorielles non disponibles pour {secteur}")
            
    except Exception as e:
        st.error(f"Erreur lors de la comparaison sectorielle: {e}")

def display_quick_charts():
    """Affiche des graphiques rapides"""
    
    st.markdown("#### 📈 Graphiques Rapides")
    
    try:
        analysis_data = SessionManager.get_analysis_data()
        if not analysis_data:
            st.warning("Aucune donnée d'analyse disponible")
            return
        
        data = analysis_data['data']
        ratios = analysis_data['ratios']
        scores = analysis_data['scores']
        
        # Graphiques simples
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown("**💧 Liquidité**")
            st.metric("Générale", f"{ratios.get('ratio_liquidite_generale', 0):.2f}")
            st.metric("Immédiate", f"{ratios.get('ratio_liquidite_immediate', 0):.2f}")
        
        with col2:
            st.markdown("**📈 Rentabilité**")
            st.metric("ROE", f"{ratios.get('roe', 0):.1f}%")
            st.metric("Marge Nette", f"{ratios.get('marge_nette', 0):.1f}%")
        
        with col3:
            st.markdown("**🎯 Performance**")
            st.metric("Score Global", f"{scores.get('global', 0)}/100")
            classe = SessionManager.get_financial_class(scores.get('global', 0))
            st.metric("Classe BCEAO", classe)
        
        # Graphique de scores (version simple)
        st.markdown("**📊 Répartition des Scores**")
        
        score_data = {
            'Catégorie': ['Liquidité', 'Solvabilité', 'Rentabilité', 'Activité', 'Gestion'],
            'Score': [
                scores.get('liquidite', 0),
                scores.get('solvabilite', 0),
                scores.get('rentabilite', 0),
                scores.get('activite', 0),
                scores.get('gestion', 0)
            ],
            'Maximum': [40, 40, 30, 15, 15]
        }
        
        # Affichage simple sous forme de barres de progression
        for i, categorie in enumerate(score_data['Catégorie']):
            score = score_data['Score'][i]
            max_score = score_data['Maximum'][i]
            percentage = (score / max_score) * 100
            
            st.write(f"**{categorie}:** {score}/{max_score} ({percentage:.0f}%)")
            st.progress(percentage / 100)
        
    except Exception as e:
        st.error(f"Erreur lors de l'affichage des graphiques: {e}")

def navigate_to_page(page_name):
    """Navigation sécurisée vers une page"""
    
    st.session_state['current_page'] = page_name
    try:
        st.query_params.page = page_name
    except Exception as e:
        st.session_state['query_params_error'] = str(e)
    
    st.rerun()

# Point d'entrée de la page
if __name__ == "__main__":
    show_unified_input_page()
