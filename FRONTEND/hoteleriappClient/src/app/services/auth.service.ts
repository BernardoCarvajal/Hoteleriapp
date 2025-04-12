import { Injectable } from '@angular/core';
import { environment } from '../../environments/environment';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';
import { UsuarioRegistro, usuarioLogin } from '../models/usuario.model';

@Injectable({
  providedIn: 'root'
})
export class AuthService {

  private apiUrl = environment.apiUrl;

  constructor(private http: HttpClient) { }

  login(userData: usuarioLogin): Observable<any>{
    const url = `${this.apiUrl}/usuarios/login`;
    return this.http.post(url, userData);
  }

  register(userData: UsuarioRegistro): Observable<any>{
    const url = `${this.apiUrl}/usuarios/registro`;
    return this.http.post(url, userData);
  }
}
