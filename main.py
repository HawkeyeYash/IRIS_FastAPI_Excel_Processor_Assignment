from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
from processor import list_tables, get_table_details, row_sum
import uvicorn

app = FastAPI(
    title="Excel Processor API",
    description="Processes Excel files using LLMs",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/list_tables")
def api_list_tables():
    return list_tables()

@app.get("/get_table_details")
def api_get_table_details(table_name: str = Query(...)):
    return get_table_details(table_name)

@app.get("/row_sum")
def api_row_sum(table_name: str = Query(...), row_name: str = Query(...)):
    return row_sum(table_name, row_name)

if __name__ == "__main__":
    uvicorn.run("main:app", host="localhost", port=9090)