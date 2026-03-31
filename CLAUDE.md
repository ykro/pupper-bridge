# pupper-bridge — Pi HTTP Bridge

## Qué es
Servidor FastAPI que corre en la Raspberry Pi del Mini Pupper 2. Expone control de servos (HardwareInterface directo), ojos LCD (Pygame + ST7789), cámara, LiDAR y navegación como endpoints HTTP.

**Este servidor corre EN EL PI, no en la laptop.**

## Arquitectura
```
Laptop (pupper-sentiment-bridge)       Pi (este servidor)
┌──────────────────────────┐           ┌─────────────────────────────┐
│ BridgeClient ─────────────┼──HTTP──▶  │ pi_bridge.py :9090          │
│                          │           │ ├─ hardware_controller.py   │
│                          │           │ │   └─ HardwareInterface    │
│                          │           │ ├─ eye_renderer.py          │
│                          │           │ │   └─ ST7789 LCD (SPI)     │
│                          │           │ ├─ camera_capture.py        │
│                          │           │ └─ lidar_reader.py          │
└──────────────────────────┘           └─────────────────────────────┘
```

## Stack
- Python 3.10 (Pi BSP), uv
- FastAPI + uvicorn
- MangDang HardwareInterface (servos directos, sin ROS2)
- Pygame + ST7789 LCD (ojos animados)
- numpy, OpenCV

## Cómo ejecutar

### En el Pi (producción)
```bash
git clone https://github.com/sidikalamini/eyes-animation.git vendor/eyes-animation
sudo apt install -y libportaudio2
uv venv --python 3.10 --system-site-packages
uv sync
uv run python -m uvicorn src.pi_bridge:app --host 0.0.0.0 --port 9090
```

### En la laptop (mock)
```bash
uv sync
uv run python -m uvicorn src.pi_bridge:app --host 0.0.0.0 --port 9090
```

## Endpoints principales

| Endpoint | Método | Body | Descripción |
|----------|--------|------|-------------|
| `/react` | POST | `{mood}` | Reacción completa: ojos + pose + dance |
| `/eyes` | POST | `{mood}` | Cambiar expresión de ojos en LCD |
| `/pose` | POST | `{pose}` | Pose predefinida |
| `/dance` | POST | `{style}` | Secuencia de baile |
| `/stop` | POST | — | Parada de emergencia |
| `/status` | GET | — | Estado del robot |

## Mock mode
Si `MangDang` no está disponible, automáticamente usa MockHardwareController (logea comandos en consola).

## Variables de entorno
- `ROBOT_NAME` — nombre del robot (default: `mini_pupper_2`)
