import { Component, Inject, OnInit } from '@angular/core';
import { MAT_DIALOG_DATA, MatDialogRef } from '@angular/material/dialog';
import { ReservasService } from '../../services/reservas.service';

@Component({
  selector: 'app-pagos',
  standalone: false,
  templateUrl: './pagos.component.html',
  styleUrl: './pagos.component.css'
})
export class PagosComponent implements OnInit {
  numero: string = '';
  expiracion: string = '';
  cvv: string = '';
  nombre: string = '';
  cargando: boolean = false;
  error: string = '';
  exito: boolean = false;
  
  // Información de costo
  calculandoCosto: boolean = true;
  costoReserva: any = null;
  
  constructor(
    @Inject(MAT_DIALOG_DATA) public data: any,
    private reservasService: ReservasService,
    private dialogRef: MatDialogRef<PagosComponent>
  ) {}
  
  ngOnInit() {
    this.calcularCostoReserva();
  }
  
  calcularCostoReserva() {
    this.calculandoCosto = true;
    const fechaInicio = this.formatearFecha(this.data?.fecha_inicio);
    const fechaFin = this.formatearFecha(this.data?.fecha_fin);
    const habitacionId = this.data?.habitacion?.id || 0;
    
    this.reservasService.calcularCostoReserva(fechaInicio, fechaFin, habitacionId).subscribe({
      next: (respuesta) => {
        this.costoReserva = respuesta;
        this.calculandoCosto = false;
      },
      error: (err) => {
        this.error = 'Error al calcular el costo de la reserva';
        this.calculandoCosto = false;
      }
    });
  }

  pagar() {
    if (!this.costoReserva) {
      this.error = 'No se ha calculado el costo de la reserva';
      return;
    }
    
    this.cargando = true;
    this.error = '';
    this.exito = false;

    const reservaPayload = {
      fecha_inicio: this.formatearFecha(this.data?.fecha_inicio),
      fecha_fin: this.formatearFecha(this.data?.fecha_fin),
      numero_huespedes: this.data?.numHuespedes || 1,
      detalles: [
        {
          habitacion_id: this.data?.habitacion?.id || 0
        }
      ]
    };

    this.reservasService.crearReserva(reservaPayload).subscribe({
      next: (reservaResp) => {
        const reservaId = (reservaResp as any).id;
        const ultimos4 = this.numero ? this.numero.replace(/\s+/g, '').slice(-4) : '';
        const referencia = `Tarjeta ****${ultimos4}`;
        const payloadPago = {
          reserva_id: reservaId,
          monto: this.costoReserva.total, // Usar el total calculado por la API
          metodo_pago: 'tarjeta',
          referencia_pago: referencia
        };

        this.reservasService.realizarPago(payloadPago).subscribe({
          next: (resp) => {
            this.exito = true;
            this.cargando = false;
            setTimeout(() => this.dialogRef.close(true), 1500);
          },
          error: (err) => {
            this.error = 'Error al procesar el pago';
            this.cargando = false;
          }
        });
      },
      error: (err) => {
        this.error = 'Error al crear la reserva';
        this.cargando = false;
      }
    });
  }

  formatearFecha(fecha: any): string {
    if (!fecha) return '';
    if (typeof fecha === 'string' && /^\d{4}-\d{2}-\d{2}$/.test(fecha)) return fecha;
    const d = new Date(fecha);
    const month = (d.getMonth() + 1).toString().padStart(2, '0');
    const day = d.getDate().toString().padStart(2, '0');
    return `${d.getFullYear()}-${month}-${day}`;
  }
}
