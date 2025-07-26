# Microservice Template - FastAPI + AWS Lambda

Este proyecto proporciona una plantilla para crear microservicios con FastAPI que pueden ejecutarse tanto localmente como en AWS Lambda, con infraestructura gestionada por CDK.

## 🚀 Quick Start

### 1. Configuración inicial
```bash
# El entorno se activa automáticamente con direnv
# Si no tienes direnv, ejecuta:
./setup.sh

# O manualmente:
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### 2. Desarrollo local (FastAPI puro)
```bash
# Ejecutar FastAPI en modo desarrollo
./scripts/local-fastapi.sh

# La API estará disponible en:
# http://localhost:8000/docs (Swagger UI)
# http://localhost:8000/api/v1/health
# http://localhost:8000/api/v1/test
```

### 3. Desarrollo local con SAM (simulando Lambda)
```bash
# Ejecutar con SAM Local (simula Lambda + API Gateway)
./scripts/run_sam.sh

# La API estará disponible en:
# http://localhost:3000/api/v1/health
# http://localhost:3000/api/v1/test
```

### 4. Deploy a AWS
```bash
# Deploy con CDK (default: dev environment)
./scripts/deploy-cdk.sh

# Deploy con nombre y ambiente específico
./scripts/deploy-cdk.sh -s "my-api" -e "prod"

# Ver opciones disponibles
./scripts/deploy-cdk.sh --help

# Esto creará:
# - Lambda function con Python 3.13
# - API Gateway
# - CloudWatch Logs
# - Nombres dinámicos basados en servicio y ambiente
```

## 📁 Estructura del Proyecto

```
microservice-template/
├── src/                          # Código fuente
│   ├── api/                      # Aplicación FastAPI
│   │   ├── core/                 # Configuración
│   │   ├── routers/              # Endpoints
│   │   ├── models/               # Modelos Pydantic
│   │   └── services/             # Lógica de negocio
│   └── lambda_handler.py         # Handler para Lambda
├── infrastructure/               # Infraestructura CDK
├── scripts/                      # Scripts de utilidad
└── template.yaml                 # Template SAM para local
```

## 🔧 Configuración

### Variables de entorno
Copia `.env.example` a `.env` y ajusta según tus necesidades:
```bash
cp .env.example .env
```

### AWS Profile
El proyecto está configurado para usar el profile `cvdv`. Cambia esto en `.envrc` si usas otro profile.

## 📝 API Endpoints

### Health Check
```
GET /api/v1/health
```
Respuesta:
```json
{
  "status": "healthy",
  "timestamp": "2024-01-01T00:00:00.000000",
  "version": "1.0.0",
  "environment": "development",
  "service": "Microservice Template"
}
```

### Test Endpoint
```
GET /api/v1/test
```
Respuesta:
```json
{
  "message": "Hello from Microservice Template! 🚀",
  "timestamp": "2024-01-01T00:00:00.000000"
}
```

## 🛠 Comandos Útiles

### CDK Commands
```bash
# Destruir infraestructura
./scripts/destroy-cdk.sh
./scripts/destroy-cdk.sh -s "my-api" -e "prod"

# Comandos manuales (desde infrastructure/)
cd infrastructure

# Ver template CloudFormation
cdk synth -c service_name="my-api" -c environment="dev"

# Verificar diferencias
cdk diff -c service_name="my-api" -c environment="dev"
```

### SAM Commands
```bash
# Build para producción
sam build

# Deploy con SAM (alternativa a CDK)
sam deploy --guided
```

## 🔄 Workflow de Desarrollo

1. **Desarrollo local**: Usa `./scripts/local-fastapi.sh` para desarrollo rápido
2. **Testing Lambda**: Usa `./scripts/run_sam.sh` para probar comportamiento en Lambda
3. **Deploy**: Usa `./scripts/deploy-cdk.sh` para desplegar a AWS

## 📦 Gestión de Dependencias

**Un solo `requirements.txt`** consolidado con:
- **Producción**: FastAPI, Mangum, Pydantic, boto3
- **Infraestructura**: AWS CDK, constructs
- **Desarrollo**: SAM CLI, black, flake8, mypy

**Entornos virtuales automáticos:**
- Root: `.venv` (desarrollo FastAPI + deploy)
- Infrastructure: `.venv` (CDK separado)
- Ambos se activan automáticamente con `direnv`

## 🎯 Características

✅ **Desacoplado**: FastAPI funciona independiente de Lambda  
✅ **Python 3.13**: Último runtime de Lambda  
✅ **Infraestructura como código**: CDK con Python  
✅ **Desarrollo local**: Con y sin simulación Lambda  
✅ **Auto-activación**: Entorno virtual con direnv  
✅ **Scripts automatizados**: Setup y deploy simplificados  
✅ **Template configurable**: Nombre de servicio y ambiente dinámicos  
✅ **Ambientes diferenciados**: dev (default) y prod con configuraciones específicas 