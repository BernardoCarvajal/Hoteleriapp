import { Injectable } from '@angular/core';
import { TranslateService } from '@ngx-translate/core';

@Injectable({
  providedIn: 'root',
})
export class LanguageService {
  constructor(private translate: TranslateService) {
    // Configurar idiomas disponibles
    this.translate.addLangs(['es', 'en']);

    // Establecer el idioma por defecto
    this.translate.setDefaultLang('es');

    // Recuperar el idioma guardado en localStorage
    const savedLang = localStorage.getItem('preferredLanguage');

    if (savedLang && ['es', 'en'].includes(savedLang)) {
      // Usar el idioma guardado en localStorage
      this.translate.use(savedLang);
    } else {
      // Establecer español como idioma predeterminado (ignorando el idioma del navegador)
      this.translate.use('es');
      // Guardar la preferencia
      localStorage.setItem('preferredLanguage', 'es');
    }
  }

  changeLanguage(lang: string) {
    this.translate.use(lang);
    // Guardar la preferencia en localStorage
    localStorage.setItem('preferredLanguage', lang);
  }

  getCurrentLanguage(): string {
    return (
      this.translate.currentLang ||
      localStorage.getItem('preferredLanguage') ||
      'es'
    );
  }
}
