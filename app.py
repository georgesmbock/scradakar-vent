# Importation de toutes les bibliothèques utiles
import numpy as np
import pandas as pd
import streamlit as st
import requests as rq
from bs4 import BeautifulSoup4 as bs 
import base64
import numpy as np
import os
import time
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px
import plotly.graph_objects as pxg

def main():
    # Configuration de la page streamlit
    st.set_page_config(page_title="SCRAPEUR")

#****************__Fonctions**__Intermédiaires__******************************
    def parsers(e):
        """"
        Cette fonction vérifie si un élément sélectionner dans soup exite puis
        affiche contenu comme text; On utilise cette appelle cette fonction
        dans la fonction simple_find crée en dessus.
    
        Args:
            e (une balise): _description_

        Returns:
            _type_: _description_
        """
        if e:
            return e.text
        return None

#-----------Statiisques----------------------------
    def stat(DF):
        col1, col2 = st.columns(2)
        df = pd.read_csv(DF)
        df.dropna(axis=0, inplace=True)
        st.write(df["prix"].describe())
        col1.write("### Histogramme des prix")
        hist = px.histogram(df['prix'], x='prix', nbins=25)
        col1.plotly_chart(hist)
        
        
    
    
# Fonction pour charger et afficher les données
    def load(dataframe, title, key, key1):
        st.markdown("""
            <style>
            div.stButton {text-align:center; margin-top: 1rem;}
            .dataframe {font-size: 16px; text-align: left;}
            .title {
                color: #3498db;
                text-align: center;
            }
            </style>
        """, unsafe_allow_html=True)
        st.write(f"<h2 class='title'>{title}</h2>", unsafe_allow_html=True)
        st.write(f"Dimensions des données : {dataframe.shape[0]} lignes et {dataframe.shape[1]} colonnes.")
        st.dataframe(dataframe, height=500)

    st.markdown("""
        <style>
        body {
            font-family: 'Arial', sans-serif;
            background-color: #f0f0f0;
        }
        h2 {
            #color: #3498db;
            #text-align: center;
        }
        
        .sidebar .sidebar-content {
            background-color: #2c3e50;
            color: white;
        }
        .sidebar .stSelectbox {
            #background-color: #3498db;
            #color: white;
        }
        .dataframe {
            background-color: #ffffff;
            border: 1px solid #d3d3d3;
            border-radius: 5px;
            box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
        }
        .title {
            color: #3498db;
            text-align: center;
        }
        </style>
    """, unsafe_allow_html=True)

    
    
    
    # ___Fonctions Scrap____________________________
    @st.cache_data
    def scrap_appart_louer(nb_pages):
        operating_progress = st.progress(0)
        
        pri = []
        detais = []
        details = []
        prices = []
        address = []
        img_link = []
        
        #category = ["-appartements-louer-10", "-appartements-vendre-61", "-terrains-vendre-13"]
        #for categorie in category:
        #url = f'https://dakarvente.com/annonces-categorie-terrains-vendre-13.html'
        for p in range(1, nb_pages + 1):
            #url = f'https://dakarvente.com/annonces-categorie-appartements-louer{-p}.html'
            url = f'https://dakarvente.com/index.php?page=annonces_categorie&id=10&sort=&nb={p}'
            answer = rq.get(url)
            answer.encoding = 'UTF-8'

            if answer.status_code == 200:
                container_html = answer.text
                soup = bs(container_html, 'html.parser')
                
                e_detais = soup.find_all('div', class_="content-desc")
                for e_detail in e_detais:
                    detais.append(parsers(e_detail).strip())
                    
                e_prix = soup.select(".content-price span")
                for price in e_prix:
                    if "FCFA" in parsers(price):
                        prices.append(parsers(price).replace("FCFA", "").strip().replace(' ', ''))
                    else:
                        address.append(price.text)
    
                address[20]="-"
                
                e_image = soup.select('h2 img')
                for image in e_image:
                    img_link.append(image['src'])
                    
                ecar1 = len(address) - len(prices)
                ecar2 = len(address) - len(img_link)
                ecar3 = len(address) - len(detais)
                
                if ecar1 > 0:
                    while ecar1 > 0:
                        prices.append(0)
                        ecar1 -= 1
                if ecar2 > 0:
                    while ecar2 > 0:  
                        img_link.append("-")
                        ecar2 -= 1
                if ecar3 > 0:
                    while ecar3 > 0:  
                        detais.append("-")
                        ecar3 -= 1
            else:
                print("ERROR !")
            
            time.sleep(3)
            print("Great Job !")
        operating_progress.progress(int((p / nb_pages) * 100))
    
        st.write("Start build trame.....") 
        operating_progress = st.progress(0)
        for nbre in prices:
            e = int(nbre)
            pri.append(e)
        obj = {
        "detail":detais,
        "prix": pri,
        "adresse": address,
        "image_lien": img_link
        }
        
        idx = [i for i in range(len(address))] 
       
        DF = pd.DataFrame(obj, columns=["detail", "prix", "adresse", "image_lien"], index=idx)
        time.sleep(8)
        operating_progress.progress(int((len(address) / len(DF) * 100)))
        st.write("Building of trame done.....")
        
        time.sleep(7)

        st.write("Launch the saving data on csv file.....")
    
        DF.to_csv("data-apparts-loues.csv", index_label=False)
        time.sleep(5)
        st.write("Data saved...")
        st.success("CONGRATULATIONS !")
        return DF
    data = "data_apparts_sales.csv"
    
        
    
#-----------****Fonction-----appartements à vendre---------------------
    def scrap_appart_vend(nb_pages):
        
        operating_progress = st.progress(0)
        
        pri = []
        detais = []
        details = []
        prices = []
        address = []
        img_link = []
        data = []

        
        for p in range(1, nb_pages + 1):
            url = f'https://dakarvente.com/index.php?page=annonces_categorie&id=61&sort=&nb={p}'
            answer = rq.get(url)
            answer.encoding = 'UTF-8'

            if answer.status_code == 200:
                container_html = answer.text
                soup = bs(container_html, 'html.parser')
                
                e_detais = soup.find_all('div', class_="content-desc")
                for e_detail in e_detais:
                    detais.append(parsers(e_detail).strip())
                    
                e_prix = soup.select(".content-price span")
                for price in e_prix:
                    if "FCFA" in parsers(price):
                        prices.append(parsers(price).replace("FCFA", "").strip().replace(' ', ''))
                    else:
                        address.append(price.text)
    
                e_image = soup.select('h2 img')
                for image in e_image:
                    img_link.append(image['src'])
                    
                ecar1 = len(address) - len(prices)
                ecar2 = len(address) - len(img_link)
                ecar3 = len(address) - len(detais)
                
                if ecar1 > 0:
                    while ecar1 > 0:
                        prices.append("0")
                        ecar1 -= 1
                if ecar2 > 0:
                    while ecar2 > 0:  
                        img_link.append("-")
                        ecar2 -= 1
                if ecar3 > 0:
                    while ecar3 > 0:  
                        detais.append("-")
                        ecar3 -= 1
            else:
                print("ERROR !")
            
            time.sleep(3)
            print("Great Job !")
        operating_progress.progress(int((p / nb_pages) * 100))
    
        st.write("Start build trame.....") 
        operating_progress = st.progress(0)
        
        for nbre in prices:
            e = int(nbre)
            pri.append(e)
        
        obj = {
        "detail":detais,
        "prix": pri,
        "adresse": address,
        "image_lien": img_link
        }
        
        idx = [i for i in range(len(address))] 
       
        DF = pd.DataFrame(obj, columns=["detail", "prix", "adresse", "image_lien"], index=idx)
        time.sleep(8)
        operating_progress.progress(int((len(address) / len(DF) * 100)))
        st.write("Building of trame done.....")
        
        time.sleep(7)

        st.write("Launch the saving data on csv file.....")
    
        DF.to_csv("data_apparts_sales.csv", index_label=False)
        time.sleep(5)
        st.write("Data saved...")
        st.success("CONGRATULATIONS !")
        return DF
    
#--------------VENTE-------TERRAIN-----------------------
    def scrap_terrain_vend(nb_pages):   
        operating_progress = st.progress(0)
        
        pri = []
        detais = []
        details = []
        prices = []
        address = []
        img_link = []
        for p in range(1, nb_pages + 1):
            url = f'https://dakarvente.com/index.php?page=annonces_categorie&id=13&sort=&nb={p}' 
            answer = rq.get(url)
            answer.encoding = 'UTF-8'

            if answer.status_code == 200:
                container_html = answer.text
                soup = bs(container_html, 'html.parser')
                
                e_detais = soup.find_all('div', class_="content-desc")
                for e_detail in e_detais:
                    detais.append(parsers(e_detail).strip())
                    
                e_prix = soup.select(".content-price span")
                for price in e_prix:
                    if "FCFA" in parsers(price):
                        prices.append(parsers(price).replace("FCFA", "").strip().replace(' ', ''))
                    else:
                        address.append(price.text)
    
                e_image = soup.select('h2 img')
                for image in e_image:
                    img_link.append(image['src'])
                    
                ecar1 = len(address) - len(prices)
                ecar2 = len(address) - len(img_link)
                ecar3 = len(address) - len(detais)
                
                if ecar1 > 0:
                    while ecar1 > 0:
                        prices.append(0)
                        ecar1 -= 1
                if ecar2 > 0:
                    while ecar2 > 0:  
                        img_link.append("-")
                        ecar2 -= 1
                if ecar3 > 0:
                    while ecar3 > 0:  
                        detais.append("-")
                        ecar3 -= 1
            else:
                print("ERROR !")
            
            time.sleep(3)
            print("Great Job !")
        operating_progress.progress(int((p / nb_pages) * 100))
    
        st.write("Start build trame.....") 
        operating_progress = st.progress(0)
        
        for nbre in prices:
            e = int(nbre)
            pri.append(e)
        obj = {
        "detail":detais,
        "prix": pri,
        "adresse": address,
        "image_lien": img_link
        }
        
        idx = [i for i in range(len(address))] 
       
        DF = pd.DataFrame(obj, columns=["detail", "prix", "adresse", "image_lien"], index=idx)
        time.sleep(8)
        operating_progress.progress(int((len(address) / len(DF) * 100)))
        st.write("Building of trame done.....")
        
        time.sleep(7)

        st.write("Launch the saving data on csv file.....")
    
        DF.to_csv("data_terrain_.csv", index_label=False)
        time.sleep(5)
        st.write("Data saved...")
        st.success("CONGRATULATIONS !")
        return DF

 # ---------------Application Streamlit------------------------------
    st.markdown("<h2 class='title'>SCRAPEUR DE DONNÉES DE L' IMMOBLIER DAKAR VENTE</h2>", unsafe_allow_html=True)
    st.markdown("<p>Cette application est encore à sa phase de devéloppement.</p>", unsafe_allow_html=True)
    st.sidebar.success("MENU")
    nb_pages_a_scrapper = st.sidebar.selectbox("Entrez le nombre de page à scraper :", list(range(1, 200)))
    options = ["Scraping avec BeautifulSoup", "Télécharger les données scrappées avec Web Scrapper", "Dash Bord","Remplir le formulaire"]
    selected_option = st.sidebar.selectbox("Sélectionnez une option",
                                        options,
                                        index=None,
                                        placeholder="CHOISISSEZ VOTRE OPTION",)
    st.sidebar.write("Option sélectionnée :", selected_option)
    # Charger les données
    if selected_option == "Scraping avec BeautifulSoup":
        st.markdown("""
            <style>
            div.stButton {text-align:center; margin-top: 1rem;}
            .dataframe {font-size: 16px; text-align: left;}
            </style>
        """, unsafe_allow_html=True)
        selected_category = st.radio("Choisir la catégorie à scraper :", ['Appartement à louer', 'Appartement à vendre', 'Terrain à vendre'])   
        if st.button('Scrapper les données'):
            if selected_category == 'Appartement à louer':
                data_scraped = scrap_appart_louer(nb_pages_a_scrapper)
                load(data_scraped, 'Données Scrappées Appartements à louer', '1', '2')
            elif selected_category == 'Appartement à vendre':
                data_scraped = scrap_appart_vend(nb_pages_a_scrapper)
                load(data_scraped, 'Appartement à vendre', '1', '101')   
            elif selected_category == 'Terrain à vendre':
                data_scraped = scrap_terrain_vend(nb_pages_a_scrapper)
                load(data_scraped, 'Terrain à vendre', '1', '101')
    elif selected_option == "Télécharger les données scrappées avec Web Scrapper":
        selected_category = st.radio("Choisissez une catégorie :", ['Appartement à louer', 'Appartement à vendre', 'Terrain à vendre'])
        if st.button('Télécharger les données scrappées avec Web Scrapper'):
            if selected_category == 'Appartement à louer':
                app_louer =pd.read_csv('./appartlouer.csv')
                del app_louer["web-scraper-order"]
                del app_louer["web-scraper-start-url"]
                st.dataframe(app_louer)
            elif selected_category == 'Appartement à vendre':
                app_louer =pd.read_csv('./appartsvente.csv')
                del app_louer["web-scraper-order"]
                del app_louer["web-scraper-start-url"]
                st.dataframe(app_louer)
            elif selected_category == 'Terrain à vendre':
                app_louer =pd.read_csv('./terrainvente.csv')
                del app_louer["web-scraper-order"]
                del app_louer["web-scraper-start-url"]
                del app_louer["image_lien-href"]
                st.dataframe(app_louer)
                
        
    elif  selected_option == "Dash Bord":
        selected_category = st.radio("Choisissez une catégorie :", ['Appartement à louer', 'Appartement à vendre', 'Terrain à vendre'])
        if st.button('Dash Bord'):
            if selected_category == 'Appartement à louer':
                data = 'data-apparts-loues.csv'
                stat(data)
            elif selected_category == 'Appartement à vendre':
                data = 'data_apparts_sales.csv'
                stat(data)
            elif selected_category == 'Terrain à vendre':
                data = 'data_terrain_.csv'
                stat(data)        
#-----------------Formulaire-------------------------------------            
    elif selected_option == "Remplir le formulaire" :
        st.components.v1.iframe(src='https://ee.kobotoolbox.org/i/LOxynrgZ',
                                width=800,
                                height=800)
    

if __name__=='__main__':
    main()