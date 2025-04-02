from fastapi import APIRouter, HTTPException, status, Depends, Query, Request
from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from datetime import date, datetime, timedelta
import calendar

from app.database import get_db
from app.models.reporte import (
    ReporteReservas, ReporteReserva, FiltroReporteReservas, ReporteOcupacion
)
from app.models.reserva_orm import ReservaORM, DetalleReservaORM, PagoORM, EstadoReserva
from app.models.user_orm import UserORM
from app.models.habitacion_orm import HabitacionORM, TipoHabitacionORM
from app.routers.usuarios import get_current_user

router = APIRouter()

# Endpoint para generar reportes de reservas
@router.get(
    "/reservas", 
    response_model=ReporteReservas,
    summary="Generar reporte de reservas",
    description="Genera un reporte detallado de reservas con filtros opcionales",
    responses={
        401: {"description": "No autenticado"},
        403: {"description": "No autorizado"}
    }
)
async def reporte_reservas(
    fecha_inicio: Optional[date] = None,
    fecha_fin: Optional[date] = None,
    estado: Optional[str] = None,
    cliente_id: Optional[int] = None,
    db: Session = Depends(get_db)
):
    """
    Generar reporte de reservas con filtros opcionales
    """
    # Eliminar referencias a variables que ya no existen
    print(f"Generando reporte de reservas")
    
    # Construir la consulta base
    query = db.query(ReservaORM)
    
    # Aplicar filtros si se proporcionan
    if fecha_inicio:
        query = query.filter(ReservaORM.fecha_inicio >= fecha_inicio)
    
    if fecha_fin:
        query = query.filter(ReservaORM.fecha_fin <= fecha_fin)
    
    if estado:
        query = query.filter(ReservaORM.estado == estado)
    
    if cliente_id:
        query = query.filter(ReservaORM.usuario_id == cliente_id)
    
    # Ejecutar la consulta
    reservas = query.all()
    
    # Procesar los resultados
    resultado_reservas = []
    ingresos_totales = 0
    ingresos_pendientes = 0
    
    for r in reservas:
        # Calcular noches de estancia
        noches = (r.fecha_fin - r.fecha_inicio).days
        
        # Calcular detalles y precios
        detalles = db.query(DetalleReservaORM).filter(DetalleReservaORM.reserva_id == r.id).all()
        pagos = db.query(PagoORM).filter(PagoORM.reserva_id == r.id).all()
        
        # Calcular totales
        subtotal = sum(d.precio_por_noche * noches for d in detalles)
        impuestos = subtotal * 0.21  # 21% IVA
        total = subtotal + impuestos
        
        # Calcular pagado
        pagado = sum(p.monto for p in pagos)
        pendiente = total - pagado
        
        # Añadir a totales
        ingresos_totales += total
        ingresos_pendientes += pendiente
        
        # Obtener habitaciones
        habitaciones = []
        for d in detalles:
            hab = db.query(HabitacionORM).filter(HabitacionORM.id == d.habitacion_id).first()
            if hab:
                habitaciones.append(hab.numero)
        
        # Obtener cliente
        cliente = db.query(UserORM).filter(UserORM.id == r.usuario_id).first()
        nombre_cliente = f"{cliente.nombre} {cliente.apellido}" if cliente else "Cliente desconocido"
        
        # Crear objeto de reporte
        reporte_reserva = ReporteReserva(
            id=r.id,
            codigo_reserva=r.codigo_reserva,
            cliente=nombre_cliente,
            fecha_inicio=r.fecha_inicio,
            fecha_fin=r.fecha_fin,
            estado=r.estado,
            habitaciones=habitaciones,
            total_pagado=pagado,
            total_pendiente=pendiente
        )
        
        resultado_reservas.append(reporte_reserva)
    
    return ReporteReservas(
        total_reservas=len(reservas),
        ingresos_totales=ingresos_totales,
        ingresos_pendientes=ingresos_pendientes,
        reservas=resultado_reservas
    )

# Endpoint para obtener ocupación en tiempo real
@router.get(
    "/ocupacion", 
    response_model=ReporteOcupacion,
    summary="Obtener reporte de ocupación",
    description="Obtiene un reporte de ocupación de habitaciones para una fecha específica",
    responses={
        401: {"description": "No autenticado"},
        403: {"description": "No autorizado"},
        404: {"description": "No se encontraron habitaciones activas"}
    }
)
async def reporte_ocupacion(
    fecha: Optional[date] = None,
    db: Session = Depends(get_db)
):
    """
    Obtener reporte de ocupación para una fecha específica (por defecto, hoy)
    """
    # Eliminar referencias a variables que ya no existen
    print(f"Generando reporte de ocupación")
    
    # Si no se proporciona fecha, usar la fecha actual
    if not fecha:
        fecha = date.today()
    
    # Obtener todas las habitaciones
    todas_habitaciones = db.query(HabitacionORM).filter(HabitacionORM.esta_activa == True).all()
    total_habitaciones = len(todas_habitaciones)
    
    if total_habitaciones == 0:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No se encontraron habitaciones activas en el sistema"
        )
    
    # Obtener reservas para la fecha especificada
    reservas = db.query(DetalleReservaORM)\
        .join(ReservaORM)\
        .filter(
            ReservaORM.fecha_inicio <= fecha,
            ReservaORM.fecha_fin > fecha,
            ReservaORM.estado.in_([EstadoReserva.CONFIRMADA.value, EstadoReserva.COMPLETADA.value])
        ).all()
    
    # Obtener IDs de habitaciones ocupadas
    habitaciones_ocupadas_ids = [r.habitacion_id for r in reservas]
    habitaciones_ocupadas = len(habitaciones_ocupadas_ids)
    
    # Calcular habitaciones disponibles
    habitaciones_disponibles = total_habitaciones - habitaciones_ocupadas
    
    # Calcular porcentaje de ocupación
    ocupacion_porcentaje = (habitaciones_ocupadas / total_habitaciones) * 100 if total_habitaciones > 0 else 0
    
    # Calcular desglose por tipo de habitación
    tipos_habitacion = db.query(TipoHabitacionORM).all()
    desglose_por_tipo = {}
    
    for tipo in tipos_habitacion:
        # Total de habitaciones por tipo
        total_por_tipo = db.query(HabitacionORM)\
            .filter(HabitacionORM.tipo_id == tipo.id, HabitacionORM.esta_activa == True)\
            .count()
        
        # Habitaciones ocupadas por tipo
        ocupadas_por_tipo = db.query(DetalleReservaORM)\
            .join(ReservaORM)\
            .join(HabitacionORM)\
            .filter(
                ReservaORM.fecha_inicio <= fecha,
                ReservaORM.fecha_fin > fecha,
                ReservaORM.estado.in_([EstadoReserva.CONFIRMADA.value, EstadoReserva.COMPLETADA.value]),
                HabitacionORM.tipo_id == tipo.id
            ).count()
        
        # Calcular disponibles y porcentaje
        disponibles_por_tipo = total_por_tipo - ocupadas_por_tipo
        porcentaje_por_tipo = (ocupadas_por_tipo / total_por_tipo) * 100 if total_por_tipo > 0 else 0
        
        desglose_por_tipo[tipo.nombre] = {
            "total": total_por_tipo,
            "ocupadas": ocupadas_por_tipo,
            "disponibles": disponibles_por_tipo,
            "porcentaje_ocupacion": porcentaje_por_tipo
        }
    
    return ReporteOcupacion(
        fecha=fecha,
        ocupacion_porcentaje=ocupacion_porcentaje,
        habitaciones_totales=total_habitaciones,
        habitaciones_ocupadas=habitaciones_ocupadas,
        habitaciones_disponibles=habitaciones_disponibles,
        desglose_por_tipo=desglose_por_tipo
    ) 