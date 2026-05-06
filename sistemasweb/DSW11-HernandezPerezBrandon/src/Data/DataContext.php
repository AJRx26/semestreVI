<?php

namespace App\Data;

use App\Models\Incidente;
use mysqli;

class DataContext
{
	private static mysqli $mysqli;
	private array $settings;

	public function __construct(array $settings)
	{
		$this->settings = $settings;
		$this->conectar();
	}

	public function __deconstruct()
	{
		self::$mysqli->close();
	}

	protected function conectar()
	{
		self::$mysqli = new mysqli(
			$this->settings['db']['host'],
			$this->settings['db']['username'],
			$this->settings['db']['password'],
			$this->settings['db']['database']
		);
		
		if (self::$mysqli->connect_errno) {
			die('Error de conexión: ' . self::$mysqli->connect_error);
		}
	}

	public function insertarIncidente(array $datos): bool
	{
		$sql = "INSERT INTO incidente (nombre, correo, rol, tipo, descripcion, evidencia) VALUES (?, ?, ?, ?, ?, ?)";
		$stmt = self::$mysqli->prepare($sql);
		$stmt->bind_param(
			"ssssss",
			$datos['nombre'],
			$datos['correo'],
			$datos['rol'],
			$datos['tipo'],
			$datos['descripcion'],
			$datos['evidencia']
		);

		$resultado = $stmt->execute();
		$stmt->close();

		return $resultado;
	}

	public function obtenerIncidentes(): array
	{
		$consulta = "SELECT * FROM incidente ORDER BY fecha_registro DESC";
		$resultado = self::$mysqli->query($consulta);
		$incidentes = [];

		while ($fila = $resultado->fetch_assoc()) {
			$incidentes[] = new Incidente(
				(int)$fila['id'],
				$fila['nombre'],
				$fila['correo'],
				$fila['rol'],
				$fila['tipo'],
				$fila['descripcion'],
				$fila['evidencia'],
				$fila['fecha_registro']
			);
		}
		return $incidentes;
	}
	
}
