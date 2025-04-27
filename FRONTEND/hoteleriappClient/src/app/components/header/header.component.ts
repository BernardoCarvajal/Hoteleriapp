import { Component } from '@angular/core';
import { Router } from '@angular/router';
import { AuthService } from '../../services/auth.service';
import { Observable } from 'rxjs';
import { jwtDecode } from 'jwt-decode';

@Component({
  selector: 'app-header',
  standalone: false,
  templateUrl: './header.component.html',
  styleUrl: './header.component.css'
})
export class HeaderComponent {
  isAuthenticated$: Observable<boolean>;

  constructor(
    private authService: AuthService,
    private router: Router
  ) {
    this.isAuthenticated$ = this.authService.isAuthenticated$;
  }

  onLogout(): void {
    this.authService.logout();
    this.router.navigate(['/login']);
  }

  isAdmin(): boolean {
    const token = this.authService.getToken();
    if (!token) {
      return false;
    }

    try {
      const decoded: any = jwtDecode(token);
      const roles: string[] = decoded.roles || [];
      return roles.includes('admin');
    } catch (e) {
      console.error('Error decodificando token:', e);
      return false;
    }
  }
}
