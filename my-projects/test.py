import json
import sys

def remove_wildcard_principals(policy_json):
    """Remove all Principal statements that reference wildcard '*' values from an AWS S3 bucket policy."""
    
    # Parse the JSON policy
    if isinstance(policy_json, str):
        policy = json.loads(policy_json)
    else:
        policy = policy_json
    
    if 'Statement' not in policy:
        return policy
    
    # Filter out statements with wildcard principals
    filtered_statements = []
    
    for statement in policy['Statement']:
        principal = statement.get('Principal')
        
        # Check if Principal is a wildcard string
        if principal == '*':
            continue
        
        # Check if Principal is a dict with wildcard values
        if isinstance(principal, dict):
            has_wildcard = False
            
            # Check each principal type (AWS, Service, Federated, CanonicalUser)
            for principal_type, principal_value in principal.items():
                if principal_value == '*':
                    has_wildcard = True
                    break
                elif isinstance(principal_value, list) and '*' in principal_value:
                    has_wildcard = True
                    break
            
            if has_wildcard:
                continue
        
        # Keep statements that don't have wildcard principals
        filtered_statements.append(statement)
    
    # Update the policy with filtered statements
    policy['Statement'] = filtered_statements
    
    return policy


def main():
    # Read from stdin if provided, otherwise use example
    if not sys.stdin.isatty():
        input_data = sys.stdin.read().strip()
    else:
        # Default example policy
        input_data = json.dumps({
            "Version": "2012-10-17",
            "Statement": [
                {
                    "Effect": "Allow",
                    "Principal": "*",
                    "Action": "s3:GetObject",
                    "Resource": "arn:aws:s3:::bucket/*"
                },
                {
                    "Effect": "Allow",
                    "Principal": {
                        "AWS": "arn:aws:iam::123456789012:root"
                    },
                    "Action": "s3:PutObject",
                    "Resource": "arn:aws:s3:::bucket/*"
                },
                {
                    "Effect": "Allow",
                    "Principal": {
                        "Service": "*"
                    },
                    "Action": "s3:ListBucket",
                    "Resource": "arn:aws:s3:::bucket"
                },
                {
                    "Effect": "Allow",
                    "Principal": {
                        "AWS": ["arn:aws:iam::123456789012:role/MyRole", "*"]
                    },
                    "Action": "s3:DeleteObject",
                    "Resource": "arn:aws:s3:::bucket/*"
                }
            ]
        })
    
    # Process the policy
    result = remove_wildcard_principals(input_data)
    
    # Output the result as JSON
    print(json.dumps(result, indent=2))


if __name__ == '__main__':
    main()