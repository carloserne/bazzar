import datetime

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
import mysql.connector
import uvicorn
from datetime import date

app = FastAPI()

# Configuración de CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configuración de conexión a MySQL
db_config = {
    "user": "uhhczpjjwxihfeow",
    "password": "poZCfmlofUeuvCnAERBX",
    "host": "bt4fgjruon3dlaapd0zb-mysql.services.clever-cloud.com",
    "database": "bt4fgjruon3dlaapd0zb"
}

# Modelo para representar un producto
class Product(BaseModel):
    id: int
    title: str
    description: str
    price: float
    discount_percentage: float
    rating: float
    stock: int
    brand: str
    category: str
    thumbnail: str

class ProductWithImages(BaseModel):
    id: int
    title: str
    description: str
    price: float
    discount_percentage: float
    rating: float
    stock: int
    brand: str
    category: str
    thumbnail: str
    images: List[str]

# Modelo para agregar una venta
class SaleInput(BaseModel):
    product_id: int
    price: float

# Endpoint para buscar productos
@app.get("/api/items", response_model=List[Product])
def get_items(q: Optional[str] = Query(None)):
    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor(dictionary=True)
    query = "SELECT * FROM productos WHERE title LIKE %s OR description LIKE %s"
    cursor.execute(query, (f"%{q}%", f"%{q}%"))
    items = cursor.fetchall()
    conn.close()
    if not items:
        raise HTTPException(status_code=404, detail="No items found")
    return items

# Endpoint para obtener un producto por ID
@app.get("/api/items/{item_id}", response_model=ProductWithImages)
def get_item(item_id: int):
    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor(dictionary=True)

    # Consulta para el producto
    cursor.execute("SELECT * FROM productos WHERE id = %s", (item_id,))
    item = cursor.fetchone()

    # Verificar si el producto existe
    if not item:
        conn.close()
        raise HTTPException(status_code=404, detail="Item not found")

    # Consulta para obtener las imágenes del producto
    cursor.execute("SELECT url FROM imagenes WHERE producto_id = %s", (item_id,))
    images = [row["url"] for row in cursor.fetchall()]

    # Agregar las imágenes al producto
    item["images"] = images
    conn.close()

    return item

# Endpoint para registrar una venta
@app.post("/api/addSale")
def add_sale(sale: SaleInput):
    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor()
    try:
        cursor.execute("INSERT INTO ventas (producto_id, precio, fecha_venta) VALUES (%s, %s, %s)",
                       (sale.product_id, sale.price, datetime.datetime.now()))
        conn.commit()
        result = True
    except:
        conn.rollback()
        result = False
    finally:
        conn.close()
    return {"success": result}

# Endpoint para obtener todas las ventas
@app.get("/api/sales")
def get_sales():
    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor(dictionary=True)

    # Consulta con JOIN para obtener detalles del producto junto con la información de la venta
    cursor.execute("""
        SELECT ventas.id, ventas.precio, ventas.fecha_venta, 
               productos.title AS product_name, productos.description AS product_description, productos.thumbnail AS product_thumbnail
        FROM ventas
        JOIN productos ON ventas.producto_id = productos.id
    """)

    sales = cursor.fetchall()
    conn.close()

    if not sales:
        raise HTTPException(status_code=404, detail="No sales found")
    return sales


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8080)
