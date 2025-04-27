import { Injectable } from '@angular/core';
import { HttpClient, HttpParams } from '@angular/common/http';
import { Observable } from 'rxjs';
import { environment } from '../../environments/environment';

@Injectable({
  providedIn: 'root'
})
export class ReservasService {

  private apiUrl = environment.apiUrl; // Ajusta la URL si es necesario

  constructor(private http: HttpClient) { }

  consultarDisponibilidad(fecha_llegada: string, fecha_salida: string, num_huespedes: number, tipo_habitacion_id?: number): Observable<any[]> {
    let params = new HttpParams()
      .set('fecha_llegada', fecha_llegada)
      .set('fecha_salida', fecha_salida)
      .set('num_huespedes', num_huespedes);

    if (tipo_habitacion_id) {
      params = params.set('tipo_habitacion_id', tipo_habitacion_id);
    }

    return this.http.get<any[]>(`${this.apiUrl}/reservas/disponibilidad`, { params });
  }

  calcularCostoReserva(fecha_inicio: string, fecha_fin: string, habitacion_id: number): Observable<any> {
    const payload = {
      fecha_inicio: fecha_inicio,
      fecha_fin: fecha_fin,
      habitaciones: [habitacion_id]
    };
    return this.http.post<any>(`${this.apiUrl}/reservas/costo`, payload);
  }

  realizarPago(pago: any): Observable<any> {
    return this.http.post(`${this.apiUrl}/reservas/pagos`, pago);
  }

  crearReserva(reserva: any) {
    return this.http.post(`${this.apiUrl}/reservas`, reserva);
  }

  obtenerMisReservas(): Observable<any[]> {
    return this.http.get<any[]>(`${this.apiUrl}/usuarios/mis-reservas`);
  }

  obtenerTicket(reservaId: number): Observable<Blob> {
    return this.http.get(`${this.apiUrl}/reservas/${reservaId}/ticket`, {
      responseType: 'blob'
    });
  }
}
