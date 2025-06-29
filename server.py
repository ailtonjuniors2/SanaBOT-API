from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session
from database import SessionLocal, Item, engine

app = FastAPI()

# ------------------- MODELO Pydantic -------------------
class ItemModel(BaseModel):
    categoria: str
    item: str
    quantidade: int
    preco: float = None

# ------------------- DEPENDÊNCIA -------------------
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# ------------------- ENDPOINTS -------------------

@app.get("/")
def home():
    return {"message": "API de Estoque Online (SQLite)", "status": "ativo"}

@app.get("/estoque")
def listar_estoque(db: Session = Depends(get_db)):
    itens = db.query(Item).all()
    resultado = {}
    for i in itens:
        cat = i.categoria.upper()
        if cat not in resultado:
            resultado[cat] = {}
        resultado[cat][i.item] = {
            "quantidade": i.quantidade,
            "preco": i.preco
        }
    return resultado

@app.post("/estoque/adicionar")
def adicionar_item(item: ItemModel, db: Session = Depends(get_db)):
    cat = item.categoria.upper()
    item_existente = db.query(Item).filter_by(categoria=cat, item=item.item).first()

    if item_existente:
        item_existente.quantidade += item.quantidade
        if item.preco is not None:
            item_existente.preco = item.preco
    else:
        novo_item = Item(categoria=cat, item=item.item, quantidade=item.quantidade, preco=item.preco)
        db.add(novo_item)

    db.commit()
    return {"msg": f"Item adicionado/atualizado na categoria {cat}"}

@app.post("/estoque/remover")
def remover_item(item: ItemModel, db: Session = Depends(get_db)):
    cat = item.categoria.upper()
    item_bd = db.query(Item).filter_by(categoria=cat, item=item.item).first()

    if not item_bd:
        raise HTTPException(status_code=404, detail="Item não encontrado")

    item_bd.quantidade -= item.quantidade
    if item_bd.quantidade <= 0:
        db.delete(item_bd)
    db.commit()
    return {"msg": "Quantidade removida"}

@app.delete("/estoque/remover_total")
def remover_total(categoria: str, item: str, db: Session = Depends(get_db)):
    cat = categoria.upper()
    item_bd = db.query(Item).filter_by(categoria=cat, item=item).first()

    if not item_bd:
        raise HTTPException(status_code=404, detail="Item não encontrado")

    db.delete(item_bd)
    db.commit()
    return {"msg": "Item removido completamente"}

@app.put("/estoque/comprar")
def comprar_item(item: ItemModel, db: Session = Depends(get_db)):
    cat = item.categoria.upper()
    item_bd = db.query(Item).filter_by(categoria=cat, item=item.item).first()

    if not item_bd:
        raise HTTPException(status_code=404, detail="Item não encontrado")

    if item_bd.quantidade < item.quantidade:
        raise HTTPException(status_code=400, detail="Quantidade insuficiente em estoque")

    item_bd.quantidade -= item.quantidade
    if item_bd.quantidade == 0:
        db.delete(item_bd)
    db.commit()
    return {"msg": "Compra registrada com sucesso"}
