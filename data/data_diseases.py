import pandas as pd
import requests
from bs4 import BeautifulSoup
from tqdm import tqdm
import pickle

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
prot_entities = set(prot_entities)
print(len(prot_entities), list(prot_entities)[:5])




disease_data = []

# Check if the request was successful
#for id in tqdm(d_entities,  : #[:30]:
for id in tqdm(disease_entities, desc='Fetching', total=len(disease_entities)):
    url = f'https://meshb-prev.nlm.nih.gov/record/ui?ui={id}'
    response = requests.get(url)
    
    if response.status_code == 200:
        soup = BeautifulSoup(response.content, 'html.parser')
        mesh_heading = scope_note = history_note = rdf_unique_identifier = None

        # Extract MeSH Heading
        try:
            mesh_heading = soup.find('dt', string='MeSH Heading      ').find_next_sibling('dd').text.strip()
        except AttributeError:
            mesh_heading = "Not available"

        # Extract Scope Note
        try:
            scope_note = soup.find('span', id='scopeNote').find('dd').text.strip()
        except AttributeError:
            scope_note = "Not available"

        # Extract History Note
        try:
            history_note = soup.find('dt', string='History Note').find_next_sibling('dd').text.strip()
        except AttributeError:
            history_note = "Not available"

        # Extract RDF Unique Identifier
        try:
            rdf_unique_identifier = soup.find('dt', string='RDF Unique Identifier').find_next_sibling('dd').find('a')['href']
        except AttributeError:
            rdf_unique_identifier = "Not available"

        # Add to list
        disease_data.append({
            'disease_id': id,
            'mesh_heading': mesh_heading,
            'scope_note': scope_note,
            'history_note': history_note,
            'rdf_unique_identifier': rdf_unique_identifier
        })

    else:
        print(f"Failed to retrieve the page for {id}. Status code: {response.status_code}")



with open('disease_data.pkl', 'wb') as f:
    pickle.dump(disease_data, f)