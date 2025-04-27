import { Component } from '@angular/core';
import { FormBuilder, FormGroup, Validators } from '@angular/forms';
import { Router } from '@angular/router';
import { MatSnackBar } from '@angular/material/snack-bar';
import { AuthService } from '../../services/auth.service';

@Component({
  selector: 'app-registro',
  standalone: false,
  templateUrl: './registro.component.html',
  styleUrl: './registro.component.css'
})
export class RegistroComponent {

  registroForm: FormGroup;
  hidePassword = true;
  hideConfirmPassword = true;

  constructor(
    private fb: FormBuilder,
    private snackBar: MatSnackBar,
    private router: Router,
    private authService: AuthService
  ){
    this.registroForm = this.fb.group({
      nombre: ['', [Validators.required, Validators.minLength(2)]],
      apellido: ['', [Validators.required, Validators.minLength(2)]],
      email: ['', [Validators.required, Validators.email]],
      telefono: ['', [Validators.required, Validators.pattern('^[0-9]{10}$')]],
      documento_identidad: ['', [Validators.required, Validators.minLength(5)]],
      password: ['', [Validators.required, Validators.minLength(8)]],
      confirmPassword: ['', [Validators.required]]
    }, { validator: this.passwordMatchValidator });
  }

  // Validador personalizado para verificar que las contraseñas coincidan
  passwordMatchValidator(form: FormGroup) {
    return form.get('password')?.value === form.get('confirmPassword')?.value
      ? null : { 'mismatch': true };
  }

  getErrorMessage(field: string): string {
    const control = this.registroForm.get(field);
    if (control?.hasError('required')) return 'Este campo es obligatorio';
    if (field === 'email' && control?.hasError('email')) return 'Ingresa un email válido';
    if (field === 'telefono' && control?.hasError('pattern')) return 'Ingresa un número de teléfono válido (10 dígitos)';
    if (field === 'password' && control?.hasError('minlength')) return 'La contraseña debe tener al menos 8 caracteres';
    if (field === 'documento_identidad' && control?.hasError('minlength')) return 'El documento debe tener al menos 5 caracteres';
    if (field === 'nombre' && control?.hasError('minlength')) return 'El nombre debe tener al menos 2 caracteres';
    if (field === 'apellido' && control?.hasError('minlength')) return 'El apellido debe tener al menos 2 caracteres';
    return '';
  }

  getPasswordMismatchError(): boolean {
    return this.registroForm.hasError('mismatch') && this.registroForm.get('confirmPassword')?.touched === true;
  }

  onSubmit(){
    if(this.registroForm.valid){
      const formData = this.registroForm.value;
      this.authService.register(formData).subscribe({
        next: (response: any) => {
          console.log('Registro exitoso', response);
          this.router.navigate(['/login']);
        },
        error: (error: any) => {
          console.error('Error en el registro', error);
          this.snackBar.open('Error en el registro', 'Cerrar', {
            duration: 3000
          });
        }
      });
    }else{
      this.snackBar.open('Por favor, complete todos los campos', 'Cerrar', {
        duration: 3000
      });
    }
  }
  
}
