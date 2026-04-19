from fastapi import FastAPI, Request, HTTPException, responses
from fastapi.responses import JSONResponse, Response
from scalar_doc import ScalarConfiguration, ScalarDoc
from xml.etree.ElementTree import Element, SubElement, tostring
import pandas as pd
import datetime

DESCRIPTION = """
# Автодокументация API
Сервер реализует API для управления каталогом товаров с поддержкой JSON и XML.
"""

app = FastAPI(
    title="HW1. Проектирование API",
    description=DESCRIPTION,
    version="1.0.0",
    docs_url=None,
    redoc_url=None
)

docs = ScalarDoc.from_spec(spec=app.openapi_url, mode="url")
docs.set_title("Автодокументация API")
docs.set_configuration(ScalarConfiguration())

# Тестовые данные
data = [
    ['Антифриз EURO G11 (-45°С) зеленый, силикатный 5кг', 1025, 11, 'антифриз', datetime.datetime(2026, 10, 16, 12, 36, 22)],
    ['Антифриз готовый фиолетовый Синтек MULTIFREEZE 5кг', 250, 38, 'антифриз', datetime.datetime(2025, 12, 11, 8, 25, 31)],
    ['Антифриз G11 зеленый', 120, 61, 'антифриз', datetime.datetime(2025, 6, 15, 15, 36, 30)],
    ['Антифриз Antifreeze OEM China OAT red -40 5кг', 390, 65, 'антифриз', datetime.datetime(2025, 11, 30, 4, 12, 39)],
    ['Антифриз G11 зеленый', 135, 93, 'антифриз', datetime.datetime(2026, 8, 25, 3, 24, 1)],
]

df = pd.DataFrame(data, columns=['Наименование товара', 'Цена, руб.', 'Скидка', 'Категория', 'dt'])
df['Год'] = df['dt'].dt.year
df = df.drop('dt', axis=1)

items_db = {str(i+1): row for i, row in enumerate(df.to_dict(orient='records'))}
next_id = len(items_db) + 1

def dict_to_xml(tag, data):
    root = Element(tag)
    for k, v in data.items():
        SubElement(root, str(k)).text = str(v)
    return tostring(root, encoding="utf-8", xml_declaration=True)

def list_to_xml(root_tag, item_tag, data_list):
    root = Element(root_tag)
    for row in data_list:
        item = SubElement(root, item_tag)
        for k, v in row.items():
            SubElement(item, str(k)).text = str(v)
    return tostring(root, encoding="utf-8", xml_declaration=True)

@app.get("/", tags=["service"])
def root():
    return {"message": "API is running"}

@app.get("/items", tags=["items"])
def get_items(request: Request):
    accept = request.headers.get("accept", "application/json")
    data = list(items_db.values())
    if "application/xml" in accept:
        return Response(content=list_to_xml("items", "item", data), media_type="application/xml")
    return JSONResponse(content=data)

@app.get("/items/{item_id}", tags=["items"])
def get_item(item_id: str, request: Request):
    if item_id not in items_db:
        raise HTTPException(status_code=404, detail="Item not found")
    accept = request.headers.get("accept", "application/json")
    data = items_db[item_id]
    if "application/xml" in accept:
        return Response(content=dict_to_xml("item", data), media_type="application/xml")
    return JSONResponse(content=data)

@app.post("/items", tags=["items"])
def create_item(item: dict):
    global next_id
    new_id = str(next_id)
    items_db[new_id] = item
    next_id += 1
    return JSONResponse(status_code=201, content={"id": new_id, "item": item})

@app.post("/foo", tags=["test"])
def post_foo(a: str):
    return f"{a} - ok"

@app.get("/docs", include_in_schema=False)
def get_docs():
    return responses.HTMLResponse(docs.to_html())