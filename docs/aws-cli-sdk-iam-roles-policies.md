# AWS CLI, SDK, IAM Roles & Policies

## Lecture 126: 🖥️ AWS EC2 Instance Metadata

> 📌 **Overview**: EC2 Instance Metadata is a powerful AWS feature that allows EC2 instances to learn about themselves — their own configuration, identity, and environment — **without needing IAM roles or external calls**. This is a foundational concept for the Developer Associate exam.

### 🧠 What is EC2 Instance Metadata?

- EC2 Instance Metadata is data about your EC2 instance that the instance itself can access
- It is available at a **special internal IP address**: `http://169.254.169.254/latest/meta-data/`
- This IP is a **link-local address** — it is only accessible from **within the EC2 instance itself**, not from outside
- No IAM credentials are needed to access the metadata endpoint
- Instance metadata is useful for **bootstrapping**, **configuration**, and **identity retrieval** inside the instance

> 💡 **Key Insight**: EC2 metadata lets your instance know **who it is** — its own IP, instance type, region, availability zone, IAM role credentials, and more — without you hardcoding anything.

### 🌐 Metadata Endpoint URL

```bash
# Access instance metadata (IMDSv1 - older method, no token required)
curl <http://169.254.169.254/latest/meta-data/>

# Common metadata paths
curl <http://169.254.169.254/latest/meta-data/ami-id>
curl <http://169.254.169.254/latest/meta-data/instance-id>
curl <http://169.254.169.254/latest/meta-data/instance-type>
curl <http://169.254.169.254/latest/meta-data/local-ipv4>
curl <http://169.254.169.254/latest/meta-data/public-ipv4>
curl <http://169.254.169.254/latest/meta-data/placement/availability-zone>
curl <http://169.254.169.254/latest/meta-data/iam/security-credentials/><role-name>
```

### 🔐 IMDSv1 vs IMDSv2 — Two Versions of Instance Metadata Service

> ⚠️ **IMPORTANT for the Exam**: AWS now strongly recommends **IMDSv2** over IMDSv1 due to security improvements. Know the difference!

| Feature | IMDSv1 | IMDSv2 |
| --- | --- | --- |
| Authentication | None (direct GET) | Session-oriented (token required) |
| Security | Less secure | More secure (mitigates SSRF attacks) |
| Method | Simple HTTP GET | PUT to get token → GET with token |
| AWS Recommendation | Legacy / Deprecated | ✅ Recommended |

#### 🔑 IMDSv2 — How It Works (Session-Oriented)

IMDSv2 uses a **two-step process**:

1. **Step 1**: PUT request to get a session token (TTL: 1 second to 21600 seconds = 6 hours)
1. **Step 2**: Use the token in subsequent GET requests

```bash
# Step 1: Get a session token (valid for 21600 seconds = 6 hours)
TOKEN=$(curl -s -X PUT "<http://169.254.169.254/latest/api/token>" \
  -H "X-aws-ec2-metadata-token-ttl-seconds: 21600")

# Step 2: Use the token to retrieve metadata
curl -s -H "X-aws-ec2-metadata-token: $TOKEN" \
  <http://169.254.169.254/latest/meta-data/instance-id>

curl -s -H "X-aws-ec2-metadata-token: $TOKEN" \
  <http://169.254.169.254/latest/meta-data/public-ipv4>

curl -s -H "X-aws-ec2-metadata-token: $TOKEN" \
  <http://169.254.169.254/latest/meta-data/placement/availability-zone>
```

### 🗂️ Common Metadata Categories

```bash
# Full list of available metadata keys
curl <http://169.254.169.254/latest/meta-data/>

# Instance identity
ami-id
instance-id
instance-type
hostname

# Network information
local-hostname
local-ipv4
public-hostname
public-ipv4
mac
network/interfaces/

# Placement
placement/availability-zone
placement/region

# IAM credentials (when an IAM role is attached)
iam/security-credentials/<role-name>

# User data (bootstrap script you provided at launch)
<http://169.254.169.254/latest/user-data>
```

### 🔄 How Metadata Architecture Works

```mermaid
graph TD
    EC2["🖥️ EC2 Instance"] -->|"HTTP GET/PUT\n169.254.169.254"| IMDS["🔌 Instance Metadata\nService (IMDS)"]
    IMDS -->|Returns metadata| EC2
    IMDS -->|"iam/security-credentials/\n<role-name>"| IAMCreds["🔑 Temporary IAM\nCredentials"]
    IAMCreds --> EC2

    EC2 -->|Uses credentials| AWS["☁️ AWS Services\n(S3, DynamoDB, etc.)"]

    subgraph "Link-Local Only (169.254.0.0/16)"
        IMDS
    end
```

> 💡 **Critical Flow**: EC2 → queries metadata → gets temporary IAM role credentials → uses them to call AWS APIs. This is the foundation of how EC2 instances authenticate with AWS services **without hardcoded keys**.

### 🔑 IAM Role Credentials via Metadata

When an IAM Role is attached to an EC2 instance, you can retrieve **temporary credentials** from the metadata service:

```bash
# Get the role name first
TOKEN=$(curl -s -X PUT "<http://169.254.169.254/latest/api/token>" \
  -H "X-aws-ec2-metadata-token-ttl-seconds: 21600")

ROLE=$(curl -s -H "X-aws-ec2-metadata-token: $TOKEN" \
  <http://169.254.169.254/latest/meta-data/iam/security-credentials/>)

# Get the temporary credentials for that role
curl -s -H "X-aws-ec2-metadata-token: $TOKEN" \
  <http://169.254.169.254/latest/meta-data/iam/security-credentials/$ROLE>
```

Response looks like:

```json
{
  "Code": "Success",
  "LastUpdated": "2024-01-01T00:00:00Z",
  "Type": "AWS-HMAC",
  "AccessKeyId": "ASIA...",
  "SecretAccessKey": "wJalrXUtnFEMI...",
  "Token": "AQoXnyc4lcK4w...",
  "Expiration": "2024-01-01T06:00:00Z"
}
```

> ⚠️ **Important**: These credentials are **temporary** and **automatically rotated** by AWS. The AWS SDK automatically fetches and refreshes these credentials — you should **never** hardcode credentials into your application!

### 🛡️ Why IMDSv2 is More Secure

```mermaid
graph LR
    Attacker["🎭 Attacker\n(SSRF Attack)"] -->|"Tricks app to make\nGET request"| App["📱 Vulnerable App\non EC2"]
    App -->|"IMDSv1: Direct GET works!\nCredentials stolen!"| IMDS1["❌ IMDSv1\n(No Token)"]

    Attacker2["🎭 Attacker\n(SSRF Attack)"] -->|"Tricks app to make\nGET request"| App2["📱 Vulnerable App\non EC2"]
    App2 -->|"IMDSv2: PUT required first!\nAttack blocked!"| IMDS2["✅ IMDSv2\n(Token Required)"]
```

- **SSRF (Server-Side Request Forgery)**: Attacker tricks an EC2-hosted web app into making requests to `169.254.169.254`
- **IMDSv1**: A simple `GET` works → credentials can be stolen via SSRF
- **IMDSv2**: Requires a `PUT` first to get a token → SSRF attacks (which typically only do GET) are blocked

### ⚙️ Configuring IMDS on an Instance

```bash
# Check current IMDS configuration
aws ec2 describe-instances --instance-ids i-1234567890abcdef0 \
  --query "Reservations[].Instances[].MetadataOptions"

# Enforce IMDSv2 only on an existing instance (disable IMDSv1)
aws ec2 modify-instance-metadata-options \
  --instance-id i-1234567890abcdef0 \
  --http-tokens required \
  --http-endpoint enabled

# Require IMDSv2 at launch (in launch template or run-instances)
aws ec2 run-instances \
  --image-id ami-12345678 \
  --instance-type t2.micro \
  --metadata-options "HttpTokens=required,HttpEndpoint=enabled"
```

### 🧩 User Data vs Instance Metadata

| Feature | User Data | Instance Metadata |
| --- | --- | --- |
| URL | `/latest/user-data` | `/latest/meta-data/` |
| Purpose | Bootstrap scripts run at launch | Dynamic info about the instance |
| Content | Shell scripts, cloud-init | AMI ID, instance ID, IP, IAM creds, etc. |
| Mutability | Set at launch, re-runs on restart | Auto-generated by AWS |
| Max Size | 16 KB | N/A |

```bash
# Retrieve user data (bootstrap script) from inside the instance
TOKEN=$(curl -s -X PUT "<http://169.254.169.254/latest/api/token>" \
  -H "X-aws-ec2-metadata-token-ttl-seconds: 21600")

curl -s -H "X-aws-ec2-metadata-token: $TOKEN" \
  <http://169.254.169.254/latest/user-data>
```

### 🆕 Instance Identity Document

A special endpoint that provides a **signed JSON document** with the instance's identity — useful for verifying the instance's identity to external services:

```bash
# Get the instance identity document
TOKEN=$(curl -s -X PUT "<http://169.254.169.254/latest/api/token>" \
  -H "X-aws-ec2-metadata-token-ttl-seconds: 21600")

curl -s -H "X-aws-ec2-metadata-token: $TOKEN" \
  <http://169.254.169.254/latest/dynamic/instance-identity/document>
```

Response includes:

```json
{
  "accountId": "123456789012",
  "architecture": "x86_64",
  "availabilityZone": "us-east-1a",
  "imageId": "ami-12345678",
  "instanceId": "i-1234567890abcdef0",
  "instanceType": "t2.micro",
  "region": "us-east-1",
  "privateIp": "172.31.0.5"
}
```

### 📋 Key Exam Takeaways

- `169.254.169.254` is the magic IP — memorize it! It's the link-local metadata endpoint accessible only from within the EC2 instance
- **IMDSv1** = simple GET, no authentication → less secure
- **IMDSv2** = PUT to get token first, then GET with token → more secure, mitigates SSRF
- `/latest/meta-data/` → instance metadata (ID, IP, AZ, IAM creds, etc.)
- `/latest/user-data` → bootstrap script provided at launch
- `/latest/dynamic/instance-identity/document` → signed identity document
- IAM role credentials are available at `/latest/meta-data/iam/security-credentials/<role-name>` and are **automatically rotated**
- The AWS SDK **automatically** uses instance metadata to retrieve IAM credentials — no manual intervention needed
- You can **enforce IMDSv2** on instances using `aws ec2 modify-instance-metadata-options --http-tokens required`
- Metadata is **not encrypted in transit** (HTTP, not HTTPS) — which is why the link-local restriction + IMDSv2 tokens are crucial for security

---

## Lecture 127: 🛠️ AWS EC2 Instance Metadata - Hands On

> 📌 **Overview**: This is a practical, hands-on lecture where Stephane demonstrates how to access EC2 Instance Metadata from within a running EC2 instance using both IMDSv1 and IMDSv2. You will SSH into an EC2 instance and run `curl` commands against the `169.254.169.254` endpoint to retrieve real metadata values live.

### 🚀 Hands-On Setup

#### Prerequisites

- A running EC2 instance (any Amazon Linux 2 / Amazon Linux 2023 instance works)
- SSH access to the instance (via key pair or EC2 Instance Connect)
- An IAM role attached to the EC2 instance (to demo credential retrieval)

```bash
# Connect to your EC2 instance via SSH
ssh -i "my-key.pem" ec2-user@<your-ec2-public-ip>

# OR use EC2 Instance Connect directly from the AWS Console
# (no key pair needed)
```

### 🔍 Step 1 — Exploring Metadata with IMDSv1

> ⚠️ **Note**: IMDSv1 works with simple GET requests and no token. It's the older, less secure method. Useful for quick demos, but always prefer IMDSv2 in production.

```bash
# List all top-level metadata categories
curl <http://169.254.169.254/latest/meta-data/>
```

You'll see output like:

```text
ami-id
ami-launch-index
ami-manifest-path
block-device-mapping/
hostname
iam/
instance-action
instance-id
instance-life-cycle
instance-type
local-hostname
local-ipv4
mac
metrics/
network/
placement/
profile
public-hostname
public-ipv4
public-keys/
reservation-id
security-groups
services/
```

```bash
# Retrieve specific metadata values
curl <http://169.254.169.254/latest/meta-data/instance-id>
# Example output: i-0abc1234def5678

curl <http://169.254.169.254/latest/meta-data/instance-type>
# Example output: t2.micro

curl <http://169.254.169.254/latest/meta-data/local-ipv4>
# Example output: 172.31.12.34

curl <http://169.254.169.254/latest/meta-data/public-ipv4>
# Example output: 54.123.45.67

curl <http://169.254.169.254/latest/meta-data/placement/availability-zone>
# Example output: us-east-1a

curl <http://169.254.169.254/latest/meta-data/placement/region>
# Example output: us-east-1

curl <http://169.254.169.254/latest/meta-data/hostname>
# Example output: ip-172-31-12-34.ec2.internal
```

### 🔐 Step 2 — Retrieving IAM Role Credentials via Metadata

> 💡 This is one of the most important things to understand: **how EC2 automatically provides credentials to your application via the metadata service**.

```bash
# First, list the IAM role attached to this instance
curl <http://169.254.169.254/latest/meta-data/iam/security-credentials/>
# Output: my-ec2-role  (the name of the IAM role)

# Then, get the temporary credentials for that role
curl <http://169.254.169.254/latest/meta-data/iam/security-credentials/my-ec2-role>
```

The response is a JSON object with temporary credentials:

```json
{
  "Code": "Success",
  "LastUpdated": "2024-01-15T10:30:00Z",
  "Type": "AWS-HMAC",
  "AccessKeyId": "ASIAIOSFODNN7EXAMPLE",
  "SecretAccessKey": "wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY",
  "Token": "AQoDYXdzEJr...<very long token>",
  "Expiration": "2024-01-15T16:30:00Z"
}
```

> ⚠️ **Key Observation**: These credentials have an `Expiration` time (~6 hours). AWS **automatically rotates** them before they expire. The AWS SDK handles this refresh transparently — your application never needs to manually manage this rotation.

### 🔒 Step 3 — Using IMDSv2 (Token-Based, Secure Method)

> ✅ **Best Practice**: Always use IMDSv2 in production. This is what Stephane demonstrates as the recommended approach.

```bash
# Step 1: Request a session token (valid for up to 6 hours = 21600 seconds)
TOKEN=$(curl -s -X PUT "<http://169.254.169.254/latest/api/token>" \
  -H "X-aws-ec2-metadata-token-ttl-seconds: 21600")

# Verify the token was received
echo $TOKEN
# Output: a long alphanumeric string

# Step 2: Use the token for all subsequent metadata requests
curl -s -H "X-aws-ec2-metadata-token: $TOKEN" \
  <http://169.254.169.254/latest/meta-data/instance-id>

curl -s -H "X-aws-ec2-metadata-token: $TOKEN" \
  <http://169.254.169.254/latest/meta-data/instance-type>

curl -s -H "X-aws-ec2-metadata-token: $TOKEN" \
  <http://169.254.169.254/latest/meta-data/placement/availability-zone>

# Get IAM credentials securely via IMDSv2
ROLE=$(curl -s -H "X-aws-ec2-metadata-token: $TOKEN" \
  <http://169.254.169.254/latest/meta-data/iam/security-credentials/>)

curl -s -H "X-aws-ec2-metadata-token: $TOKEN" \
  <http://169.254.169.254/latest/meta-data/iam/security-credentials/$ROLE>
```

### 🔄 Complete IMDSv2 Workflow Diagram

```mermaid
sequenceDiagram
    participant Shell as 🖥️ EC2 Shell
    participant IMDS as 🔌 IMDS (169.254.169.254)
    participant IAM as 🔑 IAM Service

    Shell->>IMDS: PUT /latest/api/token (TTL=21600)
    IMDS-->>Shell: Session Token (e.g., "AQAEAFi...")

    Shell->>IMDS: GET /latest/meta-data/instance-id<br/>[Header: X-aws-ec2-metadata-token: TOKEN]
    IMDS-->>Shell: i-0abc1234def56789

    Shell->>IMDS: GET /latest/meta-data/iam/security-credentials/my-role<br/>[Header: X-aws-ec2-metadata-token: TOKEN]
    IMDS->>IAM: Fetch temporary credentials for role
    IAM-->>IMDS: AccessKeyId, SecretKey, Token
    IMDS-->>Shell: JSON with temporary credentials

    Shell->>Shell: Use credentials to call AWS APIs
```

### 📁 Step 4 — Accessing User Data

```bash
# View the User Data (bootstrap script) that was passed at instance launch
curl -s -H "X-aws-ec2-metadata-token: $TOKEN" \
  <http://169.254.169.254/latest/user-data>

# Example output (if user data was provided):
#!/bin/bash
yum update -y
yum install -y httpd
systemctl start httpd
systemctl enable httpd
echo "<h1>Hello from EC2!</h1>" > /var/www/html/index.html
```

> 💡 If no user data was provided at launch, the endpoint returns a `404 Not Found`. This is expected behavior.

### 🆔 Step 5 — Instance Identity Document

```bash
# Get the full identity document (unsigned)
curl -s -H "X-aws-ec2-metadata-token: $TOKEN" \
  <http://169.254.169.254/latest/dynamic/instance-identity/document>
```

```json
{
  "accountId": "123456789012",
  "architecture": "x86_64",
  "availabilityZone": "us-east-1a",
  "billingProducts": null,
  "devpayProductCodes": null,
  "marketplaceProductCodes": null,
  "imageId": "ami-0abcdef1234567890",
  "instanceId": "i-0abc1234def56789",
  "instanceType": "t2.micro",
  "kernelId": null,
  "pendingTime": "2024-01-15T08:00:00Z",
  "privateIp": "172.31.12.34",
  "ramdiskId": null,
  "region": "us-east-1",
  "version": "2017-09-30"
}
```

### 🔧 Step 6 — Enforcing IMDSv2 Only (Disabling IMDSv1)

After testing, it's best practice to enforce IMDSv2 only so IMDSv1 is completely disabled:

```bash
# Run this from your LOCAL machine (not the EC2 instance)
# Enforce IMDSv2 on an existing running instance
aws ec2 modify-instance-metadata-options \
  --instance-id i-0abc1234def56789 \
  --http-tokens required \
  --http-endpoint enabled \
  --region us-east-1

# Verify the change
aws ec2 describe-instances \
  --instance-ids i-0abc1234def56789 \
  --query "Reservations[0].Instances[0].MetadataOptions" \
  --region us-east-1
```

Expected output after enforcement:

```json
{
  "State": "applied",
  "HttpTokens": "required",
  "HttpPutResponseHopLimit": 1,
  "HttpEndpoint": "enabled",
  "HttpProtocolIpv6": "disabled",
  "InstanceMetadataTags": "disabled"
}
```

> ⚠️ Once `HttpTokens` is set to `required`, any IMDSv1 GET request without a token will return **HTTP 401 Unauthorized**. Make sure your application uses IMDSv2 (the AWS SDK v2+ does this automatically).

### 🗂️ Summary of Key Metadata Paths Explored

| Metadata Path | What It Returns |
| --- | --- |
| `/latest/meta-data/instance-id` | EC2 instance ID (e.g., `i-0abc...`) |
| `/latest/meta-data/instance-type` | Instance type (e.g., `t2.micro`) |
| `/latest/meta-data/local-ipv4` | Private IP address |
| `/latest/meta-data/public-ipv4` | Public IP address |
| `/latest/meta-data/placement/availability-zone` | AZ (e.g., `us-east-1a`) |
| `/latest/meta-data/placement/region` | Region (e.g., `us-east-1`) |
| `/latest/meta-data/iam/security-credentials/` | IAM role name |
| `/latest/meta-data/iam/security-credentials/<role>` | Temporary credentials JSON |
| `/latest/user-data` | Bootstrap user data script |
| `/latest/dynamic/instance-identity/document` | Full identity JSON document |
| `/latest/api/token` | IMDSv2 session token (PUT request) |

### 📋 Key Exam Takeaways

- The metadata endpoint `http://169.254.169.254/latest/meta-data/` is **only accessible from inside the EC2 instance** (link-local IP)
- **IMDSv1** = simple `curl` GET with no headers — works by default but is less secure
- **IMDSv2** = must first PUT to `/latest/api/token` with a TTL header to get a session token, then use that token as a header on all GET requests
- IAM role credentials are accessible via `/latest/meta-data/iam/security-credentials/<role-name>` and contain `AccessKeyId`, `SecretAccessKey`, and `Token` (session token)
- These credentials are **temporary** — they auto-expire and are auto-rotated by AWS
- **The AWS SDK automatically queries this endpoint** — you never need to manually call it in your application code; the SDK does it transparently
- You can **disable IMDSv1** using `aws ec2 modify-instance-metadata-options --http-tokens required` — this is a security best practice
- User data (bootstrap script) is at `/latest/user-data` — returns 404 if none was specified at launch
- The `HttpPutResponseHopLimit` (default: 1) prevents metadata from being accessed from container workloads or proxies by limiting how many network hops the PUT response can travel

---

## Lecture 128: 👤 AWS CLI Profiles

> 📌 **Overview**: AWS CLI Profiles allow you to manage **multiple AWS accounts or IAM users** on the same machine by storing named credential configurations. Instead of constantly switching access keys, you simply reference a profile name. This is essential for developers working across dev, staging, and production environments.

### 🧠 Why CLI Profiles Exist

- By default, the AWS CLI uses the `[default]` profile when you run any command
- In real-world scenarios, developers often need to interact with **multiple AWS accounts** (e.g., a personal account AND a work account, or dev + prod)
- Without profiles, you'd have to manually reconfigure `aws configure` every time you switch accounts — which is error-prone and tedious
- **Named profiles** solve this by letting you store multiple credential sets and select them at will using `-profile <name>`

### 🗂️ Where AWS CLI Credentials Are Stored

The AWS CLI stores credentials and configuration in **two files** on your local machine:

| File | Purpose | Location |
| --- | --- | --- |
| `~/.aws/credentials` | Access Key ID & Secret Access Key | `C:\Users\<you>\.aws\credentials` (Windows) |
| `~/.aws/config` | Region, output format, and other config | `C:\Users\<you>\.aws\config` (Windows) |

```bash
# View your credentials file
cat ~/.aws/credentials

# View your config file
cat ~/.aws/config
```

#### 📄 Credentials File Structure

```bash
# ~/.aws/credentials

[default]
aws_access_key_id = AKIAIOSFODNN7EXAMPLE
aws_secret_access_key = wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY

[my-second-account]
aws_access_key_id = AKIAI44QH8DHBEXAMPLE
aws_secret_access_key = je7MtGbClwBF/2Zp9Utk/h3yCo8nvbEXAMPLEKEY

[production]
aws_access_key_id = AKIAIOSFODNN7EXAMPLE3
aws_secret_access_key = xRiAFVBKpQxEXAMPLEKEY3
```

#### 📄 Config File Structure

```bash
# ~/.aws/config

[default]
region = us-east-1
output = json

[profile my-second-account]
region = eu-west-1
output = json

[profile production]
region = ap-south-1
output = table
```

> ⚠️ **Important Difference**: In `~/.aws/credentials`, profile names are written as `[profile-name]`. In `~/.aws/config`, **non-default** profiles must be prefixed with the word `profile` → `[profile profile-name]`. The default is just `[default]` in both files.

### ⚙️ Creating a New Named Profile

Use `aws configure` with the `--profile` flag to set up a named profile interactively:

```bash
# Create a new named profile called "my-second-account"
aws configure --profile my-second-account
```

You'll be prompted for:

```text
AWS Access Key ID [None]: AKIAI44QH8DHBEXAMPLE
AWS Secret Access Key [None]: je7MtGbClwBF/2Zp9Utk/h3yCo8nvbEXAMPLEKEY
Default region name [None]: eu-west-1
Default output format [None]: json
```

After this, the credentials are saved to `~/.aws/credentials` under `[my-second-account]` and config under `[profile my-second-account]`.

### 🚀 Using a Named Profile in CLI Commands

Add `--profile <name>` to any AWS CLI command to use a specific profile:

```bash
# Use the default profile (no --profile flag needed)
aws s3 ls

# Use a specific named profile
aws s3 ls --profile my-second-account

# Use another profile
aws ec2 describe-instances --profile production

# Get caller identity to confirm which account/user is active
aws sts get-caller-identity
aws sts get-caller-identity --profile my-second-account
aws sts get-caller-identity --profile production
```

### 🔄 Profile Resolution Flow

```mermaid
flowchart TD
    CMD["🖥️ aws <command> [--profile name]"] --> HasProfile{"--profile\nflag provided?"}

    HasProfile -->|Yes| NamedProfile["Look up named profile\nin ~/.aws/credentials\nand ~/.aws/config"]
    HasProfile -->|No| EnvVar{"AWS_PROFILE\nenv var set?"}

    EnvVar -->|Yes| EnvProfile["Use profile from\nAWS_PROFILE env var"]
    EnvVar -->|No| EnvKeys{"AWS_ACCESS_KEY_ID\nenv var set?"}

    EnvKeys -->|Yes| EnvCreds["Use credentials\nfrom environment variables"]
    EnvKeys -->|No| DefaultProfile["Use [default] profile\nfrom ~/.aws/credentials"]

    NamedProfile --> Execute["✅ Execute AWS API Call"]
    EnvProfile --> Execute
    EnvCreds --> Execute
    DefaultProfile --> Execute
```

> 💡 **Credential Provider Chain**: The AWS SDK and CLI resolve credentials in a specific order of priority. Environment variables take precedence over the `~/.aws/credentials` file. This is important for Lambda, EC2, and CI/CD environments.

### 🌍 Setting a Profile via Environment Variable

Instead of using `--profile` on every command, you can set the `AWS_PROFILE` environment variable for your shell session:

```bash
# Linux / macOS — set for the current shell session
export AWS_PROFILE=my-second-account
aws s3 ls  # Now automatically uses my-second-account

# Windows PowerShell
$env:AWS_PROFILE = "my-second-account"
aws s3 ls

# Windows Command Prompt
set AWS_PROFILE=my-second-account
aws s3 ls

# Reset back to default
unset AWS_PROFILE          # Linux/macOS
Remove-Item Env:AWS_PROFILE  # PowerShell
```

### 🔍 Listing & Inspecting Profiles

```bash
# List all configured profiles
aws configure list-profiles

# View current active config for a profile
aws configure list --profile my-second-account

# Sample output:
#       Name                    Value             Type    Location
#       ----                    -----             ----    --------
#    profile          my-second-account           manual    --profile
# access_key     ****************EXAM shared-credentials-file
# secret_key     ****************EKEY shared-credentials-file
#     region                eu-west-1      config-file    ~/.aws/config
```

### 🔧 Manually Editing the Credentials File

You can also directly edit `~/.aws/credentials` to add, update, or remove profiles:

```bash
# Linux/macOS
nano ~/.aws/credentials

# Windows — open in notepad
notepad C:\Users\<YourUsername>\.aws\credentials
```

Example of a fully populated credentials file with 3 profiles:

```bash
[default]
aws_access_key_id = AKIAIOSFODNN7DEFAULT
aws_secret_access_key = defaultsecretkey123

[dev]
aws_access_key_id = AKIAIOSFODNN7DEVKEY
aws_secret_access_key = devsecretkey456

[prod]
aws_access_key_id = AKIAIOSFODNN7PRODKEY
aws_secret_access_key = prodsecretkey789
```

### 💡 Using Profiles in the AWS SDK (Node.js)

When building applications locally that need to use a specific profile, you can specify it in the SDK:

```javascript
import { S3Client } from "@aws-sdk/client-s3";
import { fromIni } from "@aws-sdk/credential-providers";

// Use a specific named profile from ~/.aws/credentials
const client = new S3Client({
  region: "eu-west-1",
  credentials: fromIni({ profile: "my-second-account" }),
});

// Example: List buckets using the named profile
import { ListBucketsCommand } from "@aws-sdk/client-s3";

const response = await client.send(new ListBucketsCommand({}));
console.log("Buckets:", response.Buckets);
```

```javascript
// You can also use the AWS_PROFILE env variable approach
// and the SDK will pick it up automatically — no code changes needed
// Just set: process.env.AWS_PROFILE = 'my-second-account'
// or export AWS_PROFILE=my-second-account before running your app

import { S3Client, ListBucketsCommand } from "@aws-sdk/client-s3";

// SDK automatically reads AWS_PROFILE from environment
const client = new S3Client({ region: "eu-west-1" });
const response = await client.send(new ListBucketsCommand({}));
console.log(response.Buckets);
```

> ⚠️ **Production Note**: In production (Lambda, EC2, ECS), **never use hardcoded profiles or access keys**. Attach IAM roles directly to the compute resource. Profiles are for **local development only**.

### 🏗️ Multi-Account Architecture with Profiles

```mermaid
graph TD
    Dev["👨‍💻 Developer Machine"] --> Default["[default] profile\nPersonal AWS Account\nRegion: us-east-1"]
    Dev --> Work["[work] profile\nCompany AWS Account\nRegion: eu-west-1"]
    Dev --> Prod["[production] profile\nProd AWS Account\nRegion: ap-south-1"]

    Default -->|"aws s3 ls"| PersonalAWS["☁️ Personal AWS"]
    Work -->|"aws s3 ls --profile work"| CompanyAWS["☁️ Company AWS"]
    Prod -->|"aws ec2 describe-instances --profile production"| ProdAWS["☁️ Production AWS"]
```

### 📋 Key Exam Takeaways

- **Named profiles** let you store and switch between multiple AWS credential sets on one machine
- Create a profile with: `aws configure --profile <name>`
- Use a profile in any CLI command with: `-profile <name>`
- Credentials are stored in `~/.aws/credentials`; config (region, output) in `~/.aws/config`
- In `~/.aws/config`, non-default profiles must be prefixed with `profile` keyword: `[profile my-name]`
- The `AWS_PROFILE` environment variable can set the active profile for the entire shell session without needing `-profile` on every command
- The **credential provider chain** priority: environment variables → `~/.aws/credentials` → IAM role (on EC2/Lambda)
- The `aws sts get-caller-identity` command is the fastest way to verify which account/user a profile is authenticated as
- In SDK code, use `fromIni({ profile: 'name' })` from `@aws-sdk/credential-providers` to use a named profile
- **Never use named profiles in production** — use IAM roles attached to compute resources instead

---

## Lecture 129: 🔐 AWS CLI with MFA

> **Course**: Ultimate AWS Certified Developer Associate DVA-C02 2026<br>**Instructor**: Stephane Maarek<br>**Section 12**: AWS CLI, SDK, IAM Roles & Policies

### 📌 Overview

When working with the **AWS CLI**, some operations may require **Multi-Factor Authentication (MFA)** — especially when your IAM policies enforce MFA or when you need to assume a role that has an MFA condition. In this lecture, we learn how to **authenticate the AWS CLI using MFA** by obtaining **temporary security credentials** via **AWS STS (Security Token Service)**.

---

### 🔑 Why Use MFA with the CLI?

By default, the AWS CLI uses long-term credentials (Access Key ID + Secret Access Key). However:

- Some **IAM policies** include a condition like `aws:MultiFactorAuthPresent: true`
- Without MFA, these API calls will be **denied**
- To satisfy MFA requirements, you must obtain **temporary credentials** from STS

> **Key Insight**: The CLI itself doesn't prompt for MFA. You must manually call STS to get short-lived credentials that are MFA-validated.

---

### 🏗️ Architecture: How MFA + STS Works

```mermaid
sequenceDiagram
    participant User as 👤 Developer (CLI)
    participant STS as 🔑 AWS STS
    participant IAM as 🛡️ IAM Policy
    participant Service as ☁️ AWS Service (e.g., S3)

    User->>STS: sts get-session-token (with MFA serial + token code)
    STS-->>User: Temporary Credentials (AccessKeyId, SecretAccessKey, SessionToken)
    User->>User: Export temp credentials as env vars or profile
    User->>Service: API Call (e.g., s3 ls)
    Service->>IAM: Check policy (aws:MultiFactorAuthPresent)
    IAM-->>Service: ✅ Allowed (MFA condition satisfied)
    Service-->>User: Response
```

---

### 🧩 Step-by-Step: Using MFA with the AWS CLI

#### \## Step 1: Find Your MFA Device ARN

In the AWS Console:

1. Go to **IAM → Users → Your User → Security credentials**
1. Under **Multi-Factor Authentication (MFA)**, copy the **MFA device ARN**

It looks like:

```text
arn:aws:iam::123456789012:mfa/my-user
```

---

#### \## Step 2: Call STS `get-session-token`

Use the `aws sts get-session-token` command with:

| Parameter | Description |
| --- | --- |
| `--serial-number` | ARN of your MFA device |
| `--token-code` | 6-digit code from your MFA app (Google Authenticator, etc.) |
| `--duration-seconds` | How long the temp credentials are valid (900s to 129600s) |

```bash
aws sts get-session-token \
  --serial-number arn:aws:iam::123456789012:mfa/my-user \
  --token-code 123456 \
  --duration-seconds 3600
```

#### \## Sample Response

```json
{
  "Credentials": {
    "AccessKeyId":     "ASIA...",
    "SecretAccessKey": "wJalrXUt...",
    "SessionToken":    "AQoDYXdzE...(long token)...",
    "Expiration":      "2026-06-29T12:00:00Z"
  }
}
```

> **Important**: The `SessionToken` is **mandatory** when using temporary credentials. Without it, your requests will be denied.

---

#### \## Step 3: Export Temporary Credentials

You have two main approaches to use these credentials:

##### 🅰 Option A: Export as Environment Variables

```bash
export AWS_ACCESS_KEY_ID=ASIA...
export AWS_SECRET_ACCESS_KEY=wJalrXUt...
export AWS_SESSION_TOKEN=AQoDYXdzE...
```

Now any `aws` command in this shell session will use the MFA-authenticated credentials automatically.

##### 🅱 Option B: Add as a Named CLI Profile

```bash
aws configure --profile mfa-session
# Enter the AccessKeyId and SecretAccessKey when prompted
```

Then manually add the session token to `~/.aws/credentials`:

```text
[mfa-session]
aws_access_key_id     = ASIA...
aws_secret_access_key = wJalrXUt...
aws_session_token     = AQoDYXdzE...
```

Use it with:

```bash
aws s3 ls --profile mfa-session
```

---

### 🔒 IAM Policy Enforcing MFA

Here's an example IAM policy that **denies all actions** unless MFA is present:

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "DenyWithoutMFA",
      "Effect": "Deny",
      "NotAction": [
        "iam:CreateVirtualMFADevice",
        "iam:EnableMFADevice",
        "iam:GetUser",
        "iam:ListMFADevices",
        "sts:GetSessionToken"
      ],
      "Resource": "*",
      "Condition": {
        "BoolIfExists": {
          "aws:MultiFactorAuthPresent": "false"
        }
      }
    }
  ]
}
```

> **Note**: The `NotAction` block excludes MFA-setup actions so users can still enable their own MFA device even before they've authenticated with one.

---

### ⏱️ Temporary Credential Lifetimes

| Credential Type | Duration |
| --- | --- |
| STS `get-session-token` (MFA) | 900s (15 min) to 129,600s (36 hours) |
| `assume-role` | 900s to 43,200s (12 hours) |
| IAM User long-term keys | Never expire (until rotated/deleted) |

> **Best Practice**: Use the **shortest duration** sufficient for your task to minimize the blast radius if credentials are leaked.

---

### 🔁 Credential Resolution Order (Reminder)

AWS CLI resolves credentials in this order — MFA temp credentials set as env vars take **top priority**:

```mermaid
flowchart TD
    A["1️⃣ Environment Variables\n(AWS_ACCESS_KEY_ID, AWS_SESSION_TOKEN)"] --> B["2️⃣ AWS Credentials File\n(~/.aws/credentials)"]
    B --> C["3️⃣ AWS Config File\n(~/.aws/config)"]
    C --> D["4️⃣ Container Credentials\n(ECS Task Role)"]
    D --> E["5️⃣ EC2 Instance Profile\n(Instance Metadata Service)"]
```

---

### 🛠️ Node.js: Calling STS `getSessionToken` Programmatically

```javascript
import { STSClient, GetSessionTokenCommand } from "@aws-sdk/client-sts";

const stsClient = new STSClient({ region: "us-east-1" });

const response = await stsClient.send(
  new GetSessionTokenCommand({
    SerialNumber: "arn:aws:iam::123456789012:mfa/my-user",
    TokenCode:    "123456",  // From MFA app
    DurationSeconds: 3600,
  })
);

const { AccessKeyId, SecretAccessKey, SessionToken } = response.Credentials;
console.log("Temp AccessKeyId:", AccessKeyId);
console.log("Session Token:", SessionToken);

// Now use these to create a new client with temporary credentials
import { S3Client, ListBucketsCommand } from "@aws-sdk/client-s3";

const mfaS3Client = new S3Client({
  region: "us-east-1",
  credentials: {
    accessKeyId:     AccessKeyId,
    secretAccessKey: SecretAccessKey,
    sessionToken:    SessionToken,
  },
});

const buckets = await mfaS3Client.send(new ListBucketsCommand({}));
console.log("Buckets:", buckets.Buckets);
```

---

### 🌟 Key Exam Takeaways

- `aws sts get-session-token` is used to generate **temporary credentials validated by MFA**
- You must pass `-serial-number` (MFA device ARN) and `-token-code` (6-digit OTP)
- The response includes **3 components**: `AccessKeyId`, `SecretAccessKey`, `SessionToken`
- The `SessionToken` **must always be included** when making API calls with temporary credentials
- Set these as **environment variables** or add to `~/.aws/credentials` for CLI use
- IAM policies can enforce MFA with the condition key `aws:MultiFactorAuthPresent: true`
- Temporary credentials automatically **expire** — no need to manually revoke them
- This pattern is critical when roles have **MFA condition requirements** (e.g., for sensitive S3 buckets or admin actions)

---

## Lecture 130: 🛠️ AWS SDK Overview

> **Course**: Ultimate AWS Certified Developer Associate DVA-C02 2026 \| **Instructor**: Stephane Maarek<br>**Section 12**: AWS CLI, SDK, IAM Roles & Policies

### 📌 What is the AWS SDK?

The **AWS Software Development Kit (SDK)** is a set of libraries that lets you interact with AWS services **directly from your application code** — without going through the AWS Console or CLI.

- The SDK wraps the **AWS REST APIs** into easy-to-use language-native functions
- It handles authentication (via **AWS Signature v4**), request signing, serialization, and retries automatically
- Available for many languages: **JavaScript/Node.js**, Python, Java, .NET, Go, C++, PHP, Ruby, etc.

> 💡 For the DVA-C02 exam, **Node.js SDK v3 (**`@aws-sdk`**)** is the reference implementation you should know.

---

### 🧩 Why Use the SDK?

| Approach | Best For |
| --- | --- |
| AWS Console | Manual, one-off tasks |
| AWS CLI | Scripting & automation |
| **AWS SDK** | **Application code, Lambda functions, backend services** |

When you write a Lambda function, a backend API, or any application that needs to call AWS services (S3, DynamoDB, SQS, etc.), you use the **SDK**.

---

### 🏗️ AWS SDK v3 Architecture (Node.js)

AWS SDK v3 introduced a **modular, package-per-service** design. You install only what you need.

```mermaid
graph TD
    A["Your Node.js Application"] --> B["@aws-sdk/client-s3"]
    A --> C["@aws-sdk/client-dynamodb"]
    A --> D["@aws-sdk/client-sqs"]
    B --> E["AWS S3 Service"]
    C --> F["AWS DynamoDB Service"]
    D --> G["AWS SQS Service"]
    E --> H["AWS Cloud"]
    F --> H
    G --> H
```

Each service has its own package:

- `@aws-sdk/client-s3` → Amazon S3
- `@aws-sdk/client-dynamodb` → DynamoDB
- `@aws-sdk/client-sqs` → SQS
- `@aws-sdk/client-sns` → SNS
- `@aws-sdk/client-lambda` → Lambda
- etc.

---

### 🔐 SDK Authentication & Credentials

The SDK uses a **credentials provider chain** to find credentials automatically, in this order:

```mermaid
flowchart TD
    A["SDK Call Initiated"] --> B{"Environment Variables?\nAWS_ACCESS_KEY_ID\nAWS_SECRET_ACCESS_KEY"}
    B -- Yes --> Z["✅ Use These Credentials"]
    B -- No --> C{"~/.aws/credentials file?\n[default] or named profile"}
    C -- Yes --> Z
    C -- No --> D{"ECS Task Role / EKS Service Account?"}
    D -- Yes --> Z
    D -- No --> E{"EC2 Instance Metadata?\nIAM Role attached to EC2"}
    E -- Yes --> Z
    E -- No --> F["❌ Credentials Not Found → SDK throws error"]
```

> 🚨 **NEVER hardcode AWS credentials in your application code.** This is a massive security risk. Always use the credentials chain.

#### Best Practice: Use IAM Roles

- **EC2** → Attach an **IAM Role** to the instance → SDK picks it up from instance metadata automatically
- **Lambda** → Lambda's **execution role** is automatically injected
- **ECS** → Task Role is used

---

### 🚀 Getting Started with SDK v3 (Node.js)

#### Installation

```bash
npm install @aws-sdk/client-s3
npm install @aws-sdk/client-dynamodb
# Install only what you need
```

#### Basic Pattern: Client → Command → Send

Every SDK v3 call follows the same 3-step pattern:

```javascript
import { S3Client, ListBucketsCommand } from "@aws-sdk/client-s3";

// 1️⃣ Create a Client (configure region, credentials auto-loaded from chain)
const s3Client = new S3Client({ region: "us-east-1" });

// 2️⃣ Create a Command
const command = new ListBucketsCommand({});

// 3️⃣ Send the Command
const response = await s3Client.send(command);
console.log("Buckets:", response.Buckets);
```

---

### 📦 Common SDK Operations

#### ✅ S3 — Upload and Retrieve an Object

```javascript
import {
  S3Client,
  PutObjectCommand,
  GetObjectCommand
} from "@aws-sdk/client-s3";

const s3 = new S3Client({ region: "us-east-1" });

// Upload
await s3.send(new PutObjectCommand({
  Bucket: "my-bucket",
  Key: "hello.txt",
  Body: "Hello from SDK v3!"
}));

// Download
const result = await s3.send(new GetObjectCommand({
  Bucket: "my-bucket",
  Key: "hello.txt"
}));

// Stream to string
const bodyContents = await result.Body.transformToString();
console.log(bodyContents);
```

#### ✅ DynamoDB — Put and Get Item

```javascript
import {
  DynamoDBClient,
  PutItemCommand,
  GetItemCommand
} from "@aws-sdk/client-dynamodb";

const ddb = new DynamoDBClient({ region: "us-east-1" });

// Put Item
await ddb.send(new PutItemCommand({
  TableName: "Users",
  Item: {
    userId: { S: "user-001" },
    name:   { S: "Alice" },
    age:    { N: "30" }
  }
}));

// Get Item
const response = await ddb.send(new GetItemCommand({
  TableName: "Users",
  Key: { userId: { S: "user-001" } }
}));

console.log(response.Item);
```

#### ✅ SQS — Send and Receive a Message

```javascript
import {
  SQSClient,
  SendMessageCommand,
  ReceiveMessageCommand
} from "@aws-sdk/client-sqs";

const sqs = new SQSClient({ region: "us-east-1" });
const QUEUE_URL = "<https://sqs.us-east-1.amazonaws.com/123456789/MyQueue>";

// Send
await sqs.send(new SendMessageCommand({
  QueueUrl: QUEUE_URL,
  MessageBody: JSON.stringify({ event: "order_placed", orderId: "999" }),
  DelaySeconds: 0
}));

// Receive
const data = await sqs.send(new ReceiveMessageCommand({
  QueueUrl: QUEUE_URL,
  MaxNumberOfMessages: 10,
  WaitTimeSeconds: 5  // Long polling
}));

console.log(data.Messages);
```

---

### 🌍 SDK Default Region

> **Important**: If you do not specify a `region` in the client config, the SDK will look for it in:
>
> 1. `AWS_DEFAULT_REGION` environment variable
> 1. `~/.aws/config` file
> 1. EC2 instance metadata

- **Recommendation**: Always explicitly set the region in your client config or via the `AWS_DEFAULT_REGION` env variable.
- If no region is found → SDK throws a `No region error`

```javascript
// Explicit region (recommended)
const client = new S3Client({ region: process.env.AWS_REGION || "us-east-1" });
```

---

### 🔄 SDK Request Lifecycle

```mermaid
sequenceDiagram
    participant App as Your Application
    participant SDK as AWS SDK v3
    participant Auth as Credentials Provider
    participant AWS as AWS Service API

    App->>SDK: client.send(new XxxCommand(params))
    SDK->>Auth: Resolve Credentials (env / profile / role)
    Auth-->>SDK: Access Key + Secret + Session Token
    SDK->>SDK: Sign request with SigV4
    SDK->>AWS: HTTPS Request (signed)
    AWS-->>SDK: HTTP Response (JSON/XML)
    SDK-->>App: Parsed JavaScript Object
```

---

### ⚙️ SDK Configuration Options

```javascript
import { S3Client } from "@aws-sdk/client-s3";

const s3 = new S3Client({
  region: "us-east-1",

  // Optional: Override credentials manually (use sparingly)
  credentials: {
    accessKeyId: process.env.AWS_ACCESS_KEY_ID,
    secretAccessKey: process.env.AWS_SECRET_ACCESS_KEY
  },

  // Optional: Custom endpoint (for LocalStack or mocking)
  endpoint: "<http://localhost:4566>",

  // Optional: Force path-style for S3 (needed for LocalStack)
  forcePathStyle: true
});
```

---

### 🧪 Using SDK in AWS Lambda

In Lambda, you **do NOT need to install** `@aws-sdk` — it is bundled in the Lambda runtime. However, for **SDK v3**, you should install and bundle it yourself to use the latest version and tree-shake unnecessary code.

```javascript
// Lambda handler using SDK v3 (bundled by you for best practice)
import { DynamoDBClient, PutItemCommand } from "@aws-sdk/client-dynamodb";

const ddb = new DynamoDBClient({}); // No region needed → Lambda env handles it

export const handler = async (event) => {
  await ddb.send(new PutItemCommand({
    TableName: process.env.TABLE_NAME,
    Item: {
      id:      { S: event.id },
      payload: { S: JSON.stringify(event) }
    }
  }));

  return { statusCode: 200, body: "Saved!" };
};
```

> 💡 Use `process.env.TABLE_NAME` and `process.env.AWS_REGION` — these are injected by Lambda automatically.

---

### 🆚 SDK v2 vs SDK v3

| Feature | SDK v2 (`aws-sdk`) | SDK v3 (`@aws-sdk/*`) |
| --- | --- | --- |
| Package size | Monolithic (entire SDK in one package) | Modular (install per service) |
| Tree shaking | ❌ Not supported | ✅ Supported |
| Async model | Callbacks + Promises | **Promises only (async/await)** |
| Middleware | Limited | ✅ Middleware stack |
| TypeScript | Basic types | ✅ First-class TypeScript support |
| Bundle size | Large | **Smaller (only what you use)** |

> 🚨 **For DVA-C02 and new projects, always use SDK v3.**

---

### 🌐 SDK in a Browser?

- Yes, the SDK works **in the browser** too (e.g., for S3 uploads direct from browser)
- But you must **never expose AWS credentials to the browser**
- Use **Cognito Identity Pools** to get **temporary, scoped credentials** for browser-based SDK calls

```mermaid
graph LR
    Browser["🌐 Browser App"] --> Cognito["Amazon Cognito\nIdentity Pool"]
    Cognito --> STS["AWS STS\n(Temporary Credentials)"]
    STS --> Browser
    Browser --> S3["Amazon S3\n(Direct Upload)"]
```

---

### 🧠 Key Exam Takeaways

- The **AWS SDK** is used to call AWS services from **application code**
- SDK v3 is **modular** — install only the packages you need (`@aws-sdk/client-xxx`)
- SDK resolves credentials via the **credentials provider chain** — never hardcode secrets
- In **Lambda**, the SDK is available by default; credentials come from the **execution role**
- In **EC2**, use an **IAM Instance Role** so the SDK picks up credentials automatically
- If **no region** is configured, the SDK will throw an error
- In browsers, use **Cognito Identity Pools** for temporary credentials — never embed AWS keys
- SDK v3 uses the **Command pattern**: `client.send(new XxxCommand(params))`
- All SDK calls are ultimately **signed HTTP requests** to AWS REST APIs using **SigV4**

---

## Lecture 131: ⏱️ Exponential Backoff & Service Limit Increase

> **Course**: Ultimate AWS Certified Developer Associate DVA-C02 2026 \| **Instructor**: Stephane Maarek<br>**Section 12**: AWS CLI, SDK, IAM Roles & Policies

### 📌 Overview

When working with AWS services at scale, two critical reliability concepts emerge:

1. **API Rate Limits (Throttling)** — AWS enforces limits on how many API calls you can make per second/minute per service
1. **Service Quotas (Service Limits)** — Hard or soft caps on the number of AWS resources you can provision

Understanding these limits — and how to handle them gracefully — is essential for building **resilient, production-grade applications** on AWS.

### 🚦 AWS API Rate Limits (Throttling)

Every AWS API has a maximum call rate. If you exceed it, AWS returns a `ThrottlingException` (`HTTP 429 Too Many Requests`).

#### Common Examples

| Service | API | Rate Limit |
| --- | --- | --- |
| EC2 | `DescribeInstances` | 100 calls/second |
| S3 | `GET` requests per prefix | 5,500 requests/second |
| S3 | `PUT/POST/DELETE` per prefix | 3,500 requests/second |
| DynamoDB | Read/Write capacity | Based on provisioned RCU/WCU |
| CloudWatch | `GetMetricStatistics` | 400 calls/second |

#### When Does Throttling Happen?

```mermaid
flowchart TD
    A["Your App / SDK"] -->|"API Call"| B["AWS Service Endpoint"]
    B --> C{"Rate Limit\nExceeded?"}
    C -- No --> D["✅ 200 OK — Normal Response"]
    C -- Yes --> E["❌ ThrottlingException\nHTTP 429"]
    E --> F{"Retry Strategy?"}
    F -- "No retry / instant retry" --> G["💥 Cascading failures\nDDoS your own app"]
    F -- "Exponential Backoff" --> H["✅ Graceful recovery\nEventually succeeds"]
```

> 🚨 **Never retry immediately in a tight loop.** This floods the API further and worsens the situation — it can bring down your entire application.

### 📈 Exponential Backoff

**Exponential Backoff** is a retry strategy where the wait time between retries **doubles** with each attempt, with optional **jitter** (randomness) to prevent the thundering herd problem.

#### The Strategy

```mermaid
graph LR
    A["1st Attempt\nFails"] -->|"Wait 1s"| B["2nd Attempt\nFails"]
    B -->|"Wait 2s"| C["3rd Attempt\nFails"]
    C -->|"Wait 4s"| D["4th Attempt\nFails"]
    D -->|"Wait 8s"| E["5th Attempt\n✅ Succeeds"]
```

#### Formula

> **Wait time** = `min(base * 2^attempt, max_delay)` + random jitter

| Attempt | Wait (no jitter) | Wait (with jitter) |
| --- | --- | --- |
| 1st retry | 1 second | ~0.5 – 1.5s |
| 2nd retry | 2 seconds | ~1 – 3s |
| 3rd retry | 4 seconds | ~2 – 6s |
| 4th retry | 8 seconds | ~4 – 12s |
| 5th retry | 16 seconds | ~8 – 24s |

#### ✅ Good News: AWS SDK Does This Automatically

AWS SDK v3 has **built-in retry logic with exponential backoff** enabled by default:

- Default max retries: **3**
- Default retry mode: `standard` (includes exponential backoff + jitter)

```javascript
import { S3Client } from "@aws-sdk/client-s3";

// SDK v3 applies exponential backoff automatically
// Customize retry behavior via the `maxAttempts` config
const s3 = new S3Client({
  region: "us-east-1",
  maxAttempts: 5  // Total attempts (1 initial + 4 retries)
});
```

#### Retry Modes in AWS SDK v3

| Mode | Description |
| --- | --- |
| `standard` | Retries on throttling + transient errors with exponential backoff |
| `adaptive` | Dynamic rate limiting — slows down proactively before hitting limits |
| `legacy` | Old v2 behavior (basic retries, less sophisticated) |

```javascript
import { S3Client } from "@aws-sdk/client-s3";
import { ConfiguredRetryStrategy } from "@aws-sdk/util-retry";

// Adaptive retry mode — best for high-throughput applications
const s3 = new S3Client({
  region: "us-east-1",
  retryStrategy: new ConfiguredRetryStrategy(
    5,                  // max attempts
    (attempt) => 100 * Math.pow(2, attempt)  // custom backoff: 200ms, 400ms, 800ms...
  )
});
```

### 🛠️ Implementing Exponential Backoff Manually (Node.js)

When using the AWS CLI or making direct HTTP calls (without the SDK), you must implement retry logic yourself.

```javascript
/**
 * Retry an async AWS operation with exponential backoff + jitter
 * @param {Function} operation - Async function that calls AWS
 * @param {number} maxAttempts - Maximum number of attempts
 * @param {number} baseDelayMs - Base delay in milliseconds
 */
async function retryWithExponentialBackoff(operation, maxAttempts = 5, baseDelayMs = 100) {
  let attempt = 0;

  while (attempt < maxAttempts) {
    try {
      return await operation();
    } catch (error) {
      const isThrottling =
        error.name === "ThrottlingException" ||
        error.name === "RequestLimitExceeded" ||
        error.$metadata?.httpStatusCode === 429 ||
        error.$metadata?.httpStatusCode === 503;

      if (!isThrottling || attempt === maxAttempts - 1) {
        throw error;  // Non-retryable error or max retries reached
      }

      // Exponential backoff with full jitter
      const exponentialDelay = baseDelayMs * Math.pow(2, attempt);
      const jitter = Math.random() * exponentialDelay;
      const waitMs = Math.min(exponentialDelay + jitter, 30000); // cap at 30s

      console.warn(`Attempt ${attempt + 1} throttled. Retrying in ${Math.round(waitMs)}ms...`);
      await new Promise(resolve => setTimeout(resolve, waitMs));
      attempt++;
    }
  }
}

// Usage Example
import { DynamoDBClient, PutItemCommand } from "@aws-sdk/client-dynamodb";
const ddb = new DynamoDBClient({ region: "us-east-1" });

await retryWithExponentialBackoff(async () => {
  await ddb.send(new PutItemCommand({
    TableName: "Orders",
    Item: { orderId: { S: "order-001" }, status: { S: "pending" } }
  }));
});
```

### 🚦 Which Errors Should You Retry?

> Not all errors are worth retrying. Only retry **transient** errors.

```mermaid
flowchart TD
    A["AWS API Error"] --> B{"HTTP Status Code?"}
    B -->|"5xx Server Error\n500, 503"| C["✅ RETRY\nTransient server issue"]
    B -->|"429 Too Many Requests\nThrottlingException"| D["✅ RETRY\nWith exponential backoff"]
    B -->|"4xx Client Error\n400, 403, 404"| E["❌ DO NOT RETRY\nFix your request first"]
    C --> F["Apply Exponential Backoff"]
    D --> F
    E --> G["Inspect & fix the error\nbefore trying again"]
```

| Error Type | HTTP Code | Retry? | Reason |
| --- | --- | --- | --- |
| `ThrottlingException` | 429 | ✅ Yes | Rate limit — back off and retry |
| `ServiceUnavailableException` | 503 | ✅ Yes | Transient service issue |
| Internal Server Error | 500 | ✅ Yes | AWS-side transient issue |
| `AccessDeniedException` | 403 | ❌ No | IAM permissions issue — fix policy |
| `ValidationException` | 400 | ❌ No | Malformed request — fix parameters |
| `ResourceNotFoundException` | 404 | ❌ No | Resource doesn't exist — fix logic |

### 📊 Service Quotas (Service Limits)

**Service Quotas** are the maximum number of AWS resources or operations allowed in your account per region.

#### Two Types of Limits

| Type | Description | Example |
| --- | --- | --- |
| **Soft Limits** | Default limits that can be increased via request | Lambda concurrent executions: 1,000 |
| **Hard Limits** | Fixed caps that cannot be increased | S3 object max size: 5 TB |

#### Common Service Quotas

| Service | Quota | Default |
| --- | --- | --- |
| Lambda | Concurrent executions per region | 1,000 |
| EC2 | On-Demand vCPU limit | Varies by instance family |
| SQS | Max message size | 256 KB (hard limit) |
| DynamoDB | Tables per region | 2,500 |
| IAM | Roles per account | 1,000 |

#### How to View Service Quotas

```bash
# View all service quotas for a specific service
aws service-quotas list-service-quotas \
  --service-code lambda \
  --region us-east-1

# View applied quotas (what your account actually has)
aws service-quotas list-aws-default-service-quotas \
  --service-code ec2 \
  --region us-east-1
```

### 📬 How to Request a Service Limit Increase

Two ways to increase a soft limit:

```mermaid
graph TD
    A["Need Higher Service Limit"] --> B{"Which Method?"}
    B --> C["AWS Service Quotas Console\nconsole.aws.amazon.com/servicequotas"]
    B --> D["AWS Support Center\nOpen a Support Ticket"]
    C --> E["Find the quota\nClick 'Request quota increase'\nEnter desired value\nAWS reviews & approves"]
    D --> F["Create case: Service Limit Increase\nSpecify service, region, new limit\nAWS Support reviews"]
    E --> G["✅ Limit Increased\n(Takes hours to days)"]
    F --> G
```

#### Via CLI — Request a Quota Increase

```bash
# Request an increase for Lambda concurrent executions
aws service-quotas request-service-quota-increase \
  --service-code lambda \
  --quota-code L-B99A9384 \
  --desired-value 3000 \
  --region us-east-1
```

#### Via Console Steps

1. Go to **AWS Service Quotas** console
1. Search for your service (e.g., "Lambda")
1. Find the specific quota (e.g., "Concurrent executions")
1. Click **Request quota increase**
1. Enter the desired value → Submit
1. AWS will review and notify you via email (typically within 24–48 hours)

### ⚡ Proactive Throttle Prevention Strategies

Rather than just handling throttling reactively, design your system to **avoid it proactively**:

#### \1. 🪣 Token Bucket / Rate Limiting on Your Side

```javascript
import Bottleneck from "bottleneck"; // npm install bottleneck

// Limit to 100 API calls per second to stay under AWS limits
const limiter = new Bottleneck({
  maxConcurrent: 10,
  minTime: 10  // minimum 10ms between calls = 100 calls/sec max
});

const rateLimitedS3Call = limiter.wrap(async (key) => {
  return await s3.send(new GetObjectCommand({ Bucket: "my-bucket", Key: key }));
});

// Now calling this safely rate-limits your requests
const result = await rateLimitedS3Call("my-key.json");
```

#### \2. 📦 Batch Your API Calls

Instead of many small calls, use batch APIs:

```javascript
import { DynamoDBClient, BatchWriteItemCommand } from "@aws-sdk/client-dynamodb";

const ddb = new DynamoDBClient({ region: "us-east-1" });

// ✅ Batch up to 25 items in one call instead of 25 individual PutItem calls
await ddb.send(new BatchWriteItemCommand({
  RequestItems: {
    "Orders": [
      { PutRequest: { Item: { orderId: { S: "001" }, status: { S: "pending" } } } },
      { PutRequest: { Item: { orderId: { S: "002" }, status: { S: "pending" } } } },
      // ... up to 25 items
    ]
  }
}));
```

#### \3. 🗄️ Cache Frequently Read Data

```javascript
import { S3Client, GetObjectCommand } from "@aws-sdk/client-s3";

const s3 = new S3Client({ region: "us-east-1" });
const cache = new Map();  // Simple in-memory cache

async function getCachedObject(bucket, key) {
  const cacheKey = `${bucket}/${key}`;

  if (cache.has(cacheKey)) {
    console.log("Cache hit — no API call made!");
    return cache.get(cacheKey);
  }

  const response = await s3.send(new GetObjectCommand({ Bucket: bucket, Key: key }));
  const body = await response.Body.transformToString();
  cache.set(cacheKey, body);
  return body;
}
```

### 🔗 How This Fits Together

```mermaid
sequenceDiagram
    participant App as Your Application
    participant SDK as AWS SDK v3
    participant AWS as AWS Service

    App->>SDK: client.send(command)
    SDK->>AWS: API Request #1
    AWS-->>SDK: ❌ ThrottlingException (429)
    SDK->>SDK: Wait 100ms (attempt 1)
    SDK->>AWS: API Request #2
    AWS-->>SDK: ❌ ThrottlingException (429)
    SDK->>SDK: Wait 200ms + jitter (attempt 2)
    SDK->>AWS: API Request #3
    AWS-->>SDK: ✅ 200 OK
    SDK-->>App: Successful Response
```

### 🧠 Key Exam Takeaways

- **Throttling** occurs when you exceed AWS API rate limits → AWS returns `ThrottlingException` (HTTP **429**)
- **Exponential Backoff** is the correct retry strategy: double the wait time after each failure
- Add **jitter** (randomness) to prevent the **thundering herd problem** (all clients retrying at the same time)
- **AWS SDK v3 handles retries with exponential backoff automatically** — `maxAttempts` defaults to 3
- Only retry **5xx** and **429** errors — **never retry 4xx client errors** (they won't magically fix themselves)
- **Service Quotas** are per-account, per-region limits on AWS resources and API call rates
- **Soft limits** can be increased by requesting via the **AWS Service Quotas console** or a **Support Ticket**
- **Hard limits** are fixed and cannot be changed (e.g., max S3 object size = 5 TB)
- For large-scale workloads: use **batching**, **caching**, and **client-side rate limiting** to stay within limits proactively

---

## Lecture 132: ✍️ AWS Signature v4 Signing (SigV4)

> **Course**: Ultimate AWS Certified Developer Associate DVA-C02 2026 \| **Instructor**: Stephane Maarek<br>**Section 12**: AWS CLI, SDK, IAM Roles & Policies

### 📌 What is AWS Signature v4?

**AWS Signature Version 4 (SigV4)** is the process of adding **authentication information to HTTP requests** sent to AWS services. Every single request to an AWS API — whether from the CLI, SDK, or a direct HTTP call — must be **cryptographically signed** using SigV4 before AWS will process it.

> 💡 SigV4 is the mechanism by which AWS **verifies your identity** and ensures that the request has **not been tampered with** in transit.

#### Why Does It Exist?

- Proves the request came from someone with valid AWS credentials
- Protects against **man-in-the-middle attacks** (request tampering)
- Prevents **replay attacks** (a captured request cannot be reused later — it includes a timestamp)
- Works with **IAM Access Keys**, **STS temporary credentials**, and **IAM Roles**

> 🚨 You almost never need to implement SigV4 manually — the **AWS SDK and CLI do it for you automatically**. However, understanding SigV4 is critical for the exam, especially for scenarios involving **direct HTTP calls** to AWS APIs (e.g., from a custom HTTP client, API Gateway, or IoT device).

### 🔐 What Credentials Are Used in Signing?

```mermaid
graph LR
    A["IAM User / Role"] --> B["Access Key ID\n(Public identifier)"]
    A --> C["Secret Access Key\n(Private signing key)"]
    B --> D["Included in request headers"]
    C --> E["Used to generate HMAC signature\nNEVER sent directly"]
    D --> F["AWS Verifies Signature"]
    E --> F
```

- **Access Key ID** — identifies who is making the request (sent in the header)
- **Secret Access Key** — used to **cryptographically sign** the request (never transmitted)
- **Session Token** (optional) — required when using temporary credentials from STS/IAM Roles

### 🏗️ The Four-Step SigV4 Signing Process

SigV4 signing involves building a **canonical request**, creating a **string to sign**, computing an **HMAC signature**, and adding it all to the **Authorization header** (or query string).

```mermaid
flowchart TD
    A["Step 1️⃣\nCreate Canonical Request"] --> B["Step 2️⃣\nCreate String To Sign"]
    B --> C["Step 3️⃣\nCalculate Signature\nHMAC-SHA256"]
    C --> D["Step 4️⃣\nAdd Signature to Request\nAuthorization Header or Query String"]
    D --> E["Send Signed Request to AWS"]
    E --> F["AWS Recomputes Signature\nand Compares"]
    F --> G{"Match?"}
    G -- Yes --> H["✅ Request Authorized"]
    G -- No --> I["❌ SignatureDoesNotMatch Error"]
```

#### Step 1️⃣ — Create a Canonical Request

Standardize the HTTP request into a deterministic, normalized string:

```text
HTTPMethod\n
CanonicalURI\n
CanonicalQueryString\n
CanonicalHeaders\n
SignedHeaders\n
HexEncode(Hash(RequestPayload))
```

- **HTTPMethod**: `GET`, `POST`, `PUT`, etc.
- **CanonicalURI**: URL-encoded path (e.g., `/my-bucket/my-object.txt`)
- **CanonicalQueryString**: sorted, URL-encoded query parameters
- **CanonicalHeaders**: lowercase header names + trimmed values, sorted alphabetically
- **SignedHeaders**: semicolon-separated list of signed header names (e.g., `host;x-amz-date`)
- **Hashed Payload**: SHA-256 hash of the request body (or empty string for GET)

#### Step 2️⃣ — Create the String to Sign

```text
AWS4-HMAC-SHA256\n
Timestamp (ISO 8601 format: 20240101T120000Z)\n
Scope (Date/Region/Service/aws4_request)\n
HexEncode(Hash(CanonicalRequest))
```

Example scope: `20240101/us-east-1/s3/aws4_request`

#### Step 3️⃣ — Calculate the HMAC-SHA256 Signature

Derive a **signing key** from the secret key using a chain of HMAC operations:

```text
signingKey = HMAC(HMAC(HMAC(HMAC("AWS4" + SecretKey, Date), Region), Service), "aws4_request")
signature  = HexEncode(HMAC(signingKey, StringToSign))
```

> 🔑 The key derivation uses the **date, region, and service** to scope the key. A signing key derived for `us-east-1/s3` cannot be used for `us-west-2/dynamodb`. This prevents credential theft across services/regions.

#### Step 4️⃣ — Add Signature to the Request

Two options for transmitting the signature:

| Method | How | Use Case |
| --- | --- | --- |
| **Authorization Header** | `Authorization: AWS4-HMAC-SHA256 Credential=.../SignedHeaders=.../Signature=...` | Standard API calls |
| **Query String Parameters** | `?X-Amz-Algorithm=...&X-Amz-Signature=...` | **Pre-signed URLs** (S3, etc.) |

##### Authorization Header Format

```text
Authorization: AWS4-HMAC-SHA256
  Credential=AKIAIOSFODNN7EXAMPLE/20240101/us-east-1/s3/aws4_request,
  SignedHeaders=host;x-amz-content-sha256;x-amz-date,
  Signature=fe5f80f77d5fa3beca038a248ff027d0445342fe2855ddc963176630326f1024
```

##### Required Headers in Every Signed Request

| Header | Value | Required? |
| --- | --- | --- |
| `host` | Service endpoint (e.g., `s3.amazonaws.com`) | ✅ Always |
| `x-amz-date` | ISO 8601 timestamp (e.g., `20240101T120000Z`) | ✅ Always |
| `x-amz-security-token` | STS session token | ✅ When using temporary credentials |
| `x-amz-content-sha256` | SHA-256 hash of the body | ✅ Required for S3 |

### 🌐 SigV4 in Practice: Direct HTTP Call (Node.js)

The `@aws-sdk/signature-v4` and `@smithy/signature-v4` packages provide SigV4 signing for custom HTTP clients:

```javascript
import { SignatureV4 } from "@smithy/signature-v4";
import { Sha256 } from "@aws-crypto/sha256-js";
import { defaultProvider } from "@aws-sdk/credential-provider-node";
import https from "https";

// Build a SigV4 signer
const signer = new SignatureV4({
  credentials: defaultProvider(),   // Load credentials from chain
  region: "us-east-1",
  service: "execute-api",           // Use 's3', 'dynamodb', 'execute-api', etc.
  sha256: Sha256
});

// The raw HTTP request to sign
const request = {
  method: "GET",
  hostname: "abcd1234.execute-api.us-east-1.amazonaws.com",
  path: "/prod/my-endpoint",
  headers: {
    host: "abcd1234.execute-api.us-east-1.amazonaws.com"
  },
  body: undefined
};

// Sign the request — SigV4 adds Authorization header automatically
const signedRequest = await signer.sign(request);

// Now send the signed request
const options = {
  hostname: signedRequest.hostname,
  path: signedRequest.path,
  method: signedRequest.method,
  headers: signedRequest.headers  // Contains Authorization + x-amz-date
};

const response = await new Promise((resolve, reject) => {
  const req = https.request(options, resolve);
  req.on("error", reject);
  req.end();
});

console.log("Status:", response.statusCode);
```

### 🔗 Pre-signed URLs — SigV4 via Query String

When you generate a **pre-signed S3 URL**, the SigV4 signature is embedded **in the query string** rather than a header. This allows unauthenticated users to access a specific resource temporarily.

```javascript
import { S3Client, GetObjectCommand } from "@aws-sdk/client-s3";
import { getSignedUrl } from "@aws-sdk/s3-request-presigner";

const s3 = new S3Client({ region: "us-east-1" });

// Generate a pre-signed URL valid for 1 hour (3600 seconds)
const presignedUrl = await getSignedUrl(
  s3,
  new GetObjectCommand({
    Bucket: "my-private-bucket",
    Key: "confidential-report.pdf"
  }),
  { expiresIn: 3600 }
);

console.log("Share this URL (valid 1hr):", presignedUrl);
// Output: <https://my-private-bucket.s3.amazonaws.com/confidential-report.pdf>
//         ?X-Amz-Algorithm=AWS4-HMAC-SHA256
//         &X-Amz-Credential=AKIAIOSFODNN7EXAMPLE%2F20240101%2Fus-east-1%2Fs3%2Faws4_request
//         &X-Amz-Date=20240101T120000Z
//         &X-Amz-Expires=3600
//         &X-Amz-SignedHeaders=host
//         &X-Amz-Signature=<computed-signature>
```

> 💡 The query string parameters `X-Amz-Algorithm`, `X-Amz-Credential`, `X-Amz-Date`, `X-Amz-Expires`, `X-Amz-SignedHeaders`, and `X-Amz-Signature` are the SigV4 signature embedded directly into the URL.

### 🔄 How AWS Verifies the Signature

```mermaid
sequenceDiagram
    participant Client as Your App / CLI / SDK
    participant AWS as AWS Service Endpoint
    participant IAM as AWS IAM

    Client->>Client: Compute SigV4 signature using Secret Key
    Client->>AWS: Send HTTP Request + Authorization Header
    AWS->>IAM: Look up Secret Key for provided Access Key ID
    IAM-->>AWS: Return Secret Key
    AWS->>AWS: Recompute signature using same algorithm
    AWS->>AWS: Compare computed vs received signature
    alt Signatures Match
        AWS-->>Client: ✅ 200 OK — Request Authorized
    else Mismatch
        AWS-->>Client: ❌ 403 SignatureDoesNotMatch
    end
```

- AWS **never stores or receives your Secret Key** in the request — it looks it up from its own IAM store
- AWS recomputes the signature server-side and compares it to the one you sent
- If the **timestamp** in the request is more than **±5 minutes** from AWS server time → request is rejected (replay attack prevention)

### 🕐 Timestamp Validation — Replay Attack Prevention

> 🚨 **The request timestamp must be within ±5 minutes of AWS server time.** If your system clock is out of sync, all signed requests will fail with a `RequestExpired` error.

```bash
# Check your system time vs AWS time
date -u
# Sync time on Linux
sudo ntpdate pool.ntp.org

# On AWS EC2, the instance automatically syncs to AWS time servers
# No action needed on EC2
```

### 📋 SigV4 vs Other Signing Methods

| Method | Algorithm | Used By |
| --- | --- | --- |
| **SigV4** | HMAC-SHA256 | All modern AWS APIs (current standard) |
| **SigV4A** | ECDSA (elliptic curve) | Multi-region signing (e.g., S3 Multi-Region Access Points) |
| ~~SigV2~~ | HMAC-SHA1 | Deprecated — legacy S3 only |

> 💡 **SigV4A** is an extension that uses asymmetric cryptography and allows a single signature to be valid for **multiple AWS regions** — important for S3 Multi-Region Access Points.

### 🛡️ SigV4 and API Gateway

When you use **IAM Authorization** on API Gateway, the client must sign requests using SigV4. This is a common exam pattern:

```mermaid
graph LR
    A["Client Application"] -->|"SigV4 Signed Request\nAuthorization Header"| B["API Gateway\nREST API"]
    B -->|"Validates Signature\nChecks IAM Policy"| C["AWS IAM"]
    C -->|"Authorized"| D["Lambda Function\nor Backend"]
```

```javascript
import { SignatureV4 } from "@smithy/signature-v4";
import { Sha256 } from "@aws-crypto/sha256-js";
import { defaultProvider } from "@aws-sdk/credential-provider-node";

const API_GATEWAY_URL = "<https://abc123.execute-api.us-east-1.amazonaws.com/prod>";
const REGION = "us-east-1";

async function callIAMProtectedAPI(path, body) {
  const signer = new SignatureV4({
    credentials: defaultProvider(),
    region: REGION,
    service: "execute-api",   // ← Must be "execute-api" for API Gateway
    sha256: Sha256
  });

  const url = new URL(path, API_GATEWAY_URL);
  const bodyString = JSON.stringify(body);

  const signedRequest = await signer.sign({
    method: "POST",
    hostname: url.hostname,
    path: url.pathname,
    headers: {
      "content-type": "application/json",
      "host": url.hostname
    },
    body: bodyString
  });

  const response = await fetch(`${API_GATEWAY_URL}${url.pathname}`, {
    method: "POST",
    headers: signedRequest.headers,
    body: bodyString
  });

  return await response.json();
}

// Usage
const result = await callIAMProtectedAPI("/orders", { item: "laptop", qty: 1 });
console.log(result);
```

### 🧩 Key SigV4 Components at a Glance

```mermaid
graph TD
    A["SigV4 Request"] --> B["🔑 Credential Scope\nDate / Region / Service / aws4_request"]
    A --> C["📋 Canonical Request\nMethod + URI + Headers + Body Hash"]
    A --> D["📝 String To Sign\nAlgorithm + Date + Scope + Canonical Hash"]
    A --> E["✍️ Signature\nHMAC-SHA256 of String To Sign"]
    B --> F["Authorization Header"]
    C --> F
    D --> F
    E --> F
    F --> G["Sent to AWS Endpoint"]
```

### 🧠 Key Exam Takeaways

- **Every AWS API call must be signed with SigV4** — the CLI and SDK handle this automatically
- SigV4 uses **HMAC-SHA256** with a **derived signing key** scoped to date + region + service
- The **Secret Access Key is never transmitted** — it is only used locally to compute the HMAC signature
- AWS verifies signatures by **recomputing them server-side** using the stored secret key
- Requests are rejected if the timestamp is **more than ±5 minutes** from AWS server time (prevents replay attacks)
- The signature can be passed via the **Authorization header** (standard) or **query string** (pre-signed URLs)
- **Pre-signed S3 URLs** embed SigV4 parameters (`X-Amz-Signature`, `X-Amz-Expires`, etc.) directly in the URL query string
- **API Gateway with IAM auth** requires clients to sign requests using SigV4 with service `execute-api`
- **SigV4A** is an asymmetric extension supporting multi-region signing (used with S3 Multi-Region Access Points)
- If you see `SignatureDoesNotMatch` errors: check clock sync, correct region, and correct service name in the scope

---
