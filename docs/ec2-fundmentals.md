# EC2 Fundmentals

## Lecture 31: 💰 AWS Budget Setup

> **Section 5: EC2 Fundamentals** — Before launching EC2 instances, it's crucial to set up billing controls to avoid surprise charges on your AWS account.

### 🧠 Why Set Up a Budget?

- AWS operates on a **pay-as-you-go** model — costs can accumulate quickly if resources are left running
- Setting up a budget is the **first thing you should do** before experimenting with AWS services
- Budgets help you **proactively monitor** and **control** your cloud spending
- Especially important for students and developers using the **AWS Free Tier** — a misconfigured resource can lead to unexpected bills

### 🏦 AWS Billing Dashboard Overview

- Access via: **AWS Console → Account Name (top-right) → Billing and Cost Management**
- The Billing Dashboard shows:

    - **Spend Summary** — current month-to-date charges
    - **AWS Free Tier usage tracking** — how much of your free tier limits you've consumed
    - **Bills** — detailed breakdown of charges by service
    - **Billing Preferences** — configure PDF invoices, Free Tier alerts, etc.

> 💡 **Tip:** Enable **Free Tier usage alerts** in Billing Preferences — AWS will email you when you exceed **85%** of any Free Tier limit.

### 📊 AWS Cost Management Tools Comparison

| Tool | Purpose | Granularity | Alerting |
| --- | --- | --- | --- |
| **AWS Budgets** | Proactive budget control & alerting | High (filter by service, tag, account, region) | ✅ Actual & Forecasted |
| **CloudWatch Billing Alarms** | Basic total spend alerts | Low (total account spend only) | ✅ Actual only |
| **AWS Cost Explorer** | Analyze & visualize spending | High (drill-down analysis) | ❌ No alerting |

### 🎯 AWS Budgets — Deep Dive

#### 📋 What is AWS Budgets?

- A **cost management service** that lets you set custom budgets to track costs, usage, and commitments
- Supports alerts based on **actual spend** (costs already accrued) or **forecasted spend** (predicted costs by end of period)
- You can define budgets at various levels: **account-wide**, **per service**, **per tag**, **per region**, or **per linked account**

#### 🔖 Budget Types

| Budget Type | What It Tracks | Example Use Case |
| --- | --- | --- |
| **Cost Budget** | Dollar amount spent | "Alert me if I spend more than $10/month" |
| **Usage Budget** | Service-specific consumption | "Alert me if EC2 hours exceed 750" |
| **Reservation Budget** | Reserved Instance utilization & coverage | "Are my RIs being fully used?" |
| **Savings Plans Budget** | Savings Plans utilization & coverage | "Am I maximizing my Savings Plan?" |

> For this course, you'll primarily use **Cost Budgets** to track your AWS spending during hands-on labs.

#### 🔔 Budget Notifications

- Set **multiple alert thresholds** per budget (e.g., 50%, 80%, 100%)
- Notification methods:

    - **Email** — direct email alerts to one or more addresses
    - **Amazon SNS** — publish to an SNS topic for advanced integrations (Slack, Lambda, etc.)
    - **AWS Chatbot** — integrate with Slack or Microsoft Teams

#### ⚡ Budget Actions (Advanced)

- Automatically trigger corrective actions when a threshold is exceeded:

    - **Apply an IAM policy** to restrict permissions (e.g., deny launching new instances)
    - **Apply a Service Control Policy (SCP)** for organization-level restrictions
    - **Stop EC2 or RDS instances** via AWS Systems Manager (SSM)
- Requires an **IAM role** with appropriate permissions assigned to AWS Budgets

#### 💵 AWS Budgets Pricing

- **Basic budgets** (without Actions): **Free**
- **Action-enabled budgets**: First **2 per month are free**, then **$0.10/budget/day** after that
- For this course, the free tier is more than enough

### 🛠️ Hands-On: Creating Your First AWS Budget

#### Step 1: Navigate to Budgets

```text
AWS Console → Search "Budgets" → AWS Budgets
```

#### Step 2: Create a Budget

- Click **"Create budget"**
- Choose **"Customize (advanced)"** for full control, or use a **template**:

    - **Zero spend budget** — alerts you the moment any charge appears (great for Free Tier users!)
    - **Monthly cost budget** — set a fixed dollar amount per month

#### Step 3: Configure Budget Details

- **Budget Name**: e.g., `My Monthly Budget`
- **Period**: `Monthly`
- **Budget Amount**: e.g., `$10` (or whatever you're comfortable with)
- **Scope**: All AWS services (default) or filter by specific services

#### Step 4: Set Up Alert Thresholds

- Add notifications at key thresholds:

```text
Threshold 1: 50% of budget (Actual) → early warning
Threshold 2: 80% of budget (Actual) → approaching limit
Threshold 3: 100% of budget (Forecasted) → predicted overspend
```

- Enter your **email address** for notifications

#### Step 5: Review & Create

- Review all settings and click **"Create budget"**

### 💻 AWS CLI: Budget Management

You can also manage budgets programmatically using the AWS CLI:

#### Create a Budget via CLI

```bash
aws budgets create-budget \\
    --account-id 123456789012 \\
    --budget file://budget.json \\
    --notifications-with-subscribers file://notifications.json
```

#### Example `budget.json`

```json
{
    "BudgetName": "MyMonthlyBudget",
    "BudgetLimit": {
        "Amount": "10",
        "Unit": "USD"
    },
    "BudgetType": "COST",
    "TimeUnit": "MONTHLY",
    "TimePeriod": {
        "Start": "2026-01-01T00:00:00Z"
    }
}
```

#### Example `notifications.json`

```json
[
    {
        "Notification": {
            "NotificationType": "ACTUAL",
            "ComparisonOperator": "GREATER_THAN",
            "Threshold": 80,
            "ThresholdType": "PERCENTAGE"
        },
        "Subscribers": [
            {
                "SubscriptionType": "EMAIL",
                "Address": "your-email@example.com"
            }
        ]
    }
]
```

#### Other Useful CLI Commands

```bash
# List all budgets
aws budgets describe-budgets --account-id 123456789012

# Update a budget
aws budgets update-budget --account-id 123456789012 --new-budget file://updated-budget.json

# Delete a budget
aws budgets delete-budget --account-id 123456789012 --budget-name "MyMonthlyBudget"

# Add a notification to an existing budget
aws budgets create-notification \\
    --account-id 123456789012 \\
    --budget-name "MyMonthlyBudget" \\
    --notification NotificationType=ACTUAL,ComparisonOperator=GREATER_THAN,Threshold=80,ThresholdType=PERCENTAGE \\
    --subscribers SubscriptionType=EMAIL,Address=your-email@example.com
```

### 🆓 Tracking AWS Free Tier Usage

- **Free Tier Dashboard**: `Billing Console → Free Tier` — shows usage vs. limits for all services
- **Automatic Alerts**: AWS emails you when usage exceeds **85%** of a Free Tier limit
- **Zero Spend Budget**: The best safeguard — alerts you at the first dollar of spending

> ⚠️ **Important:** Some services are **not** part of the Free Tier. Always check the [AWS Free Tier page](https://aws.amazon.com/free/) before launching a new service.

### 🧪 Exam Tips

- **AWS Budgets** can alert on both **actual** and **forecasted** spend — CloudWatch Billing Alarms can only alert on **actual** charges
- **AWS Budgets** supports **4 types**: Cost, Usage, Reservation, and Savings Plans
- **Budget Actions** can automatically apply **IAM policies**, **SCPs**, or **stop instances** when thresholds are breached
- **Cost Explorer** is for **analysis**, not alerting — use it to investigate *why* costs increased
- Know the pricing: **2 action-enabled budgets free**, then **$0.10/budget/day**
- **SNS integration** is how AWS Budgets can notify external systems (Slack, Lambda, etc.)

### 📝 Key Takeaways

- Always set up a budget **before** experimenting with AWS services
- Use a **Zero Spend Budget** if you want to stay strictly within the Free Tier
- Set **multiple thresholds** (50%, 80%, 100%) for progressive warnings
- **Budget Actions** add automation — they can shut down resources or restrict permissions automatically
- Combine **AWS Budgets** (alerting) + **Cost Explorer** (analysis) for complete cost management
- This setup protects you from surprise bills throughout the course

---

## Lecture 32: 🖥️ EC2 Basics

> **Section 5: EC2 Fundamentals** — Amazon EC2 is one of the most fundamental and important AWS services. It provides resizable compute capacity in the cloud and is the backbone of many AWS architectures.

### 🧠 What is Amazon EC2?

- **EC2** stands for **Elastic Compute Cloud**
- It is an **Infrastructure as a Service (IaaS)** offering from AWS
- EC2 allows you to rent **virtual servers** (called **instances**) in the cloud
- "Elastic" means you can **scale up or down** based on demand — launch more instances when traffic spikes, and terminate them when traffic drops
- You have full control over the OS, networking, storage, and installed software

> 💡 EC2 is arguably the **most popular** AWS service and is foundational to understanding cloud computing on AWS.

### 🏗️ What EC2 Provides

EC2 is not just about virtual machines — it encompasses several capabilities:

| Capability | Description |
| --- | --- |
| **EC2 Instances** | Virtual machines that you can rent (the core service) |
| **EBS (Elastic Block Store)** | Virtual hard drives for persistent storage attached to instances |
| **ELB (Elastic Load Balancer)** | Distributes incoming traffic across multiple instances |
| **ASG (Auto Scaling Group)** | Automatically scales the number of instances based on demand |

> These components work together to build **highly available**, **scalable**, and **fault-tolerant** applications.

### ⚙️ EC2 Configuration Options

When launching an EC2 instance, you configure the following:

#### 🖼️ Operating System (OS)

- **Linux** (Amazon Linux, Ubuntu, Red Hat, SUSE, etc.)
- **Windows** (Windows Server)
- **Mac OS** (for Apple development workloads)

#### 💻 Compute Power & Cores

- Choose how many **virtual CPUs (vCPUs)** your instance has
- Ranges from **1 vCPU** (nano/micro) to **hundreds of vCPUs** (metal/high-performance)

#### 🧠 Memory (RAM)

- Choose how much **RAM** your instance needs
- Ranges from **0.5 GiB** (t2.nano) to **multiple TBs** (memory-optimized instances)

#### 💾 Storage

- **EBS volumes** — network-attached, persistent storage (most common)
- **EC2 Instance Store** — hardware-attached, ephemeral (temporary) storage with very high I/O
- **EFS (Elastic File System)** — shared network file storage

#### 🌐 Networking

- Choose the **network speed** and type
- Assign a **public IP address** for internet access
- Place the instance in a specific **VPC**, **subnet**, and **Availability Zone**

#### 🔐 Security Group

- A **virtual firewall** that controls inbound and outbound traffic to your instance
- Define rules based on **protocol**, **port**, and **source IP**

#### 🚀 Bootstrap Script (EC2 User Data)

- A script that runs **automatically on first launch** to configure the instance
- Used to automate tasks like installing software, downloading files, starting services

### 📛 EC2 Instance Naming Convention

EC2 instance names follow a structured format that tells you everything about the hardware:

```text
  m   5   a  .  xlarge
  │   │   │     │
  │   │   │     └─── Size (nano, micro, small, medium, large, xlarge, 2xlarge...)
  │   │   └───────── Additional Options (a=AMD, g=Graviton, n=Network optimized, d=local disk)
  │   └───────────── Generation (higher = newer hardware)
  └───────────────── Family (M=General, C=Compute, R=Memory, T=Burstable, I/D=Storage)
```

#### 🔍 Examples Decoded

| Instance Name | Family | Gen | Options | Size | Summary |
| --- | --- | --- | --- | --- | --- |
| `t2.micro` | T (Burstable) | 2nd | — | micro | Entry-level, burstable, Free Tier eligible |
| `m5.xlarge` | M (General) | 5th | — | xlarge | Balanced compute/memory, 4 vCPUs, 16 GiB RAM |
| `c7gn.2xlarge` | C (Compute) | 7th | g (Graviton), n (Network) | 2xlarge | High compute, ARM-based, network optimized |
| `r6i.large` | R (Memory) | 6th | i (Intel) | large | Memory-optimized, Intel processor |

### 🏷️ EC2 Instance Type Families

#### 📊 Overview

| Family | Optimized For | Use Cases |
| --- | --- | --- |
| **General Purpose** (T, M) | Balanced CPU, memory, networking | Web servers, app servers, small databases, dev environments |
| **Compute Optimized** (C) | High-performance CPUs | Batch processing, media transcoding, HPC, ML inference, gaming servers |
| **Memory Optimized** (R, X, z) | Large in-memory datasets | In-memory databases (Redis, Memcached), real-time big data analytics, SAP HANA |
| **Storage Optimized** (I, D, H) | High sequential read/write to local storage | Data warehousing, distributed file systems, OLTP databases |
| **Accelerated Computing** (P, G, Inf, Trn) | GPUs / hardware accelerators | Machine learning training, graphics rendering, video encoding |

#### 🔥 T-Series: Burstable Instances

- **T2** and **T3** instances are **burstable** — they have a baseline CPU performance and can "burst" above it
- They accumulate **CPU credits** when idle and spend credits when bursting
- Perfect for workloads with **variable CPU usage** (e.g., small web servers, dev/test environments)
- `t2.micro` is part of the **AWS Free Tier** ✅

### 🚀 EC2 User Data (Bootstrap Script)

- EC2 User Data allows you to **automate boot tasks** when an instance launches for the **first time**
- The script runs as the **root user** (with full admin privileges)
- Common tasks:

    - Installing packages and updates
    - Downloading application code from S3 or Git
    - Starting web servers or application services

#### 📝 Example: User Data Script

```bash
#!/bin/bash
# Update the system
yum update -y

# Install Apache HTTP Server
yum install -y httpd

# Start Apache and enable it on boot
systemctl start httpd
systemctl enable httpd

# Create a simple web page
echo "<h1>Hello World from $(hostname -f)</h1>" > /var/www/html/index.html
```

> ⚠️ **Important:** User Data scripts only run during the **first boot** of the instance. If you stop and start the instance, the script does **NOT** run again.

### 🔐 Security Groups (Quick Overview)

- Act as a **virtual firewall** for your EC2 instance
- Control **inbound** (incoming) and **outbound** (outgoing) traffic
- Rules are based on:

    - **Protocol** (TCP, UDP, ICMP)
    - **Port number** (e.g., 22 for SSH, 80 for HTTP, 443 for HTTPS)
    - **Source/Destination** (IP address range or another security group)
- **Stateful**: If inbound traffic is allowed, the response is automatically allowed out
- **Default**: All inbound traffic is **denied**, all outbound traffic is **allowed**

```text
Inbound Rules Example:
┌──────────┬──────────┬─────────────────┐
│ Protocol │ Port     │ Source          │
├──────────┼──────────┼─────────────────┤
│ TCP      │ 22       │ My IP (SSH)     │
│ TCP      │ 80       │ 0.0.0.0/0 (HTTP)│
│ TCP      │ 443      │ 0.0.0.0/0 (HTTPS)│
└──────────┴──────────┴─────────────────┘
```

### 🔑 Key Pair (SSH Access)

- Used for **secure SSH access** (Linux) or **RDP access** (Windows) to your instance
- **Public Key** → stored on the EC2 instance by AWS
- **Private Key** → downloaded by you (`.pem` for Linux/Mac, `.ppk` for PuTTY on Windows)
- **AWS does NOT keep a copy** of your private key — if you lose it, you cannot recover it

> ⚠️ **Never share your private key.** Anyone with the private key can SSH into your instance.

### 🔄 EC2 Instance Lifecycle

Understanding the lifecycle states is critical for **cost management** and **data persistence**:

| State | Description | Compute Billing | EBS Billing | Data |
| --- | --- | --- | --- | --- |
| **Pending** | Instance is launching | ❌ No | ✅ Yes | — |
| **Running** | Instance is active and usable | ✅ Yes | ✅ Yes | Persistent |
| **Stopping** | Instance is shutting down | ❌ No | ✅ Yes | EBS persists, Instance Store lost |
| **Stopped** | Instance is off but can be restarted | ❌ No | ✅ Yes | EBS persists |
| **Terminated** | Instance is permanently deleted | ❌ No | ❌ No (root deleted by default) | All lost |

> 💡 **Key Insight:** When you **stop** and then **start** an instance, it may be moved to a **different physical host**, which means it gets a **new public IP** address. The private IP stays the same.

### 🆓 EC2 Free Tier

- **750 hours/month** of `t2.micro` or `t3.micro` instances for the **first 12 months**
- This means you can run **1 instance 24/7** for free (744 hours/month ≈ 750)
- Running **2 instances** simultaneously will consume the free hours in ~15 days
- Also includes:

    - **30 GB** of EBS General Purpose (gp2/gp3) storage
    - **1 GB** of EBS snapshot storage
    - **100 GB** of data transfer out to the internet
    - **1 Elastic IP** (only free when attached to a running instance)

> ⚠️ **Caution:** Always check the Free Tier dashboard. An unattached Elastic IP or forgotten EBS volume will incur charges!

### 🧪 Exam Tips

- **EC2 = IaaS** — you manage the OS, patching, and applications; AWS manages the physical hardware
- Know the **instance type naming convention**: Family + Generation + Options + Size
- **User Data** runs only on the **first launch** and runs as **root**
- **Security Groups are stateful** — if inbound is allowed, the response is automatically allowed outbound
- **Stopping** an instance does NOT delete EBS data, but **Instance Store** data is lost
- **Terminating** an instance deletes the root EBS volume by default (can be changed)
- A **new public IP** is assigned each time a stopped instance is started
- **t2.micro** is Free Tier eligible — 750 hours/month for 12 months
- EC2 integrates with **EBS**, **ELB**, and **ASG** — know how they work together

### 📝 Key Takeaways

- Amazon EC2 is the **foundation of compute** in AWS — almost everything connects back to it
- You choose the **OS**, **instance type**, **storage**, **networking**, and **security** when launching
- **User Data** automates first-boot configuration — essential for repeatable infrastructure
- **Security Groups** are your first line of defense — stateful firewalls controlling all traffic
- **Instance lifecycle** (start/stop/terminate) directly impacts **billing** and **data persistence**
- Always use the **Free Tier** wisely — monitor usage via the Billing Dashboard and set up budgets (Lecture 31)
- Understanding EC2 basics is essential before diving into **EBS**, **AMIs**, **ELB**, and **ASG** in upcoming lectures

---

## Lecture 33: 🛠️ Create an EC2 Instance with EC2 User Data to have a Website Hands On

> **Section 5: EC2 Fundamentals** — Your first hands-on lab! Launch an EC2 instance with a bootstrap script that automatically installs Apache and serves a webpage accessible from the internet.

### 🎯 Lab Objective

- Launch an EC2 instance running **Amazon Linux**
- Use **EC2 User Data** to automatically install and start **Apache (httpd)**
- Access a live **Hello World** webpage via the instance's public IP address
- Stay within the **AWS Free Tier**

### 🚀 Hands-On Walkthrough

#### Step 1: 🔍 Open the EC2 Launch Wizard

```text
AWS Console → Search "EC2" → EC2 Dashboard → "Launch instance"
```

- Confirm your preferred **region** in the top-right corner (e.g., `us-east-1`)

#### Step 2: 📝 Name Your Instance

- Enter a name: e.g., `My First Web Server`
- This creates a **Name tag** visible in the EC2 dashboard

#### Step 3: 🖼️ Select an AMI

- Choose **Amazon Linux 2023 AMI**
- Confirm it says **"Free tier eligible"** ✅
- Architecture: **64-bit (x86)**

> An AMI (Amazon Machine Image) is the template defining the OS and pre-installed software for your instance.

#### Step 4: 💻 Pick the Instance Type

- Select `t2.micro` — 1 vCPU, 1 GiB RAM
- This is the go-to Free Tier instance for learning and small workloads

#### Step 5: 🔑 Create a Key Pair

- Click **"Create new key pair"**
- **Name**: `ec2-tutorial`
- **Type**: RSA
- **Format**: `.pem` (Linux/Mac/Windows 10+) or `.ppk` (PuTTY on older Windows)
- Click **"Create key pair"** — the file auto-downloads

> ⚠️ Store this file securely. AWS will **never** let you download it again. Losing it means losing SSH access to this instance.

#### Step 6: 🔒 Configure Security Group

Create a new security group with these **inbound rules**:

| Type | Protocol | Port | Source | Why |
| --- | --- | --- | --- | --- |
| SSH | TCP | 22 | My IP | Terminal access to the server |
| HTTP | TCP | 80 | 0.0.0.0/0 | Allow web browsers to reach your site |

- ✅ Check **"Allow SSH traffic from"** → **My IP**
- ✅ Check **"Allow HTTP traffic from the internet"**

> Without the HTTP rule on port 80, browsers cannot reach your web server — the page will just time out.

#### Step 7: 💾 Storage

- Keep the default: **8 GiB gp3** (General Purpose SSD)
- **Delete on termination**: Enabled (default)
- Well within the Free Tier's **30 GiB** EBS allowance

#### Step 8: 🧩 Paste the User Data Script

- Expand **"Advanced details"** at the bottom
- Scroll down to the **"User data"** text box
- Paste this script:

```bash
#!/bin/bash
# Use this for your user data (script from top to bottom)
# install httpd (Linux 2 version)
yum update -y
yum install -y httpd
systemctl start httpd
systemctl enable httpd
echo "<h1>Hello World from $(hostname -f)</h1>" > /var/www/html/index.html
```

#### Step 9: ✅ Launch

- Review the **Summary** panel on the right
- Click **"Launch instance"**
- Wait for the success confirmation message

### 📖 User Data Script — Line by Line

```bash
#!/bin/bash
# Shebang — tells Linux to execute this with the Bash shell
```

```bash
yum update -y
# Updates all system packages to latest versions
# -y = auto-confirm all prompts (no human interaction needed)
```

```bash
yum install -y httpd
# Installs Apache HTTP Server — the most popular open-source web server
```

```bash
systemctl start httpd
# Starts the Apache service right now
```

```bash
systemctl enable httpd
# Configures Apache to auto-start on every future boot
```

```bash
echo "<h1>Hello World from $(hostname -f)</h1>" > /var/www/html/index.html
# Creates a simple HTML page in Apache's document root
# $(hostname -f) is replaced with the server's fully qualified hostname
# /var/www/html/ is the default directory Apache serves files from
```

> 💡 **Key Detail:** User Data runs **only on first boot** and executes as the **root user** — no `sudo` required. If you stop and restart the instance, the script does **not** re-run.

### 🌍 Accessing Your Website

#### Finding the Public IP

1. Navigate to **EC2 → Instances**
1. Click your instance
1. In the **Details** tab, copy the **Public IPv4 address** (e.g., `54.210.78.123`)

#### Opening in Browser

```text
<http://54.210.78.123>
```

- You should see: **Hello World from ip-172-31-xx-xx.ec2.internal**

> ⚠️ **Use** `http://` **NOT** `https://` — SSL is not configured, so HTTPS will fail. Some browsers auto-redirect to HTTPS; if the page won't load, explicitly type `http://` in the address bar.

> If nothing loads, wait **1–2 minutes** — the User Data script needs time to finish after the instance enters the "Running" state.

### 🔄 EC2 IP Addressing — What You See in the Console

| Field | Example | Behavior |
| --- | --- | --- |
| **Public IPv4** | `54.210.78.123` | Changes every time you stop and start the instance |
| **Private IPv4** | `172.31.25.10` | Stays the same for the lifetime of the instance |
| **Public IPv4 DNS** | `ec2-54-210-78-123.compute-1.amazonaws.com` | Also changes on stop/start (derived from the public IP) |

> To keep a **permanent public IP**, you would use an **Elastic IP** (covered later). For now, just note the public IP from the Details tab each time you start the instance.

### 🛑 Stopping vs Terminating — Important Distinction

| Action | What Happens | Can You Recover? |
| --- | --- | --- |
| **Stop** | Instance powers off; EBS data preserved; public IP released | ✅ Yes — start it again anytime |
| **Terminate** | Instance + root EBS volume permanently deleted | ❌ No — gone forever |

- **Stop** your instance when you're done practicing to **save Free Tier hours**
- **Terminate** only when you're completely finished and want to clean up

```text
To stop:   EC2 → Select instance → Instance State → Stop instance
To start:  EC2 → Select instance → Instance State → Start instance
To delete: EC2 → Select instance → Instance State → Terminate instance
```

### 🐛 Troubleshooting Checklist

| Problem | Likely Cause | Fix |
| --- | --- | --- |
| Page times out in browser | Security Group missing HTTP rule on port 80 | Add inbound rule: HTTP, port 80, source 0.0.0.0/0 |
| "Connection refused" | Apache not running or User Data script failed | SSH in and run `sudo systemctl status httpd` |
| Browser shows HTTPS error | Using `https://` instead of `http://` | Change URL to `http://` explicitly |
| "This site can't be reached" | Instance not in Running state or no public IP assigned | Check instance state and verify public IP exists |
| Different page after stop/start | Public IP changed | Copy the new public IP from the Details tab |

#### 🔎 Debugging User Data via SSH

If your website isn't working, SSH into the instance and check:

```bash
# Connect to your instance
ssh -i "ec2-tutorial.pem" ec2-user@<your-public-ip>

# Check if Apache is running
sudo systemctl status httpd

# View the User Data execution log
sudo cat /var/log/cloud-init-output.log

# Manually check if the HTML file was created
cat /var/www/html/index.html

# If Apache isn't running, start it manually
sudo systemctl start httpd
```

### 🧪 Exam-Relevant Concepts from This Lab

- **User Data** scripts execute **once** at first launch and run as **root**
- User Data logs are stored at `/var/log/cloud-init-output.log`
- **Security Groups** are the reason pages timeout — always check port rules first
- An instance's **public IP changes** on stop/start; use **Elastic IP** for a static address
- The **private IP never changes** during the instance's lifetime
- **AMI** defines the OS; **Instance Type** defines the hardware; **User Data** defines the configuration
- Always use `http://` unless you have configured an SSL certificate

### 📝 Key Takeaways

- Launching an EC2 instance is a **7-step wizard** in the AWS Console
- **User Data** is powerful — it turns a bare OS into a fully configured server without manual SSH
- The combination of **AMI + Instance Type + Security Group + User Data** is the foundation of every EC2 deployment
- Always verify your **Security Group** rules if you can't reach your application
- **Stop** instances when not in use to conserve Free Tier hours; **terminate** to fully clean up
- This pattern (EC2 + User Data + Apache) is the simplest form of hosting — real production setups add ELB, ASG, and more (covered in upcoming lectures)

---

## Lecture 34: 🖥️ EC2 Instance Types Basics

> **Section 5: EC2 Fundamentals** — Ultimate AWS Certified Developer Associate DVA-C02 2026

### 📌 Overview

- AWS offers a wide variety of **EC2 instance types** optimized for different use cases
- Instance types comprise varying combinations of **CPU, memory, storage, and networking capacity**
- Each instance type is grouped into an **instance family** based on the workload it is designed for
- AWS naming convention follows a specific pattern that tells you a lot about the instance

### 🏷️ EC2 Instance Naming Convention

- Instance types follow a structured naming pattern:

```text
m5.2xlarge
│ │  └──── Size (nano, micro, small, medium, large, xlarge, 2xlarge, …)
│ └─────── Generation (5th generation)
└───────── Instance Class (M = General Purpose)
```

- **Instance Class** — Indicates the family/category (e.g., `m` for General Purpose, `c` for Compute Optimized)
- **Generation** — Higher number = newer generation with improved performance and cost-efficiency
- **Size** — Determines the amount of vCPU, RAM, network bandwidth, and storage within that class

### 🔷 General Purpose Instances

- **Instance Families**: `M`, `T`, `A` (e.g., `t2.micro`, `m5.large`, `m7g.xlarge`)
- Great for a **diversity of workloads** such as web servers and code repositories
- Provide a **balance** between:

    - Compute
    - Memory
    - Networking
- **Use Cases**:

    - Web applications and app servers
    - Small and mid-size databases
    - Development and test environments
    - Backend servers for enterprise applications

> 💡 The `t2.micro` instance is part of the **AWS Free Tier** — up to 750 hours per month for 12 months.

### 🟠 Compute Optimized Instances

- **Instance Families**: `C` (e.g., `c5.large`, `c6g.xlarge`, `c7g.2xlarge`)
- Ideal for **compute-intensive tasks** that require high-performance processors
- **Use Cases**:

    - Batch processing workloads
    - Media transcoding
    - High-performance web servers
    - High-performance computing (HPC)
    - Scientific modeling & machine learning
    - Dedicated gaming servers

### 🟢 Memory Optimized Instances

- **Instance Families**: `R`, `X`, `z` (e.g., `r5.large`, `x1.16xlarge`, `z1d.large`)
- Designed for workloads that process **large datasets in memory (RAM)**
- **Use Cases**:

    - High-performance relational/non-relational databases
    - In-memory caches (e.g., ElastiCache, Redis)
    - Real-time processing of big unstructured data
    - Distributed web-scale in-memory caches
    - Business Intelligence (BI) applications

> 💡 Think **R** = **R**AM for Memory Optimized.

### 🟡 Storage Optimized Instances

- **Instance Families**: `I`, `D`, `H` (e.g., `i3.large`, `d2.xlarge`, `h1.2xlarge`)
- Suited for workloads requiring **high, sequential read/write access to large datasets** on local storage
- **Use Cases**:

    - Online Transaction Processing (OLTP) systems
    - Relational and NoSQL databases
    - Data warehousing applications
    - Distributed file systems
    - Cache for in-memory databases (e.g., Redis)

### 📊 Instance Type Comparison Example

| Feature | `t2.micro` | `t2.xlarge` | `c5d.4xlarge` | `r5.16xlarge` | `m5.8xlarge` |
| --- | --- | --- | --- | --- | --- |
| **Family** | General Purpose | General Purpose | Compute Optimized | Memory Optimized | General Purpose |
| **vCPUs** | 1 | 4 | 16 | 64 | 32 |
| **Memory (GiB)** | 1 | 16 | 32 | 512 | 128 |
| **Storage** | EBS Only | EBS Only | 1 x 400 NVMe SSD | EBS Only | EBS Only |
| **Network** | Low to Moderate | Moderate | Up to 10 Gbps | 20 Gbps | 10 Gbps |

### 🌐 EC2 Instance Comparison Tool

- AWS provides an **instance comparison website** to help you choose the right instance:

```text
<https://instances.vantage.sh/>
```

- This site (formerly `ec2instances.info`) allows you to:

    - Filter by instance family, region, and pricing
    - Compare vCPUs, memory, storage, and network performance
    - View On-Demand, Reserved, and Spot pricing side-by-side

### 🧠 Exam Tips & Key Takeaways

- **Know the naming convention** — Be able to break down an instance name like `c5.2xlarge` into class, generation, and size
- **Associate instance families with use cases**:

    - `T` / `M` → General Purpose → balanced workloads
    - `C` → Compute Optimized → batch, HPC, ML inference
    - `R` / `X` / `z` → Memory Optimized → in-memory DBs, caches
    - `I` / `D` / `H` → Storage Optimized → OLTP, data warehouses
- `t2.micro` is Free Tier eligible — commonly used in hands-on labs
- You do **NOT** need to memorize every instance type — but you should understand the **categories and their ideal workloads**
- Newer generations (higher numbers) are typically **more cost-effective** and performant

---

## Lecture 35: 🛡️ Security Groups & Classic Ports Overview

> **Section 5: EC2 Fundamentals** — Ultimate AWS Certified Developer Associate DVA-C02 2026

### 📌 Overview

- Security Groups are the **fundamental building block of network security** in AWS
- They act as a **virtual firewall** that controls inbound and outbound traffic to your EC2 instances
- Understanding Security Groups is **critical** for the exam and real-world AWS usage

### 🔐 What Are Security Groups?

- Security Groups control **how traffic is allowed into or out of** your EC2 instances
- They only contain **allow** rules — you cannot create deny rules
- Rules can reference either **IP addresses** or **other Security Groups**
- They regulate:

    - Access to specific **ports**
    - Authorized **IP ranges** (IPv4 and IPv6)
    - Control of **inbound** network traffic (from outside to the instance)
    - Control of **outbound** network traffic (from the instance to outside)

### 🧩 Security Group Rule Structure

- Each rule in a Security Group consists of:

| Component | Description | Example |
| --- | --- | --- |
| **Type** | The protocol type | SSH, HTTP, HTTPS, Custom TCP |
| **Protocol** | Transport protocol | TCP, UDP |
| **Port Range** | The port(s) to allow | 22, 80, 443, 1024–65535 |
| **Source/Destination** | Who can connect (inbound) or where traffic can go (outbound) | `0.0.0.0/0`, `192.168.1.0/24`, `sg-xxxxxxxx` |

> 💡 `0.0.0.0/0` means **all IPv4 addresses** (open to the entire internet). `::/0` means **all IPv6 addresses**.

### 🔁 Security Group — Inbound vs Outbound

#### 🔽 Inbound Rules (Incoming Traffic)

- Define what traffic is **allowed to reach** your instance
- By default, **all inbound traffic is blocked** (no rules = no access)
- You must explicitly add rules to allow traffic on specific ports

```text
Example Inbound Rules:
┌──────────┬──────────┬────────────┬─────────────────┐
│ Type     │ Protocol │ Port Range │ Source          │
├──────────┼──────────┼────────────┼─────────────────┤
│ SSH      │ TCP      │ 22         │ 203.0.113.5/32  │
│ HTTP     │ TCP      │ 80         │ 0.0.0.0/0       │
│ HTTPS    │ TCP      │ 443        │ 0.0.0.0/0       │
└──────────┴──────────┴────────────┴─────────────────┘
```

#### 🔼 Outbound Rules (Outgoing Traffic)

- Define what traffic is **allowed to leave** your instance
- By default, **all outbound traffic is allowed** (instances can reach the internet)

```text
Example Outbound Rules:
┌──────────┬──────────┬────────────┬─────────────────┐
│ Type     │ Protocol │ Port Range │ Destination     │
├──────────┼──────────┼────────────┼─────────────────┤
│ All      │ All      │ All        │ 0.0.0.0/0       │
└──────────┴──────────┴────────────┴─────────────────┘
```

### 🔗 Referencing Other Security Groups

- Instead of specifying IP addresses, you can **reference another Security Group** as the source
- This is extremely powerful for connecting AWS resources together
- Common pattern: allow an ALB's Security Group to talk to an EC2 instance's Security Group

```text
Scenario: Two EC2 instances communicating via Security Group references

┌─────────────────────┐         ┌─────────────────────┐
│  EC2 Instance A     │         │  EC2 Instance B     │
│  SG: sg-aaa111      │◄───────►│  SG: sg-bbb222      │
└─────────────────────┘         └─────────────────────┘

Instance B's Inbound Rule:
  Type: Custom TCP | Port: 3306 | Source: sg-aaa111

→ Any instance attached to sg-aaa111 can connect to Instance B on port 3306
→ No need to manage individual IP addresses!
```

- **Why is this useful?**

    - Instances can have dynamic IPs — referencing Security Groups avoids hardcoding IPs
    - When you scale (e.g., Auto Scaling Groups), new instances automatically get the right access
    - It makes your architecture more **maintainable** and **scalable**

### ⚙️ Key Characteristics of Security Groups

- **Stateful** — If traffic is allowed **in**, the response traffic is automatically allowed **out** (and vice versa)
- Can be attached to **multiple instances** simultaneously
- An instance can have **multiple Security Groups** attached (rules are aggregated)
- Locked down to a **Region / VPC** combination — if you switch regions, you need a new Security Group
- Security Groups live **outside** the EC2 instance — blocked traffic never reaches the instance
- It's good practice to maintain a **separate Security Group for SSH access**

> ⚠️ If your application gives a **"timeout" error**, it's likely a **Security Group issue** (traffic is being blocked). If you get a **"connection refused" error**, the traffic got through but the **application itself** has an error or isn't running.

### 🔢 Classic Ports You Need to Know

| Port | Protocol | Service | Description |
| --- | --- | --- | --- |
| **22** | TCP | **SSH** (Secure Shell) | Log into a Linux instance remotely |
| **21** | TCP | **FTP** (File Transfer Protocol) | Upload files to a file share |
| **22** | TCP | **SFTP** (Secure FTP) | Upload files using SSH (same port as SSH) |
| **80** | TCP | **HTTP** | Access unsecured websites |
| **443** | TCP | **HTTPS** | Access secured websites (TLS/SSL) |
| **3389** | TCP | **RDP** (Remote Desktop Protocol) | Log into a **Windows** instance remotely |

> 💡 **Exam Tip**: SSH (port 22) is for **Linux** instances, RDP (port 3389) is for **Windows** instances. SFTP reuses port 22 because it runs over SSH.

### 📐 Security Group Architecture Diagram

```text
                        INTERNET
                           │
                     ┌─────▼─────┐
                     │  Firewall  │ ◄── Security Group (Inbound Rules)
                     └─────┬─────┘
                           │  ✅ Allowed traffic passes through
                     ┌─────▼─────┐
                     │    EC2     │
                     │  Instance  │
                     └─────┬─────┘
                           │  ✅ All outbound allowed by default
                     ┌─────▼─────┐
                     │  Firewall  │ ◄── Security Group (Outbound Rules)
                     └─────┬─────┘
                           │
                        INTERNET
```

### 🧪 Common Security Group Configurations

#### 🌐 Web Server Security Group

```text
Inbound:
  - HTTP  (80)   from 0.0.0.0/0      → Public web access
  - HTTPS (443)  from 0.0.0.0/0      → Public secure access
  - SSH   (22)   from YOUR_IP/32     → Admin access only

Outbound:
  - All traffic to 0.0.0.0/0         → Default (allow all)
```

#### 🗄️ Database Security Group

```text
Inbound:
  - MySQL (3306) from sg-webserver   → Only web servers can connect
  - PostgreSQL (5432) from sg-app    → Only app servers can connect

Outbound:
  - All traffic to 0.0.0.0/0        → Default (allow all)
```

### 🧠 Exam Tips & Key Takeaways

- Security Groups are **stateful** — return traffic is automatically allowed
- NACLs (Network ACLs) are **stateless** — you must define both inbound and outbound rules (covered later in VPC section)
- **Timeout = Security Group issue** \| **Connection Refused = Application issue**
- All **inbound** traffic is **denied** by default
- All **outbound** traffic is **allowed** by default
- You can only create **allow** rules, never **deny** rules
- Referencing Security Groups is the **preferred pattern** for inter-service communication within AWS
- **Memorize the classic ports**: SSH (22), HTTP (80), HTTPS (443), RDP (3389), FTP (21)
- Security Groups are scoped to a **Region + VPC** — they do not span regions
- One Security Group can be attached to **many instances**, and one instance can have **many Security Groups**

---

## Lecture 36: 🛡️ Security Groups Hands On

> **Section 5: EC2 Fundamentals** — Ultimate AWS Certified Developer Associate DVA-C02 2026

### 📌 Overview

- This is a hands-on walkthrough for creating, configuring, and testing **Security Groups** on an EC2 instance
- You'll learn how to manage inbound/outbound rules through the AWS Console
- You'll see firsthand how Security Groups block or allow traffic and how to diagnose connectivity issues

### 🔍 Accessing Security Groups in the Console

- Navigate to **EC2 Dashboard** → **Network & Security** → **Security Groups** in the left sidebar
- Alternatively, click on your running EC2 instance → scroll to the **Security** tab → click on the attached Security Group link
- Every EC2 instance has at least **one Security Group** attached (the one created during launch)

### 📋 Reviewing the Default Security Group

- When you launched your EC2 instance (Lecture 33), a Security Group was automatically created
- Click on the Security Group ID (e.g., `sg-0abc123def456`) to inspect it

#### 🔽 Inbound Rules Tab

```text
┌──────────┬──────────┬────────────┬─────────────────┬──────────────┐
│ Type     │ Protocol │ Port Range │ Source          │ Description  │
├──────────┼──────────┼────────────┼─────────────────┼──────────────┤
│ SSH      │ TCP      │ 22         │ 0.0.0.0/0       │ Allow SSH    │
│ HTTP     │ TCP      │ 80         │ 0.0.0.0/0       │ Allow HTTP   │
└──────────┴──────────┴────────────┴─────────────────┘──────────────┘
```

- **SSH (port 22)** — Allows you to remotely connect to the instance
- **HTTP (port 80)** — Allows web traffic so you can view the website served by your instance
- Source `0.0.0.0/0` means traffic is allowed from **anywhere** on the internet

#### 🔼 Outbound Rules Tab

```text
┌──────────────┬──────────┬────────────┬─────────────────┐
│ Type         │ Protocol │ Port Range │ Destination     │
├──────────────┼──────────┼────────────┼─────────────────┤
│ All traffic  │ All      │ All        │ 0.0.0.0/0       │
└──────────────┴──────────┴────────────┴─────────────────┘
```

- By default, **all outbound traffic is allowed** — the instance can reach any destination on the internet
- This is needed for things like software updates, API calls, etc.

### 🧪 Experiment 1: Removing the HTTP Rule

> Goal: See what happens when you **delete** the HTTP inbound rule

#### Steps

1. Go to **Inbound Rules** → click **Edit inbound rules**
1. Find the rule for **HTTP (port 80)** and click **Delete** (the ✕ button on the right)
1. Click **Save rules**
1. Go back to your browser and try to access the instance's **Public IPv4 address** on port 80

#### Result

```text
Browser: http://<your-public-ip>

❌ Page is loading... loading... loading...
❌ Eventually: "This site can't be reached" / TIMEOUT ERROR
```

- The page **never loads** — it just hangs and eventually times out
- This is because the Security Group is now **blocking all HTTP traffic** on port 80

> ⚠️ **Key Insight**: A **timeout** when trying to connect to an EC2 instance is almost always a **Security Group issue**. The traffic is being silently dropped — it never reaches the instance.

### 🔄 Experiment 2: Re-adding the HTTP Rule

#### Steps

1. Go back to **Inbound Rules** → click **Edit inbound rules**
1. Click **Add rule**
1. Configure the new rule:

    - **Type**: HTTP
    - **Protocol**: TCP (auto-filled)
    - **Port Range**: 80 (auto-filled)
    - **Source**: Select **Anywhere-IPv4** → this sets it to `0.0.0.0/0`
1. Click **Save rules**
1. Refresh your browser at `http://<your-public-ip>`

#### Result

```text
Browser: http://<your-public-ip>

✅ "Hello World from <instance-hostname>"
```

- The website is accessible again — traffic on port 80 is being allowed through

### 🧪 Experiment 3: Adding an HTTPS Rule

#### Steps

1. Go to **Inbound Rules** → click **Edit inbound rules**
1. Click **Add rule**
1. Configure:

    - **Type**: HTTPS
    - **Protocol**: TCP (auto-filled)
    - **Port Range**: 443 (auto-filled)
    - **Source**: Anywhere-IPv4 (`0.0.0.0/0`)
1. Click **Save rules**

> 💡 Note: Adding port 443 won't make HTTPS work automatically — you also need an SSL/TLS certificate configured on your web server. This rule just opens the port at the firewall level.

### 🧪 Experiment 4: Restricting SSH to Your IP

- Allowing SSH from `0.0.0.0/0` (anywhere) is a **security risk** in production
- Best practice: restrict SSH to **your IP address only**

#### Steps

1. Go to **Inbound Rules** → click **Edit inbound rules**
1. Find the **SSH (port 22)** rule
1. Change the **Source** from `0.0.0.0/0` to **My IP** (the console auto-detects your public IP)
1. This sets the source to something like `203.0.113.45/32`
1. Click **Save rules**

```text
Updated SSH Rule:
┌──────────┬──────────┬────────────┬──────────────────┐
│ Type     │ Protocol │ Port Range │ Source           │
├──────────┼──────────┼────────────┼──────────────────┤
│ SSH      │ TCP      │ 22         │ 203.0.113.45/32  │
└──────────┴──────────┴────────────┴──────────────────┘
```

> 💡 `/32` means **exactly one IP address**. This is the most restrictive CIDR you can use.

### 🔗 Attaching Multiple Security Groups

- An EC2 instance can have **more than one** Security Group
- To attach or detach Security Groups:

    1. Select your EC2 instance
    1. Go to **Actions** → **Security** → **Change security groups**
    1. Search and add additional Security Groups or remove existing ones
    1. Click **Save**
- When multiple Security Groups are attached, all rules are **aggregated** — if any rule across any attached SG allows the traffic, it is allowed

### 🆕 Creating a New Security Group

#### Steps

1. Go to **EC2** → **Network & Security** → **Security Groups**
1. Click **Create security group**
1. Fill in:

    - **Security group name**: e.g., `my-custom-sg`
    - **Description**: e.g., `Custom SG for testing` (required field)
    - **VPC**: Select your default VPC
1. Add **Inbound Rules** as needed
1. Leave **Outbound Rules** as default (all traffic allowed)
1. Click **Create security group**

```text
Example: Creating a dedicated SSH Security Group

Security Group Name: ssh-access-sg
Description: Allows SSH from my IP only
VPC: vpc-xxxxxxxx (default)

Inbound Rules:
  Type: SSH | Port: 22 | Source: My IP (auto-detected)

Outbound Rules:
  Type: All traffic | Destination: 0.0.0.0/0
```

> 💡 **Best Practice**: Create separate, purpose-specific Security Groups (e.g., one for SSH, one for HTTP/HTTPS, one for database access) and compose them by attaching multiple SGs to an instance.

### 🚨 Timeout vs Connection Refused — Diagnostic Guide

| Symptom | Cause | Fix |
| --- | --- | --- |
| **Timeout** (page hangs, never loads) | Security Group is **blocking** the traffic | Add an inbound rule for the correct port and source |
| **Connection Refused** (instant error) | Traffic reached the instance, but the **application isn't running** or isn't listening on that port | Start the application or check it's bound to the correct port |

```text
Timeout scenario:
  You → [SG blocks port 80] ✕ → EC2 (traffic never arrives)

Connection Refused scenario:
  You → [SG allows port 80] ✓ → EC2 → [Apache not running] ✕
```

### 📝 Important Console Tips

- When selecting **Source** for a rule, you have several options:

    - **Custom** — Enter a specific CIDR block (e.g., `10.0.0.0/16`)
    - **Anywhere-IPv4** — Sets to `0.0.0.0/0` (open to entire internet)
    - **Anywhere-IPv6** — Sets to `::/0`
    - **My IP** — Auto-detects and fills in your current public IP with `/32`
    - **Security Group** — Reference another SG by ID
- You can add an optional **Description** to each rule for documentation purposes
- Changes to Security Groups take effect **immediately** — no need to restart the instance

### 🧠 Exam Tips & Key Takeaways

- Security Group changes are applied **instantly** — no reboot or delay
- **Timeout = Security Group blocking traffic** — this is the #1 debugging tip for the exam
- Always restrict SSH (port 22) to your own IP in production — never leave it open to `0.0.0.0/0`
- Multiple Security Groups on one instance = rules are **merged/aggregated** (union of all allow rules)
- You **cannot** create deny rules — only allow rules
- Security Groups are **stateful** — if inbound traffic is allowed, the response is automatically allowed out
- Outbound rules default to **allow all** — most use cases don't need modification
- Each Security Group is scoped to a **VPC** — you select the VPC when creating one

---

## Lecture 37: 🔑 SSH Overview

> **Section 5: EC2 Fundamentals** — Ultimate AWS Certified Developer Associate DVA-C02 2026

### 📌 Overview

- SSH (Secure Shell) is the primary way to **remotely connect** to and control your EC2 Linux instances from a terminal
- Understanding SSH is essential for managing, debugging, and configuring EC2 instances
- AWS also provides a browser-based alternative called **EC2 Instance Connect**
- The method you use depends on your **operating system**

### 🔐 What is SSH?

- SSH stands for **Secure Shell** — a cryptographic network protocol for secure remote access
- It allows you to establish a **command-line interface (CLI) session** on a remote machine
- All communication is **encrypted** between your local machine and the remote server
- SSH uses **port 22** by default — your EC2 Security Group must allow inbound traffic on this port

```text
Your Computer ──── SSH (port 22, encrypted) ────► EC2 Instance (Linux)
                                                    │
                                                    ▼
                                              Terminal / Shell
                                              (full control)
```

### 💻 SSH Access Methods by Operating System

| Your OS | SSH Method | Tool |
| --- | --- | --- |
| **Mac** | SSH CLI | Built-in Terminal (ssh command) |
| **Linux** | SSH CLI | Built-in Terminal (ssh command) |
| **Windows ≥ 10** | SSH CLI | Built-in PowerShell / CMD (ssh command) |
| **Windows &lt; 10** | PuTTY | Third-party SSH client (free) |
| **Any OS** | EC2 Instance Connect | Browser-based SSH via AWS Console |

> 💡 **Windows 10 and above** now includes a built-in SSH client in PowerShell and Command Prompt. You no longer need PuTTY unless you prefer its GUI interface.

### 🔑 How SSH Authentication Works

- SSH into EC2 does **not** use a password — it uses **key pair authentication**
- When you launch an EC2 instance, you create or select a **Key Pair**:

    - **Public Key** — stored on the EC2 instance (inside `~/.ssh/authorized_keys`)
    - **Private Key** — downloaded to your local machine as a `.pem` file (or `.ppk` for PuTTY)
- You must have the **private key** to authenticate — anyone with this file can access your instance

```text
Key Pair Authentication Flow:

┌──────────────────┐                    ┌──────────────────┐
│  Your Computer   │                    │   EC2 Instance   │
│                  │                    │                  │
│  🔒 Private Key  │ ── SSH handshake → │  🔓 Public Key   │
│  (my-key.pem)   │                    │  (authorized_keys)│
│                  │ ◄── Verified ────  │                  │
│                  │                    │                  │
│  ✅ Access       │ ◄── Shell ──────  │  Terminal ready   │
└──────────────────┘                    └──────────────────┘
```

> ⚠️ **Never share your private key (**`.pem` **file)**. Anyone with this file can SSH into your instance. Treat it like a password.

### 🖥️ SSH from Linux / Mac

- Both Linux and macOS have SSH **built into the terminal**
- Basic SSH command:

```bash
ssh -i /path/to/my-key.pem ec2-user@<public-ip>
```

- `i` specifies the **identity file** (your private key)
- `ec2-user` is the default username for **Amazon Linux** AMIs
- Replace `<public-ip>` with your instance's **Public IPv4 address**

#### 🔒 File Permission Requirement

- Before using the `.pem` file, you **must** restrict its permissions:

```bash
chmod 400 my-key.pem
```

- If you skip this step, SSH will refuse to connect with the error:

```text
WARNING: UNPROTECTED PRIVATE KEY FILE!
Permissions 0644 for 'my-key.pem' are too open.
It is required that your private key files are NOT accessible by others.
This private key will be ignored.
```

### 🪟 SSH from Windows 10+

- Windows 10 (version 1809+) and Windows 11 have a **built-in OpenSSH client**
- Open **PowerShell** or **Command Prompt** and use the same command:

```powershell
ssh -i C:\\Users\\yourname\\my-key.pem ec2-user@<public-ip>
```

- If it's your first time connecting, you'll see a fingerprint confirmation prompt — type `yes`

### 🐡 SSH from Older Windows (PuTTY)

- For Windows versions **older than 10**, use **PuTTY** — a free, open-source SSH client
- PuTTY uses `.ppk` format instead of `.pem`:

    1. Download and install **PuTTY** from the official website
    1. Open **PuTTYgen** (included with PuTTY)
    1. Click **Load** → select your `.pem` file
    1. Click **Save private key** → save as `.ppk`
    1. Open **PuTTY** → enter `ec2-user@<public-ip>` in the Host Name field
    1. Go to **Connection** → **SSH** → **Auth** → Browse for your `.ppk` file
    1. Click **Open** to connect

```text
PuTTY Workflow:

.pem file ──► PuTTYgen (convert) ──► .ppk file ──► PuTTY (connect)
```

### 🌐 EC2 Instance Connect (Browser-Based)

- AWS provides a **browser-based SSH** experience — no local SSH client or key file needed
- Works directly from the **AWS Console**

#### How to Use

1. Go to **EC2 Dashboard** → select your instance
1. Click **Connect** (top button)
1. Choose the **EC2 Instance Connect** tab
1. Verify the username (default: `ec2-user` for Amazon Linux)
1. Click **Connect**
1. A terminal opens **in your browser**

#### Requirements

- The instance must have a **public IP address**
- The Security Group must allow **SSH (port 22)** inbound
- The instance must be running **Amazon Linux 2** or an AMI with the EC2 Instance Connect agent pre-installed
- AWS temporarily pushes a **one-time-use SSH key** to the instance metadata — no need to manage `.pem` files

```text
EC2 Instance Connect Flow:

AWS Console ──► Pushes temporary SSH key ──► EC2 Instance
     │                                           │
     └──── Opens browser terminal ◄──── SSH ─────┘
```

> 💡 EC2 Instance Connect is the **easiest** way to connect — great for quick checks and learning. But for production and automation, use proper SSH with key pairs.

### 👤 Default Usernames by AMI

| AMI | Default SSH Username |
| --- | --- |
| **Amazon Linux 2 / AL2023** | `ec2-user` |
| **Ubuntu** | `ubuntu` |
| **RHEL** | `ec2-user` or `root` |
| **CentOS** | `centos` or `ec2-user` |
| **Debian** | `admin` |
| **SUSE** | `ec2-user` or `root` |
| **Fedora** | `fedora` or `ec2-user` |
| **Bitnami** | `bitnami` |

> ⚠️ Using the wrong username is a common SSH error. If you get `Permission denied (publickey)`, double-check the username for your AMI.

### 🛠️ SSH Prerequisites Checklist

Before attempting SSH, verify all of the following:

- [ ] EC2 instance is in **Running** state
- [ ] Instance has a **Public IPv4 address** (or you're connecting via a private network/VPN)
- [ ] Security Group allows **inbound SSH (port 22)** from your IP
- [ ] You have the correct `.pem` **private key** file
- [ ] File permissions on the `.pem` are set to **400** (Linux/Mac)
- [ ] You're using the correct **username** for your AMI
- [ ] You're using the correct **Public IP** (not the Private IP)

### 🧠 Exam Tips & Key Takeaways

- SSH uses **port 22** — Security Group must allow it inbound
- SSH uses **key pair authentication**, not passwords
- `.pem` files are for **Linux/Mac/Windows 10+** \| `.ppk` files are for **PuTTY**
- Always run `chmod 400 my-key.pem` on Linux/Mac before connecting
- Default username for Amazon Linux is `ec2-user`
- **EC2 Instance Connect** is a browser-based alternative — no key files needed locally
- A **timeout** when SSHing = Security Group issue (port 22 not open)
- A **"Permission denied (publickey)"** error = wrong key file, wrong username, or wrong permissions
- **Never share your private key** — if compromised, anyone can access your instances
- The upcoming lectures (38–41) provide OS-specific walkthroughs and troubleshooting for SSH

---

## Lecture 40: 🪟 How to SSH using Windows 10

> **Section 5: EC2 Fundamentals** — Ultimate AWS Certified Developer Associate DVA-C02 2026

### 📌 Overview

- Windows 10 (version 1809+) and Windows 11 include a **built-in OpenSSH client**
- You can SSH directly from **PowerShell** or **Command Prompt** without needing PuTTY
- This lecture provides a complete hands-on walkthrough for connecting to an EC2 Linux instance from Windows 10/11

### ✅ Prerequisites

- A **running** EC2 instance with a **Public IPv4 address**
- The `.pem` **private key** file downloaded when creating the key pair
- Security Group allowing **inbound SSH (port 22)** from your IP address
- Windows 10 version **1809 or later** (or Windows 11)

### 🔍 Step 1: Confirm SSH is Installed

- Open **PowerShell** or **Command Prompt** and type:

```powershell
ssh
```

- If installed correctly, you'll see the SSH usage/help output listing available flags
- If you get `'ssh' is not recognized`, enable it manually:

```text
Go to: Settings → Apps → Optional Features → Add a feature
Search for "OpenSSH Client" → Click Install
```

### 📂 Step 2: Locate Your Private Key

- Navigate to where you saved your `.pem` file (typically `Downloads` folder)
- Recommended: move it to a dedicated directory for easier management

```powershell
mkdir C:\\Users\\yourname\\.ssh
move C:\\Users\\yourname\\Downloads\\my-ec2-key.pem C:\\Users\\yourname\\.ssh\\
```

### 🔐 Step 3: Fix Key File Permissions

- This is the **most important step on Windows** — SSH will reject keys with overly broad permissions
- If you skip this, you'll encounter:

```text
WARNING: UNPROTECTED PRIVATE KEY FILE!
Permissions for 'my-ec2-key.pem' are too open.
This private key will be ignored.
Load key "my-ec2-key.pem": bad permissions
```

#### 🛠️ Fixing Permissions via GUI (Right-Click Method)

1. Right-click on the `.pem` file → **Properties**
1. Go to the **Security** tab → click **Advanced**
1. Click **Disable inheritance** → choose **"Remove all inherited permissions from this object"**
1. Click **Add** → click **"Select a principal"**
1. Type your Windows username → click **Check Names** → click **OK**
1. Grant **Full control** → click **OK** through all dialogs

#### 🛠️ Fixing Permissions via PowerShell (Command Method)

```powershell
# Remove all existing permissions
icacls "C:\\Users\\yourname\\.ssh\\my-ec2-key.pem" /inheritance:r

# Grant only your user full control
icacls "C:\\Users\\yourname\\.ssh\\my-ec2-key.pem" /grant:r "%USERNAME%:F"
```

> 💡 The goal is to ensure **only your user account** has access to the `.pem` file — no other users, no groups, no "Everyone".

### 🚀 Step 4: Connect via SSH

- Open **PowerShell** and run:

```powershell
ssh -i C:\\Users\\yourname\\.ssh\\my-ec2-key.pem ec2-user@<PUBLIC_IPv4_ADDRESS>
```

- Breaking down the command:

| Part | Meaning |
| --- | --- |
| `ssh` | The SSH client command |
| `-i C:\\...\\my-ec2-key.pem` | Path to your private key identity file |
| `ec2-user` | Default username for Amazon Linux AMIs |
| `@<PUBLIC_IPv4_ADDRESS>` | Your instance's public IP (e.g., `3.86.142.201`) |

### 🤝 Step 5: Accept the Host Fingerprint

- On your **first connection**, you'll see a fingerprint verification prompt:

```text
The authenticity of host '3.86.142.201 (3.86.142.201)' can't be established.
ECDSA key fingerprint is SHA256:xYzAbC123...
Are you sure you want to continue connecting (yes/no/[fingerprint])?
```

- Type `yes` and press Enter
- This adds the host to your `known_hosts` file — you won't be prompted again for this instance

### 🎉 Step 6: You're Connected!

- After successful authentication, you'll see the Amazon Linux welcome banner:

```text
       __|  __|_  )
       _|  (     /   Amazon Linux 2 AMI
      ___|\\___|___|

[ec2-user@ip-172-31-xx-xx ~]$
```

- You now have a **full shell session** on your EC2 instance
- Try running some commands to verify:

```bash
# Check the hostname
hostname

# Check who you are
whoami

# View system info
uname -a

# Check if Apache is running (if you used the user data script)
systemctl status httpd
```

### 🔌 Disconnecting from SSH

- To end your SSH session, simply type:

```bash
exit
```

- Or press `Ctrl + D` to close the connection
- You'll return to your local PowerShell prompt

### 🚨 Common Errors & Fixes

| Error | Cause | Solution |
| --- | --- | --- |
| **Connection timed out** | Security Group blocks port 22 | Add inbound rule: SSH (22) from your IP |
| **UNPROTECTED PRIVATE KEY FILE** | `.pem` permissions too open | Fix permissions (Step 3 above) |
| **Permission denied (publickey)** | Wrong key, wrong username, or wrong IP | Verify all three match your instance |
| **No such file or directory** | Wrong path to `.pem` file | Use the full absolute path with correct spelling |
| **Network unreachable** | Instance has no public IP or is stopped | Ensure instance is running with a public IP assigned |

### 💡 Pro Tips for Windows Users

- **Use Windows Terminal** — it's a modern, tabbed terminal that supports PowerShell, CMD, and WSL in one app
- **WSL (Windows Subsystem for Linux)** — if you prefer Linux commands, install WSL and use native `ssh` + `chmod 400`:

```bash
# Inside WSL (Ubuntu)
chmod 400 /mnt/c/Users/yourname/.ssh/my-ec2-key.pem
ssh -i /mnt/c/Users/yourname/.ssh/my-ec2-key.pem ec2-user@<PUBLIC_IP>
```

- **SSH Config File** — create `C:\\Users\\yourname\\.ssh\\config` to save connection shortcuts:

```text
Host my-ec2
    HostName 3.86.142.201
    User ec2-user
    IdentityFile C:\\Users\\yourname\\.ssh\\my-ec2-key.pem
```

- Then connect with just:

```powershell
ssh my-ec2
```

### 🧠 Exam Tips & Key Takeaways

- Windows 10+ has a **native SSH client** — PuTTY is only needed for older Windows versions
- The `.pem` key file **permissions must be restricted** to your user only — this is the #1 issue on Windows
- Default username for Amazon Linux is `ec2-user` — using the wrong username gives `Permission denied`
- **Timeout = Security Group issue** (port 22 blocked) — always check inbound rules first
- If SSH feels complex, use **EC2 Instance Connect** from the browser as an alternative (Lecture 42)
- The `.pem` file is used directly on Windows 10+ — no conversion to `.ppk` is necessary

---

## Lecture 42: 🌐 EC2 Instance Connect

> **Section 5: EC2 Fundamentals** — Ultimate AWS Certified Developer Associate DVA-C02 2026

### 📌 Overview

- EC2 Instance Connect is a **browser-based SSH solution** provided by AWS
- It lets you connect to your EC2 instance **directly from the AWS Console** — no terminal, no `.pem` file handling, no PuTTY
- It works by pushing a **temporary, one-time SSH public key** to the instance's metadata, which is valid for **60 seconds**
- This is the **simplest and fastest** way to get a shell on your EC2 instance

### 🆚 EC2 Instance Connect vs Traditional SSH

| Feature | Traditional SSH | EC2 Instance Connect |
| --- | --- | --- |
| **Tool needed** | Terminal / PuTTY | Web browser only |
| **Key management** | You manage `.pem` / `.ppk` files locally | AWS handles temporary keys automatically |
| **Key lifetime** | Permanent until you delete/rotate | Ephemeral — expires after 60 seconds |
| **File permission issues** | Common on Windows (`chmod 400`) | None — no local key files involved |
| **Port 22 required** | ✅ Yes | ✅ Yes |
| **Public IP required** | ✅ Yes | ✅ Yes |
| **Works from any computer** | Only if you have the key file | ✅ Yes — just need AWS Console access |

### 🚀 How to Use EC2 Instance Connect

#### Step-by-Step Walkthrough

1. Go to the **EC2 Dashboard** in the AWS Console
1. Select your **running instance** (click the checkbox)
1. Click the **Connect** button at the top of the page
1. You'll see multiple connection tabs — select **EC2 Instance Connect**
1. Verify the **Username** field:

    - Amazon Linux → `ec2-user`
    - Ubuntu → `ubuntu`
1. Click **Connect**
1. A new browser tab opens with a **fully functional terminal session**

```text
AWS Console Flow:

EC2 Dashboard → Select Instance → Connect → EC2 Instance Connect tab → Connect

        ┌──────────────────────────────────┐
        │  🌐 Browser Terminal Opens       │
        │                                  │
        │  __|  __|_  )                    │
        │  _|  (     /  Amazon Linux 2     │
        │  ___|\\___|___|                   │
        │                                  │
        │  [ec2-user@ip-172-31-xx-xx ~]$   │
        └──────────────────────────────────┘
```

### ⚙️ How It Works Under the Hood

- When you click **Connect**, AWS performs the following behind the scenes:

```text
1. AWS generates a temporary SSH key pair (public + private)
2. The PUBLIC key is pushed to the instance metadata
   → Placed at: /home/ec2-user/.ssh/authorized_keys
   → Valid for only 60 seconds
3. AWS uses the PRIVATE key to establish the SSH session
4. Browser terminal opens with an active connection
5. After 60 seconds, the temporary public key is automatically removed
```

- This means **no permanent keys are stored** on the instance from Instance Connect
- Each connection generates a **fresh, unique key pair** — enhancing security

### ✅ Requirements for EC2 Instance Connect

#### Instance Requirements

- Must be running **Amazon Linux 2**, **Amazon Linux 2023**, or **Ubuntu 20.04+**
- The `ec2-instance-connect` package must be installed (pre-installed on Amazon Linux 2 / AL2023 AMIs)
- Instance must have a **Public IPv4 address** (or you use VPC endpoints for private access)

#### Network Requirements

- Security Group must allow **inbound SSH (port 22)**
- The source IP range should include the **AWS EC2 Instance Connect service IP range**
- For public access, AWS connects from its own IP ranges — not from your local machine's IP

> ⚠️ **Important distinction**: With traditional SSH, port 22 must be open to **your IP**. With EC2 Instance Connect, port 22 must be open to the **AWS EC2 Instance Connect service IP range** for your region.

#### Finding the EC2 Instance Connect IP Ranges

```bash
# AWS publishes all service IP ranges in a JSON file
curl -s <https://ip-ranges.amazonaws.com/ip-ranges.json> | \\
  jq '.prefixes[] | select(.service=="EC2_INSTANCE_CONNECT" and .region=="us-east-1")'
```

```json
{
  "ip_prefix": "18.206.107.24/29",
  "region": "us-east-1",
  "service": "EC2_INSTANCE_CONNECT",
  "network_border_group": "us-east-1"
}
```

- You can add this CIDR as the **source** in your Security Group inbound rule for SSH

### 🔧 Verifying the EC2 Instance Connect Agent

- SSH into the instance (using any method) and check if the agent package is installed:

```bash
# For Amazon Linux 2 / AL2023
rpm -qa | grep ec2-instance-connect

# Expected output:
# ec2-instance-connect-1.1-19.amzn2.noarch
```

```bash
# For Ubuntu
dpkg -l | grep ec2-instance-connect

# Expected output:
# ii  ec2-instance-connect  1.1.17-0ubuntu1  all  ...
```

- If missing, install it manually:

```bash
# Amazon Linux 2
sudo yum install -y ec2-instance-connect

# Ubuntu
sudo apt-get install -y ec2-instance-connect
```

### 🖥️ EC2 Instance Connect via AWS CLI

- You can also push a key and connect from your **local terminal** using the AWS CLI:

```bash
# Push your local public key to the instance (valid for 60 seconds)
aws ec2-instance-connect send-ssh-public-key \\
  --instance-id i-0abc123def456 \\
  --instance-os-user ec2-user \\
  --ssh-public-key file://~/.ssh/id_rsa.pub \\
  --availability-zone us-east-1a

# Then immediately SSH using the corresponding private key
ssh -i ~/.ssh/id_rsa ec2-user@<PUBLIC_IP>
```

- The key is only valid for **60 seconds** — you must connect quickly after pushing it

### 🔬 Testing Commands Once Connected

- After connecting via Instance Connect, try these commands to explore your instance:

```bash
# Confirm your identity
whoami
# Output: ec2-user

# Check the instance hostname
hostname -f
# Output: ip-172-31-42-15.ec2.internal

# View instance metadata
TOKEN=$(curl -X PUT "<http://169.254.169.254/latest/api/token>" \\
  -H "X-aws-ec2-metadata-token-ttl-seconds: 21600")

curl -H "X-aws-ec2-metadata-token: $TOKEN" \\
  <http://169.254.169.254/latest/meta-data/instance-id>
# Output: i-0abc123def456

# Check if Apache is serving the web page (from Lecture 33)
curl <http://localhost>
# Output: <h1>Hello World from ip-172-31-42-15.ec2.internal</h1>
```

### 🚨 Troubleshooting EC2 Instance Connect

| Problem | Likely Cause | Resolution |
| --- | --- | --- |
| **"There was a problem connecting"** | SG doesn't allow port 22 from AWS IP ranges | Add SSH rule with source = EC2\_INSTANCE\_CONNECT CIDR for your region |
| **Connect button is grayed out** | Instance is stopped or has no public IP | Start the instance and ensure a public IP is assigned |
| **"Unable to connect using EC2 Instance Connect"** | AMI doesn't have the agent installed | Install `ec2-instance-connect` package manually |
| **Session disconnects immediately** | Instance is overwhelmed or out of memory | Check instance health and system resources |
| **Works with SSH but not Instance Connect** | SG allows your IP but not AWS service IPs | Add the EC2\_INSTANCE\_CONNECT CIDR to the SG source |

### 🔒 Security Considerations

- **No permanent keys** — temporary keys auto-expire after 60 seconds, reducing the attack surface
- **IAM-controlled access** — you can restrict who can use Instance Connect via IAM policies:

```json
{
  "Effect": "Allow",
  "Action": "ec2-instance-connect:SendSSHPublicKey",
  "Resource": "arn:aws:ec2:us-east-1:123456789012:instance/i-0abc123def456",
  "Condition": {
    "StringEquals": {
      "ec2:osuser": "ec2-user"
    }
  }
}
```

- **CloudTrail logging** — every Instance Connect session is logged, providing an audit trail of who connected and when
- **No need to distribute** `.pem` **files** — team members only need AWS Console access with appropriate IAM permissions

### 🧠 Exam Tips & Key Takeaways

- EC2 Instance Connect is a **browser-based SSH** solution — no local key files needed
- It pushes a **temporary public key** to the instance that expires after **60 seconds**
- Requires **port 22 open** in the Security Group (SSH is still used under the hood)
- The instance needs a **public IPv4 address** and the **ec2-instance-connect agent** installed
- Supported on **Amazon Linux 2, AL2023, and Ubuntu** — not all AMIs support it
- For the exam, remember it's the **easiest** way to connect but still requires port 22
- IAM policies can control **who** can use Instance Connect via `ec2-instance-connect:SendSSHPublicKey`
- It's different from **AWS Systems Manager Session Manager**, which doesn't require port 22 at all (covered in later sections)

---

## Lecture 43: 🎭 EC2 Instance Roles Demo

> **Section 5: EC2 Fundamentals** — Ultimate AWS Certified Developer Associate DVA-C02 2026

### 📌 Overview

- This lecture demonstrates **why you should never run** `aws configure` **on an EC2 instance** with personal credentials
- Instead, you should attach an **IAM Role** to the EC2 instance to grant it permissions securely
- IAM Roles for EC2 use **temporary credentials** that are automatically rotated via the instance metadata service
- This is a **critical security concept** for the Developer Associate exam

### 🚫 The Wrong Way: Using `aws configure` on EC2

#### What Happens When You Do It

- After SSH-ing into your EC2 instance, you might be tempted to run:

```bash
# ❌ NEVER DO THIS ON AN EC2 INSTANCE
aws configure
AWS Access Key ID [None]: AKIAIOSFODNN7EXAMPLE
AWS Secret Access Key [None]: wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY
Default region name [None]: us-east-1
Default output format [None]: json
```

- This stores your **personal IAM user credentials** in plaintext on the instance at `~/.aws/credentials`

#### Why This Is Dangerous

- **Anyone** who can SSH into the instance (or access the filesystem) can read your credentials
- If the instance is **compromised**, the attacker gets your personal AWS access keys
- The credentials are **long-lived** — they don't expire until you manually rotate them
- Other users or team members sharing the instance could extract and misuse your keys
- It violates the **principle of least privilege** — personal user keys often have broader permissions than needed

```text
❌ Anti-Pattern:

  Your IAM User Credentials ──► Hardcoded on EC2 ──► Anyone on the instance can steal them
       (permanent keys)              (~/.aws/credentials)
```

### ✅ The Right Way: IAM Roles for EC2

#### What Is an EC2 Instance Role?

- An **IAM Role** is an identity with specific permissions that can be **assumed** by AWS services
- When you attach a role to an EC2 instance, the instance can make AWS API calls using **temporary security credentials**
- These credentials are delivered via the **EC2 Instance Metadata Service (IMDS)** and are **automatically rotated**

```text
✅ Correct Pattern:

  IAM Role (with policies) ──► Attached to EC2 ──► Temporary credentials via metadata
    (e.g., S3ReadOnly)          (Instance Profile)    (auto-rotated, short-lived)
```

#### Key Terminology

| Term | Definition |
| --- | --- |
| **IAM Role** | A set of permissions (policies) that can be assumed by an AWS service |
| **Instance Profile** | The "container" that links an IAM Role to an EC2 instance (created automatically when you attach a role via the Console) |
| **Temporary Credentials** | Short-lived access key + secret key + session token, auto-rotated by AWS |
| **IMDS** | Instance Metadata Service — the internal endpoint (`169.254.169.254`) where EC2 retrieves its credentials |

### 🔬 Hands-On Walkthrough

#### Step 1: Verify No Credentials Are Configured

- Connect to your EC2 instance via **EC2 Instance Connect** or SSH
- Try listing S3 buckets without any credentials:

```bash
aws s3 ls
```

- Expected result with **no role attached**:

```text
Unable to locate credentials. You can configure credentials by running "aws configure".
```

- Or if you previously ran `aws configure`, first remove those credentials:

```bash
# Remove any stored credentials
rm -rf ~/.aws/credentials
rm -rf ~/.aws/config
```

#### Step 2: Create an IAM Role for EC2

1. Open the **IAM Console** → click **Roles** in the left sidebar
1. Click **Create role**
1. Select trusted entity: **AWS service**
1. Use case: **EC2** → click **Next**
1. Attach a permissions policy — for this demo, search and select: **IAMReadOnlyAccess**
1. Click **Next** → give the role a name (e.g., `DemoRoleForEC2`)
1. Click **Create role**

```text
IAM Role Configuration:

  Trusted Entity:  AWS Service → EC2
  Policy Attached: IAMReadOnlyAccess
  Role Name:       DemoRoleForEC2
```

#### Step 3: Attach the Role to Your EC2 Instance

1. Go to the **EC2 Console** → select your running instance
1. Click **Actions** → **Security** → **Modify IAM role**
1. From the dropdown, select **DemoRoleForEC2**
1. Click **Update IAM role**

```text
EC2 Console Path:

  Actions → Security → Modify IAM role → Select "DemoRoleForEC2" → Update
```

> 💡 You can attach or change an IAM Role on a **running instance** — no reboot required. The new credentials become available within seconds.

#### Step 4: Test the Permissions

- Back in your EC2 terminal, run an IAM command (allowed by our policy):

```bash
aws iam list-users
```

- Expected output — a JSON response listing IAM users:

```json
{
    "Users": [
        {
            "UserName": "stephane",
            "UserId": "AIDAEXAMPLE123",
            "Arn": "arn:aws:iam::123456789012:user/stephane",
            "CreateDate": "2024-01-15T10:30:00Z"
        }
    ]
}
```

- The command works **without any** `aws configure` — the instance is using temporary credentials from its IAM Role

#### Step 5: Verify Restricted Access

- Try an action **not permitted** by `IAMReadOnlyAccess`:

```bash
# Attempting to create a user (write action — not allowed)
aws iam create-user --user-name hacker
```

- Expected result:

```text
An error occurred (AccessDenied) when calling the CreateUser operation:
User: arn:aws:sts::123456789012:assumed-role/DemoRoleForEC2/i-0abc123def456
is not authorized to perform: iam:CreateUser
```

- The role only has **read** access — write operations are correctly denied
- Notice the ARN shows `assumed-role/DemoRoleForEC2` — confirming the instance is using the role, not personal credentials

### 🔍 How EC2 Gets Its Credentials (Behind the Scenes)

- The AWS CLI and SDKs on EC2 automatically check the **Instance Metadata Service** for credentials:

```bash
# Retrieve the IAM role name attached to this instance
TOKEN=$(curl -X PUT "<http://169.254.169.254/latest/api/token>" \\
  -H "X-aws-ec2-metadata-token-ttl-seconds: 21600")

curl -H "X-aws-ec2-metadata-token: $TOKEN" \\
  <http://169.254.169.254/latest/meta-data/iam/security-credentials/>

# Output: DemoRoleForEC2
```

```bash
# Retrieve the actual temporary credentials
curl -H "X-aws-ec2-metadata-token: $TOKEN" \\
  <http://169.254.169.254/latest/meta-data/iam/security-credentials/DemoRoleForEC2>
```

```json
{
  "AccessKeyId": "ASIAEXAMPLE...",
  "SecretAccessKey": "temporary-secret...",
  "Token": "session-token...",
  "Expiration": "2026-05-10T20:00:00Z"
}
```

- These credentials are **temporary** and **auto-rotated** before they expire
- The AWS CLI/SDK handles this transparently — you never need to manage these manually

### 📊 Credential Resolution Order (AWS CLI/SDK)

- When the AWS CLI needs credentials, it checks these sources **in order**:

```text
1. Command-line options     (--access-key, --secret-key)
2. Environment variables    (AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY)
3. ~/.aws/credentials file  (from "aws configure")
4. ~/.aws/config file       (profile-based configs)
5. ECS container credentials (if running in ECS)
6. EC2 Instance Metadata    ← THIS IS WHAT IAM ROLES USE
```

> ⚠️ If you have credentials stored in `~/.aws/credentials` (from running `aws configure`), they will take **priority** over the IAM Role credentials. Always remove personal credentials from EC2 instances.

### 🛡️ Security Best Practices

- **Never use** `aws configure` on an EC2 instance with personal/long-lived access keys
- **Always use IAM Roles** for EC2 instances — they provide temporary, auto-rotating credentials
- Follow the **principle of least privilege** — only attach policies the instance actually needs
- If you need S3 access, attach only `AmazonS3ReadOnlyAccess` (not `AdministratorAccess`)
- **One role per application function** — don't reuse a single overly-permissive role across all instances
- Regularly **audit** which roles are attached to which instances using IAM Access Advisor

### 🧠 Exam Tips & Key Takeaways

- **Never store AWS credentials on EC2** — always use IAM Roles instead
- IAM Roles for EC2 deliver **temporary credentials** via the Instance Metadata Service (IMDS)
- Credentials from roles are **automatically rotated** — you don't manage expiration
- An **Instance Profile** is the mechanism that links an IAM Role to an EC2 instance
- You can attach or change a role on a **running instance** without rebooting
- The AWS CLI credential chain checks `~/.aws/credentials` **before** instance metadata — leftover personal keys will override the role
- On the exam, if a question says "an application on EC2 needs to access S3" → the answer is **attach an IAM Role with S3 permissions**, never hardcode keys
- `IAMReadOnlyAccess` allows listing users, roles, and policies but **not** creating or deleting them

---

## Lecture 44: 💰 EC2 Instance Purchasing Options

> **Section 5: EC2 Fundamentals** — Ultimate AWS Certified Developer Associate DVA-C02 2026

### 📌 Overview

- AWS offers multiple ways to **pay for EC2 instances**, each optimized for different workload patterns
- Choosing the right purchasing option can lead to **savings of up to 72%** compared to On-Demand pricing
- This is a **heavily tested topic** on the Developer Associate exam — understanding each option and its ideal use case is essential

### 🏨 The Hotel Analogy

- Think of EC2 purchasing options like booking a hotel:

| Hotel Analogy | EC2 Option | Description |
| --- | --- | --- |
| Walk in and pay full price | **On-Demand** | Pay per second, no commitment |
| Plan ahead and book for a long stay at a discount | **Reserved** | 1 or 3 year commitment, big discount |
| Book any hotel in a chain at a discount | **Savings Plans** | Commit to a $ amount/hour, flexible usage |
| Bid on last-minute empty rooms at steep discount | **Spot Instances** | Up to 90% off, but can be interrupted |
| Rent the entire hotel floor | **Dedicated Hosts** | Physical server dedicated to you |
| Book a room where nobody else stays on your floor | **Dedicated Instances** | Hardware isolation at instance level |
| Reserve a room in advance, pay whether you use it or not | **Capacity Reservations** | Reserve capacity in a specific AZ |

### 1️⃣ On-Demand Instances

- **Pay for what you use** with no upfront commitment
- **Linux/Windows**: Billed per **second** after the first minute
- **Other OS**: Billed per **hour**
- **Highest cost** among all options — no discounts
- **No long-term commitment** — start and stop anytime

#### ✅ Best For

- **Short-term** and **unpredictable** workloads
- Applications being developed or tested for the first time
- Workloads that **cannot be interrupted**
- Users who want **flexibility** without any commitment

```text
On-Demand Pricing Example (us-east-1):
  t3.micro  → $0.0104/hour
  m5.large  → $0.096/hour
  c5.xlarge → $0.17/hour
```

### 2️⃣ Reserved Instances (RI)

- Commit to a specific **instance type, region, OS, and tenancy** for **1 or 3 years**
- Discount of up to **72%** compared to On-Demand
- Three payment options affect the discount level:

| Payment Option | Discount Level | How You Pay |
| --- | --- | --- |
| **No Upfront** | Lowest discount | Monthly payments only |
| **Partial Upfront** | Medium discount | Part upfront + reduced monthly |
| **All Upfront** | Highest discount (~72%) | Pay everything upfront |

#### 📐 Reserved Instance Scope

- **Regional RI** — discount applies to any AZ in the region; no capacity reservation
- **Zonal RI** — discount applies to a specific AZ; **reserves capacity** in that AZ

#### ✅ Best For

- Steady-state, **predictable** workloads (databases, backend servers)
- Applications that need to run **continuously** for 1–3 years

#### 🔄 Convertible Reserved Instances

- A special type of RI that allows you to **change** the instance family, OS, scope, and tenancy
- Less discount (up to **66%**) compared to standard RIs (up to **72%**)
- Useful when you think your requirements might evolve over the commitment period

```text
Standard RI:       t3.large, Linux, us-east-1 → LOCKED for 1-3 years (up to 72% off)
Convertible RI:    t3.large, Linux, us-east-1 → CAN CHANGE to m5.xlarge, Windows (up to 66% off)
```

> 💡 You can buy and sell Reserved Instances on the **Reserved Instance Marketplace** if you no longer need them.

### 3️⃣ Savings Plans

- Commit to a **consistent amount of compute usage** (measured in **$/hour**) for 1 or 3 years
- Discount of up to **72%** — same as Reserved Instances
- Usage beyond your committed amount is billed at **On-Demand** rates

#### Two Types of Savings Plans

| Type | Flexibility | Discount |
| --- | --- | --- |
| **Compute Savings Plan** | Any instance family, region, OS, tenancy, or compute service (EC2, Fargate, Lambda) | Up to 66% |
| **EC2 Instance Savings Plan** | Locked to a specific instance family and region, but flexible on size, OS, and tenancy | Up to 72% |

```text
Example — EC2 Instance Savings Plan:
  Commit: $10/hour for M5 instances in us-east-1
  ✅ m5.xlarge in us-east-1    → covered (discounted)
  ✅ m5.2xlarge in us-east-1   → covered (discounted)
  ✅ m5.large Windows, us-east-1 → covered (discounted)
  ❌ c5.xlarge in us-east-1    → NOT covered (different family)
  ❌ m5.xlarge in eu-west-1    → NOT covered (different region)
```

#### ✅ Best For

- Workloads with **flexible instance types** but consistent overall compute spend
- Organizations that want RI-level discounts with **more flexibility**

### 4️⃣ Spot Instances

- Request **unused EC2 capacity** at up to **90% discount** compared to On-Demand
- You define a **max spot price** you're willing to pay:

    - If the current spot price &lt; your max price → instance runs
    - If the current spot price &gt; your max price → instance gets a **2-minute warning**, then is **terminated or stopped**
- The **most cost-efficient** option in AWS

#### ⚠️ The Catch: Interruptions

- AWS can **reclaim** your Spot Instance at any time with a **2-minute notification**
- Your workload must be designed to handle sudden termination gracefully

#### ✅ Best For

- **Batch processing** and data analysis jobs
- **Image rendering** and media transcoding
- **Big data** and distributed computing (Hadoop, Spark)
- **CI/CD** pipelines and build servers
- Any workload that is **fault-tolerant** and can be **restarted**

#### ❌ Not Suitable For

- **Databases** or stateful applications
- **Critical workloads** that cannot tolerate interruptions
- Production web servers that must have guaranteed uptime

```text
Spot Instance Lifecycle:

  You set max price: $0.05/hour
  Current spot price: $0.03/hour → ✅ Instance runs
  Spot price rises:   $0.06/hour → ⚠️ 2-min warning → Instance interrupted
```

### 5️⃣ Dedicated Hosts

- An **entire physical server** is allocated exclusively for your use
- The most **expensive** EC2 option
- You have visibility into the **physical cores, sockets, and host ID** of the underlying hardware
- Useful for **compliance** requirements and **software licensing** (BYOL — Bring Your Own License)

#### Key Characteristics

- You control **instance placement** on the physical server
- Available as **On-Demand** or **Reserved** (1 or 3 year commitment)
- Supports **Dedicated Host Affinity** — instances always launch on the same physical host

#### ✅ Best For

- Software with **per-socket, per-core, or per-VM licensing models** (Oracle, Microsoft SQL Server, Windows Server)
- **Regulatory/compliance** requirements that mandate single-tenant hardware
- Organizations that need **consistent physical server mapping**

### 6️⃣ Dedicated Instances

- Instances run on hardware that is **dedicated to your account**
- Other instances from your **own account** may share the same physical hardware
- But **no other AWS customer's** instances will run on that hardware
- You have **no control** over instance placement (unlike Dedicated Hosts)

#### Dedicated Instances vs Dedicated Hosts

| Feature | Dedicated Instance | Dedicated Host |
| --- | --- | --- |
| **Hardware isolation** | Per-account isolation | Per-server isolation |
| **Visibility into physical hardware** | ❌ No | ✅ Yes (sockets, cores, host ID) |
| **Instance placement control** | ❌ No | ✅ Yes |
| **BYOL licensing support** | ❌ Limited | ✅ Full support |
| **Cost** | Lower | Higher |

### 7️⃣ Capacity Reservations

- **Reserve On-Demand capacity** in a specific **Availability Zone** for any duration
- You get guaranteed access to EC2 capacity **when you need it**
- **No billing discount** — you pay On-Demand rates whether the instance is running or not
- Can be combined with **Regional RIs** or **Savings Plans** to get both capacity guarantee and discount

#### ✅ Best For

- **Short-term, uninterruptible workloads** that must run in a specific AZ
- Disaster recovery planning — ensuring capacity is available during failover
- Compliance workloads that require **guaranteed capacity**

```text
Capacity Reservation:
  ✅ Guarantees capacity in a specific AZ
  ❌ Does NOT provide a billing discount on its own
  💡 Combine with Savings Plans or RIs for discount + guaranteed capacity
```

### 📊 Complete Comparison Table

| Option | Discount | Commitment | Interruption Risk | Best For |
| --- | --- | --- | --- | --- |
| **On-Demand** | None (0%) | None | ❌ None | Short-term, unpredictable workloads |
| **Reserved** | Up to 72% | 1–3 years | ❌ None | Steady-state databases, always-on apps |
| **Convertible RI** | Up to 66% | 1–3 years | ❌ None | Long-running but evolving workloads |
| **Savings Plans** | Up to 72% | 1–3 years | ❌ None | Flexible compute with consistent spend |
| **Spot** | Up to 90% | None | ✅ 2-min warning | Batch jobs, fault-tolerant processing |
| **Dedicated Host** | Varies | None or 1–3yr | ❌ None | BYOL licensing, compliance |
| **Dedicated Instance** | Varies | None | ❌ None | Hardware isolation per account |
| **Capacity Reservation** | 0% (alone) | None | ❌ None | Guaranteed AZ capacity |

### 💡 Real-World Strategy: Combining Options

- In practice, organizations **mix and match** purchasing options:

```text
Production Database (always on)     → Reserved Instance (3-year, All Upfront)
Web Servers (predictable baseline)  → Savings Plan (Compute)
Batch Processing (flexible timing)  → Spot Instances
DR Failover (must have capacity)    → Capacity Reservation + Savings Plan
Licensed Software (Oracle DB)       → Dedicated Host (Reserved)
Dev/Test (short experiments)        → On-Demand
```

### 🧠 Exam Tips & Key Takeaways

- **On-Demand** = no commitment, highest price, most flexibility
- **Reserved** = 1–3 year commit, up to 72% off, locked to instance type + region
- **Convertible RI** = can change instance attributes, up to 66% off
- **Savings Plans** = commit $/hour, more flexible than RIs, up to 72% off
- **Spot** = up to 90% off, **can be interrupted** with 2-min notice — only for fault-tolerant workloads
- **Dedicated Hosts** = full physical server for you, needed for **BYOL licensing**
- **Dedicated Instances** = hardware isolation per account but no visibility into physical server
- **Capacity Reservations** = guarantee capacity in an AZ, no discount on their own
- Exam question pattern: "A company needs to run a workload that can handle interruptions for the lowest cost" → **Spot Instances**
- Exam question pattern: "A company must use per-core software licensing" → **Dedicated Hosts**
- Exam question pattern: "A company runs a database 24/7 for 3 years" → **Reserved Instance (All Upfront)**

---
