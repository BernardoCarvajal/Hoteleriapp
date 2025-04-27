import { Component } from '@angular/core';
import { ReservasService } from '../../services/reservas.service';
import { MatDialog } from '@angular/material/dialog';
import { PagosComponent } from '../pagos/pagos.component';
import { AuthService } from '../../services/auth.service';
import { TicketComponent } from '../ticket/ticket.component';

@Component({
  selector: 'app-reservas',
  standalone: false,
  templateUrl: './reservas.component.html',
  styleUrl: './reservas.component.css'
})
export class ReservasComponent {
  fechaLlegada: string = '';
  fechaSalida: string = '';
  numHuespedes: number = 1;
  habitacionesDisponibles: any[] = [];
  buscando: boolean = false;
  error: string = '';
  minFechaLlegada: Date = new Date(Date.now() + 24 * 60 * 60 * 1000); // Mañana
  minFechaSalida: Date = this.getMinFechaSalida();
  misReservas: any[] = [];
  viendoMisReservas: boolean = false;

  constructor(private reservasService: ReservasService, private dialog: MatDialog, private authService: AuthService) {}

  abrirPago(habitacion: any) {
    const dialogRef = this.dialog.open(PagosComponent, {
      width: '420px',
      data: {
        habitacion,
        fecha_inicio: this.fechaLlegada,
        fecha_fin: this.fechaSalida,
        numHuespedes: this.numHuespedes
      }
    });

    dialogRef.afterClosed().subscribe(result => {
      if (result) {
        // Si el pago fue exitoso, recarga la disponibilidad
        this.buscarDisponibilidad();
      }
    });
  }

  getMinFechaSalida(): Date {
    if (!this.fechaLlegada) {
      return new Date(this.minFechaLlegada); // Por defecto, igual que minFechaLlegada
    }
    const llegada = new Date(this.fechaLlegada);
    return new Date(llegada.getTime() + 24 * 60 * 60 * 1000); // Un día después de llegada
  }

  setFechaLlegada(fecha: any) {
    this.fechaLlegada = fecha;
    this.minFechaSalida = this.getMinFechaSalida();
    // Si la fecha de salida es anterior o igual, la resetea
    if (this.fechaSalida && new Date(this.fechaSalida) <= new Date(this.fechaLlegada)) {
      this.fechaSalida = '';
    }
  }

  buscarDisponibilidad() {
    this.buscando = true;
    this.error = '';
    this.viendoMisReservas = false; // Asegurar que se muestra la vista de búsqueda

    // Validación extra en frontend
    if (!this.fechaLlegada || !this.fechaSalida) {
      this.error = 'Debes seleccionar ambas fechas.';
      this.buscando = false;
      return;
    }
    if (new Date(this.fechaSalida) <= new Date(this.fechaLlegada)) {
      this.error = 'La fecha de salida debe ser posterior a la fecha de llegada';
      this.buscando = false;
      return;
    }

    const fechaLlegadaStr = this.formatearFecha(this.fechaLlegada);
    const fechaSalidaStr = this.formatearFecha(this.fechaSalida);

    this.reservasService.consultarDisponibilidad(fechaLlegadaStr, fechaSalidaStr, this.numHuespedes)
      .subscribe({
        next: (data) => {
          this.habitacionesDisponibles = data;
          this.buscando = false;
        },
        error: (err) => {
          this.error = 'Error al consultar disponibilidad';
          this.buscando = false;
        }
      });
  }

  // Método para formatear la fecha
  formatearFecha(fecha: any): string {
    if (!fecha) return '';
    // Si ya es string, retorna igual
    if (typeof fecha === 'string') return fecha;
    // Si es Date, formatea
    const d = new Date(fecha);
    const month = (d.getMonth() + 1).toString().padStart(2, '0');
    const day = d.getDate().toString().padStart(2, '0');
    return `${d.getFullYear()}-${month}-${day}`;
  }

  getImagenHabitacion(tipo: string): string {
    switch (tipo.toLowerCase()) {
      case 'individual':
        return 'https://images.unsplash.com/photo-1506744038136-46273834b3fb?auto=format&fit=crop&w=400&q=80'; // Individual
      case 'doble':
        return 'https://images.unsplash.com/photo-1507089947368-19c1da9775ae?auto=format&fit=crop&w=400&q=80'; // Doble
      case 'familiar':
        return 'https://images.unsplash.com/photo-1512918728675-ed5a9ecdebfd?auto=format&fit=crop&w=400&q=80'; // Familiar
      case 'suite':
        return 'https://images.unsplash.com/photo-1464983953574-0892a716854b?auto=format&fit=crop&w=400&q=80'; // Suite
      default:
        return 'https://images.unsplash.com/photo-1503676382389-4809596d5290?auto=format&fit=crop&w=400&q=80'; // Genérica
    }
  }

  verMisReservas() {
    this.viendoMisReservas = true;
    this.misReservas = [];
    this.habitacionesDisponibles = []; // Limpiar las habitaciones disponibles
    this.reservasService.obtenerMisReservas().subscribe({
      next: (data) => {
        this.misReservas = data || [];
      },
      error: () => {
        this.misReservas = [];
      }
    });
  }

  volverABuscar() {
    this.viendoMisReservas = false;
  }

  verTicket(reserva: any) {
    this.dialog.open(TicketComponent, {
      width: '400px',
      data: reserva
    });
  }
}
