import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';
import { environment } from '../../environments/environment';
import { Usuario, Rol } from '../models/usuario.model';

@Injectable({
  providedIn: 'root'
})
export class UsuariosService {
  
  constructor(private http: HttpClient) { }

  // Obtener todos los usuarios
  getUsuarios(): Observable<Usuario[]> {
    return this.http.get<Usuario[]>(`${environment.apiUrl}/usuarios`);
  }

  // Obtener un usuario por ID
  getUsuario(id: number): Observable<Usuario> {
    return this.http.get<Usuario>(`${environment.apiUrl}/usuarios/${id}`);
  }

  // Crear un nuevo usuario (empleado)
  crearEmpleado(empleado: Partial<Usuario>): Observable<Usuario> {
    return this.http.post<Usuario>(`${environment.apiUrl}/usuarios/empleados`, empleado);
  }

  // Eliminar un usuario
  eliminarUsuario(id: number): Observable<any> {
    return this.http.delete(`${environment.apiUrl}/usuarios/${id}`);
  }

  // Actualizar un usuario
  actualizarUsuario(id: number, usuario: Partial<Usuario>): Observable<Usuario> {
    return this.http.put<Usuario>(`${environment.apiUrl}/usuarios/${id}`, usuario);
  }

  // Asignar roles a un usuario
  asignarRoles(usuarioId: number, rolesIds: number[]): Observable<Usuario> {
    return this.http.put<Usuario>(`${environment.apiUrl}/usuarios/${usuarioId}/roles`, rolesIds);
  }

  // Obtener todos los roles disponibles
  getRoles(): Observable<Rol[]> {
    return this.http.get<Rol[]>(`${environment.apiUrl}/roles`);
  }
} 