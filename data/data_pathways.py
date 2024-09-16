import pandas as pd
import requests
from bs4 import BeautifulSoup
import logging
import pickle
from tqdm import tqdm

df = pd.read_csv('/Users/seangorman/code-projects/graph_database/data&code/data/BioKG/kg.csv', index_col=0).reset_index(drop=True)

cats = ['DRUG_DISEASE_ASSOCIATION', 'DISEASE_PATHWAY_ASSOCIATION', 'DISEASE_GENETIC_DISORDER', 'PPI', 'DDI', 'PROTEIN_DISEASE_ASSOCIATION', 'Drug_Target_Interaction']

Drugs = 'db_identifier'
Diseases = 'db_identifier'
Proteins = 'UniProt_identifier'

all_entities = set(df['head'].unique().tolist() + df['tail'].unique().tolist())
print(len(all_entities))

#Get all the unique entities beginning with 'DB'
db_entities = [entity for entity in all_entities if entity.startswith('DB')]
print(len(db_entities), db_entities[:5])


disease_cats = ['DRUG_DISEASE_ASSOCIATION', 'DISEASE_PATHWAY_ASSOCIATION', 'DISEASE_GENETIC_DISORDER', 'PROTEIN_DISEASE_ASSOCIATION']
disease_entities = []
for relation in disease_cats:
    if relation == 'DRUG_DISEASE_ASSOCIATION':
        disease_entities.extend(df[df.relation == relation]['tail'].unique().tolist())
    elif relation == 'DISEASE_PATHWAY_ASSOCIATION':
        disease_entities.extend(df[df.relation == relation]['head'].unique().tolist())
    elif relation == 'DISEASE_GENETIC_DISORDER':
        disease_entities.extend(df[df.relation == relation]['head'].unique().tolist())
    elif relation == 'PROTEIN_DISEASE_ASSOCIATION':
        disease_entities.extend(df[df.relation == relation]['tail'].unique().tolist())
disease_entities = list(set(disease_entities))
print(len(disease_entities), list(disease_entities)[:5])


prot_cats = ['PPI', 'PROTEIN_DISEASE_ASSOCIATION', 'Drug_Target_Interaction']
prot_entities = []
for relation in prot_cats:
    if relation == 'PPI':
        prot_entities.extend(set(df[df.relation == relation]['head'].unique().tolist() + df[df.relation == relation]['tail'].unique().tolist()))
    elif relation == 'PROTEIN_DISEASE_ASSOCIATION':
        prot_entities.extend(df[df.relation == relation]['head'].unique().tolist())
    elif relation == 'Drug_Target_Interaction':
        prot_entities.extend(df[df.relation == relation]['tail'].unique().tolist())
prot_entities = list(set(prot_entities))
print(len(prot_entities), list(prot_entities)[:5])



pathway_entities = df[df['relation'] == 'DISEASE_PATHWAY_ASSOCIATION']['tail'].unique().tolist()

genetic_disorder_entities = df[df['relation'] == 'DISEASE_GENETIC_DISORDER']['tail'].unique().tolist()

pathway_url = 'https://www.genome.jp/dbget-bin/www_bget?pathway+{}' # map00670


def get_pathway_info(pathway):
    url = pathway_url.format(pathway)
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')
    return soup



pathway_data = []

# Iterate over each pathway with a progress bar
for pathway in tqdm(pathway_entities, total=len(pathway_entities)):
    try:
        # Get the soup object for the current pathway
        soup = get_pathway_info(pathway)
        
        # Extract the pathway name
        try:
            name_tag = soup.find('th', string='Name')
            name = name_tag.find_next_sibling('td').text.strip() if name_tag else None
        except Exception as e:
            name = None
            # Log or print the error if needed
            print(f"Error extracting name for pathway {pathway}: {e}")
        
        # Extract the pathway description
        try:
            description_tag = soup.find('th', string='Description')
            description = description_tag.find_next_sibling('td').text.strip() if description_tag else None
        except Exception as e:
            description = None
            print(f"Error extracting description for pathway {pathway}: {e}")
        
        # Extract the pathway class
        try:
            class_tag = soup.find('th', string='Class')
            class_ = class_tag.find_next_sibling('td').text.strip() if class_tag else None
        except Exception as e:
            class_ = None
            print(f"Error extracting class for pathway {pathway}: {e}")
        
        # Append the extracted data for the current pathway
        pathway_data.append({
            'pathway': pathway, 
            'name': name, 
            'description': description, 
            'class': class_
        })
    
    # Catch any other unexpected errors
    except Exception as e:
        print(f"Error processing pathway {pathway}: {e}")




with open('pathway_data.pkl', 'wb') as f:
    pickle.dump(pathway_data, f)
