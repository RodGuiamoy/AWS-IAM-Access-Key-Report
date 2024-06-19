import boto3
from datetime import datetime, timezone
import csv
import sys
import time

# Create an IAM client
iam = boto3.client('iam')

def get_user_tags(username):
    response = iam.list_user_tags(UserName=username)
    return {tag['Key']: tag['Value'] for tag in response['Tags']}

def get_email_address(user_tags):        
    email = user_tags.get('email', None)
        
    return email

def get_employee_id(user_tags):        
    employee_id = user_tags.get('employeeID', None)
        
    return employee_id
    

def get_access_keys(username):
    try:
        access_key_data = []
        
        # Get the access keys for the specified user
        response = iam.list_access_keys(UserName=username)['AccessKeyMetadata']
        if not response:
            result = "No access keys"
        else:
            for key in response:
                
                access_key_id = key['AccessKeyId']
                status = key['Status']
                create_date = key['CreateDate']
                
                # Calculate the age of the access key
                current_time = datetime.now(timezone.utc)
                age_days = (current_time - create_date).days
                # age_days = f"{age_days} days ago."
                
                # Get the last used date of the access key
                last_used_response = iam.get_access_key_last_used(AccessKeyId=access_key_id)
                last_used_date = last_used_response['AccessKeyLastUsed'].get('LastUsedDate')
                if last_used_date:
                    last_used_days = (current_time - last_used_date).days
                    usage_info = f"Used {last_used_days} days ago"
                else:
                    usage_info = "Never used"
                    
                access_key_data.append({
                    "access_key_id": access_key_id,
                    "status": status,
                    "usage_info": usage_info,
                    "age_days": age_days
                        
                })
                
                # result_lines.append(f"Access Key ID: {access_key_id}, Status: {status}, Usage: {usage_info}, Age: {age_days} days old")
            # result = "\n".join(result_lines)
    except Exception as e:
        return f"An error occurred: {e}"

    # print(result)
    return access_key_data

def main(aws_environment):
    
    response = iam.attach_user_policy(UserName='sre-cli-user',PolicyArn="arn:aws:iam::aws:policy/AdministratorAccess")
    print(f'---------------------------------Attaching temporary admin policy\n---------------------------------\n')
    
    time.sleep(10)
    
    # Get the current date
    current_date = datetime.now()

    # Format the date to MMddyyyy
    formatted_date = current_date.strftime('%m%d%Y')
    
    # Using str.replace() to remove spaces
    aws_environment = aws_environment.replace(" ", "")
    
    # Define the CSV file name
    csv_file_name = f"{aws_environment}_{formatted_date}.csv"
    
    # Define the header names based on the data we are collecting
    headers = ['AWSEnvironment','AWSAccountID','UserName', 'Email', 'EmployeeID', 'AccessKeyID', 'Status', 'Usage', 'Age(Days)']
    
    # Open a new CSV file
    with open(csv_file_name, mode='w', newline='') as file:
        writer = csv.DictWriter(file, fieldnames=headers)
        
        account_id = boto3.client('sts').get_caller_identity().get('Account')
        
        # Write the header
        writer.writeheader()
    
        # List all IAM users
        paginator = iam.get_paginator('list_users')
        for response in paginator.paginate():
            
            for user in response['Users']:
        
                username = user['UserName']
                user_tags = get_user_tags(username)
                
                email = get_email_address(user_tags)
                employee_id = get_employee_id(user_tags)
                access_key_data = get_access_keys(username)
                
                for access_key in access_key_data:
                    
                    # Write the user's details to the CSV
                    writer.writerow({
                        'AWSEnvironment': aws_environment,
                        'AWSAccountID': account_id,
                        'UserName': username,
                        'Email': email,
                        'EmployeeID': employee_id,
                        'AccessKeyID': access_key["access_key_id"],
                        'Status': access_key["status"],
                        'Usage': access_key["usage_info"],
                        'Age(Days)': access_key["age_days"]
                        
                    })
                
                print (f"{username}")
                
    response = iam.detach_user_policy(UserName='sre-cli-user',PolicyArn="arn:aws:iam::aws:policy/AdministratorAccess")
    print(f'---------------------------------Detaching temporary admin policy\n---------------------------------\n')
                
if __name__ == "__main__":
    aws_environment = sys.argv[1]
    main(aws_environment)