pipeline {
  agent any

  environment {
    REGISTRY = "localhost:5001"
    IMAGE_PREFIX = "jumptotech"
  }

  stages {
    stage('Checkout') {
      steps {
        checkout scm
        sh 'git rev-parse --short HEAD > .gitsha'
        sh 'echo "GIT SHA: $(cat .gitsha)"'
      }
    }

    stage('Build images (parallel)') {
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
            def svc = s
            builds[svc] = {
              sh """
                set -e
                echo "=== BUILD: ${svc} ==="
                docker build -t ${REGISTRY}/${IMAGE_PREFIX}/${svc}:${sha} ./services/${svc}
              """
            }
          }
          parallel builds
        }
      }
    }

    stage('Push images (sequential)') {
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

          for (s in services) {
            sh """
              set -e
              echo "=== PUSH: ${s} ==="
              docker push ${REGISTRY}/${IMAGE_PREFIX}/${s}:${sha}
            """
          }
        }
      }
    }

    stage('Verify Registry') {
      steps {
        sh '''
          echo "=== REGISTRY CATALOG ==="
          curl -s http://localhost:5001/v2/_catalog || true
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