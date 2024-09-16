import pandas as pd

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

#Get all the unique entities beginning with D and not 'DB'
d_entities = [entity for entity in all_entities if entity.startswith('D00') and not entity.startswith('DB')]
print(len(d_entities), d_entities[:5])


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



import requests
import xml.etree.ElementTree as ET
import pandas as pd
import pickle
from tqdm import tqdm

# List to store data for all proteins
prot_data = []

# Example list of UniProt IDs
uniprot_ids = prot_entities#[:1000] #['P35284', 'O75908', 'Q9Y4X0', 'Q08257']

# UniProt API URL template
protein_url = "https://www.uniprot.org/uniprot/{}.xml"

# Iterate over each UniProt ID
#for uniprot_id in uniprot_ids:
for uniprot_id in tqdm(uniprot_ids, desc='Fetching Proteins...', total=len(uniprot_ids)):

    # Initialize a dictionary to store data for this protein
    protein_dict = {'accession': uniprot_id}
    
    # Build the URL for the request
    url = protein_url.format(uniprot_id)
    
    # Send a GET request to fetch the XML content
    response = requests.get(url)

    if response.status_code == 200:
        # Parse the XML content
        root = ET.fromstring(response.content)
        ns = {'up': 'http://uniprot.org/uniprot'}

        try:
            accession = root.find('up:entry/up:accession', ns).text
            protein_dict['accession'] = accession
        except Exception as e:
            protein_dict['accession'] = None

        try:
            protein_name = root.find('up:entry/up:protein/up:recommendedName/up:fullName', ns).text
            protein_dict['protein_name'] = protein_name
        except Exception as e:
            protein_dict['protein_name'] = None

        try:
            gene_name = root.find('up:entry/up:gene/up:name[@type="primary"]', ns).text
            protein_dict['gene_name'] = gene_name
        except Exception as e:
            protein_dict['gene_name'] = None

        try:
            # Extracting family and subfamily
            similarity_comment = root.find('.//up:comment[@type="similarity"]/up:text', ns)
            family_info = similarity_comment.text
            family_parts = family_info.split(".")
            protein_dict['family'] = family_parts[0].strip() if len(family_parts) > 0 else None
            protein_dict['subfamily'] = family_parts[1].strip() if len(family_parts) > 1 else None
        except Exception as e:
            protein_dict['family'] = None
            protein_dict['subfamily'] = None

        try:
            organism_scientific = root.find('up:entry/up:organism/up:name[@type="scientific"]', ns).text
            protein_dict['organism_scientific'] = organism_scientific
        except Exception as e:
            protein_dict['organism_scientific'] = None

        try:
            organism_common = root.find('up:entry/up:organism/up:name[@type="common"]', ns).text
            protein_dict['organism_common'] = organism_common
        except Exception as e:
            protein_dict['organism_common'] = None

        try:
            function = root.find('up:entry/up:comment[@type="function"]/up:text', ns).text
            protein_dict['function'] = function
        except Exception as e:
            protein_dict['function'] = None

        try:
            disease_comment = root.find('up:entry/up:comment[@type="disease"]/up:text', ns).text
            protein_dict['disease_association'] = disease_comment
        except Exception as e:
            protein_dict['disease_association'] = None

        # Drug interactions
        try:
            drug_interactions = []
            interactions = root.findall('up:entry/up:dbReference[@type="DrugBank"]', ns)
            for interaction in interactions:
                drug_id = interaction.attrib['id']
                drug_name = interaction.find('up:property[@type="name"]', ns).attrib['value'] if interaction.find('up:property[@type="name"]', ns) else "Not available"
                drug_interactions.append((drug_name, drug_id))
            protein_dict['drug_interactions'] = drug_interactions
        except Exception as e:
            protein_dict['drug_interactions'] = None

        # Protein-protein interactions
        try:
            protein_interactions = []
            interactions = root.findall('up:entry/up:dbReference[@type="IntAct"]', ns)
            for interaction in interactions:
                protein_interaction_id = interaction.attrib['id']
                protein_interactions.append(protein_interaction_id)
            protein_dict['protein_interactions'] = protein_interactions
        except Exception as e:
            protein_dict['protein_interactions'] = None

        # Subcellular locations
        try:
            subcellular_locations = []
            locations = root.findall('up:entry/up:comment[@type="subcellular location"]/up:subcellularLocation/up:location', ns)
            for location in locations:
                subcellular_locations.append(location.text)
            protein_dict['subcellular_locations'] = subcellular_locations
        except Exception as e:
            protein_dict['subcellular_locations'] = None

        # Tissue specificity
        try:
            tissue_specificity = root.find('up:entry/up:comment[@type="tissue specificity"]/up:text', ns).text
            protein_dict['tissue_specificity'] = tissue_specificity
        except Exception as e:
            protein_dict['tissue_specificity'] = None

        # Add the protein dictionary to the main list
        prot_data.append(protein_dict)

    else:
        print(f"Failed to retrieve data for {uniprot_id}. Status code: {response.status_code}")


import pickle
with open('protein_data.pkl', 'wb') as f:
    pickle.dump(prot_data, f)