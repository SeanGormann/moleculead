from fastapi import FastAPI
from fastapi.responses import RedirectResponse
from langserve import add_routes

from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse
from typing import Any, Dict
import json
import asyncio
import logging

# Import your existing modules
from neo4j_genai.llm import OpenAILLM
from neo4j_genai.generation import GraphRAG
from neo4j import GraphDatabase
from neo4j_genai.embeddings.openai import OpenAIEmbeddings
from neo4j_genai.retrievers import HybridRetriever
from neo4j_genai.retrievers.base import RetrieverResultItem
import neo4j
import os

from .config import OPENAI_API_KEY, MISTRAL_API_KEY

os.environ["OPENAI_API_KEY"] = OPENAI_API_KEY
os.environ["MISTRAL_API_KEY"] = MISTRAL_API_KEY

app = FastAPI()

uri = "neo4j+s://d7787256.databases.neo4j.io" 
username = "neo4j"  
password = "2ENzqMQs02P5aNfgyXZUvnyENwSkvvNjh3qAiygmlm8"  

driver = GraphDatabase.driver(uri, auth=(username, password), database="neo4j")

embedder = OpenAIEmbeddings(model="text-embedding-3-small")

# Define the custom result formatter
def custom_result_formatter(record: neo4j.Record) -> RetrieverResultItem:
    node = record.get("node")
    score = record.get("score")

    # Extract properties from the node
    node_id = node.get("id")
    name = node.get("name")
    content = node.get("content")
    source = node.get("source")
    url = node.get("source") 
    title = node.get("name")  

    metadata = {
        "score": score,
        "id": node_id,
        "name": name,
        "source": source,
        "url": url,
        "title": title,
    }

    return RetrieverResultItem(
        content=content,
        metadata=metadata,
    )

# Instantiate the retriever with the custom result formatter
retriever = HybridRetriever(
    driver=driver,
    vector_index_name="VectorIndex",
    fulltext_index_name="KeywordIndex",
    embedder=embedder,
    return_properties=["id", "name", "content", "source"],  
    result_formatter=custom_result_formatter,
)

llm = OpenAILLM(model_name="gpt-4", model_params={"temperature": 0})
rag = GraphRAG(retriever=retriever, llm=llm)




@app.get("/")
async def redirect_root_to_docs():
    return RedirectResponse("/docs")

from fastapi.middleware.cors import CORSMiddleware

# Set all CORS enabled origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"],
)

example = """
Be verbose in your answer. Use the additional context to provide a detailed and comprehensive response. If there is little to no context, provide a general answer. If the context is clear, provide a specific answer.
Your goal is to bring new information to light. Think about how you can answer the question in a way that is informative and engaging. You can provide examples, analogies, or additional details to make your answer more interesting and useful.

Query_text: 'I'm studying Nephritis. What are some drugs that act on the kindey?'

Context:
'CR002\nDB05139\nCR002 blocks the activity of excess platelet-derived growth factor-D (PDGF-D), a target shown to play a role in kidney inflammation. Diabetic nephropathy, IgA nephropathy, and lupus nephritis are histologically characterized by glomerular mesangial cell proliferation and extracellular matrix accumulation. PDGF-D and its receptors play an important role in the pathogenesis of nephritis, based on their potent induction of mesangial cell proliferation and extracellular matrix accumulation shown both in vitro and in vivo. A fully human monoclonal antibody that neutralizes PDGF-D represents a novel therapeutic approach to block nephritides.', metadata={'score': 1.0, 'id': 'DB05139', 'source': 'https://go.drugbank.com/drugs/DB05139', 'url': 'https://go.drugbank.com/drugs/DB05139', 'title': 'CR002'}),
'Nephritis\nD009393\nInflammation of any part of the KIDNEY.', metadata={'score': 1.0, 'id': 'D009393', 'source': 'https://meshb-prev.nlm.nih.gov/record/ui?ui=D009393', 'url': 'https://meshb-prev.nlm.nih.gov/record/ui?ui=D009393', 'title': 'Nephritis'}),
'Aliskiren\nDB09026\nAliskiren is a renin inhibitor.9 Renin is secreted by the kidneys when blood volume and renal perfusion decrease. It normally cleaves the protein angiotensinogen to form angiotensin I. Angiotensin I is then converted to angiotensin II, an active protein. Angiotensin II is a potent vasoconstrictor that causes the release of catecholamines into the circulation. It also promotes the secretion of aldosterone in addition to sodium reabsorption, increasing blood pressure. Additionally, angiotensin II acts on the adrenal cortex where it stimulates aldosterone release. Aldosterone increases sodium reabsorption and potassium excretion in the nephron. 11', metadata={'score': 0.9894428478073425, 'id': 'DB09026', 'source': 'https://go.drugbank.com/drugs/DB09026', 'url': 'https://go.drugbank.com/drugs/DB09026', 'title': 'Aliskiren'}),
'Eplerenone\nDB00700\nEplerenone binds to the mineralocorticoid receptor and thereby blocks the binding of aldosterone (component of the renin-angiotensin-aldosterone-system, or RAAS). Aldosterone synthesis, which occurs primarily in the adrenal gland, is modulated by multiple factors, including angiotensin II and non-RAAS mediators such as adrenocorticotropic hormone (ACTH) and potassium. Aldosterone binds to mineralocorticoid receptors in both epithelial (e.g., kidney) and nonepithelial (e.g., heart, blood vessels, and brain) tissues and increases blood pressure through induction of sodium reabsorption and possibly other mechanisms.', metadata={'score': 0.9869250603984304, 'id': 'DB00700', 'source': 'https://go.drugbank.com/drugs/DB00700', 'url': 'https://go.drugbank.com/drugs/DB00700', 'title': 'Eplerenone'}),
'Nintedanib\nDB09079\nNintedanib is a small molecule, competitive, triple angiokinase inhibitor that targets multiple receptor tyrosine kinases (RTKs) and non-receptor tyrosine kinases (nRTKs). Many of these RTKs are implicated in lung fibrosis and tumour angiogenesis, so nintedanib is therefore used in the treatment of proliferative diseases such as idiopathic pulmonary fibrosis, non-small cell lung cancer, and systemic sclerosis-associated interstitial lung disease.8,9 The specific RTKs that nintedanib inhibits are platelet-derived growth factor (PDGFR) α and β, fibroblast growth factor receptor (FGFR) 1-3, vascular endothelial growth factor receptor (VEGFR) 1-3, and Fns-Like tyrosine kinase-3 (FLT3).8,9,5 Nintedanib binds to the ATP-binding pocket of these receptors and inhibits their activity, thereby blocking signalling cascades that result in the proliferation and migration of lung fibroblasts. Nintedanib also inhibits kinase signalling pathways in various cells within tumour tissues, including endothelial cells, pericytes, smooth muscle cells, and cells contributing to angiogenesis, culminating in an inhibition of cell proliferation and apoptosis of affected tumour cells.5', metadata={'score': 0.9806674414029263, 'id': 'DB09079', 'source': 'https://go.drugbank.com/drugs/DB09079', 'url': 'https://go.drugbank.com/drugs/DB09079', 'title': 'Nintedanib'}),
'Enalaprilat\nDB09477\nEnalaprilat is the active metabolite of the orally available pro-drug, enalapril. Used in the treatment of hypertension, enalapril is an ACE inhibitor that prevents Angiotensin Converting Enzyme (ACE) from transforming angiotensin I into angiotensin II. As angiotensin II is responsible for vasoconstriction and sodium reabsorption in the proximal tubule of the kidney, down-regulation of this protein results in reduced blood pressure and blood fluid volume', metadata={'score': 0.9668461802697829, 'id': 'DB09477', 'source': 'https://go.drugbank.com/drugs/DB09477', 'url': 'https://go.drugbank.com/drugs/DB09477', 'title': 'Enalaprilat'}),
'Indapamide\nDB00808\nIndapamide acts on the nephron, specifically at the proximal segment of the distal convoluted tubule where it inhibits the Na+/Cl- cotransporter, leading to reduced sodium reabsorption.4,8 As a result, sodium and water are retained in the lumen of the nephron for urinary excretion.12 The effects that follow include reduced plasma volume, reduced venous return, lower cardiac output, and ultimately decreased blood pressure.8', metadata={'score': 0.9660460868965614, 'id': 'DB00808', 'source': 'https://go.drugbank.com/drugs/DB00808', 'url': 'https://go.drugbank.com/drugs/DB00808', 'title': 'Indapamide'}),
'Cilazapril\nDB01340\nCilazapril is a pyridazine ACE inhibitor. It competes with angiotensin I for binding at the angiotensin-converting enzyme, blocking the conversion of angiotensin I to angiotensin II. As angiotensin II is a vasoconstrictor and a negative feedback mediator for renin activity, lower angiotensin II levels results in a decrease in blood pressure, an increase in renin activity, and stimulation of baroreceptor reflex mechanisms. Kininase II, an enzyme which degrades the vasodilator bradykinin, is identical to ACE and may also be inhibited.', metadata={'score': 0.9626013678291295, 'id': 'DB01340', 'source': 'https://go.drugbank.com/drugs/DB01340', 'url': 'https://go.drugbank.com/drugs/DB01340', 'title': 'Cilazapril'}),
'Enalapril\nDB00584\nThe renin-angiotensin-aldosterone system (RAAS) is a signaling pathway that works in synergism with the sympathetic system to regulate blood pressure and fluid and electrolyte homeostasis. Activation of this system upon stimulation by different factors, such as low blood pressure and nerve impulses, leads to increased release of norepinephrine (NE) from sympathetic nerve terminals and effects on the vascular growth, vasoconstriction, and salt retention in the kidneys.9 Renin is released from\nRenin acts on the precursor prottein angiotensinogen, which is a plasma globulin synthesized from the liver, to produce cleaved peptide hormone angiotensin I.9 Angiotensin I then can be further cleaved by ACE to produce angiotensin II, a vasoconstrictive peptide hormone.Label Present in different isoforms, angiotensin converting enzyme (ACE) is peptidyl dipeptidase enzyme expressed in various tissues, including the vascular tissues, such as the heart, brain, and kidneys.9 ACE also plays a role in inactivation of bradykinin, a potent vasodepressor peptide.9,Label Angiotensin II mediates various actions on the body by working on its G-protein coupled receptors, AT1 and AT2.9 It causes direct vasoconstriction of precapillary arterioles and postcapillary venules, inhibits the reuptake of NE thereby increasing available levels, stimulates the release of catecholamines from the adrenal medulla, reduces urinary excretion of sodium ions and water by promoting proximal tubular reabsorption, stimulates synthesis and release of aldosterone from the adrenal cortex, and stimulates hypertrophy of both vascular smooth muscle cells and cardiac myocytes.11', metadata={'score': 0.9623965603734422, 'id': 'DB00584', 'source': 'https://go.drugbank.com/drugs/DB00584', 'url': 'https://go.drugbank.com/drugs/DB00584', 'title': 'Enalapril'}),
'Spironolactone\nDB00421\nAldosterone is a key hormone in the renin-angiotensin-aldosterone system. By binding to the mineralocorticoid receptor at the distal tubules and collecting duct, it causes sodium reabsorption and potassium secretion, increases vascular stiffness and remodelling, and activates pro-inflammatory pathways.6,11', metadata={'score': 0.9594202098620088, 'id': 'DB00421', 'source': 'https://go.drugbank.com/drugs/DB00421', 'url': 'https://go.drugbank.com/drugs/DB00421', 'title': 'Spironolactone'})]

Response:
If you are studying nephritis, here are some drugs that act on the kidney:

1. **CR002**: This is a fully human monoclonal antibody that neutralizes platelet-derived growth factor-D (PDGF-D), which plays a role in kidney inflammation and the pathogenesis of nephritis.

2. **Aliskiren**: A renin inhibitor that affects the renin-angiotensin-aldosterone system (RAAS), which is crucial for blood pressure regulation and fluid balance in the kidneys.

3. **Eplerenone**: This drug binds to the mineralocorticoid receptor, blocking the effects of aldosterone, which is involved in sodium reabsorption and blood pressure regulation in the kidneys.

4. **Enalaprilat**: The active metabolite of enalapril, an ACE inhibitor that prevents the conversion of angiotensin I to angiotensin II, reducing vasoconstriction and sodium reabsorption in the kidneys.

5. **Indapamide**: Acts on the nephron, specifically at the proximal segment of the distal convoluted tubule, inhibiting the Na+/Cl- cotransporter and reducing sodium reabsorption.

6. **Cilazapril**: An ACE inhibitor that blocks the conversion of angiotensin I to angiotensin II, leading to decreased blood pressure and reduced sodium reabsorption in the kidneys.

7. **Enalapril**: Another ACE inhibitor that affects the RAAS, reducing vasoconstriction and sodium reabsorption in the kidneys.

8. **Spironolactone**: Binds to the mineralocorticoid receptor at the distal tubules and collecting duct, inhibiting the effects of aldosterone, which includes sodium reabsorption and potassium secretion.

These drugs can be used to manage various aspects of nephritis by targeting different pathways involved in kidney function and inflammation."""


@app.post("/my_chain/invoke")
async def invoke(request: Request):
    try:
        # Parse the JSON input
        data = await request.json()
        # Extract the query text
        query_text = data.get("input", {}).get("query")
        if not query_text:
            raise HTTPException(status_code=400, detail="Missing 'query' in 'input'")

        # Since rag.search() is synchronous, run it in a thread pool to avoid blocking
        loop = asyncio.get_event_loop()
        response = await loop.run_in_executor(
            None,
            rag.search,
            query_text,
            example,
            {"top_k": 10},
            True
        )

        # Build the raw_documents list
        raw_documents = []
        for item in response.retriever_result.items:
            metadata = item.metadata  # Access the metadata dictionary
            raw_doc = {
                "id": metadata.get("id"),
                "metadata": {
                    "title": metadata.get("title"),
                    "url": metadata.get("url"),
                    "source": metadata.get("source"),
                    # Include other metadata fields if necessary
                },
                "page_content": item.content,
                "type": "Document",  # Assuming all items are of type Document
            }
            raw_documents.append(raw_doc)

        # Construct the final output
        output = {
            "output": {
                "question": query_text,
                "response": response.answer,
                "raw_documents": raw_documents,
            }
        }

        # Return the JSON response
        return JSONResponse(content=output)

    except Exception as e:
        # Handle exceptions and return an appropriate HTTP error response
        logging.exception("Error processing request")
        return JSONResponse(
            status_code=500,
            content={"error": str(e)}
        )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
