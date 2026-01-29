pipeline {
    agent any

    environment {
        // --- CONFIGURACIÓN DE RED DOCKER ---
        
        // Dependency Track (Nombre del servicio en su docker-compose):
        // Como están en la misma red, usamos el nombre del contenedor o servicio.
        DT_URL = 'http://dtrack-apiserver:8080' 
        
        // DefectDojo:
        // ATENCIÓN: Jenkins debe hablar con el NGINX de DefectDojo, no con uwsgi.
        // El puerto interno del nginx es 8080 (el 8084 es solo para tu PC).
        // Busca el nombre del contenedor con 'docker ps', suele ser 'defectdojo-nginx-1' o similar.
        // Asumiremos que el contenedor se llama: defectdojo-nginx-1 
        // (Si falla, verifica el nombre con 'docker ps' y cámbialo aquí).
        DD_URL = 'http://defectdojo-nginx-1:8080'
        
        // Credenciales cargadas desde Jenkins
        DD_API_KEY = credentials('dd-api-key')
        DT_API_KEY = credentials('dt-api-key')
        
        // --- TU ID ---
        DD_ENGAGEMENT_ID = '1' // <--- CAMBIA ESTO POR TU ID REAL
    }

    stages {
        stage('Limpieza') {
            steps {
                cleanWs()
            }
        }
        
        stage('Checkout') {
            steps {
                checkout scm
            }
        }

        stage('SAST - Bandit') {
            agent {
                docker { 
                    image 'python:3.10-slim' 
                    args '--network devsecops-net' // Conectar agente a la red
                }
            }
            steps {
                sh 'pip install bandit'
                // Generar reporte JSON
                sh 'bandit -r . -f json -o bandit_report.json || true'
                // Security Gate (Falla si hay High Severity / High Confidence)
                sh 'bandit -r . -lll -iii' 
            }
        }

        stage('SCA - Dependency Track') {
            agent {
                docker { 
                    image 'python:3.10-slim'
                    args '--network devsecops-net'
                }
            }
            steps {
                sh 'pip install cyclonedx-bom'
                sh 'cyclonedx-py-requirements -o bom.xml'
                
                script {
                    echo "Subiendo BOM a Dependency Track..."
                    sh """
                        curl -X "POST" "${DT_URL}/api/v1/bom" \
                        -H "Content-Type: multipart/form-data" \
                        -H "X-Api-Key: ${DT_API_KEY}" \
                        -F "autoCreate=true" \
                        -F "projectName=Pygoat" \
                        -F "projectVersion=1.0" \
                        -F "bom=@bom.xml"
                    """
                }
            }
        }

        stage('Secrets - Gitleaks') {
            agent {
                docker { 
                    image 'zricethezav/gitleaks:latest'
                    args '--network devsecops-net'
                }
            }
            steps {
                sh 'gitleaks detect -v --source . --report-path gitleaks_report.json --exit-code 0'
            }
        }

        stage('Upload to DefectDojo') {
            agent {
                docker { 
                    image 'curlimages/curl:latest' 
                    args '--network devsecops-net'
                }
            }
            steps {
                script {
                    echo "Subiendo reportes a DefectDojo (ID: ${DD_ENGAGEMENT_ID})..."
                    
                    // Subir Bandit
                    sh """
                        curl -X POST "${DD_URL}/api/v2/import-scan/" \
                        -H "Authorization: Token ${DD_API_KEY}" \
                        -H "Content-Type: multipart/form-data" \
                        -F "active=true" \
                        -F "verified=true" \
                        -F "scan_type=Bandit" \
                        -F "engagement=${DD_ENGAGEMENT_ID}" \
                        -F "file=@bandit_report.json"
                    """

                    // Subir Gitleaks
                    sh """
                        curl -X POST "${DD_URL}/api/v2/import-scan/" \
                        -H "Authorization: Token ${DD_API_KEY}" \
                        -H "Content-Type: multipart/form-data" \
                        -F "active=true" \
                        -F "verified=true" \
                        -F "scan_type=Gitleaks Scan" \
                        -F "engagement=${DD_ENGAGEMENT_ID}" \
                        -F "file=@gitleaks_report.json"
                    """
                }
            }
        }
    }
}