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
    description="Obtiene un reporte de ocupación de habitaciones para un rango de fechas",
    responses={
        401: {"description": "No autenticado"},
        403: {"description": "No autorizado"},
        404: {"description": "No se encontraron habitaciones activas"}
    }
)
async def reporte_ocupacion(
    fecha_inicio: Optional[date] = None,
    fecha_fin: Optional[date] = None,
    db: Session = Depends(get_db)
):
    """
    Obtener reporte de ocupación para un rango de fechas (por defecto, solo el día de hoy)
    """
    print(f"Generando reporte de ocupación por rango: {fecha_inicio} - {fecha_fin}")
    
    # Si no se proporciona fecha de inicio, usar la fecha actual
    if not fecha_inicio:
        fecha_inicio = date.today()
    
    # Si no se proporciona fecha de fin, usar la misma fecha de inicio
    if not fecha_fin:
        fecha_fin = fecha_inicio
    
    # Asegurar que fecha_fin no sea anterior a fecha_inicio
    if fecha_fin < fecha_inicio:
        fecha_fin = fecha_inicio
    
    # Calcular la cantidad de días en el rango
    dias = (fecha_fin - fecha_inicio).days + 1
    
    # Obtener todas las habitaciones activas
    todas_habitaciones = db.query(HabitacionORM).filter(HabitacionORM.esta_activa == True).all()
    total_habitaciones = len(todas_habitaciones)
    
    if total_habitaciones == 0:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No se encontraron habitaciones activas en el sistema"
        )
    
    # Inicializar datos generales
    total_ocupadas = 0
    ocupacion_diaria = {}
    
    # Para cada día en el rango, calcular la ocupación
    current_date = fecha_inicio
    while current_date <= fecha_fin:
        # Obtener reservas para la fecha actual
        reservas = db.query(DetalleReservaORM)\
            .join(ReservaORM)\
            .filter(
                ReservaORM.fecha_inicio <= current_date,
                ReservaORM.fecha_fin > current_date,
                ReservaORM.estado.in_([EstadoReserva.CONFIRMADA.value, EstadoReserva.COMPLETADA.value])
            ).all()
        
        # Obtener IDs de habitaciones ocupadas para el día
        habitaciones_ocupadas_ids = [r.habitacion_id for r in reservas]
        habitaciones_ocupadas_dia = len(habitaciones_ocupadas_ids)
        
        # Sumar al total de ocupadas (para el promedio)
        total_ocupadas += habitaciones_ocupadas_dia
        
        # Calcular porcentaje de ocupación del día
        porcentaje_ocupacion_dia = (habitaciones_ocupadas_dia / total_habitaciones) * 100 if total_habitaciones > 0 else 0
        
        # Guardar en ocupación diaria
        fecha_str = current_date.isoformat()
        ocupacion_diaria[fecha_str] = porcentaje_ocupacion_dia
        
        # Avanzar al siguiente día
        current_date += timedelta(days=1)
    
    # Calcular promedio de ocupación para todo el período
    promedio_ocupacion = total_ocupadas / (total_habitaciones * dias) * 100 if total_habitaciones > 0 and dias > 0 else 0
    
    # Calcular habitaciones ocupadas (promedio) y disponibles
    habitaciones_ocupadas_promedio = total_ocupadas / dias if dias > 0 else 0
    habitaciones_disponibles_promedio = total_habitaciones - habitaciones_ocupadas_promedio
    
    # Calcular desglose por tipo de habitación (para todo el período)
    tipos_habitacion = db.query(TipoHabitacionORM).all()
    desglose_por_tipo = {}
    
    for tipo in tipos_habitacion:
        # Total de habitaciones por tipo
        total_por_tipo = db.query(HabitacionORM)\
            .filter(HabitacionORM.tipo_id == tipo.id, HabitacionORM.esta_activa == True)\
            .count()
        
        if total_por_tipo == 0:
            continue
        
        # Inicializar contadores
        dias_ocupacion = 0
        
        # Para cada día, contar ocupadas por tipo
        current_date = fecha_inicio
        while current_date <= fecha_fin:
            # Habitaciones ocupadas por tipo para el día actual
            ocupadas_por_tipo_dia = db.query(DetalleReservaORM)\
                .join(ReservaORM)\
                .join(HabitacionORM)\
                .filter(
                    ReservaORM.fecha_inicio <= current_date,
                    ReservaORM.fecha_fin > current_date,
                    ReservaORM.estado.in_([EstadoReserva.CONFIRMADA.value, EstadoReserva.COMPLETADA.value]),
                    HabitacionORM.tipo_id == tipo.id
                ).count()
            
            dias_ocupacion += ocupadas_por_tipo_dia
            
            # Avanzar al siguiente día
            current_date += timedelta(days=1)
        
        # Calcular promedios para el tipo
        ocupadas_promedio = dias_ocupacion / dias if dias > 0 else 0
        disponibles_promedio = total_por_tipo - ocupadas_promedio
        porcentaje_promedio = (ocupadas_promedio / total_por_tipo) * 100 if total_por_tipo > 0 else 0
        
        desglose_por_tipo[tipo.nombre] = {
            "total": total_por_tipo,
            "ocupadas": round(ocupadas_promedio, 2),
            "disponibles": round(disponibles_promedio, 2),
            "porcentaje": round(porcentaje_promedio, 2)
        }
    
    return ReporteOcupacion(
        fecha_inicio=fecha_inicio,
        fecha_fin=fecha_fin,
        ocupacion_porcentaje=round(promedio_ocupacion, 2),
        habitaciones_totales=total_habitaciones,
        habitaciones_ocupadas=round(habitaciones_ocupadas_promedio, 2),
        habitaciones_disponibles=round(habitaciones_disponibles_promedio, 2),
        desglose_por_tipo=desglose_por_tipo,
        ocupacion_diaria=ocupacion_diaria
    ) 