git pull
export AWS_PROFILE="deploy"
aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin 511905734159.dkr.ecr.us-east-1.amazonaws.com
docker pull 511905734159.dkr.ecr.us-east-1.amazonaws.com/jamun-dev:latest
docker tag 511905734159.dkr.ecr.us-east-1.amazonaws.com/jamun-dev:latest
docker push 511905734159.dkr.ecr.us-east-1.amazonaws.com/jamun-dev:latest
aws ecs update-service --cluster ECS-DEV-QA-KULTIVATE --service ifgtb-qa --force-new-deployment