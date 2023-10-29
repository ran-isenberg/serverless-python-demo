import json

import boto3


def handler(event, context):
    if event['RequestType'] == 'Create' or event['RequestType'] == 'Update':
        secret_name = event['ResourceProperties']['SecretName']
        user_pool_id = event['ResourceProperties']['UserPoolId']

        # Fetch the secret value
        secrets_client = boto3.client('secretsmanager')
        response = secrets_client.get_secret_value(SecretId=secret_name)
        secret_value = json.loads(response['SecretString'])

        # Change Cognito user password
        cognito_client = boto3.client('cognito-idp')
        cognito_client.admin_set_user_password(
            UserPoolId=user_pool_id,
            Username=secret_value['username'],
            Password=secret_value['password'],
            Permanent=True,
        )
        return {'PhysicalResourceId': 'AWS:CustomSetPass'}
