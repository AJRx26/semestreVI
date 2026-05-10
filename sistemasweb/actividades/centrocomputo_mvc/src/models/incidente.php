<?php

namespace app\models;

class Incidente
{
	public int $id;
	public string $nombre;
	public string $correo;
	public string $rol;
	public string $tipo;
	public string $descripcion;
	public ?string $evidencia;
	public string $fecha_registro;

	public function __construct(
		int $id,
		string $nombre,
		string $correo,
		string $rol,
		string $tipo,
		string $descripcion,
		?string $evidencia,
		string $fecha_registro
	) {
		$this->id = $id;
		$this->nombre = $nombre;
		$this->correo = $correo;
		$this->rol = $rol;
		$this->tipo = $tipo;
		$this->descripcion = $descripcion;
		$this->evidencia = $evidencia;
		$this->fecha_registro = $fecha_registro;
	}
}
