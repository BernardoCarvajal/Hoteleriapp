export interface Usuario{
    id?: number;
    nombre: string;
    apellido: string;
    email: string;
    telefono: string;
    documento_identidad: string;
    password?: string;
    activo?: boolean;
    roles?: Rol[];
}

export interface Rol {
    id?: number;
    nombre: string;
    descripcion?: string;
}

export interface LoginResponse {
    access_token: string;
    token_type: string;
}

export interface UsuarioRegistro{
    nombre: string;
    apellido: string;
    email: string;
    telefono: string;
    documento_identidad: string;
    password: string;
}

export interface usuarioLogin{
    email: string;
    password: string;
}