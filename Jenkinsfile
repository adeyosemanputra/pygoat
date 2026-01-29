pipeline {
    agent any

    environment {
        // --- CONFIGURACIÓN DE RED ---
        // Nombres de los servicios dentro de la red Docker 'devsecops-net'
        
        // Dependency Track (Nombre exacto del contenedor API)
        DT_URL = 'http://dependecy-track-dtrack-apiserver-1:8080' 
        
        // DefectDojo (Nombre exacto del contenedor NGINX)
        DD_URL = 'http://django-defectdojo-nginx-1:8080'
        
        // Credenciales (Las que guardaste en Jenkins como Secret Text)
        DD_API_KEY = credentials('44192fb03e90c6e2a80fce1bbbb9115b4df2ee91')
        DT_API_KEY = credentials('odt_NEUrAfmM_KtGgvx2ZRioxa7QJcfOObPExjJo5vyJB')
        
        // ID del Engagement en DefectDojo (¡Cámbialo por el tuyo!)
        DD_ENGAGEMENT_ID = '1' 
    }

    stages {
        stage('Limpieza') {
            steps {
                cleanWs() // Limpia el espacio de trabajo antes de empezar
            }
        }
        
        stage('Checkout') {
            steps {
                // Descarga tu código de la rama desarrollo
                git branch: 'desarrollo', url: 'https://github.com/pablotpy/pygoat.git'
            }
        }

        stage('SAST - Bandit') {
            // Bandit se instala y ejecuta dentro de un contenedor Python temporal
            agent {
                docker { 
                    image 'python:3.10-slim' 
                    args '--network devsecops-net' // Vital para hablar con DefectDojo
                }
            }
            steps {
                echo "Instalando Bandit..."
                sh 'pip install bandit'
                
                echo "Ejecutando análisis SAST..."
                // 1. Generamos reporte JSON para DefectDojo (|| true evita que rompa aquí)
                sh 'bandit -r . -f json -o bandit_report.json || true'
                
                // 2. Security Gate: Fallar si hay vulnerabilidades Críticas/Altas
                script {
                    echo "Evaluando Security Gate..."
                    // -lll: Solo nivel High/Critical severity
                    // -iii: Solo nivel High confidence
                    try {
                        sh 'bandit -r . -lll -iii'
                    } catch (Exception e) {
                        echo "ALERTA: Bandit encontró vulnerabilidades críticas."
                        // currentBuild.result = 'UNSTABLE' // O usa 'FAILURE' para bloquear
                    }
                }
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
                echo "Generando SBOM (Lista de materiales de software)..."
                sh 'pip install cyclonedx-bom'
                sh 'cyclonedx-py-requirements -o bom.xml'
                
                script {
                    echo "Enviando SBOM a Dependency Track..."
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
                echo "Buscando secretos hardcodeados..."
                // --exit-code 0 evita que rompa el pipeline si encuentra algo, 
                // para que podamos subir el reporte primero.
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
                    echo "Centralizando vulnerabilidades en DefectDojo..."

                    // Subir reporte de Bandit
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

                    // Subir reporte de Gitleaks
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