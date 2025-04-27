import { Component, OnInit } from '@angular/core';
import { FormBuilder, FormGroup } from '@angular/forms';
import { MatSnackBar } from '@angular/material/snack-bar';
import { ReportesService, ReporteReservas, ReporteReserva, ReporteOcupacion } from '../../services/reportes.service';
import { MatTableDataSource } from '@angular/material/table';
import { AuthService } from '../../services/auth.service';
import { Router } from '@angular/router';

@Component({
  selector: 'app-dashboard',
  standalone: false,
  templateUrl: './dashboard.component.html',
  styleUrl: './dashboard.component.css'
})
export class DashboardComponent implements OnInit {
  filtroForm: FormGroup;
  reporteReservas: ReporteReservas | null = null;
  filtroOcupacionForm: FormGroup;
  reporteOcupacion: ReporteOcupacion | null = null;
  cargando = false;
  error: string | null = null;
  maxFecha = new Date();
  tabActivo = 'reservas';
  
  // Columnas para la tabla de reservas
  columnas: string[] = ['codigo', 'cliente', 'fechas', 'estado', 'habitaciones', 'pagos'];
  
  // DataSource para la tabla
  dataSource = new MatTableDataSource<ReporteReserva>([]);

  constructor(
    private fb: FormBuilder,
    private reportesService: ReportesService,
    private snackBar: MatSnackBar,
    private authService: AuthService,
    private router: Router
  ) {
    this.filtroForm = this.fb.group({
      fechaInicio: [null],
      fechaFin: [null],
      estado: [''],
      clienteId: ['']
    });
    
    this.filtroOcupacionForm = this.fb.group({
      fecha: [new Date()]
    });
  }

  ngOnInit(): void {
    // Verificar si el usuario es administrador
    this.verificarAcceso();
    // Cargar datos iniciales
    this.cargarReporte();
  }

  verificarAcceso(): void {
    this.cargando = true;
    this.authService.getPerfil().subscribe({
      next: (usuario) => {
        this.cargando = false;
        if (!this.tieneRolAdmin(usuario)) {
          this.snackBar.open('Acceso restringido. Solo para administradores.', 'Cerrar', {
            duration: 5000
          });
          this.router.navigate(['/']);
        }
      },
      error: (error) => {
        this.cargando = false;
        console.error('Error al verificar permisos', error);
        this.snackBar.open('Error al verificar permisos. Redirigiendo...', 'Cerrar', {
          duration: 3000
        });
        this.router.navigate(['/']);
      }
    });
  }

  tieneRolAdmin(usuario: any): boolean {
    if (!usuario || !usuario.roles || usuario.roles.length === 0) {
      return false;
    }
    return usuario.roles.some((rol: any) => rol.nombre === 'admin');
  }

  cambiarTab(tab: string): void {
    this.tabActivo = tab;
    if (tab === 'reservas') {
      this.cargarReporte();
    } else if (tab === 'ocupacion') {
      this.cargarReporteOcupacion();
    }
  }

  cargarReporte(): void {
    if (this.tabActivo !== 'reservas') return;
    
    this.cargando = true;
    this.error = null;

    const filtros = this.obtenerFiltros();

    this.reportesService.getReporteReservas(
      filtros.fechaInicio,
      filtros.fechaFin,
      filtros.estado,
      filtros.clienteId
    ).subscribe({
      next: (reporte) => {
        this.reporteReservas = reporte;
        this.dataSource.data = reporte.reservas;
        this.cargando = false;
      },
      error: (error) => {
        console.error('Error al cargar reporte de reservas', error);
        this.error = 'No se pudo cargar el reporte. Por favor intente de nuevo.';
        this.cargando = false;
      }
    });
  }

  limpiarFiltros(): void {
    this.filtroForm.reset({
      fechaInicio: null,
      fechaFin: null,
      estado: '',
      clienteId: ''
    });
    this.cargarReporte();
  }

  exportarCSV(): void {
    if (!this.reporteReservas || this.reporteReservas.reservas.length === 0) return;
    
    try {
      // Preparar los datos para el CSV
      const encabezados = 'Código,Cliente,Fecha Inicio,Fecha Fin,Estado,Habitaciones,Total Pagado,Total Pendiente\n';
      
      const filas = this.reporteReservas.reservas.map(r => {
        return [
          r.codigo_reserva,
          r.cliente,
          r.fecha_inicio,
          r.fecha_fin,
          r.estado,
          r.habitaciones.join(' | '),
          r.total_pagado,
          r.total_pendiente
        ].join(',');
      }).join('\n');
      
      const csvData = encabezados + filas;
      const blob = new Blob([csvData], { type: 'text/csv;charset=utf-8;' });
      const url = URL.createObjectURL(blob);
      
      // Crear enlace para descargar
      const link = document.createElement('a');
      const fecha = new Date().toISOString().slice(0, 10);
      link.setAttribute('href', url);
      link.setAttribute('download', `reporte_reservas_${fecha}.csv`);
      link.style.visibility = 'hidden';
      
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      
      this.snackBar.open('Reporte CSV descargado exitosamente', 'Cerrar', {
        duration: 3000
      });
    } catch (error) {
      console.error('Error al exportar CSV', error);
      this.snackBar.open('Error al exportar CSV', 'Cerrar', {
        duration: 3000
      });
    }
  }

  private obtenerFiltros(): any {
    const valores = this.filtroForm.value;
    
    return {
      fechaInicio: valores.fechaInicio ? this.formatearFechaISO(valores.fechaInicio) : undefined,
      fechaFin: valores.fechaFin ? this.formatearFechaISO(valores.fechaFin) : undefined,
      estado: valores.estado || undefined,
      clienteId: valores.clienteId ? parseInt(valores.clienteId, 10) : undefined
    };
  }

  cargarReporteOcupacion(): void {
    if (this.tabActivo !== 'ocupacion') return;
    
    this.cargando = true;
    this.error = null;

    const fecha = this.filtroOcupacionForm.value.fecha;
    const fechaISO = fecha ? this.formatearFechaISO(fecha) : undefined;

    this.reportesService.getReporteOcupacion(fechaISO).subscribe({
      next: (reporte) => {
        this.reporteOcupacion = reporte;
        this.cargando = false;
      },
      error: (error) => {
        console.error('Error al cargar reporte de ocupación', error);
        this.error = 'No se pudo cargar el reporte de ocupación. Por favor intente de nuevo.';
        this.cargando = false;
      }
    });
  }

  obtenerTiposHabitacion(): string[] {
    if (!this.reporteOcupacion || !this.reporteOcupacion.desglose_por_tipo) {
      return [];
    }
    return Object.keys(this.reporteOcupacion.desglose_por_tipo);
  }

  formatearFecha(fecha: string): string {
    if (!fecha) return '';
    const f = new Date(fecha);
    return `${f.getDate().toString().padStart(2, '0')}/${(f.getMonth()+1).toString().padStart(2, '0')}/${f.getFullYear()}`;
  }

  private formatearFechaISO(fecha: Date): string {
    if (!fecha) return '';
    return `${fecha.getFullYear()}-${(fecha.getMonth()+1).toString().padStart(2, '0')}-${fecha.getDate().toString().padStart(2, '0')}`;
  }

  formatearMoneda(valor: number): string {
    return new Intl.NumberFormat('es-ES', { style: 'currency', currency: 'EUR' }).format(valor);
  }

  obtenerClaseEstado(estado: string): string {
    switch (estado?.toLowerCase()) {
      case 'pendiente':
        return 'estado-pendiente';
      case 'confirmada':
        return 'estado-confirmada';
      case 'cancelada':
        return 'estado-cancelada';
      case 'completada':
        return 'estado-completada';
      default:
        return '';
    }
  }
} 