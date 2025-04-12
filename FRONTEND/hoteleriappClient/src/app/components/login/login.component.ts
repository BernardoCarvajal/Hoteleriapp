import { Component } from '@angular/core';
import { FormBuilder, FormGroup, Validators } from '@angular/forms';
import { MatSnackBar } from '@angular/material/snack-bar';

@Component({
  selector: 'app-login',
  standalone: false,
  templateUrl: './login.component.html',
  styleUrl: './login.component.css'
})
export class LoginComponent {

  loginForm: FormGroup;
  hide = true;

  constructor(
    private fb: FormBuilder,
    private snackBar: MatSnackBar
  ){
    this.loginForm = this.fb.group({
      email: ['', [Validators.required, Validators.email]],
      password: ['', [Validators.required, Validators.minLength(6)]]
    })
  }

  onSubmit(){
    if(this.loginForm.valid){
      const email = this.loginForm.get('email')?.value;
      const password = this.loginForm.get('password')?.value;
      console.log(email, password);
    }else{
      this.snackBar.open('Por favor, complete todos los campos', 'Cerrar', {
        duration: 3000
      });
    }
  }
}
