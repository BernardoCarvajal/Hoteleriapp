import { Component, OnInit } from '@angular/core';
import { FormBuilder, FormGroup, Validators } from '@angular/forms';
import { MatDialog } from '@angular/material/dialog';
import { UsuariosService } from '../../services/usuarios.service';
import { Usuario } from '../../models/usuario.model';
import { CambiarRolesDialogComponent } from './cambiar-roles-dialog.component';
import { TranslateService } from '@ngx-translate/core';
import { LanguageService } from '../../services/language.service';

@Component({
  selector: 'app-admin',
  standalone: false,
  templateUrl: './admin.component.html',
  styleUrl: './admin.component.css',
})
export class AdminComponent implements OnInit {
  usuarios: Usuario[] = [];
  mostrarFormulario = false;
  formularioEmpleado: FormGroup;
  mensaje = '';
  tipoMensaje = '';
  cargando = false;
  hidePassword = true;

  constructor(
    private usuariosService: UsuariosService,
    private fb: FormBuilder,
    private dialog: MatDialog,
    private translate: TranslateService,
    private languageService: LanguageService
  ) {
    this.formularioEmpleado = this.fb.group({
      nombre: ['', [Validators.required, Validators.minLength(3)]],
      apellido: ['', [Validators.required, Validators.minLength(3)]],
      email: ['', [Validators.required, Validators.email]],
      password: ['', [Validators.required, Validators.minLength(6)]],
      rol: ['EMPLEADO', Validators.required],
    });
  }

  ngOnInit(): void {
    this.translate.get('ADMIN.TITLE').subscribe((res: string) => {
      console.log('Traducción cargada:', res);
    });

    this.cargarUsuarios();
  }

  cargarUsuarios(): void {
    this.cargando = true;
    this.usuariosService.getUsuarios().subscribe({
      next: (data) => {
        this.usuarios = data;
        this.cargando = false;
      },
      error: (error) => {
        console.error('Error al cargar usuarios:', error);
        this.mostrarAlerta('Error al cargar la lista de usuarios', 'danger');
        this.cargando = false;
      },
    });
  }

  toggleFormulario(): void {
    this.mostrarFormulario = !this.mostrarFormulario;
    if (this.mostrarFormulario === false) {
      this.formularioEmpleado.reset({
        rol: 'EMPLEADO',
      });
    }
  }

  crearEmpleado(): void {
    if (this.formularioEmpleado.invalid) {
      Object.values(this.formularioEmpleado.controls).forEach((control) => {
        control.markAsTouched();
      });
      return;
    }

    this.cargando = true;
    const nuevoEmpleado = this.formularioEmpleado.value;

    this.usuariosService.crearEmpleado(nuevoEmpleado).subscribe({
      next: () => {
        this.mostrarAlerta('Empleado creado exitosamente', 'success');
        this.formularioEmpleado.reset({
          rol: 'EMPLEADO',
        });
        this.cargarUsuarios();
        this.toggleFormulario();
        this.cargando = false;
      },
      error: (error) => {
        console.error('Error al crear empleado:', error);
        this.mostrarAlerta(
          error.error?.detail || 'Error al crear el empleado',
          'danger'
        );
        this.cargando = false;
      },
    });
  }

  eliminarUsuario(id: number): void {
    const usuario = this.usuarios.find((u) => u.id === id);
    if (usuario && this.tieneRolAdmin(usuario)) {
      this.mostrarAlerta(
        'No se puede eliminar un usuario administrador',
        'danger'
      );
      return;
    }

    if (confirm('¿Está seguro que desea eliminar este usuario?')) {
      this.cargando = true;
      this.usuariosService.eliminarUsuario(id).subscribe({
        next: () => {
          this.mostrarAlerta('Usuario eliminado exitosamente', 'success');
          this.cargarUsuarios();
        },
        error: (error) => {
          console.error('Error al eliminar usuario:', error);
          this.mostrarAlerta('Error al eliminar el usuario', 'danger');
          this.cargando = false;
        },
      });
    }
  }

  abrirDialogRoles(usuario: Usuario): void {
    if (this.tieneRolAdmin(usuario)) {
      this.mostrarAlerta(
        'No se puede cambiar los roles de un administrador',
        'danger'
      );
      return;
    }

    const dialogRef = this.dialog.open(CambiarRolesDialogComponent, {
      width: '500px',
      data: { usuario },
    });

    dialogRef.afterClosed().subscribe((result) => {
      if (result) {
        this.cargarUsuarios();
        this.mostrarAlerta('Roles actualizados correctamente', 'success');
      }
    });
  }

  tieneRolAdmin(usuario: Usuario): boolean {
    if (!usuario || !usuario.roles || usuario.roles.length === 0) {
      return false;
    }
    return usuario.roles.some((rol) => rol.nombre === 'admin');
  }

  mostrarAlerta(mensaje: string, tipo: string): void {
    this.mensaje = mensaje;
    this.tipoMensaje = tipo;
    setTimeout(() => {
      this.mensaje = '';
    }, 5000);
  }

  // Helpers para validaciones de formulario
  get nombreNoValido(): boolean {
    return this.formularioInvalido('nombre');
  }

  get apellidoNoValido(): boolean {
    return this.formularioInvalido('apellido');
  }

  get emailNoValido(): boolean {
    return this.formularioInvalido('email');
  }

  get passwordNoValido(): boolean {
    return this.formularioInvalido('password');
  }

  formularioInvalido(campo: string): boolean {
    return (
      (this.formularioEmpleado.get(campo)?.invalid &&
        this.formularioEmpleado.get(campo)?.touched) ||
      false
    );
  }
}
