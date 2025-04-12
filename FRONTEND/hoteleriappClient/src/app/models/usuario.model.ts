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