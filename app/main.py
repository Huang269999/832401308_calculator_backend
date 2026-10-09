"""FastAPI entry point."""

from __future__ import annotations

import os
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.calculator_service import CalculationError, calculate_expression
from app.database import (
    clear_history,
    delete_history,
    get_history,
    init_database,
    save_history,
)
from app.schemas import CalculateRequest


def _cors_origins() -> list[str]:
    raw = os.getenv(
        "CORS_ORIGINS",
        "http://127.0.0.1:5500,http://localhost:5500",
    )
    return [item.strip() for item in raw.split(",") if item.strip()]


@asynccontextmanager
async def lifespan(_: FastAPI):
    init_database()
    yield


app = FastAPI(
    title="Front-End/Back-End Calculator API",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=_cors_origins(),
    allow_credentials=False,
    allow_methods=["GET", "POST", "DELETE"],
    allow_headers=["Content-Type"],
)


@app.get("/api/health")
def health() -> dict[str, object]:
    return {"success": True, "message": "Calculator backend is running"}


@app.post("/api/calculate")
def calculate(request: CalculateRequest):
    try:
        result = calculate_expression(request.expression)
    except CalculationError as exc:
        return JSONResponse(
            status_code=400,
            content={"success": False, "message": str(exc)},
        )

    history_id = save_history(request.expression.strip(), result)
    return {
        "success": True,
        "id": history_id,
        "expression": request.expression.strip(),
        "result": result,
    }


@app.get("/api/history")
def history():
    return {"success": True, "data": get_history()}


@app.delete("/api/history/{history_id}")
def remove_history(history_id: int):
    if history_id <= 0:
        return JSONResponse(
            status_code=400,
            content={"success": False, "message": "历史记录 ID 非法"},
        )

    if not delete_history(history_id):
        return JSONResponse(
            status_code=404,
            content={"success": False, "message": "历史记录不存在"},
        )

    return {"success": True, "message": "删除成功"}


@app.delete("/api/history")
def remove_all_history():
    deleted_count = clear_history()
    return {
        "success": True,
        "message": "历史记录已清空",
        "deleted_count": deleted_count,
    }
