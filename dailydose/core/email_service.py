"""
Email services for sending daily word emails using AWS SES.
"""
import os
import boto3
from botocore.exceptions import ClientError
from jinja2 import Environment, FileSystemLoader, select_autoescape
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# AWS SES Configuration
AWS_REGION = os.environ.get("AWS_REGION", "us-east-1")
AWS_ACCESS_KEY_ID = os.environ.get("AWS_ACCESS_KEY_ID")
AWS_SECRET_ACCESS_KEY = os.environ.get("AWS_SECRET_ACCESS_KEY")
EMAIL_SENDER = os.environ.get("EMAIL_SENDER", "noreply@example.com")
EMAIL_ENABLED = os.environ.get("EMAIL_ENABLED", "false").lower() == "true"

# Initialize SES client if credentials are available
ses_client = None
if EMAIL_ENABLED and AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY:
    try:
        ses_client = boto3.client(
            'ses',
            region_name=AWS_REGION,
            aws_access_key_id=AWS_ACCESS_KEY_ID,
            aws_secret_access_key=AWS_SECRET_ACCESS_KEY
        )
    except Exception as e:
        print(f"Error initializing AWS SES client: {e}")
        EMAIL_ENABLED = False

def initialize_templates():
    """Initialize the Jinja2 template environment."""
    # Path to templates folder
    template_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "templates")
    
    # Create template directory if it doesn't exist
    if not os.path.exists(template_dir):
        os.makedirs(template_dir)
    
    # Initialize Jinja2 environment
    return Environment(
        loader=FileSystemLoader(template_dir),
        autoescape=select_autoescape(['html', 'xml'])
    )

# Initialize Jinja2 environment
template_env = initialize_templates()

def send_word_email(recipient_email, word_data):
    """
    Send an email with word information to the specified recipient.
    
    Args:
        recipient_email (str): Email address to send to
        word_data (dict): Word data to include in the email
        
    Returns:
        bool: True if email was sent successfully, False otherwise
    """
    if not EMAIL_ENABLED or not ses_client:
        print("Email sending is disabled or not configured.")
        return False
    
    try:
        # Check if the template exists, if not, create it
        template_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 
                                    "templates", "word_email.html")
        
        if not os.path.exists(template_path):
            print("Email template not found. Creating default template...")
            create_default_template()
        else:
            print("Using existing email template.")
        
        # Reload the template environment to pick up any changes
        global template_env
        template_env = initialize_templates()
        
        # Load the template
        template = template_env.get_template("word_email.html")
        
        # Render HTML body
        html_body = template.render(
            word=word_data.get("word", ""),
            phonetics=word_data.get("phonetics", []),
            meanings=word_data.get("meanings", []),
            difficulty=word_data.get("difficulty", "")
        )
        
        # Send email via SES
        response = ses_client.send_email(
            Source=EMAIL_SENDER,
            Destination={
                'ToAddresses': [recipient_email]
            },
            Message={
                'Subject': {
                    'Data': f"📚 Daily Word: {word_data.get('word', '').upper()}"
                },
                'Body': {
                    'Html': {
                        'Data': html_body
                    }
                }
            }
        )
        
        print(f"Email sent! Message ID: {response['MessageId']}")
        return True
    
    except ClientError as e:
        print(f"Error sending email via SES: {e}")
        return False
    except Exception as e:
        print(f"Unexpected error when sending email: {e}")
        return False

def create_default_template():
    """
    Create a default email template if one doesn't exist.
    Note: This function is now mainly a fallback as we're using a manually created template.
    """
    # Path to templates folder
    template_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "templates")
    template_path = os.path.join(template_dir, "word_email.html")
    
    # Create the directory if it doesn't exist
    if not os.path.exists(template_dir):
        os.makedirs(template_dir)
    
    # Simple default HTML template with basic formatting - as a fallback
    default_template = """<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Daily Word: {{ word|upper }}</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            line-height: 1.6;
            color: #333;
            max-width: 600px;
            margin: 0 auto;
            padding: 20px;
        }
        .header {
            text-align: center;
            padding: 20px 0;
            border-bottom: 2px solid #4a86e8;
            margin-bottom: 20px;
        }
        .word {
            font-size: 32px;
            font-weight: bold;
            color: #4a86e8;
        }
        .pronunciation {
            font-style: italic;
            margin: 10px 0;
        }
        .section {
            margin-bottom: 20px;
            padding: 15px;
            background-color: #f9f9f9;
            border-radius: 5px;
        }
        .part-of-speech {
            font-style: italic;
            color: #666;
        }
    </style>
</head>
<body>
    <div class="header">
        <div class="word">{{ word|upper }} 📚</div>
        {% if phonetics and phonetics[0]['text'] %}
        <div class="pronunciation">{{ phonetics[0]['text'] }}</div>
        {% endif %}
    </div>

    {% if meanings %}
    <div class="section">
        <h2>Definitions</h2>
        {% for meaning in meanings %}
            <div>
                <p class="part-of-speech">[{{ meaning.partOfSpeech }}]</p>
                {% for definition in meaning.definitions %}
                    <p>• {{ definition.definition }}</p>
                    {% if definition.example %}
                        <p><em>Example: "{{ definition.example }}"</em></p>
                    {% endif %}
                {% endfor %}
            </div>
        {% endfor %}
    </div>
    {% endif %}

    <p>This email was sent by the Daily Word application to help you expand your vocabulary.</p>
</body>
</html>
"""
    
    # Write the template to file
    with open(template_path, 'w') as f:
        f.write(default_template)
    
    # Reload the template environment
    global template_env
    template_env = initialize_templates()

def get_subscribers():
    """Get a list of subscriber email addresses from environment or config file."""
    # Get from environment variable if set (comma-separated list)
    subscribers_env = os.environ.get("EMAIL_SUBSCRIBERS", "")
    if subscribers_env:
        return [email.strip() for email in subscribers_env.split(",") if email.strip()]
    
    # Otherwise, check if a subscribers file exists
    subscribers_file = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 
                                   "subscribers.txt")
    
    if os.path.exists(subscribers_file):
        with open(subscribers_file, "r") as f:
            # Filter out comments and empty lines
            return [line.strip() for line in f if line.strip() and not line.strip().startswith('#')]
    
    return [] 