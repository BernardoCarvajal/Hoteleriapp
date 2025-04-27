import { Injectable } from '@angular/core';
import { HttpClient, HttpParams } from '@angular/common/http';
import { Observable, of } from 'rxjs';
import { catchError, map } from 'rxjs/operators';
import { Reserva } from '../models/reserva.model';
import { environment } from '../../environments/environment';

@Injectable({
  providedIn: 'root'
})
export class ReservaService {
  private apiUrl = `${environment.apiUrl}/reservas`;

  constructor(private http: HttpClient) { }

  getReservas(filtros?: any): Observable<Reserva[]> {
    let params = new HttpParams();
    
    if (filtros) {
      // Convertir los filtros a parámetros de consulta
      Object.keys(filtros).forEach(key => {
        if (filtros[key] !== null && filtros[key] !== undefined && filtros[key] !== '') {
          params = params.set(key, filtros[key]);
        }
      });
    }

    return this.http.get<Reserva[]>(this.apiUrl, { params }).pipe(
      map(reservas => reservas || []),
      catchError(error => {
        console.error('Error al obtener reservas', error);
        return of([]);
      })
    );
  }

  getReservaById(id: number): Observable<Reserva> {
    return this.http.get<Reserva>(`${this.apiUrl}/${id}`).pipe(
      catchError(error => {
        console.error('Error al obtener reserva', error);
        throw error;
      })
    );
  }

  crearReserva(reserva: Reserva): Observable<Reserva> {
    return this.http.post<Reserva>(this.apiUrl, reserva).pipe(
      catchError(error => {
        console.error('Error al crear reserva', error);
        throw error;
      })
    );
  }

  actualizarReserva(id: number, reserva: Reserva): Observable<Reserva> {
    return this.http.put<Reserva>(`${this.apiUrl}/${id}`, reserva).pipe(
      catchError(error => {
        console.error('Error al actualizar reserva', error);
        throw error;
      })
    );
  }

  cambiarEstado(id: number, estado: string): Observable<Reserva> {
    return this.http.patch<Reserva>(`${this.apiUrl}/${id}/estado`, { estado }).pipe(
      catchError(error => {
        console.error('Error al cambiar estado de reserva', error);
        throw error;
      })
    );
  }

  eliminarReserva(id: number): Observable<any> {
    return this.http.delete(`${this.apiUrl}/${id}`).pipe(
      catchError(error => {
        console.error('Error al eliminar reserva', error);
        throw error;
      })
    );
  }
} 