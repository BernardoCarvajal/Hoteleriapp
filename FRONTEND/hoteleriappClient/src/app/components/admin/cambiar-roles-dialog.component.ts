import { Component, Inject, OnInit } from '@angular/core';
import { MAT_DIALOG_DATA, MatDialogRef } from '@angular/material/dialog';
import { Usuario, Rol } from '../../models/usuario.model';
import { UsuariosService } from '../../services/usuarios.service';
import { FormBuilder, FormGroup } from '@angular/forms';

@Component({
  selector: 'app-cambiar-roles-dialog',
  standalone: false,
  template: `
    <h2 mat-dialog-title>Cambiar rol de usuario</h2>
    <mat-dialog-content>
      <div class="user-info mb-3">
        <strong>Usuario:</strong> {{data.usuario.nombre}} {{data.usuario.apellido}} ({{data.usuario.email}})
      </div>
      <div *ngIf="cargando" class="text-center">
        <mat-spinner diameter="40" class="mx-auto"></mat-spinner>
        <p class="mt-2">Cargando roles...</p>
      </div>
      <form [formGroup]="rolesForm" *ngIf="!cargando && roles.length > 0">
        <p>Seleccione un rol para el usuario:</p>
        <mat-radio-group formControlName="rolSeleccionado" class="roles-container">
          <div *ngFor="let rol of roles">
            <mat-radio-button [value]="rol.id" class="mb-2">
              <strong>{{rol.nombre}}</strong>
              <div class="text-muted small">{{rol.descripcion}}</div>
            </mat-radio-button>
          </div>
        </mat-radio-group>
      </form>
    </mat-dialog-content>
    <mat-dialog-actions align="end">
      <button mat-button mat-dialog-close>Cancelar</button>
      <button mat-raised-button color="primary" [disabled]="cargando || guardando || rolesForm.invalid" (click)="guardarRoles()">
        <mat-spinner diameter="20" *ngIf="guardando" class="me-2"></mat-spinner>
        Guardar
      </button>
    </mat-dialog-actions>
  `,
  styles: [`
    .roles-container {
      display: flex;
      flex-direction: column;
      margin-bottom: 20px;
    }
    .mat-radio-button {
      margin-bottom: 10px;
    }
  `]
})
export class CambiarRolesDialogComponent implements OnInit {
  roles: Rol[] = [];
  cargando = true;
  guardando = false;
  rolesForm: FormGroup;

  constructor(
    public dialogRef: MatDialogRef<CambiarRolesDialogComponent>,
    @Inject(MAT_DIALOG_DATA) public data: { usuario: Usuario },
    private usuariosService: UsuariosService,
    private fb: FormBuilder
  ) {
    this.rolesForm = this.fb.group({
      rolSeleccionado: ['', { validators: [] }]
    });
  }

  ngOnInit(): void {
    this.cargarRoles();
  }

  cargarRoles(): void {
    this.cargando = true;
    this.usuariosService.getRoles().subscribe({
      next: (roles) => {
        // Filtrar para excluir el rol de admin
        this.roles = roles.filter(rol => rol.nombre !== 'admin');
        this.cargando = false;
        
        // Establecer el rol seleccionado inicialmente (el primero que no sea admin)
        const rolActual = this.data.usuario.roles?.find(r => r.nombre !== 'admin');
        if (rolActual?.id) {
          this.rolesForm.patchValue({
            rolSeleccionado: rolActual.id
          });
        }
      },
      error: (error) => {
        console.error('Error al cargar roles:', error);
        this.cargando = false;
      }
    });
  }

  guardarRoles(): void {
    this.guardando = true;
    const rolSeleccionado = this.rolesForm.get('rolSeleccionado')?.value;
    
    if (!rolSeleccionado) {
      this.guardando = false;
      return;
    }
    
    // Enviar solo el ID del rol seleccionado en un array (la API espera un array)
    this.usuariosService.asignarRoles(this.data.usuario.id!, [rolSeleccionado]).subscribe({
      next: (usuario) => {
        this.guardando = false;
        this.dialogRef.close(usuario);
      },
      error: (error) => {
        console.error('Error al guardar rol:', error);
        this.guardando = false;
      }
    });
  }
} 