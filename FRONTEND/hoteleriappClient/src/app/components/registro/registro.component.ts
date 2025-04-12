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
  hide = true;

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
      password: ['', [Validators.required, Validators.minLength(6)]]
    });
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
