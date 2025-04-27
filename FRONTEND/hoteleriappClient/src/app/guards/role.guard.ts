import { Injectable } from '@angular/core';
import { CanActivate, ActivatedRouteSnapshot, RouterStateSnapshot, Router } from '@angular/router';
import { Observable, of } from 'rxjs';
import { AuthService } from '../services/auth.service';
import { jwtDecode } from 'jwt-decode';

@Injectable({
  providedIn: 'root'
})
export class RoleGuard implements CanActivate {

  constructor(
    private authService: AuthService,
    private router: Router
  ) {}

  canActivate(
    route: ActivatedRouteSnapshot,
    state: RouterStateSnapshot
  ): Observable<boolean> {
    const expectedRoles: string[] = route.data['roles'];
    const token = this.authService.getToken();

    if (!token) {
      this.router.navigate(['/login']);
      return of(false);
    }

    let userRoles: string[] = [];
    try {
      const decoded: any = jwtDecode(token);
      userRoles = decoded.roles || [];
    } catch (e) {
      this.router.navigate(['/login']);
      return of(false);
    }

    // Verifica si el usuario tiene al menos uno de los roles requeridos
    const hasRole = expectedRoles.some(role => userRoles.includes(role));
    if (!hasRole) {
      this.router.navigate(['/unauthorized']); // O la ruta que prefieras
      return of(false);
    }

    return of(true);
  }
} 