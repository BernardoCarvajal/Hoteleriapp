import { Component, OnInit } from '@angular/core';
import { FormBuilder, FormGroup, Validators } from '@angular/forms';
import { TranslateService } from '@ngx-translate/core';
import {
  ReservaService,
  Room,
  Reservation,
} from '../../services/reserva.service';
import { MatSnackBar } from '@angular/material/snack-bar';
import { MatDialog } from '@angular/material/dialog';
import { PagosComponent } from '../pagos/pagos.component';
import { AuthService } from '../../services/auth.service';
import { TicketComponent } from '../ticket/ticket.component';
import { LanguageService } from '../../services/language.service';

@Component({
  selector: 'app-reservas',
  standalone: false,
  templateUrl: './reservas.component.html',
  styleUrl: './reservas.component.css',
})
export class ReservasComponent implements OnInit {
  searchForm: FormGroup;
  availableRooms: Room[] = [];
  loading = false;
  searchPerformed = false;
  fechaLlegada: string = '';
  fechaSalida: string = '';
  numHuespedes: number = 1;
  habitacionesDisponibles: Room[] = [];
  buscando: boolean = false;
  error: string = '';
  minFechaLlegada: Date = new Date(Date.now() + 24 * 60 * 60 * 1000); // Mañana
  minFechaSalida: Date = this.getMinFechaSalida();
  misReservas: Reservation[] = [];
  viendoMisReservas: boolean = false;

  constructor(
    private fb: FormBuilder,
    private translate: TranslateService,
    private reservaService: ReservaService,
    private snackBar: MatSnackBar,
    private dialog: MatDialog,
    private authService: AuthService,
    private languageService: LanguageService
  ) {
    this.searchForm = this.fb.group({
      arrivalDate: ['', Validators.required],
      departureDate: ['', Validators.required],
      guests: [1, [Validators.required, Validators.min(1)]],
    });
  }

  ngOnInit(): void {}

  onSearch(): void {
    if (this.searchForm.valid) {
      this.loading = true;
      this.searchPerformed = true;
      const formData = this.searchForm.value;

      this.reservaService
        .consultarDisponibilidad(
          formData.arrivalDate,
          formData.departureDate,
          formData.guests
        )
        .subscribe({
          next: (response: Room[]) => {
            this.availableRooms = response;
            this.loading = false;
          },
          error: (error: any) => {
            console.error('Error al buscar disponibilidad:', error);
            this.snackBar.open(
              this.translate.instant('RESERVATION.ERROR'),
              this.translate.instant('COMMON.CLOSE'),
              { duration: 3000 }
            );
            this.loading = false;
          },
        });
    }
  }

  selectRoom(room: Room): void {
    const dialogRef = this.dialog.open(PagosComponent, {
      width: '500px',
      data: {
        room,
        arrivalDate: this.searchForm.get('arrivalDate')?.value,
        departureDate: this.searchForm.get('departureDate')?.value,
        guests: this.searchForm.get('guests')?.value,
      },
    });

    dialogRef.afterClosed().subscribe((result) => {
      if (result) {
        this.snackBar.open(
          this.translate.instant('RESERVATION.CONFIRMED'),
          this.translate.instant('COMMON.CLOSE'),
          { duration: 3000 }
        );
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
    if (
      this.fechaSalida &&
      new Date(this.fechaSalida) <= new Date(this.fechaLlegada)
    ) {
      this.fechaSalida = '';
    }
  }

  buscarDisponibilidad() {
    this.buscando = true;
    this.error = '';
    this.viendoMisReservas = false; // Asegurar que se muestra la vista de búsqueda

    // Validación extra en frontend
    if (!this.fechaLlegada || !this.fechaSalida) {
      this.error = this.translate.instant('RESERVATION.ERROR');
      this.buscando = false;
      return;
    }
    if (new Date(this.fechaSalida) <= new Date(this.fechaLlegada)) {
      this.error = this.translate.instant('RESERVATION.ERROR');
      this.buscando = false;
      return;
    }

    const fechaLlegadaStr = this.formatearFecha(this.fechaLlegada);
    const fechaSalidaStr = this.formatearFecha(this.fechaSalida);

    this.reservaService
      .consultarDisponibilidad(
        fechaLlegadaStr,
        fechaSalidaStr,
        this.numHuespedes
      )
      .subscribe({
        next: (data: Room[]) => {
          this.habitacionesDisponibles = data;
          this.buscando = false;
        },
        error: (err: any) => {
          this.error = this.translate.instant('RESERVATION.ERROR');
          this.buscando = false;
        },
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

  getImagenHabitacion(tipo: string | undefined | null): string {
    if (!tipo) {
      return 'https://images.unsplash.com/photo-1503676382389-4809596d5290?auto=format&fit=crop&w=400&q=80'; // Imagen por defecto
    }

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

  getTipoHabitacionTraducido(tipo: string | undefined | null): string {
    if (!tipo) return '';

    switch (tipo.toLowerCase()) {
      case 'individual':
        return this.translate.instant('ROOM.INDIVIDUAL');
      case 'doble':
        return this.translate.instant('ROOM.DOBLE');
      case 'familiar':
        return this.translate.instant('ROOM.FAMILIAR');
      case 'suite':
        return this.translate.instant('ROOM.SUITE');
      default:
        return tipo; // Devuelve el tipo original si no hay traducción
    }
  }

  verMisReservas(): void {
    this.viendoMisReservas = true;
    this.availableRooms = [];
    this.misReservas = [];
    this.reservaService.obtenerMisReservas().subscribe({
      next: (data: Reservation[]) => {
        this.misReservas = data || [];
      },
      error: (error: any) => {
        console.error('Error al obtener reservas:', error);
        this.snackBar.open(
          this.translate.instant('RESERVATION.ERROR'),
          this.translate.instant('COMMON.CLOSE'),
          { duration: 3000 }
        );
      },
    });
  }

  volverABuscar(): void {
    this.viendoMisReservas = false;
    this.misReservas = [];
  }

  verTicket(reserva: Reservation) {
    this.dialog.open(TicketComponent, {
      width: '400px',
      data: reserva,
    });
  }

  abrirPago(habitacion: Room) {
    const dialogRef = this.dialog.open(PagosComponent, {
      width: '420px',
      data: {
        habitacion,
        fecha_inicio: this.fechaLlegada,
        fecha_fin: this.fechaSalida,
        numHuespedes: this.numHuespedes,
      },
    });

    dialogRef.afterClosed().subscribe((result) => {
      if (result) {
        this.buscarDisponibilidad();
      }
    });
  }
}
