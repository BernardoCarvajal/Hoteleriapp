export interface Cliente {
  id: number;
  nombre: string;
  email?: string;
  telefono?: string;
}

export interface Habitacion {
  id: number;
  numero: string;
  tipo: string;
  precio: number;
}

export interface Pago {
  id: number;
  monto: number;
  fecha: string;
  metodo: string;
}

export interface Reserva {
  id: number;
  codigo: string;
  fechaInicio: string;
  fechaFin: string;
  estado: 'pendiente' | 'confirmada' | 'cancelada' | 'completada';
  cliente?: Cliente;
  habitaciones?: Habitacion[];
  pagos?: Pago[];
  total?: number;
  pagado?: number;
  createdAt?: string;
  updatedAt?: string;
} 