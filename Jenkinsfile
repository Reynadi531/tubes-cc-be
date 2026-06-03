pipeline {
    agent any

    parameters {
        string(name: 'REGISTRY_URL', defaultValue: 'docker.io', description: 'Container registry host, for example docker.io, ghcr.io, or registry.example.com')
        string(name: 'IMAGE_REPOSITORY', defaultValue: 'your-namespace/yuki-agent', description: 'Registry repository path for the image')
        string(name: 'REGISTRY_CREDENTIALS_ID', defaultValue: 'docker-registry-credentials', description: 'Jenkins username/password credential ID for the registry')
        booleanParam(name: 'PUSH_LATEST', defaultValue: true, description: 'Also tag and push the image as latest')
    }

    environment {
        DOCKER_BUILDKIT = '1'
    }

    stages {
        stage('Checkout') {
            steps {
                checkout scm
            }
        }

        stage('Prepare') {
            steps {
                script {
                    env.SHORT_SHA = sh(
                        script: 'git rev-parse --short=12 HEAD',
                        returnStdout: true
                    ).trim()

                    env.IMAGE_NAME = "${params.REGISTRY_URL}/${params.IMAGE_REPOSITORY}"
                    env.BUILD_TAG_NAME = "${env.IMAGE_NAME}:${env.BUILD_NUMBER}"
                    env.SHA_TAG_NAME = "${env.IMAGE_NAME}:${env.SHORT_SHA}"
                    env.LATEST_TAG_NAME = "${env.IMAGE_NAME}:latest"
                }
            }
        }

        stage('Build Image') {
            steps {
                sh '''
                    docker build \
                        --file Dockerfile \
                        --tag "$BUILD_TAG_NAME" \
                        --tag "$SHA_TAG_NAME" \
                        .
                '''
            }
        }

        stage('Verify Image') {
            steps {
                sh 'docker image inspect "$BUILD_TAG_NAME"'
            }
        }

        stage('Push Image') {
            steps {
                withCredentials([usernamePassword(
                    credentialsId: params.REGISTRY_CREDENTIALS_ID,
                    usernameVariable: 'REGISTRY_USERNAME',
                    passwordVariable: 'REGISTRY_PASSWORD'
                )]) {
                    sh '''
                        set +x
                        printf '%s' "$REGISTRY_PASSWORD" | docker login "$REGISTRY_URL" --username "$REGISTRY_USERNAME" --password-stdin
                        set -x

                        docker push "$BUILD_TAG_NAME"
                        docker push "$SHA_TAG_NAME"

                        if [ "$PUSH_LATEST" = "true" ]; then
                            docker tag "$BUILD_TAG_NAME" "$LATEST_TAG_NAME"
                            docker push "$LATEST_TAG_NAME"
                        fi

                        docker logout "$REGISTRY_URL"
                    '''
                }
            }
        }
    }

    post {
        always {
            sh '''
                docker image rm "$BUILD_TAG_NAME" "$SHA_TAG_NAME" "$LATEST_TAG_NAME" >/dev/null 2>&1 || true
            '''
        }
    }
}
