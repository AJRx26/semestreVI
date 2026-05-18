<?php

namespace app\data;

use app\models\incidente;
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

	public function __destruct()
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
			die('Error de conexion: ' . self::$mysqli->connect_error);
		}
	}

	public function insertarIncidente(array $datos): bool
	{
		$sql = "INSERT INTO incidente (nombre, correo, rol, tipo, descripcion, evidencia) VALUES (?, ?, ?, ?, ?, ?)";

		$stmt = self::$mysqli->prepare($sql);
		$stmt->bind_param(
			"ssssss"
			$datos['nombre'],
			$datos['correo'],
			$datos['rol'],
			$datos['tipo'],
			$datos['descripcion'],
			$datos['evidencia']
		);

		$resultado = $stmt->execute();
		$stmt->close();

		return $resultado
	}
}
