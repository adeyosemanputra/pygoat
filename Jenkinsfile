pipeline {
    agent any

    environment {
        // SEMGREP_BASELINE_REF = ""
        SEMGREP_APP_TOKEN = credentials('SEMGREP_APP_TOKEN')
        // SEMGREP_PR_ID = "${env.CHANGE_ID}"
        // SEMGREP_TIMEOUT = "300"

        // --- ADD THIS LINE ---
        // Add the Python user scripts directory to the PATH so 'semgrep' can be found
        PATH = "${env.PATH}:/Users/linish/Library/Python/3.9/bin"
    }

    stages {
        stage('Checkout Code') {
            steps {
                checkout scm
            }
        }

        stage('Install Semgrep') { // Keeping this stage as per your original script
            steps {
                sh 'pip3 install --upgrade semgrep'
            }
        }

        stage('Run Semgrep Scan') {
            steps {
                sh 'semgrep ci' // Now 'semgrep' should be found because of the updated PATH
            }
        }
    }
    // Add post block if you have one, or if you want to archive logs
    // post {
    //     always {
    //         // Example: cleanWs()
    //     }
    // }
}
