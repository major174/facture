import streamlit as st
import pandas as pd
from io import BytesIO
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.platypus import Table, TableStyle
import base64
import locale
import re
from datetime import datetime

locale.setlocale(locale.LC_ALL, '')

if 'data_list' not in st.session_state:
    st.session_state.data_list = []

if 'row_to_edit' not in st.session_state:
    st.session_state.row_to_edit = None

if 'pdf_history' not in st.session_state:
    st.session_state.pdf_history = []

if 'invoice_counter' not in st.session_state:
    st.session_state.invoice_counter = 1

st.title("Facture des clients ")

nom_client = st.text_input("Client")
adresse = st.text_input("Adresse")
col1, col2, col3, col4 = st.columns(4)

current_date = datetime.now().strftime("%d-%m-%Y")

with col1:
    designation = st.text_input("Désignation",key="text")

with col2:
    quantite_vendue_text = st.text_input("Quantité Vendue",key="vend")

with col3:
    prix_vente_unitaires = st.text_input("Prix de Vente Unitaire",key="unit")
    prix_vente_unitaire = int(prix_vente_unitaires) if prix_vente_unitaires else 0

with col4:
    quantite_match = re.match(r'\d+', quantite_vendue_text)
    quantite_vendue = int(quantite_match.group()) if quantite_match else 0
    quantite_vendue = int(quantite_vendue) if quantite_vendue else 0
    prix_vente_total = quantite_vendue * prix_vente_unitaire
df_updated = pd.DataFrame(st.session_state.data_list)
def clear_text():
    st.session_state["text"] = ""
    st.session_state["vend"] = ""
    st.session_state["unit"] = ""
add_button_column, button_column = st.columns(2)

       
with add_button_column:
    if st.button("Ajouter"):
        if len(df_updated) == 30:
            st.warning("Veuillez enregistrer cette facture car vous avez atteint la limite. Une fois qu'on appuie sur le bouton 'Ajouter', il n'ajoute plus de données.")
        elif designation and quantite_vendue is not None and prix_vente_unitaire is not None:
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
if st.button("Effacers le tableau "):
        st.session_state.data_list = []  # Efface la liste des données
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

if st.button("Télécharger en PDF"):
    pdf_bytes = BytesIO()
    c = canvas.Canvas(pdf_bytes, pagesize=letter)

    c.setFont("Helvetica-Bold", 16)
    c.drawString(30, 750, "Facture")
    c.line(30, 740, 550, 740)

    client_info_y = 720
    c.setFont("Helvetica", 12)
    c.drawString(30, client_info_y, f"Nom du Client: {nom_client}")
    c.drawString(30, client_info_y - 15, "Date: " + current_date)
    c.drawString(30, client_info_y - 30, "Adresse:" + adresse)
    c.line(30, client_info_y - 40, 550, client_info_y - 40)
    
    if len(df_updated) <=20:
        table_offset = 40
    else :
        table_offset = 200
           
    
    table_start_y = client_info_y - 40 - table_offset

    max_table_height = 400

    # Calculer la hauteur totale du tableau
    total_table_height = len(df_updated) * 20

    # Si la hauteur totale du tableau est inférieure à la hauteur maximale autorisée, ajuster la position du tableau vers le bas
    if total_table_height < max_table_height:
        table_start_y = client_info_y - 40 - total_table_height + table_offset

    table_data = [list(df_updated.columns)] + df_updated.values.tolist()
    col_max_widths = [150, 100, 100, 150]

    for i in range(1, len(table_data)):
        for j in range(1, len(table_data[i])):
            table_data[i][j] = str(table_data[i][j])

    col_widths = [min(col_max_widths[i], max([len(str(row[i])) for row in table_data]) * 12) for i in range(len(df_updated.columns))]
    table_height = min(len(df_updated) * 20, max_table_height)

    table = Table(table_data, colWidths=col_widths)
    table.setStyle(TableStyle([('GRID', (0, 0), (-1, -1), 1, (0, 0, 0))]))

    table.wrapOn(c, 0, 0)
    table.drawOn(c, 30, table_start_y - table_height)

    c.setFont("Helvetica-Bold", 12)
    sum_prix_vente_total = df_updated["Prix de Vente Total"].replace({' ': '', '\xa0': ''}, regex=True).apply(pd.to_numeric, errors='coerce').sum()
    formatted_sum = locale.format_string("%d", sum_prix_vente_total, grouping=True)
    c.drawString(400, table_start_y - table_height - 30, f"Montant total : {formatted_sum}")

    invoice_number = st.session_state.invoice_counter
    st.session_state.invoice_counter += 1
    pdf_filename = f"tableau_facture_{invoice_number}.pdf"
    c.save()

    pdf_info = {"Numéro de Facture": invoice_number, "Nom du fichier": pdf_filename, "Date de création": datetime.now().strftime("%d-%m-%Y %H:%M:%S")}
    st.session_state.pdf_history.append(pdf_info)

    pdf_bytes.seek(0)
    b64_pdf = base64.b64encode(pdf_bytes.read()).decode()

    st.markdown(f'<a href="data:application/pdf;base64,{b64_pdf}" download="{pdf_filename}">Télécharger le PDF (Facture {invoice_number})</a>', unsafe_allow_html=True)
