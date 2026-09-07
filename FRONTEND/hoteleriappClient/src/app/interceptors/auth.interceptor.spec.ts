import { HttpHandler, HttpRequest, HttpResponse } from '@angular/common/http';
import { of } from 'rxjs';
import { AuthInterceptor } from './auth.interceptor';

describe('AuthInterceptor', () => {
  afterEach(() => localStorage.removeItem('auth_token'));

  it('adds the saved bearer token to API requests', () => {
    localStorage.setItem('auth_token', 'test-token');
    const next = jasmine.createSpyObj<HttpHandler>('HttpHandler', ['handle']);
    next.handle.and.returnValue(of(new HttpResponse()));
    new AuthInterceptor().intercept(new HttpRequest('GET', '/api/usuarios/perfil'), next);
    expect(next.handle.calls.mostRecent().args[0].headers.get('Authorization')).toBe('Bearer test-token');
  });

  it('leaves requests unauthenticated when no token is saved', () => {
    localStorage.removeItem('auth_token');
    const request = new HttpRequest('GET', '/api/usuarios/login');
    const next = jasmine.createSpyObj<HttpHandler>('HttpHandler', ['handle']);
    next.handle.and.returnValue(of(new HttpResponse()));
    new AuthInterceptor().intercept(request, next);
    expect(next.handle).toHaveBeenCalledWith(request);
    expect(request.headers.has('Authorization')).toBeFalse();
  });
});
