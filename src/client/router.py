from fastapi import APIRouter, HTTPException
from fastapi.params import Depends
from sqlalchemy.orm import Session
from src.config import get_db
from src.client.models import *
from src.client.schemas import *
from typing import List
from uuid import UUID
router = APIRouter()

@router.get("/clients/{clientId}", tags=["Clients"], name="Получение клиента по ID",
            description="Возвращает информацию о клиенте по его ID.")
def get_client_by_id(clientId: UUID, db: Session = Depends(get_db)):
    existing_client = db.query(ClientModel).filter(ClientModel.client_id == clientId).one_or_none()
    if not existing_client:
        raise HTTPException(status_code=404, detail="Client not found")
    return existing_client


@router.post("/clients/bulk", tags=["Clients"], status_code=201, name="Массовое создание/обновление клиентов",
             description="Создаёт новых или обновляет существующих клиентов.")
def bulk(client_data: List[ClientSchema], db: Session = Depends(get_db)):
    try:
        for client in client_data:
            client_id_uuid = client.client_id
            existing_client = db.query(ClientModel).filter(ClientModel.client_id == client_id_uuid).one_or_none()
            if existing_client:
                existing_client.login = client.login
                existing_client.age = client.age
                existing_client.location = client.location
                existing_client.gender = client.gender
            else:
                new_client = ClientModel(
                    client_id=client.client_id,
                    login=client.login,
                    age=client.age,
                    location=client.location,
                    gender=client.gender,
                )
                db.add(new_client)
        db.commit()
    except:
        db.rollback()
        raise HTTPException(status_code=400, detail="Bulk data is not valid")
    return client_data

