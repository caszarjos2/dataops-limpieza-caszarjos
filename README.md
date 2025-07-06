# DataOps - Python ✕ Docker ✕ Jenkins  
Proceso automático de un data entry de nuevos usuarios.

---

## 1. Descripción

Este proyecto ejecuta, de forma **100 % automatizada**, el flujo mensual de nuevos usuarios :

1. **Ingesta**  
   - Extrae la tabla **`rrhh.empleado`** desde PostgreSQL.

2. **Transformación**  
   - Tratamos valores faltantes y nulos

3. **Salida**  
   - Exporta el resultado a **Excel** (`empleados_limpios_{periodo}.csvxlsx`).  

4. **Orquestación**  
   - Todo el código corre dentro de un contenedor **Docker** reproducible.  
   - Un **pipeline de Jenkins** se encarga de compilar la imagen, ejecutar el job y publicar artefactos.

---

## 2. Arquitectura

```

┌──────────────┐    docker run    ┌────────────────┐
│ Jenkins Job  │ ───────────────► │  Contenedor    │
│  (pipeline)  │                  │  Python 3.11   │
└──────────────┘                  │                │
▲                                 │ 1. Lee CSV     │
│                                 │ 2. Lee PG      │
│  logs / artefactos              │ 3. Limpia      │
└─────────────────────────────────│                │
                                  └────────────────┘

```

---

## 3. Tecnologías

| Componente | Versión | Propósito |
|------------|---------|-----------|
| Python     | 3.11    | Transformaciones y lógica de negocio |
| Pandas     | 2.x     | Procesamiento de datos tabulares     |
| psycopg2-binary | 2.9 | Conexión PostgreSQL                 |
| openpyxl   | 3.x     | Exportar a Excel                     |
| Docker     | 24+     | Aislamiento y portabilidad           |
| Jenkins    | 2.452+  | CI/CD y orquestación DataOps         |

---

## 4. Estructura de carpetas

```

.
├─ app/
│  ├─ main.py          # script principal
│  ├─ config.json      # credenciales y rutas (NO commitear prod)
│  └─ requirements.txt
├─ data/               # aquí se montan los CSV de cada mes
├─ Dockerfile
└─ Jenkinsfile

````

---

## 5. Prerequisitos

| Requisito | Notas |
|-----------|-------|
| Docker Engine | activo y con permisos para compilar imágenes |
| Jenkins agent | con acceso a Docker / Podman |
| PostgreSQL | tabla `rrhh.empleado` accesible desde el runner |
| Variable `CONFIG_FILE` | (opcional) ruta al `config.json` dentro del contenedor |

---

## 6. Archivo `config.json` de ejemplo

```jsonc
{
  "db": {
    "host": "db.example.internal",
    "port": 5432,
    "dbname": "dmc",
    "user": "usr_ro_dmc_rrhh_estudiantes",
    "password": "********"
  }
}
````

> **Seguridad :** monta el JSON como *secret* (Docker Swarm) o credencial de Jenkins; evita incluirlo en el repositorio.

---

## 7. Construcción y prueba local

```bash
# clonar
git clone https://github.com/caszarjos2/dataops-limpieza-caszarjos.git
cd app
```

---

## 8. Pipeline Jenkins (ejemplo)

```groovy
pipeline {
  agent any

  environment {
    IMAGE = "dev-ops-app-app:latest"
  }

  stages {
    stage('Checkout') {
      steps {
        checkout scm
      }
    }

    stage('Build') {
      steps {
        echo '🔧 Construyendo imagen Docker...'
        sh 'docker build -t $IMAGE .'
      }
    }

    stage('Ejecutar limpieza de datos') {
      steps {
        echo '🚀 Ejecutando ETL dentro del contenedor...'
        sh '''
          docker run --rm \
            -v $WORKSPACE/config.json:/app/config.json:ro \
            -v $WORKSPACE/data:/app/data:ro \
            -v $WORKSPACE/data/output:/app/data/output \
            $IMAGE
        '''
      }
    }

    stage('Publicar CSV limpio') {
      steps {
        echo '📦 Publicando artefacto CSV...'
        archiveArtifacts artifacts: 'data/output/*.csv', fingerprint: true
      }
    }
  }

  post {
    success {
      echo '✅ Pipeline ejecutado con éxito. CSV generado.'
    }
    failure {
      echo '❌ Error en el pipeline. Revisar logs.'
    }
  }
}

```

* El stage **Test job** ejecuta el contenedor con los archivos de prueba.
* El artefacto Excel se publica en Jenkins para descarga inmediata.

---

## 9. Licencia

DMC © 2025 — Miguelangel / DMC Institute
Se permite uso comercial y modificación bajo los términos de la licencia.

