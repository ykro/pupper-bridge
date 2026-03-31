# pupper-bridge — Pi HTTP Bridge para Mini Pupper 2

Servidor FastAPI que corre en la Raspberry Pi del Mini Pupper 2. Expone control de servos, ojos LCD, cámara, LiDAR y navegación como endpoints HTTP.

**Este servidor corre EN EL PI, no en la laptop.**

## Arquitectura

```
Laptop (pupper-sentiment-bridge)       Pi (este servidor)
┌──────────────────────────┐           ┌─────────────────────────────┐
│ main.py                  │           │ pi_bridge.py :9090          │
│ ├─ Gemini Live API       │           │ ├─ hardware_controller.py   │
│ ├─ AudioManager          │           │ │   └─ HardwareInterface    │
│ └─ BridgeClient ─────────┼──HTTP──▶  │ ├─ eye_renderer.py         │
│                          │           │ │   └─ ST7789 LCD (SPI)     │
└──────────────────────────┘           │ ├─ camera_capture.py        │
                                       │ ├─ lidar_reader.py          │
                                       │ └─ poses.py (numpy 3x4)    │
                                       └─────────────────────────────┘
```

## Stack
- Python 3.10 (Pi BSP), uv
- FastAPI + uvicorn
- MangDang HardwareInterface (servos directos, sin ROS2)
- Pygame + ST7789 LCD (ojos animados)
- OpenCV, numpy

## Setup en el Pi

### 1. Clonar el repo
```bash
git clone git@github.com:YOUR_USER/pupper-bridge.git ~/pupper-bridge
cd ~/pupper-bridge
```

### 2. Clonar librería de ojos
```bash
git clone https://github.com/sidikalamini/eyes-animation.git vendor/eyes-animation
```

### 3. Instalar dependencias del sistema
```bash
sudo apt install -y libportaudio2
```

### 4. Crear venv con system site-packages
El Pi necesita `MangDang.mini_pupper.HardwareInterface`, `spidev` y `RPi.GPIO` del Python del sistema (BSP del Mini Pupper):
```bash
uv venv --python 3.10 --system-site-packages
uv sync
```

### 5. Iniciar el bridge
```bash
uv run python -m uvicorn src.pi_bridge:app --host 0.0.0.0 --port 9090
```

## Mock mode (laptop, sin robot)

Si `MangDang` no está disponible, corre automáticamente en mock:
```bash
uv sync
uv run python -m uvicorn src.pi_bridge:app --host 0.0.0.0 --port 9090
```

En mock:
- Servos se logean en consola (no se mueven)
- Ojos se logean en consola (no hay LCD)
- Cámara retorna placeholder JPEG
- LiDAR retorna datos simulados
- Navegación simula llegada en 5s

## Endpoints

| Endpoint | Método | Body | Descripción |
|----------|--------|------|-------------|
| `/react` | POST | `{mood}` | **Reacción completa**: ojos + pose + dance según mood |
| `/eyes` | POST | `{mood}` | Cambiar expresión de ojos en LCD |
| `/pose` | POST | `{pose: sit\|stand\|greet\|excited\|sad}` | Pose predefinida |
| `/dance` | POST | `{style: default\|wiggle}` | Secuencia de baile |
| `/cmd_vel` | POST | `{linear_x, linear_y, angular_z, duration}` | Comando de velocidad |
| `/stop` | POST | — | Parada de emergencia |
| `/camera/frame` | GET | — | Snapshot JPEG |
| `/lidar/scan` | GET | — | Scan LiDAR (distancias + ángulos) |
| `/lidar/people` | GET | — | Personas detectadas |
| `/status` | GET | — | Estado del robot |
| `/tracking/start` | POST | — | Habilitar tracking |
| `/tracking/stop` | POST | — | Deshabilitar tracking |
| `/nav/goto` | POST | `{x, y, theta}` | Objetivo de navegación |
| `/nav/status` | GET | — | Estado de navegación |
| `/nav/cancel` | POST | — | Cancelar navegación |

### Mood → Reacción (`/react`)

| Mood | Ojos | Pose | Dance |
|------|------|------|-------|
| happy | Crescent/green | excited | wiggle |
| sad | Blue | sad | — |
| angry | Red | stand | — |
| surprised | Big/neon | greet | default |
| neutral | Default/cyber | stand | — |
| curious | Amber | greet | — |

### Probar con curl
```bash
# Status
curl http://PI_IP:9090/status

# Reacción de sentimiento (ojos + pose + dance)
curl -X POST http://PI_IP:9090/react \
  -H "Content-Type: application/json" \
  -d '{"mood": "happy"}'

# Solo ojos
curl -X POST http://PI_IP:9090/eyes \
  -H "Content-Type: application/json" \
  -d '{"mood": "surprised"}'

# Pose
curl -X POST http://PI_IP:9090/pose \
  -H "Content-Type: application/json" \
  -d '{"pose": "sit"}'

# Dance
curl -X POST http://PI_IP:9090/dance \
  -H "Content-Type: application/json" \
  -d '{"style": "wiggle"}'

# Parada
curl -X POST http://PI_IP:9090/stop
```

## Estructura del código
```
src/
├── pi_bridge.py            # FastAPI app, todos los endpoints
├── hardware_controller.py  # HardwareController (servos) + MockHardwareController
├── eye_renderer.py         # EyeRenderer (Pygame → ST7789 LCD)
├── poses.py                # 5 poses numpy 3x4 (abduction, hip, knee × 4 patas)
├── camera_capture.py       # Captura JPEG: web interface → mock
└── lidar_reader.py         # LiDAR scans + detección de personas
vendor/
└── eyes-animation/         # Librería de ojos animados (clonar manualmente)
```

## Variables de entorno
- `ROBOT_NAME` — nombre del robot (default: `mini_pupper_2`)
