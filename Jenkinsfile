pipeline {
  agent any

  environment {
    REGISTRY = "localhost:5000"
    IMAGE_PREFIX = "jumptotech"
  }

  stages {
    stage('Checkout') {
      steps {
        checkout scm
        sh 'git rev-parse --short HEAD > .gitsha'
      }
    }

    stage('Build & Push (local registry)') {
      steps {
        script {
          def sha = readFile('.gitsha').trim()

          def services = [
            "auth-service",
            "courses-service",
            "enrollment-service",
            "content-service",
            "news-service",
            "gateway-service"
          ]

          def builds = [:]

          for (s in services) {
            builds[s] = {
              sh """
                echo "Building ${s}..."
                docker build -t ${REGISTRY}/${IMAGE_PREFIX}/${s}:${sha} ./services/${s}
                docker push ${REGISTRY}/${IMAGE_PREFIX}/${s}:${sha}
              """
            }
          }

          parallel builds
        }
      }
    }

    stage('Smoke test (optional)') {
      steps {
        sh '''
          echo "Images pushed to local registry:"
          curl -s http://localhost:5000/v2/_catalog || true
        '''
      }
    }
  }

  post {
    always {
      sh 'docker image prune -f || true'
    }
  }
}