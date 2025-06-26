from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import json
import os
import httpx
import asyncio

app = FastAPI()
@app.get("/")
def home():
    return {"message": "API de Estoque Online", "status": "ativo"}
CAMINHO_ESTOQUE = "estoque.json"

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=int(os.environ.get("PORT", 8000)))


class ItemModel(BaseModel):
    categoria: str
    item: str
    quantidade: int
    preco: float = None  # Novo campo


def carregar_estoque():
    if not os.path.exists(CAMINHO_ESTOQUE):
        with open(CAMINHO_ESTOQUE, "w") as f:
            json.dump({}, f)
    with open(CAMINHO_ESTOQUE, "r") as f:
        return json.load(f)


def salvar_estoque(estoque):
    with open(CAMINHO_ESTOQUE, "w") as f:
        json.dump(estoque, f, indent=4)


@app.post("/estoque/adicionar")
def adicionar_item(item: ItemModel):
    if not item.categoria or not item.item:
        raise HTTPException(status_code=400, detail="Categoria e item são obrigatórios")
    estoque = carregar_estoque()
    cat = item.categoria.upper()

    if cat not in estoque:
        estoque[cat] = {}

    if item.item in estoque[cat]:
        estoque[cat][item.item]["quantidade"] += item.quantidade
    else:
        estoque[cat][item.item] = {
            "quantidade": item.quantidade,
            "preco": item.preco if item.preco else 50.00  # Valor padrão
        }

    salvar_estoque(estoque)
    return {"msg": f"Item adicionado/atualizado na categoria {cat}"}


@app.post("/estoque/remover")
def remover_item(item: ItemModel):
    estoque = carregar_estoque()
    cat = item.categoria.upper()

    if cat in estoque and item.item in estoque[cat]:
        estoque[cat][item.item]["quantidade"] -= item.quantidade
        if estoque[cat][item.item]["quantidade"] <= 0:
            del estoque[cat][item.item]
        salvar_estoque(estoque)
        return {"msg": "Quantidade removida"}
    raise HTTPException(status_code=404, detail="Item não encontrado")


@app.delete("/estoque/remover_total")
def remover_item_total(categoria: str, item: str):
    estoque = carregar_estoque()
    cat = categoria.upper()

    if cat in estoque and item in estoque[cat]:
        del estoque[cat][item]
        salvar_estoque(estoque)
        return {"msg": "Item removido completamente"}
    raise HTTPException(status_code=404, detail="Item não encontrado")

@app.get("/estoque")
def get_estoque():
    return carregar_estoque()