import { provideZoneChangeDetection } from '@angular/core';
import { provideHttpClientTesting } from '@angular/common/http/testing';
import { TranslateFakeLoader, TranslateLoader } from '@ngx-translate/core';
import { AppModule } from '../app.module';

// Render production components with an isolated HTTP backend and local translations.
export const appTestConfig = {
  imports: [AppModule],
  providers: [provideZoneChangeDetection(), provideHttpClientTesting(),
    { provide: TranslateLoader, useClass: TranslateFakeLoader }],
};
