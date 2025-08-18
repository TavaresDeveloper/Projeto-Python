#importação das bibliotecas necessárias
from pymongo import MongoClient
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import os


#títutlo da aplicação

st.title("Desafio de Estágio")

#Importação do banco de dados baseado em mongoDB

Mongo_URI = "mongodb://localhost:27017/"




#importação do diretório contendo a base de dados com validação e otimização
@st.cache_data(show_spinner = "Carregando dados...")
def load_data():
    data_path = os.path.join(os.path.dirname(__file__), 'base de dados', 'dados_completos.parquet')

    if not os.path.exists(data_path):
        st.error("Nenhum arquivo encontrado no diretório 'base de dados'")
        st.stop()


    df = pd.read_parquet(data_path)


    return df

df = load_data()

# Título da barra de filtragem
st.sidebar.header('Filtrar')



listarEstados = sorted(df['state'].unique())
listarAnos = sorted(df['year'].unique())


#criação de labels interaitivos para o usuário

selecaoEstado = st.sidebar.selectbox( label= "Selecione o estado desejado", options=listarEstados)
listarCondados = sorted(df[df['state'] == selecaoEstado]['county'].unique())
selecaoCondado = st.sidebar.selectbox(label = "Selecione o condado desejado", options=listarCondados)
selecaoAno = st.sidebar.selectbox(label = "Selecione o ano desejado", options=listarAnos)





@st.cache_data

def filtrar_dados(df, selecaoEstado, selecaoCondado, selecaoAno):
        df_filtragem = df[
                 (df['state']==selecaoEstado) &
                 (df['county']==selecaoCondado) &
                 (df['year']==selecaoAno)
        ]
        return df_filtragem


df_filtragem = filtrar_dados(df, selecaoEstado, selecaoCondado, selecaoAno)

df_monthly = df_filtragem.groupby(['Year-Month']).agg({
    'cases': 'mean',
    'deaths': 'mean'

    }).reset_index()


#Geração dos gráficos
if not df_monthly.empty:
    deaths = go.Scatter(x = df_monthly['Year-Month'], y = df_monthly['deaths'],
                       name = 'Mortes', mode = 'lines', line=dict(color='blue'))

    cases = go.Bar(x = df_monthly['Year-Month'], y = df_monthly['cases'],
                    name = 'Casos', yaxis = 'y2', opacity = 0.6, marker=dict(color='red'))

    #configuração de um layout para o gráfico
    layout = go.Layout(
        title = 'Casos de COVID-19 nos Estados Unidos de 2020 à 2023',
        xaxis = dict(title = 'Mês'),
        yaxis = dict(title ='Casos', range = [0, df_monthly['cases']]),
        yaxis2 = dict(title = 'mortes', range = [0, df_monthly['deaths']], overlaying='y', side='right'),
        legend = dict(x=0, y=1.1, orientation='h'),
        barmode = 'overlay',
    )

    #adição do gráfico à uma figura exibição com streamlit
    fig = go.Figure(data=[cases, deaths], layout=layout)
    st.plotly_chart(fig)

    # criação de conexão com o banco com validação
    if st.button("Armazenar os dados"):
        try:
            client = MongoClient(Mongo_URI)
            db = client.get_database('casos_de_covid')
            collection = db.get_collection('casos_e_mortes')
            # variáveis para extração do número de casos e mortes.
            total_de_casos = int(df_monthly['cases'].sum())
            total_de_mortes = int(df_monthly['deaths'].sum())
            data_to_insert = {
                "Estado": selecaoEstado,
                "Condado": selecaoCondado,
                "Ano": int(selecaoAno),
                "Mortes": total_de_mortes,
                "Casos": total_de_casos
            }

            if collection.find_one({
                'Estado': selecaoEstado,
                'Condado': selecaoCondado,
                'Ano': int(selecaoAno)
            }):
                st.info("Dados já armazanedos! Por favor, insira dados diferentes.")
            else:
                collection.insert_one(data_to_insert)
                st.success("Armazenado com sucesso!")

        except Exception as e:
            st.error(f"Falha ao inserir os dados ao banco: {e}")

        finally:
            client.close()

else:
    st.warning(f"Não há dados disponíveis para {selecaoCondado} ,{selecaoEstado} em {selecaoAno}.")
