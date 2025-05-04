import {
  Component,
  Inject,
  OnInit,
  ElementRef,
  ViewChild,
} from '@angular/core';
import { MAT_DIALOG_DATA, MatDialogRef } from '@angular/material/dialog';
import { DomSanitizer, SafeUrl } from '@angular/platform-browser';
import { ReservasService } from '../../services/reservas.service';
import { environment } from '../../../environments/environment';
import { CommonModule } from '@angular/common';
import { MatButtonModule } from '@angular/material/button';
import { MatIconModule } from '@angular/material/icon';
import jsPDF from 'jspdf';
import html2canvas from 'html2canvas';

@Component({
  selector: 'app-ticket',
  templateUrl: './ticket.component.html',
  styleUrl: './ticket.component.css',
  standalone: true,
  imports: [CommonModule, MatButtonModule, MatIconModule],
})
export class TicketComponent implements OnInit {
  @ViewChild('ticketContent') ticketContent!: ElementRef;

  cargando = true;
  error = '';
  ticketUrl: SafeUrl | null = null;
  qrDataUrl: string = '';
  generandoPDF = false;

  constructor(
    @Inject(MAT_DIALOG_DATA) public reserva: any,
    private dialogRef: MatDialogRef<TicketComponent>,
    private reservasService: ReservasService,
    private sanitizer: DomSanitizer
  ) {}

  ngOnInit() {
    this.generarQR();
    this.cargarTicket();
  }

  cargarTicket() {
    if (!this.reserva || !this.reserva.id) {
      this.error =
        'No se pudo cargar el ticket: información de reserva incompleta';
      this.cargando = false;
      return;
    }

    // Simulamos la carga del ticket para que se vea la interfaz
    setTimeout(() => {
      this.cargando = false;
    }, 1000);

    // Comentamos la llamada al servidor ya que probablemente no está implementada aún
    /*
    this.reservasService.obtenerTicket(this.reserva.id).subscribe({
      next: (blob) => {
        this.ticketUrl = this.sanitizer.bypassSecurityTrustUrl(URL.createObjectURL(blob));
        this.cargando = false;
      },
      error: (err) => {
        console.error('Error al obtener ticket', err);
        this.error = 'No se pudo cargar el ticket';
        this.cargando = false;
      }
    });
    */
  }

  generarQR() {
    // Datos para el QR
    const ticketData = {
      id: this.reserva.id,
      codigo: this.reserva.code,
      fechaInicio: this.formatearFecha(this.reserva.startDate),
      fechaFin: this.formatearFecha(this.reserva.endDate),
      habitaciones: this.reserva.rooms || [],
      total: this.reserva.total,
    };

    // URL para acceder al ticket directamente
    const ticketUrl = `${environment.apiUrl.replace('/api', '')}/ticket/${
      this.reserva.id
    }`;

    // Generamos el QR usando una API
    this.qrDataUrl = `https://api.qrserver.com/v1/create-qr-code/?size=150x150&data=${encodeURIComponent(
      ticketUrl
    )}`;
  }

  formatearFecha(fecha: any): string {
    if (!fecha) return '';
    const d = new Date(fecha);
    const options: Intl.DateTimeFormatOptions = {
      year: 'numeric',
      month: 'long',
      day: 'numeric',
    };
    return d.toLocaleDateString('es-ES', options);
  }

  getCurrentDate(): string {
    const today = new Date();
    const options: Intl.DateTimeFormatOptions = {
      year: 'numeric',
      month: 'long',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
    };
    return today.toLocaleDateString('es-ES', options);
  }

  cerrar() {
    this.dialogRef.close();
  }

  descargarTicket() {
    if (this.generandoPDF) return;

    this.generandoPDF = true;

    setTimeout(() => {
      // Asegurarse de que el contenido del ticket está cargado
      const ticketElement = document.querySelector(
        '.ticket-content'
      ) as HTMLElement;

      if (!ticketElement) {
        this.generandoPDF = false;
        return;
      }

      html2canvas(ticketElement, {
        scale: 2, // Mayor calidad
        useCORS: true, // Para cargar imágenes de otros dominios (QR)
        allowTaint: true,
        backgroundColor: '#ffffff',
      })
        .then((canvas) => {
          const imgData = canvas.toDataURL('image/png');
          const pdf = new jsPDF('p', 'mm', 'a4');
          const imgWidth = 210; // A4 width in mm
          const pageHeight = 297; // A4 height in mm
          const imgHeight = (canvas.height * imgWidth) / canvas.width;

          // Añadir encabezado
          pdf.setFontSize(18);
          pdf.setTextColor(40);
          pdf.text('Hoteleriapp - Ticket de Reserva', 105, 15, {
            align: 'center',
          });

          // Añadir imagen del ticket
          pdf.addImage(imgData, 'PNG', 0, 25, imgWidth, imgHeight);

          // Añadir pie de página
          pdf.setFontSize(10);
          pdf.setTextColor(100);
          pdf.text(
            'Este documento es un comprobante oficial de su reserva en Hoteleriapp',
            105,
            285,
            { align: 'center' }
          );
          pdf.text(`Generado el ${this.getCurrentDate()}`, 105, 290, {
            align: 'center',
          });

          // Guardar PDF
          pdf.save(`Ticket_Reserva_${this.reserva.code}.pdf`);
          this.generandoPDF = false;
        })
        .catch((err) => {
          console.error('Error al generar PDF', err);
          this.generandoPDF = false;
        });
    }, 500);
  }
}
