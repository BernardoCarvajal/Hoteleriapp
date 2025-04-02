from fastapi import APIRouter, HTTPException, status, Depends, Query
from typing import List, Optional
from sqlalchemy.orm import Session
from datetime import date, datetime, timedelta
import random
import string
import qrcode
from io import BytesIO
from fastapi.responses import StreamingResponse

from app.database import get_db
from app.models.reserva import (
    ConsultaDisponibilidad, HabitacionDisponible, ReservaCreate, 
    Reserva, CalculoCosto, CostoReserva, PagoCreate, Pago,
    EstadoReserva, MetodoPago
)
from app.models.habitacion_orm import HabitacionORM, TipoHabitacionORM
from app.models.reserva_orm import ReservaORM, DetalleReservaORM, PagoORM

router = APIRouter()

# Endpoint para consultar disponibilidad de habitaciones
@router.get("/disponibilidad", response_model=List[HabitacionDisponible])
async def consultar_disponibilidad(
    fecha_llegada: date = Query(..., description="Fecha de llegada"),
    fecha_salida: date = Query(..., description="Fecha de salida"),
    num_huespedes: int = Query(1, gt=0, description="Número de huéspedes"),
    tipo_habitacion_id: Optional[int] = Query(None, description="ID del tipo de habitación (opcional)"),
    db: Session = Depends(get_db)
):
    """
    Consultar disponibilidad de habitaciones para un período específico
    """
    # Validar fechas
    if fecha_llegada <= date.today():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="La fecha de llegada debe ser posterior a hoy"
        )
    
    if fecha_salida <= fecha_llegada:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="La fecha de salida debe ser posterior a la fecha de llegada"
        )
    
    # Obtener habitaciones ocupadas para ese período
    reservas = db.query(DetalleReservaORM)\
        .join(ReservaORM)\
        .filter(
            ReservaORM.fecha_inicio < fecha_salida,
            ReservaORM.fecha_fin > fecha_llegada,
            ReservaORM.estado != EstadoReserva.CANCELADA.value
        ).all()
    
    habitaciones_ocupadas = [r.habitacion_id for r in reservas]
    
    # Consultar habitaciones disponibles
    query = db.query(HabitacionORM).join(TipoHabitacionORM)
    
    if habitaciones_ocupadas:
        query = query.filter(HabitacionORM.id.notin_(habitaciones_ocupadas))
    
    # Filtrar por tipo de habitación si se especifica
    if tipo_habitacion_id:
        query = query.filter(HabitacionORM.tipo_id == tipo_habitacion_id)
    
    # Filtrar por capacidad para el número de huéspedes
    query = query.filter(TipoHabitacionORM.capacidad >= num_huespedes)
    
    # Filtrar solo habitaciones activas
    query = query.filter(HabitacionORM.esta_activa == True)
    
    # Ejecutar la consulta
    habitaciones = query.all()
    
    # Convertir a formato de respuesta
    resultado = []
    for h in habitaciones:
        resultado.append(HabitacionDisponible(
            id=h.id,
            numero=h.numero,
            tipo=h.tipo.nombre,
            capacidad=h.tipo.capacidad,
            precio_por_noche=h.tipo.precio_base,
            descripcion=h.tipo.descripcion
        ))
    
    return resultado

# Endpoint para registrar una reserva
@router.post("", response_model=Reserva, status_code=status.HTTP_201_CREATED)
async def crear_reserva(
    reserva: ReservaCreate,
    db: Session = Depends(get_db)
):
    """
    Registrar una nueva reserva
    """
    # Generar código de reserva único
    codigo_reserva = ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))
    
    # Crear objeto de reserva
    nueva_reserva = ReservaORM(
        usuario_id=1,  # Por ahora usamos un usuario fijo (se cambiará cuando implementemos autenticación)
        fecha_inicio=reserva.fecha_inicio,
        fecha_fin=reserva.fecha_fin,
        numero_huespedes=reserva.numero_huespedes,
        estado=EstadoReserva.PENDIENTE.value,
        codigo_reserva=codigo_reserva,
        notas="Reserva creada automáticamente"
    )
    
    db.add(nueva_reserva)
    db.flush()  # Para obtener el ID de la reserva
    
    # Crear detalles de la reserva
    for detalle in reserva.detalles:
        # Obtener tipo de habitación y precio
        habitacion = db.query(HabitacionORM).filter(HabitacionORM.id == detalle.habitacion_id).first()
        if not habitacion:
            db.rollback()
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Habitación con ID {detalle.habitacion_id} no encontrada"
            )
        
        # Verificar disponibilidad para las fechas solicitadas
        reserva_existente = db.query(DetalleReservaORM)\
            .join(ReservaORM)\
            .filter(
                DetalleReservaORM.habitacion_id == detalle.habitacion_id,
                ReservaORM.fecha_inicio < reserva.fecha_fin,
                ReservaORM.fecha_fin > reserva.fecha_inicio,
                ReservaORM.estado != EstadoReserva.CANCELADA.value
            ).first()
        
        if reserva_existente:
            db.rollback()
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"La habitación {habitacion.numero} no está disponible para las fechas seleccionadas"
            )
        
        # Crear detalle
        nuevo_detalle = DetalleReservaORM(
            reserva_id=nueva_reserva.id,
            habitacion_id=detalle.habitacion_id,
            precio_por_noche=habitacion.tipo.precio_base
        )
        
        db.add(nuevo_detalle)
    
    db.commit()
    db.refresh(nueva_reserva)
    
    return nueva_reserva

# Endpoint para calcular el costo de una reserva
@router.post("/costo", response_model=CostoReserva)
async def calcular_costo(
    calculo: CalculoCosto,
    db: Session = Depends(get_db)
):
    """
    Calcular el costo total de una reserva
    """
    # Verificar que las habitaciones existen
    habitaciones = db.query(HabitacionORM).filter(HabitacionORM.id.in_(calculo.habitaciones)).all()
    if len(habitaciones) != len(calculo.habitaciones):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Una o más habitaciones no existen"
        )
    
    # Calcular número de noches
    delta = calculo.fecha_fin - calculo.fecha_inicio
    num_noches = delta.days
    
    if num_noches <= 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El período de reserva debe ser de al menos una noche"
        )
    
    # Calcular costo por habitación
    desglose = {}
    subtotal = 0
    
    for habitacion in habitaciones:
        tipo = db.query(TipoHabitacionORM).filter(TipoHabitacionORM.id == habitacion.tipo_id).first()
        precio_noche = tipo.precio_base
        costo_habitacion = precio_noche * num_noches
        subtotal += costo_habitacion
        
        desglose[f"habitacion_{habitacion.numero}"] = {
            "tipo": tipo.nombre,
            "precio_noche": precio_noche,
            "noches": num_noches,
            "subtotal": costo_habitacion
        }
    
    # Calcular impuestos (21% por ejemplo)
    tasa_impuesto = 0.21
    impuestos = subtotal * tasa_impuesto
    total = subtotal + impuestos
    
    # Incluir información adicional en el desglose
    desglose["informacion"] = {
        "fecha_llegada": calculo.fecha_inicio.isoformat(),
        "fecha_salida": calculo.fecha_fin.isoformat(),
        "noches": num_noches,
        "tasa_impuesto": f"{tasa_impuesto * 100}%"
    }
    
    return CostoReserva(
        subtotal=subtotal,
        impuestos=impuestos,
        total=total,
        desglose=desglose
    )

# Endpoint para realizar el pago de una reserva
@router.post("/pagos", response_model=Pago, status_code=status.HTTP_201_CREATED)
async def realizar_pago(
    pago: PagoCreate,
    db: Session = Depends(get_db)
):
    """
    Registrar el pago de una reserva
    """
    # Verificar que la reserva existe
    reserva = db.query(ReservaORM).filter(ReservaORM.id == pago.reserva_id).first()
    if not reserva:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Reserva con ID {pago.reserva_id} no encontrada"
        )
    
    # Verificar estado de la reserva
    if reserva.estado == EstadoReserva.CANCELADA.value:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No se puede pagar una reserva cancelada"
        )
    
    # Calcular el costo total de la reserva
    detalles = db.query(DetalleReservaORM).filter(DetalleReservaORM.reserva_id == reserva.id).all()
    num_noches = (reserva.fecha_fin - reserva.fecha_inicio).days
    
    subtotal = sum(detalle.precio_por_noche * num_noches for detalle in detalles)
    impuestos = subtotal * 0.21  # 21% de IVA
    total = subtotal + impuestos
    
    # Calcular el total ya pagado
    pagos_previos = db.query(PagoORM).filter(PagoORM.reserva_id == reserva.id).all()
    total_pagado = sum(p.monto for p in pagos_previos)
    
    # Verificar que el pago no exceda lo pendiente
    pendiente = total - total_pagado
    if pago.monto > pendiente:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"El monto del pago (€{pago.monto}) excede el saldo pendiente (€{pendiente})"
        )
    
    # Crear pago
    nuevo_pago = PagoORM(
        reserva_id=pago.reserva_id,
        monto=pago.monto,
        metodo_pago=pago.metodo_pago,
        referencia_pago=pago.referencia_pago,
        estado=EstadoReserva.CONFIRMADA.value
    )
    
    db.add(nuevo_pago)
    
    # Actualizar estado de la reserva
    if total_pagado + pago.monto >= total:
        reserva.estado = EstadoReserva.CONFIRMADA.value
    
    db.commit()
    db.refresh(nuevo_pago)
    
    return nuevo_pago

# Endpoint para generar ticket con código QR
@router.get("/{reserva_id}/ticket", response_class=StreamingResponse)
async def generar_ticket(
    reserva_id: int,
    db: Session = Depends(get_db)
):
    """
    Generar un ticket con código QR para check-in
    """
    # Buscar la reserva
    reserva = db.query(ReservaORM).filter(ReservaORM.id == reserva_id).first()
    if not reserva:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Reserva con ID {reserva_id} no encontrada"
        )
    
    # Verificar que la reserva esté confirmada
    if reserva.estado != EstadoReserva.CONFIRMADA.value:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Solo se pueden generar tickets para reservas confirmadas"
        )
    
    # Generar datos para el QR
    qr_data = {
        "reserva_id": reserva.id,
        "codigo": reserva.codigo_reserva,
        "llegada": reserva.fecha_inicio.isoformat(),
        "salida": reserva.fecha_fin.isoformat(),
        "timestamp": datetime.now().isoformat()
    }
    
    # Convertir a string
    qr_string = str(qr_data)
    
    # Generar QR
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(qr_string)
    qr.make(fit=True)
    
    img = qr.make_image(fill_color="black", back_color="white")
    
    # Convertir a bytes para la respuesta
    img_bytes = BytesIO()
    img.save(img_bytes, "PNG")
    img_bytes.seek(0)
    
    return StreamingResponse(img_bytes, media_type="image/png") 