# Deploy to AWS Elastic Beanstalk

This Flask application is configured for the Elastic Beanstalk Python platform.
The deployment uses the `application:application` WSGI entry point and the
`/health` route for environment health checks. Model files are loaded relative
to `application.py`, so the app does not depend on the process working directory.

## Prerequisites

- An AWS account and permission to create Elastic Beanstalk environments, EC2
  instances, security groups, an Auto Scaling group, and a load balancer.
- AWS CLI v2 and the Elastic Beanstalk CLI (`eb`) installed.
- Git installed, since EB CLI packages the current Git commit.

Use AWS IAM Identity Center/SSO when available rather than long-lived access
keys. In PowerShell, configure and verify a profile:

```powershell
aws configure sso --profile forest-fire-app
aws sso login --profile forest-fire-app
$env:AWS_PROFILE = "forest-fire-app"
aws sts get-caller-identity
```

Do not put AWS credentials in the repository or application environment.

## Prepare and deploy

From the project directory:

1. Review `requirements.txt` before deploying. The serialized estimators report
   scikit-learn version `1.9.0`; its exact pin is intentional because
   scikit-learn pickle files are not guaranteed to work across versions.
2. Commit the deployment files and model files. EB CLI uses the Git commit as
   its deployment source bundle; uncommitted changes may not be included.
3. Check that the selected Python platform branch is available in the region,
   then initialize the EB application:

   ```powershell
   eb platform list --region ap-south-1
   eb init forest-fire-app --platform python-3.12 --region ap-south-1
   ```

   If `python-3.12` is no longer offered, select a currently supported Python
   3 platform branch and verify that all pinned packages provide compatible
   wheels before choosing it.
4. Create a load-balanced environment (the default `eb create` behavior):

   ```powershell
   eb create forest-fire-app-prod
   ```

   This provisions AWS resources and incurs charges. A load balancer costs
   extra, but is the appropriate starting point for a production environment.
   For a temporary low-cost test only, `eb create forest-fire-app-test --single`
   avoids the load balancer but is not highly available.
5. Deploy subsequent committed changes and check health:

   ```powershell
   eb deploy forest-fire-app-prod
   eb health forest-fire-app-prod
   eb open forest-fire-app-prod
   ```

   The environment's health check is configured to call `/health`.

## Production follow-up

- Add a domain and an AWS Certificate Manager certificate, configure HTTPS on
  the load balancer, and redirect HTTP to HTTPS before handling real user data.
- Review the environment's instance type, Auto Scaling limits, monitoring, and
  log retention against expected traffic and budget.
- Confirm that the public app is reachable and that `GET /health` returns
  `{"status":"ok"}` after deployment.
- To remove an environment and stop its ongoing resource charges:

  ```powershell
  eb terminate forest-fire-app-prod
  ```
