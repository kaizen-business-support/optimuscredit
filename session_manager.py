"""
Gestionnaire d'état centralisé pour l'application OptimusCredit
Ce module garantit la cohérence des données entre toutes les pages
VERSION FIXED - Compatibilité backward complète
"""

import streamlit as st
from datetime import datetime
from typing import Dict, Any, Optional, Tuple

class SessionManager:
    """Gestionnaire centralisé pour l'état de session de l'application"""
    
    # Clés standardisées pour l'état de session
    ANALYSIS_RESULTS = 'analysis_results'
    CURRENT_PAGE = 'current_page'
    RESET_COUNTER = 'reset_counter'
    
    @staticmethod
    def initialize():
        """Initialise l'état de session avec les valeurs par défaut"""
        if SessionManager.CURRENT_PAGE not in st.session_state:
            st.session_state[SessionManager.CURRENT_PAGE] = 'home'
        
        if SessionManager.RESET_COUNTER not in st.session_state:
            st.session_state[SessionManager.RESET_COUNTER] = 0
    
    @staticmethod
    def has_analysis_data() -> bool:
        """Vérifie si des données d'analyse valides existent"""
        if SessionManager.ANALYSIS_RESULTS not in st.session_state:
            return False
        
        analysis_results = st.session_state[SessionManager.ANALYSIS_RESULTS]
        
        # Vérifier la structure complète
        required_keys = ['data', 'ratios', 'scores', 'metadata']
        if not all(key in analysis_results for key in required_keys):
            return False
        
        # Vérifier que les scores sont valides
        scores = analysis_results.get('scores', {})
        if not isinstance(scores, dict) or 'global' not in scores:
            return False
        
        # Vérifier que les ratios existent
        ratios = analysis_results.get('ratios', {})
        if not isinstance(ratios, dict) or len(ratios) == 0:
            return False
        
        return True
    
    @staticmethod
    def get_analysis_info() -> Tuple[int, Dict[str, Any]]:
        """Récupère les informations d'analyse actuelles"""
        if not SessionManager.has_analysis_data():
            return 0, {}
        
        analysis_results = st.session_state[SessionManager.ANALYSIS_RESULTS]
        score = analysis_results['scores'].get('global', 0)
        metadata = analysis_results.get('metadata', {})
        
        return score, metadata
    
    @staticmethod
    def get_analysis_data() -> Optional[Dict[str, Any]]:
        """Récupère toutes les données d'analyse"""
        if not SessionManager.has_analysis_data():
            return None
        
        return st.session_state[SessionManager.ANALYSIS_RESULTS]
    
    @staticmethod
    def store_analysis_results(data: Dict[str, Any], ratios: Dict[str, Any], 
                             scores: Dict[str, Any], metadata: Dict[str, Any]):
        """Stocke les résultats d'analyse de manière unifiée avec COMPATIBILITÉ BACKWARD"""
        
        # Ajouter timestamp si pas présent
        if 'date_analyse' not in metadata:
            metadata['date_analyse'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        # Ajouter compteur de ratios
        metadata['ratios_count'] = len(ratios)
        
        # Structure unifiée
        analysis_results = {
            'data': data,
            'ratios': ratios,
            'scores': scores,
            'metadata': metadata,
            'version': '2.1.0',  # Version pour compatibilité future
            'timestamp': datetime.now().isoformat()
        }
        
        # Nettoyer d'abord toutes les anciennes données
        SessionManager.clear_analysis_data()
        
        # Stocker la nouvelle analyse
        st.session_state[SessionManager.ANALYSIS_RESULTS] = analysis_results
        
        # 🔧 CORRECTION CRITIQUE : Maintenir les variables legacy pour compatibilité
        # avec d'éventuelles autres pages qui les utilisent encore
        st.session_state['analysis_data'] = data
        st.session_state['analysis_ratios'] = ratios
        st.session_state['analysis_scores'] = scores
        st.session_state['analysis_secteur'] = metadata.get('secteur', '')
        st.session_state['analysis_done'] = True
        st.session_state['analysis_date'] = metadata.get('date_analyse', '')
        
        # 🔧 NOUVEAU : Variables d'état pour contrôler l'affichage
        st.session_state['analysis_completed'] = True
        st.session_state['analysis_running'] = False
        st.session_state['analysis_just_completed'] = True
    
    @staticmethod
    def ensure_backward_compatibility():
        """Assure la compatibilité backward avec les anciennes variables"""
        
        # Si on a analysis_results mais pas les variables legacy, les créer
        if (SessionManager.ANALYSIS_RESULTS in st.session_state and 
            'analysis_data' not in st.session_state):
            
            analysis_results = st.session_state[SessionManager.ANALYSIS_RESULTS]
            
            # Recréer les variables legacy
            st.session_state['analysis_data'] = analysis_results.get('data', {})
            st.session_state['analysis_ratios'] = analysis_results.get('ratios', {})
            st.session_state['analysis_scores'] = analysis_results.get('scores', {})
            
            metadata = analysis_results.get('metadata', {})
            st.session_state['analysis_secteur'] = metadata.get('secteur', '')
            st.session_state['analysis_done'] = True
            st.session_state['analysis_date'] = metadata.get('date_analyse', '')
            st.session_state['analysis_completed'] = True
            st.session_state['analysis_running'] = False
    
    @staticmethod
    def clear_analysis_data():
        """Nettoie toutes les données d'analyse"""
        
        # Liste exhaustive de toutes les clés d'analyse possibles
        analysis_keys = [
            # Structure principale
            SessionManager.ANALYSIS_RESULTS,
            
            # Variables legacy (compatibilité)
            'analysis_data', 'analysis_ratios', 'analysis_scores', 
            'analysis_secteur', 'analysis_done', 'analysis_date',
            
            # États de l'interface
            'show_sectoral', 'show_charts', 'current_analysis_file',
            
            # États spécifiques aux pages
            'excel_analysis_complete', 'manual_analysis_complete',
            'analysis_completed', 'analysis_running', 'analysis_just_completed',
            
            # Cache et données temporaires
            'temp_data', 'temp_ratios', 'temp_scores',
            'uploaded_file_data', 'file_analysis_progress',
            
            # Variables spécifiques au file uploader
            'uploaded_file_content', 'uploaded_file_name', 'uploaded_file_type',
            'analysis_in_progress',
            
            # Variables de contrôle d'interface
            'file_uploader_key', 'complete_reset',
            
            # Variables de navigation anciennes
            'page'
        ]
        
        # Supprimer toutes les clés d'analyse
        for key in analysis_keys:
            if key in st.session_state:
                del st.session_state[key]
    
    @staticmethod
    def reset_application():
        """Réinitialise complètement l'application"""
        
        # Sauvegarder la page actuelle pour y retourner
        current_page = st.session_state.get(SessionManager.CURRENT_PAGE, 'home')
        
        # IMPORTANT: Sauvegarder l'ancien reset_counter pour l'incrémenter
        old_counter = st.session_state.get(SessionManager.RESET_COUNTER, 0)
        
        # Nettoyer toutes les données d'analyse
        SessionManager.clear_analysis_data()
        
        # CORRECTION: Incrémenter le compteur de reset pour forcer la recréation des widgets
        st.session_state[SessionManager.RESET_COUNTER] = old_counter + 1
        
        # Marquer qu'un reset complet a eu lieu
        st.session_state['complete_reset'] = True
        
        # Retourner à la page d'import pour un nouveau fichier
        st.session_state[SessionManager.CURRENT_PAGE] = 'home'
    
    @staticmethod
    def get_current_page() -> str:
        """Récupère la page actuelle"""
        return st.session_state.get(SessionManager.CURRENT_PAGE, 'home')
    
    @staticmethod
    def set_current_page(page: str):
        """Définit la page actuelle"""
        st.session_state[SessionManager.CURRENT_PAGE] = page
    
    @staticmethod
    def get_reset_counter() -> int:
        """Récupère le compteur de reset pour les widgets"""
        return st.session_state.get(SessionManager.RESET_COUNTER, 0)
    
    @staticmethod
    def get_financial_class(score: int) -> str:
        """Retourne la classe financière selon le score BCEAO"""
        if score >= 85:
            return "A+"
        elif score >= 70:
            return "A"
        elif score >= 55:
            return "B"
        elif score >= 40:
            return "C"
        elif score >= 25:
            return "D"
        else:
            return "E"
    
    @staticmethod
    def get_interpretation(score: int) -> Tuple[str, str]:
        """Retourne l'interprétation du score avec couleur"""
        if score >= 85:
            return "Excellence financière", "green"
        elif score >= 70:
            return "Très bonne situation", "green"
        elif score >= 55:
            return "Bonne situation", "orange"
        elif score >= 40:
            return "Situation moyenne", "orange"
        elif score >= 25:
            return "Situation faible", "red"
        else:
            return "Situation très faible", "red"
    
    @staticmethod
    def debug_session_state() -> Dict[str, Any]:
        """Retourne un aperçu de l'état de session pour debug"""
        debug_info = {
            'has_analysis': SessionManager.has_analysis_data(),
            'current_page': SessionManager.get_current_page(),
            'reset_counter': SessionManager.get_reset_counter(),
            'total_keys': len(st.session_state.keys()),
            'analysis_keys': [],
            'backward_compatibility': {}
        }
        
        # Identifier les clés liées à l'analyse
        analysis_prefixes = ['analysis_', 'show_', 'temp_', 'file_', 'complete_']
        for key in st.session_state.keys():
            if any(key.startswith(prefix) for prefix in analysis_prefixes) or key == SessionManager.ANALYSIS_RESULTS:
                debug_info['analysis_keys'].append(key)
        
        # Vérifier la compatibilité backward
        legacy_vars = ['analysis_data', 'analysis_ratios', 'analysis_scores', 'analysis_done']
        for var in legacy_vars:
            debug_info['backward_compatibility'][var] = var in st.session_state
        
        if SessionManager.has_analysis_data():
            score, metadata = SessionManager.get_analysis_info()
            debug_info['score'] = score
            debug_info['secteur'] = metadata.get('secteur', 'N/A')
            debug_info['date_analyse'] = metadata.get('date_analyse', 'N/A')
        
        return debug_info
    
    @staticmethod
    def show_debug_info():
        """Affiche les informations de debug (à utiliser temporairement)"""
        debug_info = SessionManager.debug_session_state()
        
        with st.expander("🔍 Debug - État de Session", expanded=False):
            st.json(debug_info)
            
            st.markdown("**Toutes les clés de session:**")
            st.write(list(st.session_state.keys()))


# Fonctions utilitaires pour faciliter l'utilisation
def init_session():
    """Fonction d'initialisation simple à appeler dans main.py"""
    SessionManager.initialize()
    # 🔧 CORRECTION : Assurer la compatibilité backward à chaque initialisation
    SessionManager.ensure_backward_compatibility()

def has_analysis() -> bool:
    """Fonction simple pour vérifier la présence d'analyse"""
    # 🔧 CORRECTION : Assurer la compatibilité avant de vérifier
    SessionManager.ensure_backward_compatibility()
    return SessionManager.has_analysis_data()

def get_analysis():
    """Fonction simple pour récupérer l'analyse"""
    # 🔧 CORRECTION : Assurer la compatibilité avant de récupérer
    SessionManager.ensure_backward_compatibility()
    return SessionManager.get_analysis_data()

def clear_analysis():
    """Fonction simple pour nettoyer l'analyse"""
    SessionManager.clear_analysis_data()

def reset_app():
    """Fonction simple pour réinitialiser l'app"""
    SessionManager.reset_application()

def store_analysis(data, ratios, scores, metadata):
    """Fonction simple pour stocker l'analyse"""
    SessionManager.store_analysis_results(data, ratios, scores, metadata)
