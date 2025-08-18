import pandas as pd
import os
import glob

# importação
data_dir = os.path.join(os.path.dirname(__file__), 'base de dados')
all_files = glob.glob(os.path.join(data_dir, '*.csv'))

# Verificação da presença dos arquivos
if not all_files:
    print("Nenhum arquivo CSV encontrado.")
else:
    # concatenação dos arquivos CSV
    df = pd.concat([pd.read_csv(f) for f in all_files], ignore_index=True)

    # Processamento das colunas
    df['date'] = pd.to_datetime(df['date'])
    df['year'] = df['date'].dt.year
    df['Year-Month'] = df['date'].dt.strftime('%Y-%m').astype(str)

    # Salva como parquet
    output_path = os.path.join(data_dir, 'dados_completos.parquet')
    df.to_parquet(output_path, index=False)
    print(f"Arquivo .parquet salvo em: {output_path}")
