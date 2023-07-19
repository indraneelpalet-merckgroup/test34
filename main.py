from classes.ClusterExtraction import ClusterExtraction
from classes.NumberExtraction import NumberExtraction
from pydantic import BaseModel
from fastapi import FastAPI, Form, Request, UploadFile, File, Path
from fastapi.logger import logger
import sys, os, shutil, subprocess

import uvicorn


app = FastAPI()
ALLOWED_EXTENSIONS = set(['pdf'])
global clusterExtractor
global numberExtractor
clusterExtractor = ClusterExtraction()
numberExtractor = NumberExtraction(os.environ['BROKER_ENDPOINT'])


class ClusterRequestBody(BaseModel): 
    description: str
    title: str

class TypeAheadRequestBody(BaseModel): 
    documentType: str = Form(...)
    file: UploadFile = File(...)
    
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.post("/getCluster")
def getCluster(body: ClusterRequestBody):
    description = body.description
    title = body.title
    cluster = clusterExtractor.extractCluster(description, title)
    return {"clusterIdentified": True, "clusterName": cluster} if not cluster == "NOT IDENTIFIED" else {"clusterIdentified": False, "clusterName": cluster}

@app.post("/documents")
def getTypeAheads(documentType: str = Form(...),file: UploadFile = File(...)):
    if allowed_file(file.filename):
        file_object = file.file
        with open(file.filename, 'wb') as f_dest:
            shutil.copyfileobj(file_object, f_dest)
        #strip to one page only
        outfile_name = f"tmp_{file.filename}"
        subprocess.check_output(["gs",
                                 '-dBATCH', '-dNOPAUSE', '-sPageList=1', '-sDEVICE=pdfwrite',
                                 '-sOUTPUTFILE=%s' % (outfile_name,), file.filename])
        data = numberExtractor.start_extraction(outfile_name)
        os.remove(file.filename)
        os.remove(outfile_name)
        return data

if __name__ == "__main__":
    uvicorn.run('myapp:app', host = sys.argv[1], port = 8000)
else:
    print(app.openapi())
