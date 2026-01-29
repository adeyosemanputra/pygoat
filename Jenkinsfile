pipeline {
    agent any

    environment {
        // Rutas de red internas
        DT_URL = 'http://dependecy-track-dtrack-apiserver-1:8080' 
        DD_URL = 'http://django-defectdojo-nginx-1:8080'
        
        // Credenciales
        DD_API_KEY = credentials('dd-api-key')
        DT_API_KEY = credentials('dt-api-key')
        DD_ENGAGEMENT_ID = '1' // <--- TU ID AQUÍ
        
        // Configuración común de Docker para no repetir
        // Montamos el volumen exacto y la red devsecops-net
        DOCKER_ARGS = '--rm --network devsecops-net -v /var/jenkins_home:/var/jenkins_home -w ${WORKSPACE}'
    }

    stages {
        stage('Limpieza') {
            steps {
                cleanWs()
            }
        }
        
        stage('Checkout') {
            steps {
                git branch: 'desarrollo', url: 'https://github.com/pablotpy/pygoat.git'
            }
        }

        stage('SAST - Bandit') {
            steps {
                script {
                    echo "Ejecutando Bandit en contenedor Python..."
                    // Ejecutamos docker run manual, igual que en tu prueba
                    sh """
                        docker run ${DOCKER_ARGS} python:3.10-slim /bin/bash -c " \
                            pip install bandit && \
                            bandit -r . -f json -o bandit_report.json || true \
                        "
                    """
                }
            }
        }

        stage('SCA - Dependency Track') {
            steps {
                script {
                    echo "Generando SBOM y enviando a Dependency Track..."
                    sh """
                        docker run ${DOCKER_ARGS} python:3.10-slim /bin/bash -c " \
                            pip install cyclonedx-bom && \
                            cyclonedx-py-requirements -o bom.xml && \
                            curl -v -X POST '${DT_URL}/api/v1/bom' \
                                -H 'Content-Type: multipart/form-data' \
                                -H 'X-Api-Key: ${DT_API_KEY}' \
                                -F 'autoCreate=true' \
                                -F 'projectName=Pygoat' \
                                -F 'projectVersion=1.0' \
                                -F 'bom=@bom.xml' \
                        "
                    """
                }
            }
        }

        stage('Secrets - Gitleaks') {
            steps {
                script {
                    echo "Buscando secretos..."
                    // Gitleaks ya trae su propio binario, no necesita /bin/bash -c complicado
                    sh """
                        docker run ${DOCKER_ARGS} zricethezav/gitleaks:latest \
                        detect -v --source . --report-path gitleaks_report.json --exit-code 0
                    """
                }
            }
        }

        stage('Upload to DefectDojo') {
            steps {
                script {
                    echo "Subiendo reportes a DefectDojo..."
                    // Usamos una imagen con CURL para subir los archivos
                    sh """
                        docker run ${DOCKER_ARGS} curlimages/curl:latest /bin/sh -c " \
                            curl -v -X POST '${DD_URL}/api/v2/import-scan/' \
                                -H 'Authorization: Token ${DD_API_KEY}' \
                                -H 'Content-Type: multipart/form-data' \
                                -F 'active=true' \
                                -F 'verified=true' \
                                -F 'scan_type=Bandit' \
                                -F 'engagement=${DD_ENGAGEMENT_ID}' \
                                -F 'file=@bandit_report.json' && \
                            curl -v -X POST '${DD_URL}/api/v2/import-scan/' \
                                -H 'Authorization: Token ${DD_API_KEY}' \
                                -H 'Content-Type: multipart/form-data' \
                                -F 'active=true' \
                                -F 'verified=true' \
                                -F 'scan_type=Gitleaks Scan' \
                                -F 'engagement=${DD_ENGAGEMENT_ID}' \
                                -F 'file=@gitleaks_report.json' \
                        "
                    """
                }
            }
        }
    }
}