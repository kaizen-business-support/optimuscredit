"""
Page de génération de rapports - Version avec Export PDF
"""

import streamlit as st
import pandas as pd
from datetime import datetime
from reportlab.lib.pagesizes import letter, A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.lib.units import inch, cm
from reportlab.graphics.shapes import Drawing
from reportlab.graphics.charts.barcharts import VerticalBarChart
from reportlab.graphics.charts.piecharts import Pie
import io

try:
    from session_manager import SessionManager
except ImportError:
    st.error("❌ Impossible d'importer session_manager.py")
    st.stop()

def show_reports_page():
    """Affiche la page de génération de rapports"""
    
    # Vérifier si des données d'analyse existent
    if not SessionManager.has_analysis_data():
        st.warning("⚠️ Aucune analyse disponible pour générer des rapports.")
        st.info("👈 Utilisez le menu de navigation pour analyser vos données financières.")
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("📤 Import Excel", type="primary", use_container_width=True):
                SessionManager.set_current_page('excel_import')
                st.rerun()
        with col2:
            if st.button("✏️ Saisie Manuelle", use_container_width=True):
                SessionManager.set_current_page('manual_input')
                st.rerun()
        return
    
    # Récupérer les données d'analyse
    analysis_data = SessionManager.get_analysis_data()
    data = analysis_data['data']
    ratios = analysis_data['ratios']
    scores = analysis_data['scores']
    metadata = analysis_data['metadata']
    
    st.title("📋 Génération de Rapports PDF")
    st.markdown("---")
    
    # Résumé de l'analyse
    display_analysis_summary(data, scores, metadata)
    
    # Types de rapports
    st.header("📄 Rapports Disponibles")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📊 Synthèse Exécutive")
        st.markdown("*Rapport condensé sur 2-3 pages*")
        st.markdown("""
        **Contenu :**
        - Score global et interprétation
        - Ratios clés avec normes
        - Points forts et faiblesses
        - Recommandations prioritaires
        """)
        
        if st.button("📄 Générer Synthèse PDF", type="primary", use_container_width=True):
            generate_executive_summary_pdf(data, ratios, scores, metadata)
    
    with col2:
        st.subheader("📋 Rapport Détaillé")
        st.markdown("*Analyse complète sur 8-12 pages*")
        st.markdown("""
        **Contenu :**
        - États financiers complets
        - Tous les ratios (25+)
        - Comparaison sectorielle
        - Plan d'action détaillé
        """)
        
        if st.button("📄 Générer Rapport Complet PDF", type="secondary", use_container_width=True):
            generate_detailed_report_pdf(data, ratios, scores, metadata)
    
    # Options supplémentaires
    st.markdown("---")
    st.header("📊 Export Données")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("**📈 Tableau Excel des Ratios**")
        if st.button("📥 Télécharger Excel", use_container_width=True):
            download_excel_ratios(ratios, scores)
    
    with col2:
        st.markdown("**📋 Données CSV**")
        if st.button("📥 Télécharger CSV", use_container_width=True):
            download_csv_data(ratios, scores)

def display_analysis_summary(data, scores, metadata):
    """Affiche un résumé de l'analyse"""
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        score_global = scores.get('global', 0)
        interpretation, color = SessionManager.get_interpretation(score_global)
        st.metric("Score Global", f"{score_global}/100", interpretation)
    
    with col2:
        classe = SessionManager.get_financial_class(score_global)
        st.metric("Classe BCEAO", classe)
    
    with col3:
        secteur = metadata.get('secteur', 'Non spécifié').replace('_', ' ').title()
        st.metric("Secteur", secteur)
    
    with col4:
        ca = data.get('chiffre_affaires', 0)
        st.metric("CA (FCFA)", f"{ca:,.0f}")

def generate_executive_summary_pdf(data, ratios, scores, metadata):
    """Génère la synthèse exécutive en PDF"""
    
    try:
        with st.spinner("📄 Génération de la synthèse PDF..."):
            
            # Créer un buffer en mémoire
            buffer = io.BytesIO()
            
            # Créer le document PDF
            doc = SimpleDocTemplate(
                buffer,
                pagesize=A4,
                rightMargin=2*cm,
                leftMargin=2*cm,
                topMargin=2*cm,
                bottomMargin=2*cm
            )
            
            # Styles
            styles = getSampleStyleSheet()
            title_style = ParagraphStyle(
                'CustomTitle',
                parent=styles['Heading1'],
                fontSize=20,
                spaceAfter=30,
                alignment=1,  # Centré
                textColor=colors.HexColor('#1f4e79')
            )
            
            heading_style = ParagraphStyle(
                'CustomHeading',
                parent=styles['Heading2'],
                fontSize=14,
                spaceAfter=12,
                textColor=colors.HexColor('#2c5aa0')
            )
            
            # Contenu du document
            story = []
            
            # Titre
            story.append(Paragraph("SYNTHÈSE EXÉCUTIVE", title_style))
            story.append(Paragraph("Analyse Financière selon les Normes BCEAO", styles['Normal']))
            story.append(Spacer(1, 20))
            
            # Informations générales
            info_data = [
                ['Entreprise', metadata.get('fichier_nom', 'Non spécifié')],
                ['Date d\'analyse', metadata.get('date_analyse', datetime.now().strftime('%d/%m/%Y'))],
                ['Secteur d\'activité', metadata.get('secteur', 'Non spécifié').replace('_', ' ').title()],
                ['Source des données', metadata.get('source', 'Import').replace('_', ' ').title()]
            ]
            
            info_table = Table(info_data, colWidths=[4*cm, 10*cm])
            info_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#f1f1f1')),
                ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
                ('FONTSIZE', (0, 0), (-1, -1), 10),
                ('GRID', (0, 0), (-1, -1), 1, colors.black)
            ]))
            
            story.append(info_table)
            story.append(Spacer(1, 20))
            
            # Score global
            score_global = scores.get('global', 0)
            interpretation, _ = SessionManager.get_interpretation(score_global)
            classe = SessionManager.get_financial_class(score_global)
            
            story.append(Paragraph("SCORE GLOBAL BCEAO", heading_style))
            
            score_data = [
                ['Score Global', f'{score_global}/100'],
                ['Classe', classe],
                ['Interprétation', interpretation]
            ]
            
            score_table = Table(score_data, colWidths=[6*cm, 8*cm])
            score_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#e8f4fd')),
                ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, -1), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, -1), 12),
                ('GRID', (0, 0), (-1, -1), 1, colors.black)
            ]))
            
            story.append(score_table)
            story.append(Spacer(1, 20))
            
            # Performance par catégorie
            story.append(Paragraph("PERFORMANCE PAR CATÉGORIE", heading_style))
            
            categories_data = [
                ['Catégorie', 'Score', 'Maximum', 'Performance'],
                ['Liquidité', f"{scores.get('liquidite', 0)}", '40', f"{(scores.get('liquidite', 0)/40)*100:.0f}%"],
                ['Solvabilité', f"{scores.get('solvabilite', 0)}", '40', f"{(scores.get('solvabilite', 0)/40)*100:.0f}%"],
                ['Rentabilité', f"{scores.get('rentabilite', 0)}", '30', f"{(scores.get('rentabilite', 0)/30)*100:.0f}%"],
                ['Activité', f"{scores.get('activite', 0)}", '15', f"{(scores.get('activite', 0)/15)*100:.0f}%"],
                ['Gestion', f"{scores.get('gestion', 0)}", '15', f"{(scores.get('gestion', 0)/15)*100:.0f}%"]
            ]
            
            categories_table = Table(categories_data, colWidths=[4*cm, 2*cm, 2*cm, 3*cm])
            categories_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2c5aa0')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
                ('FONTSIZE', (0, 0), (-1, -1), 10),
                ('GRID', (0, 0), (-1, -1), 1, colors.black)
            ]))
            
            story.append(categories_table)
            story.append(Spacer(1, 20))
            
            # Indicateurs financiers clés
            story.append(Paragraph("INDICATEURS FINANCIERS CLÉS", heading_style))
            
            financial_data = [
                ['Indicateur', 'Montant (FCFA)'],
                ['Chiffre d\'Affaires', f"{data.get('chiffre_affaires', 0):,.0f}"],
                ['Total Actif', f"{data.get('total_actif', 0):,.0f}"],
                ['Résultat Net', f"{data.get('resultat_net', 0):,.0f}"],
                ['Capitaux Propres', f"{data.get('capitaux_propres', 0):,.0f}"]
            ]
            
            financial_table = Table(financial_data, colWidths=[6*cm, 8*cm])
            financial_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2c5aa0')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
                ('FONTSIZE', (0, 0), (-1, -1), 10),
                ('GRID', (0, 0), (-1, -1), 1, colors.black)
            ]))
            
            story.append(financial_table)
            story.append(Spacer(1, 20))
            
            # Ratios clés
            story.append(Paragraph("RATIOS CLÉS", heading_style))
            
            key_ratios_data = [
                ['Ratio', 'Valeur', 'Norme BCEAO', 'Statut'],
                ['Liquidité Générale', f"{ratios.get('ratio_liquidite_generale', 0):.2f}", '> 1.5', 
                 '✓ Conforme' if ratios.get('ratio_liquidite_generale', 0) >= 1.5 else '✗ Non conforme'],
                ['Autonomie Financière', f"{ratios.get('ratio_autonomie_financiere', 0):.1f}%", '> 30%',
                 '✓ Conforme' if ratios.get('ratio_autonomie_financiere', 0) >= 30 else '✗ Non conforme'],
                ['ROE', f"{ratios.get('roe', 0):.1f}%", '> 10%',
                 '✓ Conforme' if ratios.get('roe', 0) >= 10 else '✗ Non conforme'],
                ['Marge Nette', f"{ratios.get('marge_nette', 0):.1f}%", '> 5%',
                 '✓ Conforme' if ratios.get('marge_nette', 0) >= 5 else '✗ Non conforme']
            ]
            
            ratios_table = Table(key_ratios_data, colWidths=[4*cm, 3*cm, 3*cm, 4*cm])
            ratios_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2c5aa0')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
                ('FONTSIZE', (0, 0), (-1, -1), 9),
                ('GRID', (0, 0), (-1, -1), 1, colors.black)
            ]))
            
            story.append(ratios_table)
            story.append(Spacer(1, 20))
            
            # Points forts et faiblesses
            story.append(Paragraph("POINTS FORTS ET FAIBLESSES", heading_style))
            
            strengths = identify_strengths_pdf(scores, ratios)
            weaknesses = identify_weaknesses_pdf(scores, ratios)
            
            points_data = [['Points Forts', 'Points Faibles']]
            max_items = max(len(strengths), len(weaknesses))
            
            for i in range(max_items):
                strength = strengths[i] if i < len(strengths) else ""
                weakness = weaknesses[i] if i < len(weaknesses) else ""
                points_data.append([f"• {strength}" if strength else "", f"• {weakness}" if weakness else ""])
            
            points_table = Table(points_data, colWidths=[7*cm, 7*cm])
            points_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2c5aa0')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
                ('FONTSIZE', (0, 0), (-1, -1), 9),
                ('GRID', (0, 0), (-1, -1), 1, colors.black)
            ]))
            
            story.append(points_table)
            story.append(Spacer(1, 20))
            
            # Recommandations prioritaires
            story.append(Paragraph("RECOMMANDATIONS PRIORITAIRES", heading_style))
            
            recommendations = generate_priority_recommendations_pdf(scores, ratios)
            
            if recommendations:
                rec_data = [['Priorité', 'Recommandation']]
                for i, rec in enumerate(recommendations, 1):
                    rec_data.append([f"{i}.", rec])
                
                rec_table = Table(rec_data, colWidths=[1*cm, 13*cm])
                rec_table.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2c5aa0')),
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                    ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                    ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                    ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
                    ('FONTSIZE', (0, 0), (-1, -1), 9),
                    ('GRID', (0, 0), (-1, -1), 1, colors.black)
                ]))
                
                story.append(rec_table)
            else:
                story.append(Paragraph("✓ Situation financière satisfaisante. Maintenir les bonnes pratiques.", styles['Normal']))
            
            story.append(Spacer(1, 20))
            
            # Conclusion
            story.append(Paragraph("CONCLUSION", heading_style))
            
            if score_global >= 70:
                conclusion_text = "La situation financière de l'entreprise est satisfaisante selon les normes BCEAO. Les indicateurs montrent une bonne maîtrise de la gestion financière."
            elif score_global >= 40:
                conclusion_text = "La situation financière présente quelques faiblesses qui nécessitent une attention particulière. Des améliorations ciblées permettront de renforcer la position financière."
            else:
                conclusion_text = "La situation financière nécessite des actions correctives urgentes. Un plan de redressement doit être mis en place rapidement."
            
            story.append(Paragraph(conclusion_text, styles['Normal']))
            story.append(Spacer(1, 20))
            
            # Pied de page
            story.append(Paragraph(f"Rapport généré le {datetime.now().strftime('%d/%m/%Y à %H:%M')} - Outil d'Analyse Financière BCEAO", 
                                 ParagraphStyle('Footer', parent=styles['Normal'], fontSize=8, textColor=colors.grey)))
            
            # Construire le PDF
            doc.build(story)
            
            # Préparer le téléchargement
            buffer.seek(0)
            
            st.download_button(
                label="📥 Télécharger Synthèse PDF",
                data=buffer.read(),
                file_name=f"synthese_executive_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf",
                mime="application/pdf",
                type="primary"
            )
            
            st.success("✅ Synthèse PDF générée avec succès!")
            
    except Exception as e:
        st.error(f"❌ Erreur lors de la génération du PDF: {str(e)}")
        st.info("💡 Assurez-vous que la bibliothèque reportlab est installée: pip install reportlab")

def generate_detailed_report_pdf(data, ratios, scores, metadata):
    """Génère le rapport détaillé en PDF"""
    
    try:
        with st.spinner("📄 Génération du rapport détaillé PDF..."):
            
            buffer = io.BytesIO()
            doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=2*cm, leftMargin=2*cm, topMargin=2*cm, bottomMargin=2*cm)
            
            styles = getSampleStyleSheet()
            title_style = ParagraphStyle('CustomTitle', parent=styles['Heading1'], fontSize=18, spaceAfter=30, alignment=1, textColor=colors.HexColor('#1f4e79'))
            heading_style = ParagraphStyle('CustomHeading', parent=styles['Heading2'], fontSize=14, spaceAfter=12, textColor=colors.HexColor('#2c5aa0'))
            
            story = []
            
            # Page de titre
            story.append(Paragraph("RAPPORT D'ANALYSE FINANCIÈRE DÉTAILLÉ", title_style))
            story.append(Paragraph("Conforme aux Normes BCEAO", styles['Normal']))
            story.append(Spacer(1, 40))
            
            # Table des matières
            story.append(Paragraph("TABLE DES MATIÈRES", heading_style))
            toc_items = [
                "1. Résumé Exécutif",
                "2. Analyse du Bilan", 
                "3. Analyse du Compte de Résultat",
                "4. Analyse Détaillée des Ratios",
                "5. Comparaison Sectorielle",
                "6. Recommandations et Plan d'Action",
                "7. Conclusion"
            ]
            
            for item in toc_items:
                story.append(Paragraph(item, styles['Normal']))
            
            story.append(PageBreak())
            
            # 1. Résumé Exécutif
            story.append(Paragraph("1. RÉSUMÉ EXÉCUTIF", heading_style))
            
            score_global = scores.get('global', 0)
            interpretation, _ = SessionManager.get_interpretation(score_global)
            
            story.append(Paragraph(f"""
            L'analyse financière réalisée selon les normes BCEAO révèle un score global de {score_global}/100, 
            classant l'entreprise avec une évaluation "{interpretation.lower()}".
            """, styles['Normal']))
            
            story.append(Spacer(1, 20))
            
            # 2. Analyse du Bilan
            story.append(Paragraph("2. ANALYSE DU BILAN", heading_style))
            
            # Structure de l'actif
            story.append(Paragraph("2.1 Structure de l'Actif", styles['Heading3']))
            
            total_actif = data.get('total_actif', 1)
            actif_data = [
                ['Poste', 'Montant (FCFA)', '% du Total'],
                ['Immobilisations nettes', f"{data.get('immobilisations_nettes', 0):,.0f}", f"{(data.get('immobilisations_nettes', 0)/total_actif)*100:.1f}%"],
                ['Actif circulant', f"{data.get('total_actif_circulant', 0):,.0f}", f"{(data.get('total_actif_circulant', 0)/total_actif)*100:.1f}%"],
                ['Trésorerie', f"{data.get('tresorerie', 0):,.0f}", f"{(data.get('tresorerie', 0)/total_actif)*100:.1f}%"],
                ['TOTAL ACTIF', f"{total_actif:,.0f}", "100.0%"]
            ]
            
            actif_table = Table(actif_data, colWidths=[5*cm, 4*cm, 3*cm])
            actif_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2c5aa0')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
                ('FONTSIZE', (0, 0), (-1, -1), 9),
                ('GRID', (0, 0), (-1, -1), 1, colors.black)
            ]))
            
            story.append(actif_table)
            story.append(Spacer(1, 20))
            
            # 3. Analyse des Ratios Détaillée
            story.append(Paragraph("4. ANALYSE DÉTAILLÉE DES RATIOS", heading_style))
            
            # Ratios de liquidité
            story.append(Paragraph("4.1 Ratios de Liquidité", styles['Heading3']))
            
            liquidite_data = [
                ['Ratio', 'Valeur', 'Norme', 'Interprétation'],
                ['Liquidité Générale', f"{ratios.get('ratio_liquidite_generale', 0):.2f}", '> 1.5', get_ratio_interpretation('liquidite_generale', ratios.get('ratio_liquidite_generale', 0))],
                ['Liquidité Immédiate', f"{ratios.get('ratio_liquidite_immediate', 0):.2f}", '> 1.0', get_ratio_interpretation('liquidite_immediate', ratios.get('ratio_liquidite_immediate', 0))],
                ['BFR en jours de CA', f"{ratios.get('bfr_jours_ca', 0):.0f}", '< 60 jours', get_ratio_interpretation('bfr_jours', ratios.get('bfr_jours_ca', 0))]
            ]
            
            liquidite_table = Table(liquidite_data, colWidths=[4*cm, 2*cm, 2*cm, 4*cm])
            liquidite_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#e8f4fd')),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
                ('FONTSIZE', (0, 0), (-1, -1), 8),
                ('GRID', (0, 0), (-1, -1), 1, colors.black)
            ]))
            
            story.append(liquidite_table)
            story.append(Spacer(1, 20))
            
            # Recommandations
            story.append(Paragraph("6. RECOMMANDATIONS ET PLAN D'ACTION", heading_style))
            
            recommendations = generate_detailed_recommendations_pdf(scores, ratios)
            
            for priority, recs in recommendations.items():
                if recs:
                    story.append(Paragraph(f"6.{list(recommendations.keys()).index(priority)+1} {priority}", styles['Heading3']))
                    for i, rec in enumerate(recs, 1):
                        story.append(Paragraph(f"{i}. {rec}", styles['Normal']))
                    story.append(Spacer(1, 10))
            
            # Conclusion
            story.append(Paragraph("7. CONCLUSION", heading_style))
            
            if score_global >= 70:
                conclusion = "L'entreprise présente une situation financière satisfaisante selon les critères BCEAO. Les indicateurs révèlent une gestion maîtrisée et des perspectives favorables."
            elif score_global >= 40:
                conclusion = "L'entreprise présente une situation financière acceptable mais avec des faiblesses qui nécessitent une attention soutenue."
            else:
                conclusion = "L'entreprise fait face à des difficultés financières importantes qui nécessitent des actions correctives urgentes."
            
            story.append(Paragraph(conclusion, styles['Normal']))
            story.append(Spacer(1, 20))
            
            # Pied de page
            story.append(Paragraph(f"Rapport généré le {datetime.now().strftime('%d/%m/%Y à %H:%M')} - Outil d'Analyse Financière BCEAO", 
                                 ParagraphStyle('Footer', parent=styles['Normal'], fontSize=8, textColor=colors.grey)))
            
            doc.build(story)
            buffer.seek(0)
            
            st.download_button(
                label="📥 Télécharger Rapport Détaillé PDF",
                data=buffer.read(),
                file_name=f"rapport_detaille_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf",
                mime="application/pdf",
                type="primary"
            )
            
            st.success("✅ Rapport détaillé PDF généré avec succès!")
            
    except Exception as e:
        st.error(f"❌ Erreur lors de la génération du PDF: {str(e)}")

def download_excel_ratios(ratios, scores):
    """Télécharge les ratios en format Excel"""
    
    # Créer un DataFrame avec les ratios
    ratios_data = []
    
    for key, value in ratios.items():
        ratio_name = key.replace('_', ' ').title()
        category = get_ratio_category(key)
        
        if isinstance(value, (int, float)):
            ratios_data.append([category, ratio_name, f"{value:.4f}", get_ratio_unit(key)])
        else:
            ratios_data.append([category, ratio_name, str(value), get_ratio_unit(key)])
    
    df_ratios = pd.DataFrame(ratios_data, columns=["Catégorie", "Ratio", "Valeur", "Unité"])
    
    # Convertir en Excel
    excel_buffer = io.BytesIO()
    with pd.ExcelWriter(excel_buffer, engine='xlsxwriter') as writer:
        df_ratios.to_excel(writer, sheet_name='Ratios', index=False)
        
        # Ajouter les scores
        scores_data = []
        for key, value in scores.items():
            scores_data.append([key.title(), value])
        
        df_scores = pd.DataFrame(scores_data, columns=["Catégorie", "Score"])
        df_scores.to_excel(writer, sheet_name='Scores', index=False)
    
    excel_buffer.seek(0)
    
    st.download_button(
        label="📥 Télécharger Excel",
        data=excel_buffer.read(),
        file_name=f"ratios_financiers_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )

def download_csv_data(ratios, scores):
    """Télécharge les données en CSV"""
    
    # Créer les données CSV
    csv_data = []
    
    # Ajouter les ratios
    for key, value in ratios.items():
        ratio_name = key.replace('_', ' ').title()
        category = get_ratio_category(key)
        
        if isinstance(value, (int, float)):
            csv_data.append([category, ratio_name, f"{value:.4f}", get_ratio_unit(key)])
        else:
            csv_data.append([category, ratio_name, str(value), get_ratio_unit(key)])
    
    # Ajouter les scores
    for key, value in scores.items():
        csv_data.append(['Score', key.title(), str(value), 'points'])
    
    df = pd.DataFrame(csv_data, columns=["Catégorie", "Indicateur", "Valeur", "Unité"])
    csv_string = df.to_csv(index=False, encoding='utf-8')
    
    st.download_button(
        label="📥 Télécharger CSV",
        data=csv_string,
        file_name=f"donnees_financieres_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
        mime="text/csv"
    )

# Fonctions utilitaires pour les PDFs

def identify_strengths_pdf(scores, ratios):
    """Identifie les points forts pour le PDF"""
    strengths = []
    
    if scores.get('liquidite', 0) >= 30:
        strengths.append("Excellente liquidité")
    if scores.get('solvabilite', 0) >= 30:
        strengths.append("Structure financière solide")
    if scores.get('rentabilite', 0) >= 20:
        strengths.append("Rentabilité satisfaisante")
    if ratios.get('roe', 0) >= 15:
        strengths.append("Excellente rentabilité des capitaux propres")
    if ratios.get('ratio_autonomie_financiere', 0) >= 40:
        strengths.append("Forte autonomie financière")
    
    return strengths[:5]

def identify_weaknesses_pdf(scores, ratios):
    """Identifie les points faibles pour le PDF"""
    weaknesses = []
    
    if scores.get('liquidite', 0) < 20:
        weaknesses.append("Liquidité insuffisante")
    if scores.get('solvabilite', 0) < 20:
        weaknesses.append("Structure financière fragile")
    if scores.get('rentabilite', 0) < 15:
        weaknesses.append("Rentabilité faible")
    if ratios.get('ratio_liquidite_generale', 0) < 1.2:
        weaknesses.append("Ratio de liquidité critique")
    if ratios.get('marge_nette', 0) < 3:
        weaknesses.append("Marge nette insuffisante")
    
    return weaknesses[:5]

def generate_priority_recommendations_pdf(scores, ratios):
    """Génère des recommandations prioritaires pour le PDF"""
    recommendations = []
    
    if scores.get('liquidite', 0) < 25:
        recommendations.append("Améliorer la liquidité immédiatement")
    if scores.get('solvabilite', 0) < 25:
        recommendations.append("Renforcer la structure financière")
    if scores.get('rentabilite', 0) < 15:
        recommendations.append("Optimiser la rentabilité opérationnelle")
    
    return recommendations[:3]

def generate_detailed_recommendations_pdf(scores, ratios):
    """Génère des recommandations détaillées par priorité"""
    recommendations = {
        "Actions Urgentes (0-1 mois)": [],
        "Actions Importantes (1-3 mois)": [],
        "Actions Moyen Terme (3-6 mois)": []
    }
    
    if scores.get('liquidite', 0) < 25:
        recommendations["Actions Urgentes (0-1 mois)"].append("Négocier des délais de paiement avec les fournisseurs")
        recommendations["Actions Urgentes (0-1 mois)"].append("Accélérer le recouvrement des créances clients")
    
    if scores.get('solvabilite', 0) < 25:
        recommendations["Actions Importantes (1-3 mois)"].append("Préparer une augmentation de capital")
        recommendations["Actions Importantes (1-3 mois)"].append("Renégocier les dettes financières")
    
    if scores.get('rentabilite', 0) < 15:
        recommendations["Actions Moyen Terme (3-6 mois)"].append("Analyser et optimiser la structure des coûts")
        recommendations["Actions Moyen Terme (3-6 mois)"].append("Améliorer les marges commerciales")
    
    return recommendations

def get_ratio_category(ratio_key):
    """Retourne la catégorie d'un ratio"""
    if any(x in ratio_key for x in ['liquidite', 'bfr', 'tresorerie']):
        return 'Liquidité'
    elif any(x in ratio_key for x in ['autonomie', 'endettement', 'solvabilite']):
        return 'Solvabilité'
    elif any(x in ratio_key for x in ['roe', 'roa', 'marge', 'rentabilite']):
        return 'Rentabilité'
    elif any(x in ratio_key for x in ['rotation', 'delai']):
        return 'Activité'
    else:
        return 'Gestion'

def get_ratio_unit(ratio_key):
    """Retourne l'unité d'un ratio"""
    if any(x in ratio_key for x in ['marge', 'autonomie', 'endettement', 'roe', 'roa']):
        return '%'
    elif any(x in ratio_key for x in ['jours', 'delai']):
        return 'jours'
    elif 'rotation' in ratio_key:
        return 'fois'
    else:
        return 'ratio'

def get_ratio_interpretation(ratio_type, value):
    """Retourne l'interprétation d'un ratio"""
    if ratio_type == 'liquidite_generale':
        if value >= 2.0:
            return "Excellent"
        elif value >= 1.5:
            return "Bon"
        elif value >= 1.0:
            return "Acceptable"
        else:
            return "Critique"
    elif ratio_type == 'liquidite_immediate':
        if value >= 1.0:
            return "Bon"
        elif value >= 0.8:
            return "Acceptable"
        else:
            return "Faible"
    elif ratio_type == 'bfr_jours':
        if value <= 30:
            return "Excellent"
        elif value <= 60:
            return "Bon"
        elif value <= 90:
            return "Acceptable"
        else:
            return "Critique"
    else:
        return "À analyser"