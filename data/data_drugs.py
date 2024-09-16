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
prot_entities = set(prot_entities)
print(len(prot_entities), list(prot_entities)[:5])



def extract_associated_conditions(soup):
    try:
        # Find the table with associated conditions in the HTML
        table = soup.find("table", {"id": "drug-associated-conditions-table"})
        
        if table:
            indications = []
            # Find all rows in the table body
            rows = table.find("tbody").find_all("tr")
            for row in rows:
                # The 'Indication' column seems to be the second column (index 1)
                cols = row.find_all("td")
                if len(cols) > 1:
                    indication = cols[1].text.strip()
                    indications.append(indication)
            
            return indications
        else:
            print("Table with associated conditions not found.")
            return []
    
    except Exception as e:
        print(f"Error extracting associated conditions: {e}")
        return None


# Function to extract target, enzyme, or transporter details (name, gene, organism, and ID)
def extract_interactions(soup, section_name):
    try:
        # Find the relevant section header by its text
        section = soup.find('h3', string=section_name)
        
        if section:
            interactions = []
            # Find the next sibling that contains the relevant bond-list
            bond_list = section.find_next_sibling("div", class_="bond-list")
            
            if bond_list:
                # Extract each interaction card in the bond-list
                cards = bond_list.find_all("div", class_="card")
                
                for card in cards:
                    # Extract relevant details from each card
                    name = card.find("strong").text.strip() if card.find("strong") else None
                    gene = card.find("dt", string="Gene Name").find_next_sibling("dd").text.strip() if card.find("dt", string="Gene Name") else None
                    organism = card.find("dt", string="Organism").find_next_sibling("dd").text.strip() if card.find("dt", string="Organism") else None
                    uniprot_id = card.find("dt", string="Uniprot ID").find_next_sibling("dd").text.strip() if card.find("dt", string="Uniprot ID") else None
                    
                    # Add the extracted data to the list of interactions
                    interactions.append({
                        "name": name,
                        "gene": gene,
                        "organism": organism,
                        "uniprot_id": uniprot_id
                    })
            return interactions
        else:
            print(f"{section_name} section not found.")
            return []
    
    except Exception as e:
        print(f"Error extracting {section_name}: {e}")
        return None




import requests
from bs4 import BeautifulSoup
import logging
from tqdm import tqdm

# Set up logging to write to a file
logging.basicConfig(filename='logs/drug_extraction.log', level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

logging.info("Starting New extraction...")

# Base URL for the drug page
base_url = "https://go.drugbank.com/drugs/{}"

# List of drug IDs
db_entities_test = ['DB01590', 'DB13624', 'DB05304', 'DB05897', 'DB00904']  # Add your list of disease IDs here

results = {}

# Check if the request was successful
for id in tqdm(db_entities, desc='Fetching Drugs...', total=len(db_entities)):
    url = base_url.format(id)
    response = requests.get(url)
    
    if response.status_code == 200:
        soup = BeautifulSoup(response.content, 'html.parser')

        # Extract drug name
        drug_name = soup.find("meta", {"name": "dc.title"})['content'] if soup.find("meta", {"name": "dc.title"}) else None

        # Extract DB ID
        drug_id = id

        # Extract Mechanism of Action (MOA)
        moa = None
        try:
            moa_section = soup.find("dt", {"id": "mechanism-of-action"})
            moa = moa_section.find_next("p").text.strip() if moa_section else None
        except Exception as e:
            logging.error(f"Error extracting MOA for {drug_id}: {e}")

        # Extract Associated Conditions (Diseases)
        associated_conditions = None
        try:
            associated_conditions = extract_associated_conditions(soup)
        except Exception as e:
            logging.error(f"Error extracting associated conditions for {drug_id}: {e}")

        # Extract Targets, Enzymes, Transporters
        targets, enzymes, transporters = None, None, None
        try:
            targets = extract_interactions(soup, 'Targets')
        except Exception as e:
            logging.error(f"Error extracting Targets for {drug_id}: {e}")

        try:
            enzymes = extract_interactions(soup, 'Enzymes')
        except Exception as e:
            logging.error(f"Error extracting Enzymes for {drug_id}: {e}")

        try:
            transporters = extract_interactions(soup, 'Transporters')
        except Exception as e:
            logging.error(f"Error extracting Transporters for {drug_id}: {e}")

        # Extract SMILES
        smiles = None
        try:
            smiles = soup.find("dt", {"id": "smiles"}).find_next("dd").text.strip()
        except Exception as e:
            logging.error(f"Error extracting SMILES for {drug_id}: {e}")

        # Create a dictionary for the current drug and store it in the results with drug_id as key
        drug_data = {
            "drug_name": drug_name,
            "moa": moa,
            "smiles": smiles,
            "associated_conditions": associated_conditions,
            "targets": targets,
            "enzymes": enzymes,
            "transporters": transporters
        }
        results[drug_id] = drug_data

    else:
        logging.warning(f"Failed to fetch data for {drug_id}. Status code: {response.status_code}")

# You can also log the results at the end if needed
logging.info(f"Extraction complete. Total drugs processed: {len(results)}")


with open('drug_data.pkl', 'wb') as f:
    pickle.dump(results, f)