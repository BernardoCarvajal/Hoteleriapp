import { Injectable } from '@angular/core';
import { HttpClient, HttpParams } from '@angular/common/http';
import { Observable } from 'rxjs';
import { environment } from '../../environments/environment';

export interface ReporteReserva {
  id: number;
  codigo_reserva: string;
  cliente: string;
  fecha_inicio: string;
  fecha_fin: string;
  estado: string;
  habitaciones: string[];
  total_pagado: number;
  total_pendiente: number;
}

export interface ReporteReservas {
  total_reservas: number;
  ingresos_totales: number;
  ingresos_pendientes: number;
  reservas: ReporteReserva[];
}

export interface ReporteOcupacion {
  fecha: string;
  ocupacion_porcentaje: number;
  habitaciones_totales: number;
  habitaciones_ocupadas: number;
  habitaciones_disponibles: number;
  desglose_por_tipo: Record<string, any>;
}

@Injectable({
  providedIn: 'root'
})
export class ReportesService {

  constructor(private http: HttpClient) { }

  /**
   * Obtiene un reporte de todas las reservas con filtros opcionales
   * @param fechaInicio Fecha de inicio del filtro
   * @param fechaFin Fecha fin del filtro
   * @param estado Estado de las reservas a filtrar
   * @param clienteId ID del cliente para filtrar
   */
  getReporteReservas(
    fechaInicio?: string,
    fechaFin?: string,
    estado?: string,
    clienteId?: number
  ): Observable<ReporteReservas> {
    let params = new HttpParams();
    
    if (fechaInicio) {
      params = params.set('fecha_inicio', fechaInicio);
    }
    
    if (fechaFin) {
      params = params.set('fecha_fin', fechaFin);
    }
    
    if (estado) {
      params = params.set('estado', estado);
    }
    
    if (clienteId) {
      params = params.set('cliente_id', clienteId.toString());
    }
    
    return this.http.get<ReporteReservas>(`${environment.apiUrl}/reportes/reservas`, { params });
  }

  /**
   * Obtiene un reporte de ocupación de habitaciones para una fecha específica
   * @param fecha Fecha para el reporte de ocupación (YYYY-MM-DD)
   */
  getReporteOcupacion(fecha?: string): Observable<ReporteOcupacion> {
    let params = new HttpParams();
    
    if (fecha) {
      params = params.set('fecha', fecha);
    }
    
    return this.http.get<ReporteOcupacion>(`${environment.apiUrl}/reportes/ocupacion`, { params });
  }
} 