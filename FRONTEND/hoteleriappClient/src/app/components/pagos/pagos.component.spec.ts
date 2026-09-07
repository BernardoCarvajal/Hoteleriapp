import { MAT_DIALOG_DATA, MatDialogRef } from '@angular/material/dialog';
import { appTestConfig } from '../../testing/app-test-config';
import { ComponentFixture, TestBed } from '@angular/core/testing';

import { PagosComponent } from './pagos.component';

describe('PagosComponent', () => {
  let component: PagosComponent;
  let fixture: ComponentFixture<PagosComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({ ...appTestConfig, providers: [...appTestConfig.providers, { provide: MAT_DIALOG_DATA, useValue: { fecha_inicio: '2026-09-10', fecha_fin: '2026-09-12', habitacion: { id: 1 } } }, { provide: MatDialogRef, useValue: { close: jasmine.createSpy('close') } }] })
    .compileComponents();

    fixture = TestBed.createComponent(PagosComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
