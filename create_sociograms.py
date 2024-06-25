import pandas as pd
import re
from unidecode import unidecode
import matplotlib.pyplot as plt
import networkx as nx
import pandas as pd
from io import StringIO
import matplotlib.colors as mcolors
import os
import numpy as np

# Funció per eliminar els accents d'una cadena de text
def remove_accents(input_str):
    return unidecode(input_str)

# Funció per convertir l'adreça de correu en nom i cognom
def email_to_name(email):
    match = re.match(r"(\w+)\.(\w+)(\d*)@.*", email)
    if match:
        return match.group(1).capitalize() + " " + match.group(2).capitalize()[:-2]
    else:
        return email

# Procedim a generar els sociogrames per cada un dels fitxers CSV que has mencionat.
def create_and_save_sociogram(csv_file_path, output_image_path, directed, preferences='positive'):
    # Llegim les dades
    df = pd.read_csv(csv_file_path)

    # Creem el graf
    if directed:
        G = nx.from_pandas_edgelist(df, 'source', 'target', create_using=nx.DiGraph())
    else:
        G = nx.from_pandas_edgelist(df, 'source', 'target')

    # Calculem la mida dels nodes basada en el grau
    degrees = dict(G.degree())
    node_sizes = [v * 100 for v in degrees.values()]

    # Assignem colors als nodes basats en el seu grau
    min_degree, max_degree = min(degrees.values()), max(degrees.values())
    degree_range = max_degree - min_degree if max_degree - min_degree > 0 else 1
    colors = [((degree - min_degree) / degree_range) for degree in degrees.values()]

    # Definim un mapa de colors personalitzat
    if preferences == 'positive':
        color_map = mcolors.LinearSegmentedColormap.from_list('custom_colormap', ['red', 'yellow', 'green'])
    else:
        color_map = mcolors.LinearSegmentedColormap.from_list('custom_colormap', ['green', 'yellow', 'red'])

    node_colors = [color_map(color) for color in colors]

    # Dibuixem el graf
    plt.figure(figsize=(15, 15))
    pos = nx.spring_layout(G, k=0.5, iterations=20)
    nx.draw(G, pos, with_labels=True, node_size=node_sizes, node_color=node_colors, 
            font_size=10, font_weight='bold', edge_color='gray', arrows=directed)

    # Guardem el graf com a imatge PNG
    plt.savefig(output_image_path)
    plt.close()


# Directori on es troben els fitxers de dades
data_directory = 'data/'  # Canvia a la ruta de la teva carpeta 'data'

# Llista de tots els fitxers .csv dins del directori 'data'
data_files = [os.path.join(data_directory, f) for f in os.listdir(data_directory) if f.endswith('.csv')]

for f in data_files:
  # Llegir les dades (substitueix 'data.txt' amb el nom del teu fitxer)
  data = pd.read_csv(f, sep=",", skipinitialspace=True)
  group = f[f.find("_")+1:-4]
  print(group)

  # Convertir els correus a noms
  data['Adreça electrònica'] = data['Adreça electrònica'].apply(email_to_name)

  # Separar les dades en dues categories: amb qui volen treballar i amb qui no volen
  preferits = data.iloc[:, 2:7]
  no_preferits = data.iloc[:, 7:12]
  # Identificar les columnes relacionades amb l'oci
  oci_positiu = data.iloc[:, 12:17]  # Preferències positives d'oci
  oci_negatiu = data.iloc[:, 17:22]  # Preferències negatives d'oci

  # Crear un DataFrame per a les preferències positives
  rows_positiu = []
  for index, row in preferits.iterrows():
      email = data.at[index, 'Adreça electrònica']
      for col in preferits.columns:
          if pd.notna(row[col]):
              rows_positiu.append({'source': email, 'target': remove_accents(row[col])})
  
  positiu = pd.DataFrame(rows_positiu)
  
  # Crear un DataFrame per a les preferències negatives
  rows_negatiu = []
  for index, row in no_preferits.iterrows():
      email = data.at[index, 'Adreça electrònica']
      for col in no_preferits.columns:
          if pd.notna(row[col]):
              rows_negatiu.append({'source': email, 'target': remove_accents(row[col])})
  
  negatiu = pd.DataFrame(rows_negatiu)

  # Crear un DataFrame per a les preferències positives d'oci
  rows_oci_positiu = []
  for index, row in oci_positiu.iterrows():
      email = data.at[index, 'Adreça electrònica']
      for col in oci_positiu.columns:
          if pd.notna(row[col]):
              rows_oci_positiu.append({'source': email, 'target': remove_accents(row[col])})
  
  oci_positiu_df = pd.DataFrame(rows_oci_positiu)
  
  # Crear un DataFrame per a les preferències negatives d'oci
  rows_oci_negatiu = []
  for index, row in oci_negatiu.iterrows():
      email = data.at[index, 'Adreça electrònica']
      for col in oci_negatiu.columns:
          if pd.notna(row[col]):
              rows_oci_negatiu.append({'source': email, 'target': remove_accents(row[col])})
  
  oci_negatiu_df = pd.DataFrame(rows_oci_negatiu)
  # Desar els resultats en fitxers CSV
  positiu.to_csv(f'preferencies_positives_{group}.csv', index=False)
  negatiu.to_csv(f'preferencies_negatives_{group}.csv', index=False)
  
  # Desar els resultats en fitxers CSV separats
  oci_positiu_df.to_csv(f'preferencies_oci_positives_{group}.csv', index=False)
  oci_negatiu_df.to_csv(f'preferencies_oci_negatives_{group}.csv', index=False)

  # Rutes dels fitxers CSV
  csv_files = {
      "preferencies_positives": f"preferencies_positives_{group}.csv",
      "preferencies_negatives": f"preferencies_negatives_{group}.csv",
      "preferencies_oci_positives": f"preferencies_oci_positives_{group}.csv",
      "preferencies_oci_negatives": f"preferencies_oci_negatives_{group}.csv"
  }
  
  # Rutes de les imatges a guardar
  image_files = {
      "sociograma_preferencies_positives": f"sociograma_preferencies_positives_{group}.png",
      "sociograma_preferencies_negatives": f"fsociograma_preferencies_negatives_{group}.png",
      "sociograma_preferencies_oci_positives": f"sociograma_preferencies_oci_positives_{group}.png",
      "sociograma_preferencies_oci_negatives": f"sociograma_preferencies_oci_negatives_{group}.png"
  }
  
  # Crear i guardar els sociogrames per cada fitxer CSV
  for key in csv_files:
    create_and_save_sociogram(csv_files[key], image_files["sociograma_" + key], True)

