pipeline {
    agent any

    environment {
        IMAGE_NAME = "pragnasri22bcd30/pragnasri-2022bcd0030"
        BUILD_TAG = "${env.BUILD_NUMBER}"
    }
    
    stages {

        stage('Checkout') {
            steps {
                checkout scm
            }
        }

        stage('Setup Python Virtual Environment') {
            steps {
                sh '''
                python3 -m venv venv
                . venv/bin/activate
                pip install -r requirements.txt
                '''
            }
        }

        stage('Train Model') {
            steps {
                sh '''
                . venv/bin/activate
                python scripts/train.py
                '''
            }
        }

        stage('Read Accuracy') {
            steps {
                script {
                    def metrics = readJSON file: 'app/artifacts/metrics.json'
                    env.CURRENT_R2 = metrics.r2.toString()
                    env.CURRENT_MSE = metrics.mse.toString()

                    echo "Current R2: ${env.CURRENT_R2}"
                    echo "Current MSE: ${env.CURRENT_MSE}"
                }
            }
        }

        stage('Compare Accuracy') {
            steps {
                script {
                    env.MODEL_IMPROVED = "false"

                    withCredentials([string(credentialsId: 'best-metrics',
                                            variable: 'BEST_JSON')]) {

                        def best = readJSON text: BEST_JSON

                        if (env.CURRENT_R2.toFloat() > best.r2.toFloat() &&
                            env.CURRENT_MSE.toFloat() < best.mse.toFloat()) {

                            env.MODEL_IMPROVED = "true"
                            echo "Model improved"
                        } else {
                            echo "Model did not improve"
                        }
                    }
                }
            }
        }

        stage('Build Docker Image') {
            when {
                expression { env.MODEL_IMPROVED == "true" }
            }
            steps {
                sh "docker build -t ${IMAGE_NAME}:${BUILD_TAG} -t ${IMAGE_NAME}:latest ."
            }
        }

        stage('Push Docker Image') {
            when {
                expression { env.MODEL_IMPROVED == "true" }
            }
            steps {
                withCredentials([usernamePassword(
                    credentialsId: 'dock-creds',
                    usernameVariable: 'DOCKER_USER',
                    passwordVariable: 'DOCKER_PASS'
                )]) {
                    sh '''
                    echo $DOCKER_PASS | docker login -u $DOCKER_USER --password-stdin
                    docker push ${IMAGE_NAME}:${BUILD_TAG}
                    docker push ${IMAGE_NAME}:latest
                    '''
                }
            }
        }
    }

    post {
        always {
            archiveArtifacts artifacts: 'app/artifacts/**', allowEmptyArchive: true
        }
    }
}
