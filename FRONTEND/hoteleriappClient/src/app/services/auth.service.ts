import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { BehaviorSubject, Observable, tap } from 'rxjs';
import { environment } from '../../environments/environment';
import { usuarioLogin, LoginResponse, UsuarioRegistro } from '../models/usuario.model';

@Injectable({
  providedIn: 'root'
})
export class AuthService {
  private readonly TOKEN_KEY = 'auth_token';
  private isAuthenticatedSubject = new BehaviorSubject<boolean>(this.hasValidToken());

  isAuthenticated$ = this.isAuthenticatedSubject.asObservable();

  constructor(private http: HttpClient) {}

  login(credentials: usuarioLogin): Observable<LoginResponse> {
    return this.http.post<LoginResponse>(`${environment.apiUrl}/usuarios/login`, credentials)
      .pipe(
        tap(response => {
          this.setSession(response);
        })
      );
  }

  logout(): void {
    localStorage.removeItem(this.TOKEN_KEY);
    this.isAuthenticatedSubject.next(false);
  }

  private setSession(response: LoginResponse): void {
    localStorage.setItem(this.TOKEN_KEY, response.access_token);
    this.isAuthenticatedSubject.next(true);
  }

  getToken(): string | null {
    return localStorage.getItem(this.TOKEN_KEY);
  }

  private hasValidToken(): boolean {
    const token = this.getToken();
    return !!token;
  }

  register(userData: UsuarioRegistro): Observable<any>{
    const url = `${environment.apiUrl}/usuarios/registro`;
    return this.http.post(url, userData);
  }

  getPerfil(): Observable<any> {
    return this.http.get<any>(`${environment.apiUrl}/usuarios/perfil`);
  }

}
