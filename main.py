# AJOUTEZ CETTE FONCTION DANS VOTRE main.py

def show_diagnostic_mode():
    """Mode diagnostic intégré"""
    
    st.title("🔍 Diagnostic Navigation - Mode Intégré")
    
    # Test de l'analyse
    st.subheader("📊 Test de l'Analyse")
    
    analysis_available = has_analysis()
    st.write(f"**has_analysis():** {analysis_available}")
    
    if analysis_available:
        try:
            score, metadata = SessionManager.get_analysis_info()
            st.success(f"✅ Analyse trouvée - Score: {score}/100")
            st.write(f"**Métadonnées:** {metadata}")
        except Exception as e:
            st.error(f"❌ Erreur récupération: {e}")
    
    # Test de navigation
    st.subheader("🧪 Test Navigation")
    
    current_page = st.session_state.get('current_page', 'Non défini')
    st.write(f"**Page actuelle:** {current_page}")
    
    # Bouton de test AVEC debug
    if st.button("🔬 TEST - Navigation vers Analysis", key="test_nav_debug"):
        st.write("🔄 Tentative de navigation...")
        
        # Debug étape par étape
        st.session_state['current_page'] = 'analysis'
        st.write(f"✅ current_page = {st.session_state['current_page']}")
        
        try:
            st.query_params.page = 'analysis'
            st.write("✅ query_params défini")
        except Exception as e:
            st.write(f"⚠️ query_params failed: {e}")
        
        st.write("🔄 Lancement st.rerun()...")
        st.rerun()
    
    # Test des variables importantes
    st.subheader("📋 Variables Importantes")
    
    important_vars = [
        'current_page', 'nav_timestamp', 'analysis_results',
        'analysis_data', 'analysis_ratios', 'analysis_scores'
    ]
    
    for var in important_vars:
        if var in st.session_state:
            value = st.session_state[var]
            if isinstance(value, dict):
                st.write(f"✅ **{var}:** Dict avec {len(value)} éléments")
            else:
                st.write(f"✅ **{var}:** {value}")
        else:
            st.write(f"❌ **{var}:** Non trouvé")
    
    # Retour normal
    if st.button("🏠 Retour Normal", key="exit_debug"):
        st.session_state['current_page'] = 'home'
        st.rerun()

# MODIFIEZ VOTRE FONCTION display_sidebar_navigation() 
# Ajoutez CETTE LIGNE dans la sidebar, après les normes BCEAO :

# Dans display_sidebar_navigation(), ajoutez :
        st.markdown("---")
        # DIAGNOSTIC MODE
        if st.button("🔍 MODE DIAGNOSTIC", key="diagnostic_mode", type="secondary", use_container_width=True):
            st.session_state['diagnostic_active'] = True
            st.rerun()

# MODIFIEZ VOTRE FONCTION display_main_content()
# Ajoutez CETTE CONDITION au début :

# Dans display_main_content(), ajoutez au début :
    # Mode diagnostic
    if st.session_state.get('diagnostic_active', False):
        show_diagnostic_mode()
        return
