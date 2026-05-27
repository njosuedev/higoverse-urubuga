from fastapi import FastAPI
from routers.purchase import router as purchase_router
from routers.sale import router as sale_router

app = FastAPI(
    title="POS Inventory System",
    description="Backend API for products, stock, purchases and sales",
    version="1.0.0"
)

# =========================
# ROUTERS
# =========================
app.include_router(
    purchase_router,
    prefix="/api",
    tags=["Purchases"]
)

app.include_router(
    sale_router,
    prefix="/api",
    tags=["Sales"]
)

# =========================
# ROOT ENDPOINT
# =========================
@app.get("/")
def home():
    return {
        "message": "POS API is running",
        "docs": "/docs",
        "status": "healthy",
        "version": "1.0.0"
    }