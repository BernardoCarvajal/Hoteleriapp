from sqlalchemy.orm import Session
from typing import List, Optional

from app.models.hotel_orm import HotelORM
from app.models.hotel import HotelCreate, HotelUpdate

class HotelService:
    @staticmethod
    def get_hotels(db: Session, skip: int = 0, limit: int = 100) -> List[HotelORM]:
        """
        Obtiene la lista de todos los hoteles
        """
        return db.query(HotelORM).offset(skip).limit(limit).all()

    @staticmethod
    def get_hotel(db: Session, hotel_id: int) -> Optional[HotelORM]:
        """
        Obtiene un hotel por su ID
        """
        return db.query(HotelORM).filter(HotelORM.id == hotel_id).first()

    @staticmethod
    def create_hotel(db: Session, hotel: HotelCreate) -> HotelORM:
        """
        Crea un nuevo hotel
        """
        db_hotel = HotelORM(**hotel.model_dump())
        db.add(db_hotel)
        db.commit()
        db.refresh(db_hotel)
        return db_hotel

    @staticmethod
    def update_hotel(db: Session, hotel_id: int, hotel: HotelUpdate) -> Optional[HotelORM]:
        """
        Actualiza un hotel existente
        """
        db_hotel = HotelService.get_hotel(db, hotel_id)
        if db_hotel:
            hotel_data = hotel.model_dump(exclude_unset=True)
            for key, value in hotel_data.items():
                if value is not None:
                    setattr(db_hotel, key, value)
            db.commit()
            db.refresh(db_hotel)
        return db_hotel

    @staticmethod
    def delete_hotel(db: Session, hotel_id: int) -> bool:
        """
        Elimina un hotel
        """
        db_hotel = HotelService.get_hotel(db, hotel_id)
        if db_hotel:
            db.delete(db_hotel)
            db.commit()
            return True
        return False 