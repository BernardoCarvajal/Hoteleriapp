import { Component, OnInit } from '@angular/core';
import { LanguageService } from './services/language.service';

@Component({
  selector: 'app-root',
  templateUrl: './app.component.html',
  standalone: false,
  styleUrl: './app.component.css',
})
export class AppComponent implements OnInit {
  title = 'hoteleriappClient';

  constructor(private languageService: LanguageService) {}

  ngOnInit(): void {
    console.log('Idioma actual:', this.languageService.getCurrentLanguage());
  }
}
