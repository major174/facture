import streamlit as st
import pandas as pd
from io import BytesIO
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
import base64
import locale
import re
from datetime import datetime
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image, HRFlowable

locale.setlocale(locale.LC_ALL, '')

if 'data_list' not in st.session_state:
    st.session_state.data_list = []

if 'row_to_edit' not in st.session_state:
    st.session_state.row_to_edit = None

if 'pdf_history' not in st.session_state:
    st.session_state.pdf_history = []

if 'invoice_counter' not in st.session_state:
    st.session_state.invoice_counter = 1

st.title("Facture des clients")

nom_client = st.text_input("Client")
adresse = st.text_input("Adresse")
col1, col2, col3, col4 = st.columns(4)

current_date = datetime.now().strftime("%d-%m-%Y")

with col1:
    designation = st.text_input("Désignation", key="text")

with col2:
    quantite_vendue_text = st.text_input("Quantité Vendue", key="vend")

with col3:
    prix_vente_unitaires = st.text_input("Prix de Vente Unitaire", key="unit")
    prix_vente_unitaire = int(prix_vente_unitaires) if prix_vente_unitaires else 0

with col4:
    quantite_match = re.match(r'\d+', quantite_vendue_text)
    quantite_vendue = int(quantite_match.group()) if quantite_match else 0
    prix_vente_total = quantite_vendue * prix_vente_unitaire

df_updated = pd.DataFrame(st.session_state.data_list)

def clear_text():
    st.session_state["text"] = ""
    st.session_state["vend"] = ""
    st.session_state["unit"] = ""

add_button_column, button_column = st.columns(2)

with add_button_column:
    if st.button("Ajouter"):
        if designation and quantite_vendue is not None and prix_vente_unitaire is not None:
            st.session_state.data_list.append({
                "DESIGNATION": designation,
                "QUANTITE VENDUE": quantite_vendue_text,
                "Prix de Vente Unitaire": prix_vente_unitaire,
                "Prix de Vente Total": prix_vente_total
            })
            df_updated = pd.DataFrame(st.session_state.data_list)

with button_column:
    st.button("Effacer", on_click=clear_text)

st.write("Facture", df_updated)

if st.button("Effacer le tableau"):
    st.session_state.data_list = []
    st.session_state.row_to_edit = None

st.header("Modifier la facture")

row_indices = [i for i in range(len(st.session_state.data_list))]
selected_row = st.selectbox("Sélectionner une ligne à modifier :", row_indices)

if selected_row is not None:
    st.session_state.row_to_edit = selected_row
    new_designation = st.text_input("Nouvelle Désignation", value=st.session_state.data_list[selected_row]["DESIGNATION"])
    new_quantite_vendues = st.text_input("Nouvelle Quantité Vendue", value=str(st.session_state.data_list[selected_row]["QUANTITE VENDUE"]))
    new_prix_vente_unitaire_text = st.text_input("Nouveau Prix de Vente Unitaire", value=str(st.session_state.data_list[selected_row]["Prix de Vente Unitaire"]))
    new_prix_vente_unitaire_text = new_prix_vente_unitaire_text.replace('\xa0', '')
    new_prix_vente_unitaire = int(new_prix_vente_unitaire_text) if new_prix_vente_unitaire_text else 0

if st.button("Appliquer modifications"):
    if st.session_state.row_to_edit is not None:
        quantite = re.match(r'\d+', new_quantite_vendues)
        new_quantite_vendue = int(quantite.group()) if quantite else 0
        new_prix_vente_total = new_quantite_vendue * new_prix_vente_unitaire

        st.session_state.data_list[st.session_state.row_to_edit]["DESIGNATION"] = new_designation
        st.session_state.data_list[st.session_state.row_to_edit]["QUANTITE VENDUE"] = new_quantite_vendues 
        st.session_state.data_list[st.session_state.row_to_edit]["Prix de Vente Unitaire"] = locale.format_string("%d", new_prix_vente_unitaire, grouping=True)
        st.session_state.data_list[st.session_state.row_to_edit]["Prix de Vente Total"] = locale.format_string("%d", new_prix_vente_total, grouping=True)

        st.session_state.row_to_edit = None

import random
from reportlab.lib.utils import ImageReader
from reportlab.platypus import Image

def generate_pdf(pdf_bytes, data, nom_client, adresse, current_date):
    doc = SimpleDocTemplate(pdf_bytes, pagesize=letter, topMargin=0.5*inch)
    story = []

    styles = getSampleStyleSheet()
    normal_style = ParagraphStyle(
        'Normal',
        fontSize=12,
        alignment=1,  # 1 pour centré
    )
    company_style = ParagraphStyle(
        'Company',
        fontSize=24,
        alignment=1,
        fontName='Helvetica-Bold',
    )
    title_style = ParagraphStyle(
        'Title',
        fontSize=16,
        alignment=0,  # 0 pour aligné à gauche
        spaceAfter=12,
        fontName='Helvetica-Bold',
    )

    # Nom de l'entreprise en haut
    story.append(Paragraph("ETS KIEMDE PINGDBA JULES (KPJ)", company_style))
    story.append(Spacer(1, 0.1*inch))

    # Logo en dessous du nom de l'entreprise
    try:
        logo = Image("logo.png", width=2*inch, height=2*inch)
        story.append(logo)
    except:
        story.append(Paragraph("Logo non trouvé", normal_style))

    # Informations de l'entreprise (centrées)
    story.append(Paragraph("Vente de pièces détachées de toute marque", normal_style))
    story.append(Paragraph("Au marché de théâtre populaire", normal_style))
    story.append(Paragraph("Tel : 78-66-32 32 / 70 33 80 59", normal_style))
    story.append(Paragraph("WhatsApp : 75 29 19 79", normal_style))
    
    # Trait horizontal
    story.append(Spacer(1, 0.25*inch))
    story.append(HRFlowable(width="100%", thickness=1, color=colors.black))
    story.append(Spacer(1, 0.25*inch))

    # Générer un numéro de facture aléatoire
    invoice_number = f"FACT-{random.randint(10000, 99999)}"

    # Titre "Facture" et numéro de facture
    story.append(Paragraph(f"Facture N° {invoice_number}", title_style))
    story.append(Spacer(1, 0.1*inch))

    # Informations du client (alignées à gauche)
    client_style = ParagraphStyle(
        'Client',
        fontSize=12,
        alignment=0,  # 0 pour aligné à gauche
    )
    story.append(Paragraph(f"Nom du Client: {nom_client}", client_style))
    story.append(Paragraph(f"Date: {current_date}", client_style))
    story.append(Paragraph(f"Adresse: {adresse}", client_style))
    story.append(Spacer(1, 0.25*inch))

    # Tableau
    table_data = [["DESIGNATION", "QUANTITE VENDUE", "Prix de Vente Unitaire", "Prix de Vente Total"]]
    for row in data.values.tolist():
        formatted_row = row[:2]  # Garder les deux premières colonnes telles quelles
        # Formater le Prix de Vente Unitaire
        prix_unitaire = float(str(row[2]).replace(' ', '').replace('\xa0', ''))
        formatted_row.append(f"{prix_unitaire:,.0f}".replace(',', ' '))
        # Formater le Prix de Vente Total
        total = float(str(row[3]).replace(' ', '').replace('\xa0', ''))
        formatted_row.append(f"{total:,.0f}".replace(',', ' '))
        table_data.append(formatted_row)

    table = Table(table_data)
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 12),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('TEXTCOLOR', (0, 1), (-1, -1), colors.black),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('TOPPADDING', (0, 1), (-1, -1), 6),
        ('BOTTOMPADDING', (0, 1), (-1, -1), 6),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ]))
    story.append(table)

    # Total
    total = sum(float(str(row[-1]).replace(' ', '').replace('\xa0', '')) for row in table_data[1:])
    story.append(Spacer(1, 0.25*inch))
    total_style = ParagraphStyle(
        'Total',
        fontSize=12,
        alignment=2,  # 2 pour aligné à droite
        fontName='Helvetica-Bold',
    )
    formatted_total = f"{total:,.0f}".replace(',', ' ')
    story.append(Paragraph(f"Montant total : {formatted_total}", total_style))

    doc.build(story)

if st.button("Télécharger en PDF"):
    pdf_bytes = BytesIO()
    generate_pdf(pdf_bytes, df_updated, nom_client, adresse, current_date)
    pdf_bytes.seek(0)

    invoice_number = st.session_state.invoice_counter
    st.session_state.invoice_counter += 1
    pdf_filename = f"tableau_facture_{invoice_number}.pdf"

    pdf_info = {"Numéro de Facture": invoice_number, "Nom du fichier": pdf_filename, "Date de création": datetime.now().strftime("%d-%m-%Y %H:%M:%S")}
    st.session_state.pdf_history.append(pdf_info)

    b64_pdf = base64.b64encode(pdf_bytes.read()).decode()

    st.markdown(f'<a href="data:application/pdf;base64,{b64_pdf}" download="{pdf_filename}">Télécharger le PDF (Facture {invoice_number})</a>', unsafe_allow_html=True)