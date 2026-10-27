# IAM and AWS cli

## Lecture 11: 🔐 IAM Introduction: Users, Groups, Policies

> **Section 4: IAM & AWS CLI**<br>AWS Certified Developer Associate (DVA-C02)

### 🌐 What is IAM?

- **IAM** stands for **Identity and Access Management** — it is a **Global Service** (not region-scoped).
- IAM is the foundation of **security in AWS** — it controls **who** can access **what** in your AWS account.
- When you first create an AWS account, a **Root Account** is created by default.

    - The root account has **unrestricted access** to everything in the AWS account.
    - ⚠️ The root account should **never** be used or shared for day-to-day tasks.
    - Best practice: Use the root account **only** for initial setup, then create IAM users.

### 👥 IAM Users

- An **IAM User** represents a **person or service** within your organization.
- Each user has their own **credentials** (username/password for console, access keys for CLI/SDK).
- Users can be assigned permissions **directly** or through **groups**.
- A user **does not have to belong** to any group — but this is not recommended.
- A user can belong to **multiple groups**.

> 💡 **Best Practice**: Create one IAM user per physical person. Never share credentials between people.

### 👨‍👩‍👧‍👦 IAM Groups

- **Groups** are collections of IAM users.
- Groups allow you to assign permissions to **multiple users at once** — making management much easier.
- Example groups: `Developers`, `Operations`, `Finance`, `Admins`.
- **Important constraints**:

    - Groups can only contain **users**, NOT other groups (no nesting).
    - A user can belong to **multiple groups** simultaneously.

```text
Example Structure:
───────────────────────────────
Group: Developers
  ├── Alice
  ├── Bob
  └── Charlie

Group: Operations
  ├── David
  └── Alice  ← Alice is in BOTH groups

No Group:
  └── Fred   ← Possible, but NOT recommended
───────────────────────────────
```

### 📜 IAM Policies

- **Policies** are **JSON documents** that define **permissions** — what a user or group is allowed (or denied) to do.
- Policies follow the **Least Privilege Principle**: only grant the minimum permissions a user needs to perform their job.

#### 📄 Policy Structure

A policy document consists of the following key elements:

```json
{
  "Version": "2012-10-17",
  "Id": "S3-Account-Permissions",
  "Statement": [
    {
      "Sid": "AllowS3ReadAccess",
      "Effect": "Allow",
      "Principal": {
        "AWS": "arn:aws:iam::123456789012:root"
      },
      "Action": [
        "s3:GetObject",
        "s3:ListBucket"
      ],
      "Resource": [
        "arn:aws:s3:::my-bucket/*"
      ],
      "Condition": {
        "StringEquals": {
          "s3:prefix": "home/"
        }
      }
    }
  ]
}
```

#### 🔑 Policy Elements Explained

| Element | Description |
| --- | --- |
| **Version** | Policy language version — always use `"2012-10-17"` (latest) |
| **Id** | Optional identifier for the policy |
| **Statement** | One or more individual permission rules (required) |
| **Sid** | Optional statement identifier (human-readable label) |
| **Effect** | Either `"Allow"` or `"Deny"` |
| **Principal** | The account, user, or role the policy applies to |
| **Action** | List of API calls that are allowed or denied |
| **Resource** | List of AWS resources the actions apply to |
| **Condition** | Optional conditions for when the policy is in effect |

#### 📌 Types of Policies

- **Inline Policy**: A policy attached **directly** to a single user — a one-to-one relationship.

    - Use sparingly; harder to manage at scale.
- **Managed Policy (Group/User Attached)**: A policy attached to a **group** — all users in that group inherit the permissions.

    - This is the **recommended approach** for managing permissions.
- **AWS Managed Policy**: Pre-built policies created and maintained by AWS (e.g., `AmazonS3ReadOnlyAccess`).
- **Customer Managed Policy**: Custom policies you create and manage yourself.

> 💡 If a user belongs to multiple groups, the user inherits permissions from **all** groups they belong to. Permissions are **additive** (union of all policies), unless there is an explicit **Deny** — which always takes precedence.

### 🧠 How Policies Are Evaluated

```text
┌─────────────────────────────────────────┐
│         Policy Evaluation Logic         │
├─────────────────────────────────────────┤
│                                         │
│  1. All policies are gathered           │
│     (user + group + resource policies)  │
│                                         │
│  2. By default → DENY (implicit deny)   │
│                                         │
│  3. Evaluate all applicable statements  │
│     - If any statement says DENY →      │
│       ❌ DENIED (explicit deny wins)    │
│     - If any statement says ALLOW →     │
│       ✅ ALLOWED                        │
│     - If no statement matches →         │
│       ❌ DENIED (implicit deny)         │
│                                         │
└─────────────────────────────────────────┘
```

- **Explicit Deny** always overrides any Allow.
- If there is no matching policy at all, the action is **implicitly denied**.

### 🏗️ Real-World Example

Imagine an organization with the following structure:

```text
Company AWS Account
│
├── Group: Developers
│   ├── Policy: AmazonEC2FullAccess
│   ├── Policy: AmazonS3ReadOnlyAccess
│   ├── Alice
│   └── Bob
│
├── Group: Admins
│   ├── Policy: AdministratorAccess
│   └── Alice  ← Alice gets BOTH group permissions
│
└── User: Fred (no group)
    └── Inline Policy: IAMReadOnlyAccess
```

- **Alice** has: `EC2FullAccess` + `S3ReadOnly` (from Developers) + `AdministratorAccess` (from Admins).
- **Bob** has: `EC2FullAccess` + `S3ReadOnly` (from Developers only).
- **Fred** has: `IAMReadOnlyAccess` (inline policy, no group).

### ⚡ Key Exam Takeaways

- IAM is a **global** service — not scoped to any specific AWS region.
- **Root account** should not be used for everyday tasks — create IAM users instead.
- **Groups** contain users only — groups cannot contain other groups.
- **Policies** are JSON documents that define permissions using the **Effect/Action/Resource** model.
- Always apply the **Least Privilege Principle** — grant only the permissions needed.
- An **explicit Deny** in any policy always overrides an Allow.
- Users can belong to **multiple groups** and inherit combined permissions.
- **AWS Managed Policies** are maintained by AWS and cover common use cases — prefer these when possible.

    ---

## Lecture 12: 🛠️ IAM Users & Groups Hands On

> **Section 4: IAM & AWS CLI**<br>AWS Certified Developer Associate (DVA-C02)

### 🔑 Accessing IAM in the AWS Console

- Navigate to the **IAM** service by searching for "IAM" in the AWS Console search bar.
- IAM is a **Global Service** — there is no region selector. Everything you create in IAM applies across all AWS regions.
- On the IAM Dashboard, you'll see a summary of your account's IAM resources: Users, Groups, Roles, Policies, and Identity Providers.

> 💡 Notice the **Account ID** and **Sign-in URL** on the IAM Dashboard. You can customize the sign-in URL with an **Account Alias** for easier access.

### 👥 Creating an IAM Group

1. **Group name**: Enter a descriptive name (e.g., `admin`, `developers`).

- Navigate to **IAM → User groups** in the left sidebar.
- Click **Create group**.

#### 🪜 Steps to Create a Group

1. **Attach permissions policies**: Search for and attach an AWS managed policy.

    - For an admin group, attach the `AdministratorAccess` policy.
    - This policy grants full access to all AWS services and resources.

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": "*",
      "Resource": "*"
    }
  ]
}
```

1. Click **Create user group**.

> ⚠️ The `AdministratorAccess` policy uses a wildcard (`*`) for both Action and Resource — meaning **full unrestricted access**. Only assign this to trusted admin users.

### 👤 Creating an IAM User

- Navigate to **IAM → Users** in the left sidebar.
- Click **Create user**.

#### 🪜 Steps to Create a User

1. **User name**: Enter a name (e.g., `stephane`, `dev-user`).
1. **Provide user access to the AWS Management Console**: Check this option if the user needs console access.

    - Select **"I want to create an IAM user"** (as opposed to Identity Center).
    - Choose a **Console password**:

        - **Autogenerated password** — AWS generates a random password.
        - **Custom password** — You set the password manually.
    - Optionally check **"Users must create a new password at next sign-in"** to force a password reset.
1. Click **Next**.

#### 📂 Assigning the User to a Group

1. **Set permissions**: Choose **Add user to group**.

    - Select the group you created earlier (e.g., `admin`).
    - The user will **inherit** all policies attached to that group.
1. Click **Next**.

#### 🏷️ Adding Tags (Optional)

1. **Tags**: Add optional key-value pairs for metadata.

    - Example: `Department = Engineering`, `Environment = Production`.
    - Tags help with **organization, cost allocation, and access control**.
1. Click **Create user**.

#### 📋 Retrieving Credentials

- After creation, you'll see a **success screen** with:

    - **Console sign-in URL**
    - **User name**
    - **Console password** (if autogenerated — download or copy it now)

> ⚠️ This is the **only time** you can view/download the autogenerated password. Save it securely before closing this page.

#### Understanding Permissions Inheritance

### 🔍 Verifying the User Setup

#### Checking User Details

- Go to **IAM → Users → click on the user name**.
- You'll see several tabs:

| Tab | Description |
| --- | --- |
| **Permissions** | Shows all policies attached (directly + inherited from groups) |
| **Groups** | Shows which groups the user belongs to |
| **Tags** | Displays any metadata tags |
| **Security credentials** | Manage password, access keys, MFA, and SSH keys |
| **Access Advisor** | Shows which services the user has accessed and when |

- Under the **Permissions** tab, you'll see the attached policies and their **source**:

    - Policies inherited from a **group** will show the group name as the source.
    - Policies attached **directly** to the user will show "Attached directly".

```text
Permissions Tab Example:
─────────────────────────────────────────────
Policy Name              │ Type     │ Attached via
─────────────────────────────────────────────
AdministratorAccess      │ Managed  │ Group: admin
─────────────────────────────────────────────
```

### 🔐 Signing In as the New IAM User

#### Using the IAM Sign-in URL

1. Copy the **IAM sign-in URL** from the IAM Dashboard (or the user creation success page).

    - Format: `https://<account-id-or-alias>.signin.aws.amazon.com/console`
1. Open a **private/incognito browser window** (to avoid conflicts with your root account session).
1. Enter:

    - **Account ID** (or alias)
    - **IAM user name**
    - **Password**
1. You are now logged in as the IAM user.

> 💡 You can verify you're signed in as the IAM user by checking the **top-right corner** of the console — it will display the IAM user name and account ID (e.g., `stephane @ 123456789012`).

### 🏷️ Setting an Account Alias

- On the **IAM Dashboard**, find the **AWS Account** section.
- Click **Create** next to the Account Alias field.
- Enter a unique alias (e.g., `my-company-dev`).
- The sign-in URL now becomes: `https://my-company-dev.signin.aws.amazon.com/console`

> 💡 Account aliases must be **globally unique** across all AWS accounts. If your preferred alias is taken, try a variation.

### 👨‍👩‍👧‍👦 Adding More Users & Groups

#### Creating Additional Groups

- You can create more groups (e.g., `developers`, `operations`) and attach different policies to each.
- Example:

```text
Group: developers
  └── Policy: AmazonEC2FullAccess
  └── Policy: AmazonS3ReadOnlyAccess

Group: operations
  └── Policy: AmazonEC2ReadOnlyAccess
  └── Policy: CloudWatchFullAccess
```

#### Assigning a User to Multiple Groups

- Go to **IAM → Users → select the user**.
- Under the **Groups** tab, click **Add user to groups**.
- Select additional groups and confirm.
- The user now **inherits permissions from all assigned groups**.

```text
User: Alice
  ├── Group: admin        → AdministratorAccess
  └── Group: developers   → EC2FullAccess, S3ReadOnlyAccess

Result: Alice has ALL of these permissions combined.
```

### 🗑️ Removing Users & Groups

#### Removing a User from a Group

- Go to **IAM → User groups → select the group**.
- Under the **Users** tab, select the user and click **Remove users**.
- The user will **immediately lose** the permissions inherited from that group.

#### Deleting a User

- Go to **IAM → Users → select the user**.
- Click **Delete** and confirm by typing the user name.
- ⚠️ This action is **irreversible** — the user and all associated credentials are permanently deleted.

#### Deleting a Group

- Go to **IAM → User groups → select the group**.
- Click **Delete** and confirm.
- Deleting a group does **not delete** the users in it — they just lose the group's permissions.

### ⚡ Key Exam Takeaways

- Always create **IAM users** for individuals — never use the **root account** for daily tasks.
- Use **groups** to manage permissions efficiently — attach policies to groups, not individual users.
- Users inherit all permissions from every group they belong to — permissions are **additive**.
- The `AdministratorAccess` managed policy grants full access to all AWS services and resources.
- **Tags** on users are optional but useful for organization, cost tracking, and attribute-based access control (ABAC).
- **Account aliases** provide human-friendly sign-in URLs and must be globally unique.
- The **Access Advisor** tab shows service-level last-accessed data — useful for auditing and applying least privilege.

---

## Lecture 13: 🔄 AWS Console Simultaneous Sign-in

> **Section 4: IAM & AWS CLI**<br>Ultimate AWS Certified Developer Associate DVA-C02 2026 — Stephane Maarek

### 🧩 The Problem: Managing Multiple AWS Accounts

- When working with AWS, you often need to sign into **multiple AWS accounts** or **multiple IAM users** simultaneously
- By default, a single browser session only supports **one active AWS login** at a time
- Signing into a second account in the same browser **logs you out** of the first one
- This is a common pain point for developers who manage:

    - A **personal** AWS account and a **work** AWS account
    - A **root account** and an **IAM user** account
    - Multiple environments like **dev**, **staging**, and **production**

### 🛠️ Solutions for Simultaneous Sign-in

#### 🌐 Using Multiple Browser Profiles

- Most modern browsers (Chrome, Firefox, Edge) support **separate profiles**
- Each profile maintains its own **cookies, sessions, and storage**
- You can sign into a different AWS account in each browser profile

> **How it works:** Browser profiles are completely isolated from each other, so AWS sees each profile as a separate browser session.

```bash
# Example: Chrome profiles
# Profile 1 → AWS Root Account
# Profile 2 → IAM User (Dev)
# Profile 3 → IAM User (Prod)
```

#### 🕵️ Using Incognito / Private Windows

- Open an **Incognito window** (Chrome) or **Private window** (Firefox/Edge)
- Sign into a second AWS account in the incognito session
- The incognito session is **isolated** from the regular browser session
- **Limitation:** You can only have **one additional session** via incognito (regular + incognito = 2 accounts)

#### 🧪 Using Firefox Multi-Account Containers

- Firefox offers a feature called **Multi-Account Containers**
- Each container tab has its own **isolated cookie storage**
- You can create containers like `AWS-Dev`, `AWS-Prod`, `AWS-Root`
- This allows **multiple simultaneous sign-ins** within a single browser window

```bash
# Firefox Container Setup Example
# Container: AWS-Root     → Root account login
# Container: AWS-Dev      → IAM user for dev environment
# Container: AWS-Staging  → IAM user for staging environment
# Container: AWS-Prod     → IAM user for production environment
```

> 💡 **Tip:** Firefox Multi-Account Containers is considered the most flexible solution for simultaneous AWS sign-in, as it supports more than two sessions without needing entirely separate browser profiles.

### 🔑 AWS IAM Identity Center (SSO) Approach

- For organizations, **IAM Identity Center** (formerly AWS SSO) provides a centralized portal
- Users can see **all accounts** they have access to in a single dashboard
- Clicking on an account opens a **new session** with temporary credentials
- This is the **enterprise-grade** solution for managing multiple account sign-ins

```bash
# IAM Identity Center portal URL example
<https://my-company.awsapps.com/start>

# From the portal, users can:
# 1. See all assigned AWS accounts
# 2. Choose a role (e.g., Developer, Admin)
# 3. Click "Management Console" to open a new session
# 4. Or copy temporary CLI credentials
```

### 📋 Practical Tips for Developers

#### Browser Strategy Comparison

| Method | Max Simultaneous Sessions | Ease of Setup | Best For |
| --- | --- | --- | --- |
| Multiple Browser Profiles | Unlimited | Medium | Long-term multi-account work |
| Incognito / Private Window | 2 (regular + incognito) | Easy | Quick one-off access |
| Firefox Containers | Unlimited | Easy | Developers needing flexibility |
| IAM Identity Center (SSO) | Unlimited | Complex (admin setup) | Enterprise / Organizations |

#### 🎯 Best Practices

- **Label your browser profiles** clearly (e.g., `AWS-Dev`, `AWS-Prod`) to avoid accidentally making changes in the wrong account
- **Use different browser themes** or colors for each profile to visually distinguish accounts
- **Never use the root account** for daily tasks — always sign in as an IAM user or use IAM Identity Center
- **Bookmark the correct console URLs** in each profile to avoid cross-account confusion

```bash
# IAM User sign-in URL format
https://<account-id-or-alias>.signin.aws.amazon.com/console

# Example
<https://123456789012.signin.aws.amazon.com/console>
<https://my-company-dev.signin.aws.amazon.com/console>
```

### ⚠️ Common Pitfalls

- **Mixing up accounts:** Without visual cues, it's easy to accidentally deploy resources to the wrong account

    - Always check the **account name/ID** in the top-right corner of the AWS Console
- **Session expiration:** IAM user console sessions expire after **12 hours** by default
- **Federated sessions:** If using SSO/federation, session duration depends on the configured **maximum session duration** of the IAM role

> **Exam Tip:** For the DVA-C02 exam, understand that IAM Identity Center (AWS SSO) is the recommended way to manage access across multiple AWS accounts in an organization. It integrates with AWS Organizations for centralized access management.

### 📝 Key Takeaways

- AWS Console supports **only one active sign-in per browser session**
- Use **browser profiles**, **incognito windows**, or **Firefox containers** for simultaneous sign-in
- **IAM Identity Center** is the enterprise solution for managing multi-account access
- Always **visually distinguish** your sessions to prevent accidental cross-account operations
- Label your profiles, use different themes, and verify the account name before performing actions

---

## Lecture 14: 📜 IAM Policies

> **Section 4: IAM & AWS CLI**<br>Ultimate AWS Certified Developer Associate DVA-C02 2026 — Stephane Maarek

### 🧭 What Are IAM Policies?

- IAM Policies are **JSON documents** that define **permissions** in AWS
- They specify **who** can do **what** on **which resources** and under **what conditions**
- Policies are the foundation of the entire AWS security model
- They follow the principle of **least privilege** — grant only the permissions needed to perform a task

> 💡 **Key Concept:** By default, all permissions are **implicitly denied**. You must explicitly grant access via policies.

### 🏗️ IAM Policy Structure

- Every IAM policy is a JSON document with a well-defined structure
- Understanding each element is **critical** for the DVA-C02 exam

```json
{
  "Version": "2012-10-17",
  "Id": "S3-Account-Permissions",
  "Statement": [
    {
      "Sid": "AllowS3ListAccess",
      "Effect": "Allow",
      "Principal": {
        "AWS": "arn:aws:iam::123456789012:root"
      },
      "Action": [
        "s3:ListBucket",
        "s3:GetObject"
      ],
      "Resource": [
        "arn:aws:s3:::my-bucket",
        "arn:aws:s3:::my-bucket/*"
      ],
      "Condition": {
        "StringEquals": {
          "s3:prefix": ["home/", "docs/"]
        }
      }
    }
  ]
}
```

#### 🔍 Breakdown of Each Element

| Element | Required? | Description |
| --- | --- | --- |
| `Version` | ✅ Yes | Policy language version — always use `"2012-10-17"` |
| `Id` | ❌ Optional | An identifier for the policy (user-defined) |
| `Statement` | ✅ Yes | One or more individual permission statements (array) |
| `Sid` | ❌ Optional | Statement ID — a user-friendly identifier for the statement |
| `Effect` | ✅ Yes | `"Allow"` or `"Deny"` |
| `Principal` | Depends | The account, user, or role the policy applies to (used in **resource-based** policies) |
| `Action` | ✅ Yes | List of API actions the policy allows or denies |
| `Resource` | ✅ Yes | List of AWS resources the actions apply to (ARN format) |
| `Condition` | ❌ Optional | Conditions under which the policy is in effect |

### 📂 Types of IAM Policies

#### 🔵 AWS Managed Policies

- **Pre-built** policies created and maintained by AWS
- Cover common use cases (e.g., `AmazonS3ReadOnlyAccess`, `AdministratorAccess`)
- Automatically **updated by AWS** when new services or API actions are introduced
- Identified by an **orange AWS icon** in the console
- Cannot be edited — they are **read-only**

```json
// Example: AWS Managed Policy — AmazonS3ReadOnlyAccess
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "s3:Get*",
        "s3:List*",
        "s3:Describe*",
        "s3-object-lambda:Get*",
        "s3-object-lambda:List*"
      ],
      "Resource": "*"
    }
  ]
}
```

#### 🟢 Customer Managed Policies

- Policies **created by you** (the AWS account user)
- Fully customizable and **reusable** across multiple users, groups, and roles
- **Best practice** — create your own policies tailored to your organization's needs
- You can **version** them (up to 5 versions) to track changes
- Can be updated and modified at any time

```json
// Example: Custom policy — allow only read access to a specific S3 bucket
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "AllowReadFromProjectBucket",
      "Effect": "Allow",
      "Action": [
        "s3:GetObject",
        "s3:ListBucket"
      ],
      "Resource": [
        "arn:aws:s3:::project-data-bucket",
        "arn:aws:s3:::project-data-bucket/*"
      ]
    }
  ]
}
```

#### 🟡 Inline Policies

- Policies **embedded directly** into a single user, group, or role
- Have a **strict one-to-one relationship** with the principal entity
- If the user/group/role is deleted, the inline policy is **also deleted**
- **Not reusable** across multiple entities
- Generally **not recommended** except for strict one-to-one permission assignments

```json
// Example: Inline policy attached directly to a user
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": "dynamodb:PutItem",
      "Resource": "arn:aws:dynamodb:us-east-1:123456789012:table/Orders"
    }
  ]
}
```

> ⚠️ **Exam Tip:** AWS recommends using **Customer Managed Policies** over Inline Policies for better reusability, version control, and manageability.

### 🧲 How Policies Are Attached

#### 👥 Group-Level Policies (Recommended)

- Attach policies to **IAM Groups** and add users to those groups
- All users in the group **inherit** the group's policies
- This is the **recommended approach** — easier to manage at scale

```bash
# Scenario: 3 groups with different policies

Developers Group  →  Policy: AmazonEC2FullAccess, AmazonS3ReadOnlyAccess
Testers Group     →  Policy: AmazonS3ReadOnlyAccess
Admins Group      →  Policy: AdministratorAccess
```

#### 👤 User-Level Policies

- Policies can be attached **directly to individual users**
- A user can have both **group-inherited policies** AND **directly attached policies**
- The effective permissions = union of all attached policies (unless there's an explicit Deny)

#### 🎭 Role-Level Policies

- Policies attached to **IAM Roles** define what the role is allowed to do
- Roles are assumed by AWS services (EC2, Lambda, etc.) or federated users

### 🔄 Policy Inheritance & Evaluation

#### 📊 How Users Get Permissions

- A user's **effective permissions** are the **combination** of:

    1. Policies attached **directly** to the user
    1. Policies **inherited** from all groups the user belongs to
    1. Any **resource-based policies** granting access

```bash
# Example: User "Alice" belongs to two groups

Alice (User)
├── Group: Developers → Policy: EC2FullAccess, S3ReadOnly
├── Group: Auditors   → Policy: CloudTrailReadOnly
└── Direct Policy     → Policy: DynamoDBFullAccess

# Alice's effective permissions:
# EC2FullAccess + S3ReadOnly + CloudTrailReadOnly + DynamoDBFullAccess
```

#### 🚦 Policy Evaluation Logic

- AWS evaluates all applicable policies together when a request is made
- The evaluation follows this order:

```bash
1. By default → DENY everything (implicit deny)
2. Evaluate all applicable policies
3. If ANY policy has an explicit "Deny" → ACCESS DENIED (always wins)
4. If ANY policy has an "Allow" → ACCESS ALLOWED
5. If neither Allow nor Deny → IMPLICIT DENY (default)
```

> 🔴 **Critical Rule:** An **explicit Deny** ALWAYS overrides an Allow. This is the most important policy evaluation rule for the exam.

```json
// Example: Explicit Deny overrides Allow
// Policy 1: Allow all S3 actions
{
  "Effect": "Allow",
  "Action": "s3:*",
  "Resource": "*"
}

// Policy 2: Deny deleting objects from a specific bucket
{
  "Effect": "Deny",
  "Action": "s3:DeleteObject",
  "Resource": "arn:aws:s3:::critical-bucket/*"
}

// Result: User CAN do everything in S3 EXCEPT delete objects from critical-bucket
```

### 🌍 Identity-Based vs Resource-Based Policies

#### 🪪 Identity-Based Policies

- Attached to **IAM users, groups, or roles**
- Define what the **identity** (principal) is allowed to do
- Answer the question: *"What can this user/role do?"*

```json
// Identity-based: Attached to a user or role
{
  "Effect": "Allow",
  "Action": "s3:GetObject",
  "Resource": "arn:aws:s3:::my-bucket/*"
}
// No "Principal" field — the principal is whoever the policy is attached to
```

#### 🗄️ Resource-Based Policies

- Attached directly to **AWS resources** (S3 buckets, SQS queues, SNS topics, etc.)
- Define **who** (which principal) can access **this specific resource**
- Answer the question: *"Who can access this resource?"*
- Include a `Principal` element

```json
// Resource-based: Attached to an S3 bucket
{
  "Effect": "Allow",
  "Principal": {
    "AWS": "arn:aws:iam::111122223333:root"
  },
  "Action": "s3:GetObject",
  "Resource": "arn:aws:s3:::shared-bucket/*"
}
// The "Principal" field specifies WHO is allowed
```

### 🛡️ Understanding ARNs (Amazon Resource Names)

- ARNs **uniquely identify** AWS resources across all of AWS
- Used in `Resource` and `Principal` fields of policies

```bash
# ARN Format
arn:partition:service:region:account-id:resource-type/resource-id

# Examples
arn:aws:s3:::my-bucket                          # S3 bucket
arn:aws:s3:::my-bucket/*                        # All objects in bucket
arn:aws:iam::123456789012:user/Alice             # IAM user
arn:aws:ec2:us-east-1:123456789012:instance/i-1234567890abcdef0  # EC2 instance
arn:aws:dynamodb:us-east-1:123456789012:table/Orders             # DynamoDB table
arn:aws:lambda:us-east-1:123456789012:function:MyFunction        # Lambda function
```

> 💡 **Note:** Some services like **S3** and **IAM** are global, so the `region` and/or `account-id` fields may be empty (e.g., `arn:aws:s3:::my-bucket`).

### 🔐 Wildcard Matching in Policies

- AWS policies support **wildcards** ( and `?`) for flexible permission definitions

```json
// Allow ALL S3 actions
"Action": "s3:*"

// Allow all "Get" actions on S3
"Action": "s3:Get*"

// Allow access to ALL resources
"Resource": "*"

// Allow access to all objects in a specific bucket
"Resource": "arn:aws:s3:::my-bucket/*"
```

| Wildcard | Meaning | Example |
| --- | --- | --- |
| `*` | Matches **any combination** of characters | `s3:Get*` matches `s3:GetObject`, `s3:GetBucketPolicy`, etc. |
| `?` | Matches **any single** character | Rarely used in practice |

### 🎯 IAM Policy Conditions

- Conditions add **fine-grained control** to when a policy statement applies
- Common condition keys include IP address, time, MFA, tags, and more

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": "ec2:*",
      "Resource": "*",
      "Condition": {
        "IpAddress": {
          "aws:SourceIp": "203.0.113.0/24"
        },
        "Bool": {
          "aws:MultiFactorAuthPresent": "true"
        }
      }
    }
  ]
}
```

#### 🧩 Common Condition Operators

| Operator | Type | Example Use Case |
| --- | --- | --- |
| `StringEquals` | Exact string match | Match a specific tag value |
| `StringLike` | String with wildcards | Match patterns like `project-*` |
| `IpAddress` | IP range (CIDR) | Restrict access to office IP |
| `NotIpAddress` | Exclude IP range | Block specific IPs |
| `DateGreaterThan` | Date comparison | Allow access after a date |
| `Bool` | Boolean check | Require MFA (`aws:MultiFactorAuthPresent`) |
| `ArnLike` | ARN pattern match | Match specific resource patterns |

### 📋 Policy Visual Editor vs JSON Editor

- The AWS Console provides **two ways** to create policies:

    - **Visual Editor** — GUI-based, beginner-friendly, select services/actions/resources from dropdowns
    - **JSON Editor** — Write raw JSON, more powerful, full control
- Both produce the same JSON policy document under the hood
- For the exam, you need to be comfortable **reading and understanding JSON policies**

### 📝 Key Takeaways

- IAM Policies are **JSON documents** that define permissions using `Effect`, `Action`, `Resource`, and optional `Condition`
- Three types: **AWS Managed** (pre-built), **Customer Managed** (custom, reusable), and **Inline** (embedded, not reusable)
- Policies can be attached at the **group**, **user**, or **role** level — group-level is recommended
- An **explicit Deny always wins** over any Allow
- **Identity-based policies** define what a principal can do; **Resource-based policies** define who can access a resource
- Use **wildcards** () for flexible permission matching
- **Conditions** enable fine-grained, context-aware access control (IP, MFA, time, tags)
- Always follow the **principle of least privilege**

---

## Lecture 15: 🛠️ IAM Policies Hands On

> **Section 4: IAM & AWS CLI**<br>Ultimate AWS Certified Developer Associate DVA-C02 2026 — Stephane Maarek

### 🧭 What This Lecture Covers

- Navigating IAM policies in the AWS Management Console
- Understanding how users inherit permissions from groups
- Attaching and detaching policies from users and groups
- Creating a custom IAM policy using both the Visual Editor and JSON Editor
- Testing the effect of policy changes in real time

### 👥 Viewing Group Permissions in the Console

#### 🔎 Steps to Inspect a Group's Policy

1. Open the **IAM Dashboard** in the AWS Console
1. Click **User groups** in the left sidebar
1. Select the group you want to inspect (e.g., `admin`)
1. Navigate to the **Permissions** tab
1. You'll see all policies currently attached to that group

```bash
# Navigation
IAM Dashboard → User groups → [group name] → Permissions
```

#### 📄 Reading the AdministratorAccess Policy

- Click on the policy name (e.g., `AdministratorAccess`) to inspect it
- Select the **JSON** tab to see the raw policy document

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": "*",
      "Resource": "*"
    }
  ]
}
```

- `Action: *` grants access to **every API call** across all AWS services
- `Resource: *` means it applies to **all resources** in the account
- This is the most powerful managed policy — effectively root-level access

> ⚠️ **Best Practice:** Reserve `AdministratorAccess` only for break-glass admin accounts. Day-to-day users should have scoped-down permissions.

### 🧪 Demonstrating Policy Inheritance

#### 🎯 Scenario Setup

- Suppose you have a user called `stephane` who belongs to the `admin` group
- The `admin` group has `AdministratorAccess` attached
- The user automatically **inherits** all permissions from the group without any direct policy attachment

```bash
# Inheritance flow
admin (Group)
  └── Policy: AdministratorAccess
        └── User: stephane → inherits full admin access
```

#### 🔄 What Happens When You Remove a User from a Group?

1. Go to **User groups → admin → Users tab**
1. Remove the user `stephane` from the group
1. Now `stephane` has **zero permissions** (unless other policies are directly attached)
1. If `stephane` tries to access any AWS service, they'll get **Access Denied**

> 💡 This demonstrates the power of group-based permission management — adding or removing a user from a group instantly changes their access.

### ➕ Attaching Policies Directly to a User

#### 🔗 Adding an Inline or Managed Policy

1. Navigate to **IAM → Users → \[select user\]**
1. Go to the **Permissions** tab
1. Click **Add permissions**
1. Choose **Attach policies directly**
1. Search for a policy like `IAMReadOnlyAccess`
1. Select it and click **Next → Add permissions**

```bash
# After attaching, the Permissions tab shows:
┌──────────────────────────┬──────────────────────┐
│ Policy Name              │ Attached Via         │
├──────────────────────────┼──────────────────────┤
│ AdministratorAccess      │ Group: admin         │
│ IAMReadOnlyAccess        │ Attached directly    │
└──────────────────────────┴──────────────────────┘
```

- The **Attached via** column tells you exactly where each policy originates
- A user's effective permissions = **union of all group policies + directly attached policies**

### ✏️ Creating a Custom IAM Policy

#### 🖱️ Method 1: Visual Editor

1. Go to **IAM → Policies → Create policy**
1. The **Visual editor** tab is selected by default
1. Choose a **Service** (e.g., `IAM`)
1. Under **Actions**, expand categories and select specific permissions:

    - `List` → `ListUsers`, `ListGroups`
    - `Read` → `GetUser`, `GetGroup`
1. Under **Resources**, choose `All resources` or specify ARNs
1. Click **Next**, give it a name (e.g., `MyCustomIAMPolicy`), and create

```bash
# Visual Editor lets you pick:
# ✅ Service       → IAM, S3, EC2, Lambda, etc.
# ✅ Actions       → Categorized as List / Read / Write / Permissions management
# ✅ Resources     → All resources or specific ARNs
# ✅ Conditions    → Optional restrictions (IP, MFA, tags, etc.)
```

#### 📝 Method 2: JSON Editor

- Click the **JSON** tab in the policy creation screen
- Write or paste a JSON policy document directly

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "AllowIAMListAndRead",
      "Effect": "Allow",
      "Action": [
        "iam:ListUsers",
        "iam:ListGroups",
        "iam:GetUser",
        "iam:GetGroup",
        "iam:ListPolicies"
      ],
      "Resource": "*"
    }
  ]
}
```

> 💡 **Tip:** You can switch between Visual Editor and JSON at any time — they stay in sync. Changes in one view are reflected in the other.

#### 🏷️ Naming and Reviewing the Policy

- After defining the policy, click **Next**
- Provide a **Name** (e.g., `MyCustomIAMReadPolicy`) and an optional **Description**
- Review the permissions summary — AWS shows a table of services, access levels, and resources
- Click **Create policy**

### 🔍 Understanding the Policy Summary View

- When viewing any policy, AWS provides **three tabs**:

| Tab | What It Shows |
| --- | --- |
| **Permissions** | Human-readable summary — services, access level (List/Read/Write/Full), resources |
| **JSON** | Raw JSON policy document |
| **Policy versions** | Version history (up to 5 versions for customer managed policies) |

```bash
# Access level categories in the summary:
# 📋 List               → Actions that enumerate resources (e.g., ListBuckets)
# 👁️ Read               → Actions that retrieve data (e.g., GetObject)
# ✍️ Write              → Actions that create/modify resources (e.g., PutObject)
# 🔐 Permissions mgmt   → Actions that manage permissions (e.g., PutBucketPolicy)
# 🏷️ Tagging            → Actions related to resource tags
```

### 🗑️ Removing Policies from a User

#### Detaching a Directly Attached Policy

1. Go to **IAM → Users → \[select user\] → Permissions**
1. Find the policy you want to remove
1. Click the **X** or **Remove** button next to the policy
1. Confirm the removal

#### Removing Group Membership

- To revoke group-inherited permissions, remove the user from the group:

    - **IAM → User groups → \[group\] → Users → Remove user**

> 🔴 **Important:** Removing a directly attached policy does NOT affect group-inherited policies, and vice versa. They are independent.

### 🎯 Hands-On: Testing Permission Changes Live

#### Experiment Workflow

```bash
# Step 1: User "stephane" is in "admin" group → has full access
#         Try accessing IAM, EC2, S3 → ✅ Everything works

# Step 2: Remove "stephane" from "admin" group
#         Try accessing any service → ❌ Access Denied everywhere

# Step 3: Attach "IAMReadOnlyAccess" directly to "stephane"
#         Try accessing IAM → ✅ Can view users, groups, policies
#         Try creating a new user → ❌ Access Denied (read-only)
#         Try accessing EC2 → ❌ Access Denied (no EC2 policy)

# Step 4: Add "stephane" back to "admin" group
#         Full access restored → ✅ Everything works again
```

> 💡 **Key Learning:** Permission changes take effect **immediately** — no need to log out and back in. Just refresh the console page.

### 🔐 Understanding the Policy Evaluation in Practice

- When `stephane` has both group and direct policies, AWS **merges** all policies:

```bash
# Effective permissions = Group policies ∪ Direct policies

# If Group policy says:   Allow s3:*
# And Direct policy says:  Allow iam:List*
# Effective result:        Allow s3:* AND iam:List*

# But if ANY policy says:  Deny s3:DeleteBucket
# Then:                    s3:DeleteBucket is DENIED (explicit Deny wins)
```

### 📝 Key Takeaways

- Group-based policies are the **recommended** way to manage permissions at scale
- Users **inherit** all policies from every group they belong to
- You can also attach policies **directly** to users, but this is harder to manage
- The **Visual Editor** is beginner-friendly; the **JSON Editor** offers full control — both produce identical results
- Permission changes are **instant** — no session restart needed
- The **Policy Summary** view helps you quickly understand what a policy allows without reading raw JSON
- Always check the **Attached via** column to understand where a user's permissions originate

---

## Lecture 16: 🔐 IAM MFA Overview

> **Section 4: IAM & AWS CLI**<br>Ultimate AWS Certified Developer Associate DVA-C02 2026 — Stephane Maarek

### 🛡️ Why Do We Need Password Policies & MFA?

- Your AWS account and IAM users must be **protected** against unauthorized access
- Two complementary defense mechanisms exist:

    - **Strong password policies** — first line of defense
    - **Multi-Factor Authentication (MFA)** — second line of defense
- Together, they form a **defense-in-depth** strategy that dramatically reduces the risk of account compromise

> 💡 **Core Principle:** Even if a password is stolen or cracked, MFA ensures the attacker still cannot access your account without the physical/virtual device.

### 🔑 IAM Password Policy

- AWS lets you define **account-wide password rules** that apply to all IAM users
- Configured via **IAM → Account settings → Password policy**

#### 📏 Configurable Password Requirements

| Setting | Description | Default |
| --- | --- | --- |
| **Minimum length** | Minimum number of characters required | 8 characters |
| **Require uppercase** | At least one uppercase letter (A–Z) | Not enforced |
| **Require lowercase** | At least one lowercase letter (a–z) | Not enforced |
| **Require numbers** | At least one digit (0–9) | Not enforced |
| **Require symbols** | At least one non-alphanumeric character (!@#$%^&\*) | Not enforced |
| **Password expiration** | Force users to change password after N days | Disabled |
| **Prevent reuse** | Remember last N passwords to block re-use | Disabled |
| **Allow self-change** | Let users change their own password | Enabled |

```bash
# Example: A strong password policy configuration
Minimum length:          14 characters
Require uppercase:       ✅ Yes
Require lowercase:       ✅ Yes
Require numbers:         ✅ Yes
Require symbols:         ✅ Yes
Password expiration:     90 days
Prevent reuse:           Last 5 passwords remembered
Allow users to change:   ✅ Yes
```

> 🎯 **Exam Tip:** Password policies help protect against **brute-force attacks**. MFA protects against **credential theft** (phishing, leaks, shoulder surfing).

### 🔒 Multi-Factor Authentication (MFA)

#### 🧩 What Is MFA?

- MFA adds a **second layer of verification** beyond just a password
- To log in, users need:

    1. **Something they know** — their password
    1. **Something they have** — a physical or virtual MFA device
- Even if the password is compromised, the account remains secure as long as the MFA device is not also compromised

```bash
# MFA Login Flow
┌─────────────┐     ┌──────────────────┐     ┌──────────────┐
│  Enter       │ ──→ │  Enter MFA Code   │ ──→ │  Access      │
│  Password    │     │  (6-digit token)  │     │  Granted ✅  │
└─────────────┘     └──────────────────┘     └──────────────┘

# Without correct MFA code → Access Denied ❌
```

#### 🎯 Who Should Use MFA?

- **Root account** — **absolutely mandatory**, this is the most privileged account
- **All IAM users** — strongly recommended, especially those with console access
- **Users with elevated privileges** — admins, developers with production access

> 🔴 **Critical:** AWS strongly recommends enabling MFA on the **root account** as the very first security step after creating your AWS account.

### 📱 MFA Device Options in AWS

#### 1️⃣ Virtual MFA Device

- A software-based authenticator app installed on your phone or computer
- Generates a new **time-based one-time password (TOTP)** every 30 seconds
- A single virtual device can support **multiple tokens** (multiple AWS accounts/users)

```bash
# Popular Virtual MFA Apps
┌──────────────────────┬─────────────────────┐
│ App                  │ Platform            │
├──────────────────────┼─────────────────────┤
│ Google Authenticator │ iOS, Android        │
│ Authy               │ iOS, Android, Desktop│
│ Microsoft Auth.     │ iOS, Android        │
│ Duo Mobile          │ iOS, Android        │
└──────────────────────┴─────────────────────┘
```

- **Setup process:** Scan a QR code with the app → enter two consecutive codes to verify → MFA is activated
- **Cost:** Free
- **Best for:** Individual developers, personal accounts, cost-conscious setups

#### 2️⃣ Universal 2nd Factor (U2F) Security Key

- A **physical hardware device** that plugs into your computer's USB port
- Based on the **FIDO U2F** open standard
- You press a button on the key to authenticate — no codes to type

```bash
# Example U2F Device
YubiKey 5 Series (by Yubico)
├── Interface: USB-A, USB-C, NFC, Lightning
├── Protocol: FIDO U2F / FIDO2 / WebAuthn
├── Supports: Multiple AWS accounts with a single key
└── Cost: ~$25–$75 per key
```

- **Best for:** Teams requiring strong physical security, compliance-driven environments
- **Advantage:** Phishing-resistant — the key verifies the website's identity before authenticating

#### 3️⃣ Hardware Key Fob MFA Device

- A small physical device with a screen that displays a **rotating 6-digit code**
- Provided by third-party vendors like **Gemalto (Thales)**

```bash
# Hardware Key Fob
Gemalto / Thales MFA Device
├── Display: 6-digit OTP on small LCD screen
├── Battery: Lasts several years
├── No USB required: standalone device
└── Cost: ~$13–$30
```

- **Best for:** Organizations with strict hardware-based security policies

#### 4️⃣ Hardware Key Fob for AWS GovCloud

- A **special hardware device** specifically for **AWS GovCloud (US)** accounts
- Provided by **SurePassID**
- Required for government workloads with elevated compliance needs (FedRAMP, ITAR, etc.)

```bash
# GovCloud MFA
SurePassID MFA Device
├── Designed for: AWS GovCloud (US) region
├── Compliance: FedRAMP High, ITAR, DoD
└── Procurement: Through SurePassID vendor
```

### 🆚 MFA Device Comparison

| Feature | Virtual MFA | U2F Security Key | Hardware Key Fob | GovCloud Key Fob |
| --- | --- | --- | --- | --- |
| **Type** | Software app | Physical USB device | Physical token | Physical token |
| **Code Entry** | Type 6-digit code | Press a button | Type 6-digit code | Type 6-digit code |
| **Cost** | Free | $25–$75 | $13–$30 | Varies |
| **Phishing Resistant** | ❌ No | ✅ Yes | ❌ No | ❌ No |
| **Multi-account** | ✅ Yes | ✅ Yes | ❌ One per device | ❌ One per device |
| **Best For** | Personal / Dev | Enterprise / High Security | Compliance | GovCloud |

### 🧠 How MFA Works Under the Hood (TOTP)

- Virtual MFA and hardware key fobs use the **Time-based One-Time Password (TOTP)** algorithm
- Both AWS and the device share a **secret seed** during initial setup
- Every 30 seconds, a new 6-digit code is derived from the seed + current timestamp
- AWS verifies the code by performing the same calculation server-side

```python
# Simplified TOTP concept (RFC 6238)
import hmac, hashlib, time, struct

def generate_totp(secret_seed):
    # Current 30-second time window
    time_step = int(time.time()) // 30

    # HMAC-SHA1 of time step using the shared secret
    hmac_hash = hmac.new(secret_seed, struct.pack(">Q", time_step), hashlib.sha1).digest()

    # Extract 6-digit code from hash
    offset = hmac_hash[-1] & 0x0F
    code = struct.unpack(">I", hmac_hash[offset:offset+4])[0] & 0x7FFFFFFF
    return code % 1000000  # 6-digit OTP
```

> 💡 This is why your authenticator app codes **expire every 30 seconds** — the time window ensures each code is only valid briefly.

### ⚠️ Important Considerations

#### 🔄 Losing Your MFA Device

- If you lose access to your MFA device, you may get **locked out** of your account
- **Root account recovery:** Contact AWS Support with identity verification
- **IAM user recovery:** An administrator can deactivate MFA for the affected user
- **Prevention:** For the root account, consider registering **multiple MFA devices** (AWS now supports this)

```bash
# AWS supports multiple MFA devices per user (up to 8)
# Root account: register at least 2 MFA devices for redundancy
Root Account MFA Devices:
  ├── Primary:   Virtual MFA (Google Authenticator on phone)
  └── Backup:    U2F Security Key (YubiKey stored in safe)
```

#### 🔐 MFA with AWS CLI & SDK

- MFA can also be required for **programmatic access** (CLI/SDK), not just console login
- This is configured via IAM policy conditions using `aws:MultiFactorAuthPresent`

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Deny",
      "Action": "*",
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

- When MFA is required for CLI access, users must call `sts:GetSessionToken` with their MFA code first, then use the temporary credentials returned

```bash
# Getting temporary credentials with MFA for CLI
aws sts get-session-token \\
  --serial-number arn:aws:iam::123456789012:mfa/username \\
  --token-code 123456 \\
  --duration-seconds 3600
```

### 📝 Key Takeaways

- **Password policies** enforce strong passwords across all IAM users (length, complexity, expiration, reuse prevention)
- **MFA** adds a second authentication factor — something you **have** in addition to something you **know**
- AWS supports **4 types** of MFA devices: Virtual MFA, U2F Security Key, Hardware Key Fob, and GovCloud Key Fob
- **Virtual MFA** (Google Authenticator, Authy) is the most common and free option
- **U2F keys** (YubiKey) provide the strongest protection because they are **phishing-resistant**
- **Always enable MFA on the root account** — this is non-negotiable
- AWS now supports registering **up to 8 MFA devices** per user for redundancy
- MFA can be enforced for both **console** and **programmatic (CLI/SDK)** access via IAM policy conditions

---

## Lecture 17: 🛠️ IAM MFA Hands On

> **Section 4: IAM & AWS CLI**<br>Ultimate AWS Certified Developer Associate DVA-C02 2026 — Stephane Maarek

### 🧭 What This Lecture Covers

- Configuring the **IAM Password Policy** for your AWS account
- Enabling **Multi-Factor Authentication (MFA)** on the root account
- Setting up MFA for an IAM user
- Using a virtual MFA device (Google Authenticator / Authy) with the AWS Console

### 🔑 Part 1: Setting Up the IAM Password Policy

#### 📍 Navigating to Password Policy Settings

1. Sign in to the AWS Console as an **admin** or root user
1. Go to **IAM** service
1. In the left sidebar, click **Account settings**
1. Scroll to the **Password policy** section
1. Click **Edit** to customize the policy

```bash
# Console Navigation
IAM → Account settings → Password policy → Edit
```

#### ⚙️ Configuring the Policy

- By default, AWS uses a **default password policy** with basic requirements
- Click **Custom** to set your own rules

```bash
# Recommended Custom Password Policy Settings

✅ Minimum password length:            14 characters
✅ Require at least one uppercase:      A-Z
✅ Require at least one lowercase:      a-z
✅ Require at least one number:         0-9
✅ Require at least one symbol:         !@#$%^&*()
✅ Enable password expiration:          90 days
✅ Prevent password reuse:              Remember last 5 passwords
✅ Allow users to change own password:  Yes
```

- After configuring, click **Save changes**
- This policy now applies to **all IAM users** in the account when they create or change passwords

> 💡 **Note:** The password policy does NOT apply to the root account — only IAM users. The root account password is managed separately.

### 🔐 Part 2: Enabling MFA on the Root Account

#### 🚨 Why Root Account MFA Is Critical

- The root account has **unrestricted access** to everything in your AWS account
- If compromised, an attacker can delete all resources, rack up charges, or steal data
- Enabling MFA is the **single most important security action** you can take

#### 📍 Step-by-Step: Activating Root Account MFA

1. Sign in to the AWS Console using your **root account** (email + password)
1. Click your **account name** in the top-right corner
1. Select **Security credentials** from the dropdown
1. Scroll to the **Multi-factor authentication (MFA)** section
1. Click **Assign MFA device**

```bash
# Console Navigation
Top-right account menu → Security credentials → Multi-factor authentication → Assign MFA device
```

#### 📝 Naming and Choosing the Device Type

- **Device name:** Give it a descriptive name (e.g., `my-phone-mfa`, `root-google-auth`)
- **Device type:** Choose one of the following:

```bash
# MFA Device Type Options in the Console
┌─────────────────────────────────────────────────┐
│  ○ Authenticator app        (Virtual MFA)       │
│  ○ Security key             (U2F / FIDO2)       │
│  ○ Hardware TOTP token      (Physical key fob)  │
└─────────────────────────────────────────────────┘
```

- For this hands-on, select **Authenticator app** → Click **Next**

#### 📱 Setting Up the Virtual MFA App

1. AWS displays a **QR code** on screen
1. Open your authenticator app on your phone:

    - **Google Authenticator** (recommended, free)
    - **Authy** (supports cloud backup)
    - **Microsoft Authenticator**
1. In the app, tap **+** (add account) → **Scan QR code**
1. Point your camera at the QR code displayed in the AWS Console
1. The app starts generating **6-digit codes** that rotate every 30 seconds

```bash
# What the authenticator app shows after scanning:
┌──────────────────────────────────┐
│  Amazon Web Services             │
│  root-account@example.com        │
│                                  │
│        4 7 2  8 1 3              │
│        ████████░░ (expires in 12s)│
└──────────────────────────────────┘
```

#### ✅ Verifying the MFA Setup

- AWS asks you to enter **two consecutive MFA codes** to confirm the device is working
- Wait for the first code → type it in **MFA code 1**
- Wait for the code to rotate (new 30-second window) → type the new code in **MFA code 2**
- Click **Add MFA**

```bash
# Verification prompt
MFA code 1:  [ 472813 ]     ← first 6-digit code
MFA code 2:  [ 935201 ]     ← WAIT for rotation, then enter the next code

# ⚠️ Common mistake: entering the same code twice
# You MUST enter two DIFFERENT consecutive codes
```

- Once verified, you'll see a **success message**: "MFA device assigned successfully"
- The MFA section now shows your device with a status of **Active**

> ✅ **Done!** From now on, every root account login will require both the password AND a 6-digit MFA code.

### 👤 Part 3: Enabling MFA for an IAM User

#### 📍 Two Ways to Set Up MFA for IAM Users

**Option A: Admin enables MFA for a user**

1. Go to **IAM → Users → \[select user\]**
1. Click the **Security credentials** tab
1. Under **Multi-factor authentication (MFA)**, click **Assign MFA device**
1. Follow the same QR code scanning process as the root account

```bash
# Console Path
IAM → Users → [username] → Security credentials → Assign MFA device
```

**Option B: User enables MFA for themselves**

1. The IAM user signs into the console with their own credentials
1. Clicks their **username** in the top-right → **Security credentials**
1. Scrolls to the MFA section and clicks **Assign MFA device**
1. Scans the QR code with their authenticator app

> 💡 **Note:** For Option B to work, the user must have the `iam:EnableMFADevice` and related permissions, or the admin must attach a policy allowing self-service MFA management.

#### 🔧 Self-Service MFA Policy

- To let users manage their own MFA without giving them full IAM admin access:

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "AllowUserToManageOwnMFA",
      "Effect": "Allow",
      "Action": [
        "iam:EnableMFADevice",
        "iam:CreateVirtualMFADevice",
        "iam:DeleteVirtualMFADevice",
        "iam:DeactivateMFADevice",
        "iam:ResyncMFADevice",
        "iam:ListMFADevices"
      ],
      "Resource": [
        "arn:aws:iam::*:mfa/${aws:username}",
        "arn:aws:iam::*:user/${aws:username}"
      ]
    }
  ]
}
```

### 🔄 Testing the MFA Login Flow

#### 🧪 Signing In After MFA Is Enabled

1. Sign out of the AWS Console
1. Navigate to the sign-in page and enter your email (root) or IAM credentials
1. After password verification, AWS now presents an **MFA challenge screen**
1. Open your authenticator app and read the current 6-digit code
1. Enter the code and click **Submit**
1. You're now signed in with MFA-verified access

```bash
# Login flow WITH MFA enabled
Step 1: Enter email/username + password     → Submit
Step 2: AWS presents MFA challenge screen   → "Enter MFA code"
Step 3: Open authenticator app              → Read 6-digit code
Step 4: Enter code                          → Submit
Step 5: ✅ Console access granted
```

### 🔧 Managing MFA Devices After Setup

#### 📋 Viewing Assigned MFA Devices

```bash
# For root account:
Top-right menu → Security credentials → MFA section

# For IAM users:
IAM → Users → [username] → Security credentials → MFA section
```

#### ♻️ Replacing or Removing an MFA Device

- To **remove** an existing MFA device: Select the device → Click **Remove**
- To **replace** it (e.g., new phone): Remove the old one first, then assign a new one
- AWS supports **up to 8 MFA devices** per user, so you can add backup devices without removing the primary one

```bash
# Recommended: Register multiple MFA devices for redundancy
Root Account MFA:
  ├── Device 1: Google Authenticator (primary phone)
  ├── Device 2: Authy (backup phone or tablet)
  └── Device 3: YubiKey (physical backup in a safe)
```

#### 🔁 Resynchronizing an MFA Device

- If your authenticator app's clock drifts, codes might stop working
- Go to the MFA section → select the device → click **Resync**
- Enter two consecutive valid codes to resynchronize the time

### ⚠️ Troubleshooting Common MFA Issues

| Issue | Cause | Solution |
| --- | --- | --- |
| Code rejected during setup | Entered same code twice | Wait for rotation, enter two **different** consecutive codes |
| Code rejected during login | Clock drift on phone | Resync the device in IAM settings, or ensure phone time is auto-synced |
| Lost phone / MFA device | No backup MFA registered | Root: contact AWS Support; IAM user: admin can deactivate MFA |
| QR code won't scan | Screen glare or camera issue | Click **Show secret key** to manually enter the seed into your app |
| Can't find MFA option | Insufficient permissions | Ensure the user has `iam:EnableMFADevice` permission |

> 🔴 **Critical:** If you lose your root account MFA device and have no backup, you must go through AWS Support's **identity verification process**, which can take 24–72 hours. Always register backup devices.

### 📝 Key Takeaways

- The **password policy** is configured under IAM → Account settings and applies to all IAM users
- MFA on the **root account** is set up via the top-right menu → Security credentials
- MFA for **IAM users** is configured under their Security credentials tab in the IAM console
- Always use **Authenticator app** (virtual MFA) as the minimum — it's free and easy
- Enter **two different consecutive codes** during MFA setup verification (common mistake: entering the same code)
- Register **multiple MFA devices** (up to 8) per account for redundancy
- Users can manage their own MFA if granted the appropriate self-service IAM permissions
- If codes stop working, **resync** the device or verify your phone's clock is auto-syncing

---

## Lecture 22: ⌨️ AWS CLI Hands On

> **Section 4: IAM & AWS CLI** — In this hands-on lecture, we explore how to use the AWS Command Line Interface (CLI) to interact with AWS services directly from your terminal. This is a critical skill for the Developer Associate exam and real-world AWS development.

### 🔧 What is the AWS CLI?

- The **AWS CLI** (Command Line Interface) is an open-source tool that enables you to interact with AWS services using commands in your terminal or command prompt.
- It provides **direct access** to the public APIs of AWS services.
- You can use it to **manage AWS resources**, automate tasks via scripts, and perform operations that would otherwise require the AWS Management Console.
- The CLI is built on top of the **AWS SDK for Python (Boto3)**.

> 💡 The AWS CLI is an alternative to using the AWS Management Console — everything you can do in the Console, you can do via the CLI (and more).

### 🛠️ Prerequisites

- You must have the **AWS CLI installed** on your machine (covered in Lectures 19–21 for Windows, macOS, and Linux).
- You need **AWS Access Keys** configured (Access Key ID + Secret Access Key) — generated from the IAM Console.
- Access Keys are linked to an **IAM User**, and permissions are determined by the policies attached to that user.

### 🔑 Configuring the AWS CLI

- Before using the CLI, you must configure it with your credentials using the `aws configure` command:

```bash
aws configure
```

- You will be prompted for four values:

```text
AWS Access Key ID [None]: AKIAIOSFODNN7EXAMPLE
AWS Secret Access Key [None]: wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY
Default region name [None]: us-east-1
Default output format [None]: json
```

| Parameter | Description |
| --- | --- |
| **Access Key ID** | Your IAM user's access key identifier |
| **Secret Access Key** | Your IAM user's secret key (keep this private!) |
| **Default region** | The AWS region to send requests to (e.g., `us-east-1`, `eu-west-1`) |
| **Default output format** | Response format: `json`, `yaml`, `text`, or `table` |

- These credentials are stored locally in `~/.aws/credentials` and the config in `~/.aws/config`.

```bash
# View stored credentials
cat ~/.aws/credentials
```

```text
[default]
aws_access_key_id = AKIAIOSFODNN7EXAMPLE
aws_secret_access_key = wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY
```

```bash
# View config
cat ~/.aws/config
```

```text
[default]
region = us-east-1
output = json
```

### 🧪 Hands-On: Using AWS CLI Commands

#### 📋 Listing IAM Users

- One of the first commands to try is listing all IAM users in your account:

```bash
aws iam list-users
```

- Sample output (JSON format):

```json
{
    "Users": [
        {
            "UserName": "admin",
            "UserId": "AIDAJKLMNOPQRSTUVWXYZ",
            "Arn": "arn:aws:iam::123456789012:user/admin",
            "Path": "/",
            "CreateDate": "2026-01-15T10:30:00Z"
        },
        {
            "UserName": "developer",
            "UserId": "AIDAABCDEFGHIJKLMNOPQ",
            "Arn": "arn:aws:iam::123456789012:user/developer",
            "Path": "/",
            "CreateDate": "2026-03-20T14:45:00Z"
        }
    ]
}
```

#### 📋 Listing IAM Groups

```bash
aws iam list-groups
```

#### 📋 Listing IAM Policies Attached to a User

```bash
aws iam list-attached-user-policies --user-name admin
```

```json
{
    "AttachedPolicies": [
        {
            "PolicyName": "AdministratorAccess",
            "PolicyArn": "arn:aws:iam::aws:policy/AdministratorAccess"
        }
    ]
}
```

### 📐 AWS CLI Command Structure

- All AWS CLI commands follow a consistent structure:

```bash
aws <service> <action> [--options]
```

| Component | Example | Description |
| --- | --- | --- |
| `aws` | `aws` | The CLI binary |
| `<service>` | `iam`, `s3`, `ec2` | The AWS service to interact with |
| `<action>` | `list-users`, `describe-instances` | The API action to perform |
| `--options` | `--user-name admin` | Additional parameters |

#### 🔍 Common Examples

```bash
# List all S3 buckets
aws s3 ls

# Describe EC2 instances
aws ec2 describe-instances

# List Lambda functions
aws lambda list-functions

# Get caller identity (who am I?)
aws sts get-caller-identity
```

- The `aws sts get-caller-identity` command is especially useful for verifying which IAM user or role your CLI is configured as:

```bash
aws sts get-caller-identity
```

```json
{
    "UserId": "AIDAJKLMNOPQRSTUVWXYZ",
    "Account": "123456789012",
    "Arn": "arn:aws:iam::123456789012:user/admin"
}
```

### 🔄 Changing Output Formats

- You can override the default output format per command using the `-output` flag:

```bash
# Table format — great for readability
aws iam list-users --output table

# Text format — useful for scripting and piping
aws iam list-users --output text

# YAML format
aws iam list-users --output yaml
```

### 🌍 Specifying a Region Per Command

- You can override the default region on any command using `-region`:

```bash
aws ec2 describe-instances --region eu-west-1
```

- This is useful when you need to query resources in a different region than your default.

### 🔐 Permissions & the CLI

- The AWS CLI uses the **same permissions** as the IAM user whose access keys are configured.
- If your IAM user does **not** have permission to perform an action, the CLI will return an **AccessDenied** error:

```bash
aws iam create-user --user-name testuser
```

```json
{
    "Error": {
        "Code": "AccessDenied",
        "Message": "User: arn:aws:iam::123456789012:user/developer is not authorized to perform: iam:CreateUser"
    }
}
```

> ⚠️ **Exam Tip**: If the CLI returns an `AccessDenied` error, the IAM user or role lacks the required permissions. Check the IAM policies attached to the user/group/role.

### 🧹 Dry Run Mode

- Some AWS CLI commands support `-dry-run` to test whether you have the required permissions **without actually executing** the action:

```bash
aws ec2 run-instances --dry-run --image-id ami-0abcdef1234567890 --instance-type t2.micro
```

- If you have permission, you'll see a `DryRunOperation` error (which means it would have succeeded).
- If you don't have permission, you'll see an `UnauthorizedOperation` error.

### 📝 CLI Help System

- The AWS CLI has a built-in help system accessible at any level:

```bash
# Top-level help
aws help

# Service-level help
aws iam help

# Command-level help
aws iam list-users help
```

- This is extremely helpful for discovering available commands and understanding required parameters.

### ⚡ Key Takeaways

- The AWS CLI allows you to **interact with AWS services from the terminal** using access keys.
- Use `aws configure` to set up your **credentials and default region**.
- CLI commands follow the pattern: `aws <service> <action> [--options]`.
- The CLI respects **IAM permissions** — you can only do what your IAM user/role is allowed to do.
- Use `-output` to change response format (`json`, `table`, `text`, `yaml`).
- Use `-region` to override the default region per command.
- Use `-dry-run` to test permissions without executing an action.
- Use `aws sts get-caller-identity` to verify your current identity.
- **Protect your Access Keys** — never share them or commit them to source code.

> 🎯 **Exam Relevance**: The CLI is heavily tested in the Developer Associate exam. Understand the command structure, how permissions affect CLI access, the `--dry-run` flag, and how to troubleshoot `AccessDenied` errors.

---

## Lecture 23: ☁️ AWS CloudShell

> **Overview**: AWS CloudShell is a browser-based, pre-authenticated shell environment provided directly within the AWS Management Console. It eliminates the need to install or configure the AWS CLI locally — you get a fully managed terminal with the CLI pre-installed, automatically authenticated with your current console credentials.

### 🌐 What is AWS CloudShell?

- **AWS CloudShell** is a **free**, browser-based shell available directly from the AWS Management Console.
- It provides a **Linux-based environment** with common development tools and the AWS CLI **pre-installed**.
- You are **automatically authenticated** using the credentials of the IAM user or role you used to sign in to the Console — no need to run `aws configure`.
- It's essentially like having a terminal in the cloud, ready to go with zero setup.

> 💡 Think of CloudShell as your "instant terminal" — no installation, no credential management, just open and start running AWS commands.

### 🚀 How to Access CloudShell

- In the AWS Management Console, look for the **CloudShell icon** (a terminal/shell icon) in the **top navigation bar** (near the region selector and notifications bell).
- Click the icon, and a terminal panel opens at the bottom of your browser (or in a new tab).
- The first time you launch it, it may take a few seconds to provision the environment.

> ⚠️ **Region Availability**: CloudShell is **not available in every AWS region**. If the icon is grayed out, try switching to a supported region (e.g., `us-east-1`, `eu-west-1`, `ap-southeast-1`).

### ✅ Key Features of AWS CloudShell

#### 🔑 Pre-Authenticated Environment

- CloudShell automatically inherits the **credentials and permissions** of the IAM user or role you're signed in with.
- No need to configure access keys — just start running commands:

```bash
# Verify your identity — no configuration needed!
aws sts get-caller-identity
```

```json
{
    "UserId": "AIDAJKLMNOPQRSTUVWXYZ",
    "Account": "123456789012",
    "Arn": "arn:aws:iam::123456789012:user/admin"
}
```

#### 🛠️ Pre-Installed Tools

- CloudShell comes with a rich set of tools already installed:

| Tool | Description |
| --- | --- |
| **AWS CLI v2** | Latest version of the AWS CLI |
| **Python 3** | Python runtime + pip |
| **Node.js** | JavaScript runtime + npm |
| **Git** | Version control |
| **Make** | Build automation |
| **pip** | Python package manager |
| **npm** | Node.js package manager |
| **vim / nano** | Text editors |
| **jq** | JSON processor |
| **bash / zsh** | Shell environments |

```bash
# Check pre-installed AWS CLI version
aws --version

# Check Python version
python3 --version

# Check Node.js version
node --version

# Check Git version
git --version
```

#### 💾 Persistent Storage (1 GB)

- CloudShell provides **1 GB of persistent storage** per region in your **home directory** (`/home/cloudshell-user`).
- Files saved in your home directory **persist between sessions** — they survive when you close and reopen CloudShell.
- Files saved **outside** the home directory (e.g., `/tmp`) are **ephemeral** and will be lost when the session ends.

```bash
# Your home directory — files here persist
cd ~
pwd
# /home/cloudshell-user

# Create a persistent file
echo "This file will persist!" > ~/my-notes.txt

# This file will be LOST after session ends
echo "Temporary" > /tmp/temp-file.txt
```

> ⚠️ **Important**: If you don't use CloudShell for **120 days**, your persistent storage may be **deleted**. Use it periodically to keep your files.

#### 📤 File Upload & Download

- CloudShell supports **uploading** files from your local machine and **downloading** files from the CloudShell environment.
- Use the **Actions** menu (top-right of the CloudShell panel) to:

    - **Upload file**: Transfer a file from your local machine to CloudShell.
    - **Download file**: Specify a file path in CloudShell and download it to your local machine.

```bash
# After uploading a file, it appears in your home directory
ls ~/uploaded-file.txt

# To download, use Actions > Download file and provide the path
# Example: /home/cloudshell-user/my-script.sh
```

#### 🪟 Multiple Tabs & Split View

- You can open **multiple terminal tabs** within CloudShell — useful for running parallel commands.
- You can also **split the screen** to view multiple terminals side by side.
- Use the **"+"** button or the **Actions** menu to create new tabs.

#### 🌍 Region-Specific

- CloudShell operates in the **region you have selected** in the Console.
- The default region for CLI commands matches your Console region — no need to pass `-region`.
- Each region has its own **separate 1 GB persistent storage**.

```bash
# Commands run in the region you've selected in the Console
# If your Console is set to us-east-1:
aws s3 ls
# Lists S3 buckets (S3 is global, but API calls go through us-east-1)

aws ec2 describe-instances
# Lists EC2 instances in us-east-1
```

### 🆚 CloudShell vs Local AWS CLI

| Feature | AWS CloudShell | Local AWS CLI |
| --- | --- | --- |
| **Installation** | None required | Must install CLI |
| **Authentication** | Automatic (Console credentials) | Must run `aws configure` with access keys |
| **Storage** | 1 GB persistent per region | Unlimited (local disk) |
| **Customization** | Limited (can install packages) | Full control |
| **Access** | Browser only | Any terminal |
| **Cost** | Free | Free (CLI itself) |
| **Offline** | ❌ Not available | ✅ Available |
| **Session Timeout** | ~20 min idle timeout | No timeout |

### 🧪 Hands-On: Running Commands in CloudShell

#### 📋 List IAM Users

```bash
aws iam list-users
```

#### 📦 List S3 Buckets

```bash
aws s3 ls
```

#### 🖥️ Describe EC2 Instances

```bash
aws ec2 describe-instances --query "Reservations[*].Instances[*].[InstanceId,State.Name,InstanceType]" --output table
```

#### 📝 Create and Run a Script

```bash
# Create a simple script
cat > ~/list-services.sh << 'EOF'
#!/bin/bash
echo "=== IAM Users ==="
aws iam list-users --output table
echo ""
echo "=== S3 Buckets ==="
aws s3 ls
echo ""
echo "=== Current Region EC2 Instances ==="
aws ec2 describe-instances --query "Reservations[*].Instances[*].InstanceId" --output text
EOF

# Make it executable
chmod +x ~/list-services.sh

# Run it
./list-services.sh
```

#### 📦 Install Additional Packages

```bash
# Install a Python package
pip3 install boto3

# Install a Node.js package
npm install -g aws-cdk
```

> 💡 Installed packages in the home directory persist, but system-level installs outside `~` may not survive session restarts.

### ⏱️ Session Behavior & Timeouts

- CloudShell sessions **automatically time out** after approximately **20 minutes of inactivity**.
- When a session times out, the **compute environment is recycled**, but your **home directory files persist**.
- If you're running a long process, keep the tab active to prevent timeout.
- You can **restart** the environment from the **Actions** menu if needed (this resets the compute but keeps persistent storage).

### 🔒 Security Considerations

- CloudShell inherits the **exact permissions** of the logged-in IAM user/role.
- If your IAM user has `AdministratorAccess`, CloudShell has full access.
- If your IAM user has limited permissions, CloudShell is equally limited.
- You can **restrict CloudShell access** via IAM policies:

```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Sid": "DenyCloudShell",
            "Effect": "Deny",
            "Action": [
                "cloudshell:*"
            ],
            "Resource": "*"
        }
    ]
}
```

- This policy would **prevent** a user from launching CloudShell entirely.

### 💰 Pricing

- AWS CloudShell is **completely free** to use.
- You only pay for the **AWS resources** you create or interact with through CloudShell (e.g., launching an EC2 instance).
- The compute environment, storage (up to 1 GB), and data transfer for CloudShell itself are **no cost**.

### ⚡ Key Takeaways

- **AWS CloudShell** is a free, browser-based terminal built into the AWS Console.
- It comes **pre-authenticated** — no need to configure credentials or access keys.
- It includes **pre-installed tools**: AWS CLI v2, Python, Node.js, Git, and more.
- You get **1 GB of persistent storage** per region in your home directory.
- You can **upload and download files** between your local machine and CloudShell.
- CloudShell operates in the **region selected in the Console**.
- Sessions **time out after ~20 minutes** of inactivity, but home directory files persist.
- Access to CloudShell can be controlled via **IAM policies** using `cloudshell:*` actions.
- It's ideal for **quick tasks**, testing CLI commands, and running scripts without local setup.

> 🎯 **Exam Tip**: Know that CloudShell is a **free, pre-authenticated** shell in the Console. Understand that it uses the **same permissions** as the signed-in user, provides **1 GB persistent storage**, and is **not available in all regions**. It's a popular alternative to setting up a local CLI environment.

---

## Lecture 24: 🎭 IAM Roles for AWS Services

> **Overview**: IAM Roles are a fundamental AWS identity mechanism that allows AWS services (like EC2, Lambda, etc.) to perform actions on your behalf. Unlike IAM Users which are tied to a person, IAM Roles are designed to be **assumed** by entities that need temporary credentials to interact with AWS resources.

### 🤔 Why Do AWS Services Need Roles?

- AWS services often need to perform actions on **other AWS services** on your behalf.
- For example, an **EC2 instance** might need to read from an S3 bucket, or a **Lambda function** might need to write to a DynamoDB table.
- You **cannot** attach Access Keys to an AWS service the way you would for a human user — this is insecure and unmanageable.
- Instead, you assign an **IAM Role** to the service, granting it the permissions it needs through policies.

> 💡 IAM Roles are like "hats" that an AWS service can put on to gain specific permissions. The service **assumes** the role and gets **temporary security credentials** automatically.

### 🎯 What is an IAM Role?

- An **IAM Role** is an IAM identity with specific permissions, but it is **not associated with a specific person**.
- It is intended to be **assumable** by anyone or anything that needs it — AWS services, IAM users, or even external identities.
- When a role is assumed, AWS provides **temporary security credentials** (Access Key ID, Secret Access Key, and a Session Token) that expire automatically.
- Roles use **IAM Policies** (just like users and groups) to define what actions are allowed or denied.

#### 🏗️ Role Components

| Component | Description |
| --- | --- |
| **Trust Policy** | Defines **who** can assume the role (e.g., which AWS service, user, or account) |
| **Permissions Policy** | Defines **what** the role can do (e.g., read S3, write DynamoDB) |
| **Session Duration** | How long the temporary credentials remain valid (default: 1 hour, max: 12 hours) |

### 🖥️ Common Use Cases for IAM Roles

#### 📦 EC2 Instance Roles

- The most common use case in the Developer Associate exam.
- An EC2 instance needs to access AWS services (e.g., S3, DynamoDB, SQS).
- You create an IAM Role with the necessary permissions and **attach it to the EC2 instance** via an **Instance Profile**.
- The EC2 instance automatically receives **temporary credentials** that are rotated by AWS.

```text
EC2 Instance  →  Assumes IAM Role  →  Gets Temporary Credentials  →  Accesses S3/DynamoDB/etc.
```

> ⚠️ **Never** store Access Keys on an EC2 instance. Always use IAM Roles instead — this is a critical best practice and common exam question.

#### ⚡ Lambda Execution Roles

- Every Lambda function must have an **execution role** (also called a Lambda Role).
- This role defines what AWS services the Lambda function can interact with.
- Common permissions: CloudWatch Logs (for logging), S3, DynamoDB, SQS, etc.

#### 🔄 Other AWS Service Roles

- **ECS Task Roles** — permissions for containers running in ECS.
- **CloudFormation Roles** — permissions for CloudFormation to create/modify resources.
- **CodeDeploy Roles** — permissions to deploy applications.
- **Step Functions Roles** — permissions to invoke Lambda, access DynamoDB, etc.

### 🔐 Trust Policy (Who Can Assume the Role?)

- The **Trust Policy** is a JSON document that specifies which **principals** (entities) are allowed to assume the role.
- For AWS service roles, the principal is the service itself.

#### 📋 Example: Trust Policy for EC2

```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Principal": {
                "Service": "ec2.amazonaws.com"
            },
            "Action": "sts:AssumeRole"
        }
    ]
}
```

- This trust policy says: **only the EC2 service** can assume this role.

#### 📋 Example: Trust Policy for Lambda

```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Principal": {
                "Service": "lambda.amazonaws.com"
            },
            "Action": "sts:AssumeRole"
        }
    ]
}
```

### 📜 Permissions Policy (What Can the Role Do?)

- The **Permissions Policy** is attached to the role and defines what actions the role can perform.
- These are standard IAM policies — the same JSON structure used for users and groups.

#### 📋 Example: Permissions Policy for S3 Read Access

```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": [
                "s3:GetObject",
                "s3:ListBucket"
            ],
            "Resource": [
                "arn:aws:s3:::my-bucket",
                "arn:aws:s3:::my-bucket/*"
            ]
        }
    ]
}
```

#### 📋 Example: Permissions for Lambda Logging

```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": [
                "logs:CreateLogGroup",
                "logs:CreateLogStream",
                "logs:PutLogEvents"
            ],
            "Resource": "arn:aws:logs:*:*:*"
        }
    ]
}
```

### 🏷️ Instance Profiles (EC2 + Roles)

- An **Instance Profile** is the container that passes an IAM Role to an EC2 instance.
- When you create an IAM Role for EC2 via the AWS Console, an Instance Profile with the **same name** is created automatically.
- When using the CLI or CloudFormation, you must create the Instance Profile separately and associate the role with it.

```text
IAM Role  ←→  Instance Profile  ←→  EC2 Instance
```

```bash
# Create an instance profile (CLI)
aws iam create-instance-profile --instance-profile-name MyEC2Profile

# Add role to instance profile
aws iam add-role-to-instance-profile \\
    --instance-profile-name MyEC2Profile \\
    --role-name MyEC2Role

# Associate instance profile with a running EC2 instance
aws ec2 associate-iam-instance-profile \\
    --instance-id i-0abcdef1234567890 \\
    --iam-instance-profile Name=MyEC2Profile
```

### 🔄 How Role Assumption Works (Behind the Scenes)

1. An AWS service (e.g., EC2) **assumes** the IAM Role.
1. AWS **STS** (Security Token Service) generates **temporary credentials**:

    - Access Key ID
    - Secret Access Key
    - Session Token
    - Expiration timestamp
1. The service uses these credentials to make **API calls** to other AWS services.
1. When credentials **expire**, STS automatically **rotates** them (for service roles like EC2).

```bash
# On an EC2 instance with a role, you can see the temporary credentials:
curl <http://169.254.169.254/latest/meta-data/iam/security-credentials/MyEC2Role>
```

```json
{
    "Code": "Success",
    "LastUpdated": "2026-05-03T10:00:00Z",
    "Type": "AWS-HMAC",
    "AccessKeyId": "ASIATEMP...",
    "SecretAccessKey": "tempSecret...",
    "Token": "sessionToken...",
    "Expiration": "2026-05-03T16:00:00Z"
}
```

> 💡 The credentials are fetched from the **EC2 Instance Metadata Service** (IMDS) at `169.254.169.254`. The AWS CLI and SDKs do this automatically — you don't need to manage it yourself.

### 🆚 IAM Roles vs IAM Users

| Feature | IAM User | IAM Role |
| --- | --- | --- |
| **Intended for** | People (humans) | Services, applications, cross-account access |
| **Credentials** | Permanent (Access Keys, password) | Temporary (auto-rotated) |
| **Authentication** | Long-term credentials | `sts:AssumeRole` |
| **Best for** | Console login, CLI access by humans | EC2, Lambda, ECS, cross-account |
| **Credential rotation** | Manual | Automatic |
| **Can have MFA** | ✅ Yes | ✅ Yes (for user-assumed roles) |

### 📝 AWS Managed Policies for Common Roles

- AWS provides **managed policies** that cover common use cases, so you don't have to write custom policies from scratch:

| Managed Policy | Use Case |
| --- | --- |
| `AmazonS3ReadOnlyAccess` | Read-only access to all S3 buckets |
| `AmazonS3FullAccess` | Full access to S3 |
| `AmazonDynamoDBFullAccess` | Full access to DynamoDB |
| `AWSLambdaBasicExecutionRole` | Lambda → CloudWatch Logs |
| `AmazonEC2RoleforSSM` | EC2 → Systems Manager |
| `AmazonECSTaskExecutionRolePolicy` | ECS task execution permissions |

```bash
# Attach a managed policy to a role
aws iam attach-role-policy \\
    --role-name MyEC2Role \\
    --policy-arn arn:aws:iam::aws:policy/AmazonS3ReadOnlyAccess
```

### ⚡ Key Takeaways

- **IAM Roles** allow AWS services to perform actions on your behalf using **temporary credentials**.
- Roles have two key components: a **Trust Policy** (who can assume it) and a **Permissions Policy** (what it can do).
- The most common use case is **EC2 Instance Roles** — never use Access Keys on an EC2 instance.
- **Instance Profiles** are the bridge between an IAM Role and an EC2 instance.
- Temporary credentials are provided by **AWS STS** and are **automatically rotated**.
- Other services that commonly use roles: **Lambda**, **ECS**, **CloudFormation**, **CodeDeploy**.
- Use **AWS Managed Policies** for common permission sets to simplify role configuration.
- Roles follow the **principle of least privilege** — only grant the permissions the service actually needs.

> 🎯 **Exam Tips**:
>
> - If a question mentions an EC2 instance needing access to S3/DynamoDB → the answer involves **IAM Roles**, not Access Keys.
> - Know the difference between **Trust Policy** and **Permissions Policy**.
> - Understand that roles provide **temporary credentials** via STS.
> - Lambda **always** needs an execution role — even if it doesn't access other services (it still needs CloudWatch Logs permissions).

---

## Lecture 25: 🛠️ IAM Roles Hands On

> **Overview**: This hands-on lecture demonstrates how to create an IAM Role for AWS services through the AWS Management Console. We walk through selecting a trusted entity, attaching permission policies, and reviewing the finished role configuration.

### 🚀 Navigating to IAM Roles

- Open the **IAM Console** → click **Roles** in the left sidebar.
- You may see pre-existing roles (AWS creates some service-linked roles automatically).
- Click the **Create role** button to start the creation wizard.

### 📋 Role Creation Wizard

#### 🔹 Step 1: Choose Trusted Entity

- The first decision is **who can assume this role**. AWS offers these entity types:

| Entity Type | When to Use |
| --- | --- |
| **AWS service** | EC2, Lambda, ECS, etc. need to call other AWS APIs |
| **AWS account** | Cross-account access scenarios |
| **Web identity** | Federated login via Cognito, Google, Facebook |
| **SAML 2.0 federation** | Corporate SSO / Active Directory |
| **Custom trust policy** | Manually author the trust JSON |

- Select **AWS service**, then pick **EC2** from the service list.
- This tells AWS: "EC2 instances are allowed to assume this role."

> 💡 Behind the scenes, AWS generates a trust policy automatically:

```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Principal": {
                "Service": "ec2.amazonaws.com"
            },
            "Action": "sts:AssumeRole"
        }
    ]
}
```

#### 🔹 Step 2: Attach Permissions

- Search for and select **IAMReadOnlyAccess** — a managed policy granting read-only visibility into IAM.
- You can attach multiple policies if needed (e.g., also adding `AmazonS3ReadOnlyAccess`).
- Click **Next** to proceed.

> The `IAMReadOnlyAccess` policy permits actions like `iam:List*` and `iam:Get*` but blocks any modifications.

```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": [
                "iam:GenerateCredentialReport",
                "iam:GenerateServiceLastAccessedDetails",
                "iam:Get*",
                "iam:List*",
                "iam:SimulateCustomPolicy",
                "iam:SimulatePrincipalPolicy"
            ],
            "Resource": "*"
        }
    ]
}
```

#### 🔹 Step 3: Name and Review

- **Role name**: `DemoRoleForEC2`
- **Description**: "Allows EC2 instances to read IAM resources"
- Optionally add **Tags** for organization (e.g., `Project: DVA-C02-Lab`).
- Review the trusted entities and attached policies, then click **Create role**.

### 🔍 Inspecting the Role

After creation, click into **DemoRoleForEC2** to explore its details:

#### 📜 Permissions Tab

- Lists every policy attached to the role.
- Expand any policy to view its full JSON document.
- Use **Add permissions** to attach additional policies later.

#### 🤝 Trust Relationships Tab

- Displays the trust policy JSON — confirms `ec2.amazonaws.com` as the trusted principal.
- Click **Edit trust policy** to modify which entities can assume this role.

#### 📊 Access Advisor Tab

- Shows which AWS services were accessed using this role, along with timestamps.
- Extremely useful for **auditing** and tightening permissions to follow least privilege.

### 🖥️ Previewing Role Usage with EC2

- This role will be **attached to an EC2 instance** in a later lecture (Lecture 43).
- Once attached, any CLI/SDK command run on that instance automatically uses the role's temporary credentials.

```bash
# From inside the EC2 instance (role attached):
aws iam list-users          # ✅ Succeeds — read-only allowed
aws iam create-user --user-name bob   # ❌ AccessDenied — write not permitted
```

> ⚠️ **Best Practice**: Never place long-term Access Keys on an EC2 instance. Always assign an IAM Role instead — credentials are temporary and auto-rotated by AWS STS.

### ✏️ Managing Roles After Creation

#### ➕ Attaching Additional Policies

```bash
aws iam attach-role-policy \\
    --role-name DemoRoleForEC2 \\
    --policy-arn arn:aws:iam::aws:policy/AmazonS3ReadOnlyAccess
```

#### ➖ Detaching a Policy

```bash
aws iam detach-role-policy \\
    --role-name DemoRoleForEC2 \\
    --policy-arn arn:aws:iam::aws:policy/IAMReadOnlyAccess
```

#### 🔄 Updating the Trust Policy

```bash
aws iam update-assume-role-policy \\
    --role-name DemoRoleForEC2 \\
    --policy-document file://new-trust-policy.json
```

#### 🗑️ Deleting the Role (Cleanup)

- You must detach all policies and remove the role from any instance profiles before deletion:

```bash
# Detach policies first
aws iam detach-role-policy \\
    --role-name DemoRoleForEC2 \\
    --policy-arn arn:aws:iam::aws:policy/IAMReadOnlyAccess

# Remove from instance profile
aws iam remove-role-from-instance-profile \\
    --instance-profile-name DemoRoleForEC2 \\
    --role-name DemoRoleForEC2

# Delete instance profile and role
aws iam delete-instance-profile --instance-profile-name DemoRoleForEC2
aws iam delete-role --role-name DemoRoleForEC2
```

### ⚡ Key Takeaways

- Creating a role involves three decisions: **who assumes it** (trust), **what it can do** (permissions), and **what it's called** (naming).
- The Console auto-generates the trust policy when you pick a service like EC2.
- **IAMReadOnlyAccess** is a great starter policy for learning — it lets you query IAM without risk of modification.
- The **Access Advisor** tab helps enforce least privilege by showing which permissions are actually used.
- Roles created for EC2 automatically get a matching **Instance Profile** when created through the Console.
- You'll use this exact role in Lecture 43 to demonstrate EC2 Instance Roles in action.

> 🎯 **Exam Tip**: The Console creates the Instance Profile automatically with the same name as the role. When using CLI or CloudFormation, you must create the Instance Profile separately and associate the role — a common gotcha on the exam.

---

## Lecture 26: 🔒 IAM Security Tools

> **Overview**: AWS provides built-in security tools within IAM to help you audit and review permissions across your account. This lecture covers two essential tools — the **IAM Credentials Report** (account-level) and **IAM Access Advisor** (user-level) — both critical for maintaining security hygiene and enforcing the principle of least privilege.

### 🛡️ Two Key IAM Security Tools

| Tool | Scope | Purpose |
| --- | --- | --- |
| **IAM Credentials Report** | Account-level | Lists all IAM users and the status of their credentials |
| **IAM Access Advisor** | User-level | Shows which services a specific user accessed and when |

> 💡 Both tools help answer the question: *"Are my IAM users configured securely, and are they using only the permissions they need?"*

### 📊 Tool 1: IAM Credentials Report

#### 🔎 What Is It?

- A **downloadable CSV report** that lists **every IAM user** in your AWS account along with the status of their various credentials.
- It is an **account-wide** audit — it covers all users at once.
- Helps identify security risks like unused accounts, old access keys, or users without MFA.

#### 📋 Information Included in the Report

The CSV report contains a row per IAM user with columns including:

| Column | What It Tells You |
| --- | --- |
| `user` | The IAM username |
| `arn` | The user's Amazon Resource Name |
| `user_creation_time` | When the user was created |
| `password_enabled` | Whether a console password is set |
| `password_last_used` | When the password was last used to sign in |
| `password_last_changed` | When the password was last rotated |
| `password_next_rotation` | When the password is due for rotation (if a policy is set) |
| `mfa_active` | Whether MFA is enabled (**critical security check**) |
| `access_key_1_active` | Whether Access Key 1 is active |
| `access_key_1_last_rotated` | When Access Key 1 was last rotated |
| `access_key_1_last_used_date` | When Access Key 1 was last used |
| `access_key_1_last_used_region` | Which region Access Key 1 was used from |
| `access_key_1_last_used_service` | Which service Access Key 1 was used for |
| `access_key_2_active` | Whether Access Key 2 is active |
| `access_key_2_last_rotated` | When Access Key 2 was last rotated |
| `access_key_2_last_used_date` | When Access Key 2 was last used |
| `cert_1_active` / `cert_2_active` | Whether X.509 signing certificates are active |

#### 🚨 What to Look For (Red Flags)

- `mfa_active = false` → User does not have MFA enabled — security risk!
- `password_last_used` is very old or `N/A` → Potentially unused account — consider disabling.
- `access_key_1_last_used_date` is months/years ago → Stale access key — rotate or deactivate.
- `access_key_1_active = true` AND `access_key_2_active = true` → Two active keys — review if both are necessary.
- `password_last_changed` is very old → Password hasn't been rotated — enforce rotation policy.

#### 🖥️ Generating the Report

**Via Console:**

- IAM Console → left sidebar → **Credential report** → **Download report**
- The report is generated as a `.csv` file.

**Via CLI:**

```bash
# Step 1: Request the report to be generated
aws iam generate-credential-report

# Step 2: Download the report (base64 encoded)
aws iam get-credential-report --output text --query Content | base64 --decode > credential-report.csv

# View the CSV
cat credential-report.csv
```

> ⚠️ The report can only be generated **once every 4 hours**. If you request it again within that window, you'll receive the cached version.

### 🔍 Tool 2: IAM Access Advisor

#### 🔎 What Is It?

- A **per-user** tool that shows which AWS services a specific IAM user (or role) has accessed and when.
- Found on the **Access Advisor** tab when you view an individual user or role in the IAM Console.
- Helps you identify **unused permissions** so you can tighten policies and follow **least privilege**.

#### 📋 Information Provided

For each AWS service, Access Advisor shows:

| Field | Description |
| --- | --- |
| **Service name** | The AWS service (e.g., Amazon S3, Amazon EC2, IAM) |
| **Last accessed** | The date and time the user last accessed this service |
| **Granted via** | Which policy granted the user access to this service |
| **Tracking period** | Data is available for the last **400 days** |

#### 💡 How to Use Access Advisor

- If a user has `AdministratorAccess` but has **only ever accessed S3 and EC2**, you can:

    1. Remove `AdministratorAccess`.
    1. Replace it with more targeted policies for just S3 and EC2.
    1. This enforces the **principle of least privilege**.
- If a service shows **"Not accessed in the tracking period"**, the user likely doesn't need permission for that service at all.

#### 🖥️ Viewing Access Advisor

**Via Console:**

- IAM Console → **Users** → click a user → **Access Advisor** tab.
- You'll see a table listing every AWS service and when it was last accessed.

**Via CLI:**

```bash
# Step 1: Generate the service last accessed details
aws iam generate-service-last-accessed-details \\
    --arn arn:aws:iam::123456789012:user/admin

# Returns a JobId
# {
#     "JobId": "abcd-1234-efgh-5678"
# }

# Step 2: Retrieve the results using the JobId
aws iam get-service-last-accessed-details \\
    --job-id abcd-1234-efgh-5678
```

```json
{
    "JobStatus": "COMPLETED",
    "ServicesLastAccessed": [
        {
            "ServiceName": "Amazon S3",
            "ServiceNamespace": "s3",
            "LastAuthenticated": "2026-05-01T08:30:00Z",
            "TotalAuthenticatedEntities": 1
        },
        {
            "ServiceName": "AWS Lambda",
            "ServiceNamespace": "lambda",
            "LastAuthenticated": "2026-04-15T12:00:00Z",
            "TotalAuthenticatedEntities": 1
        },
        {
            "ServiceName": "Amazon DynamoDB",
            "ServiceNamespace": "dynamodb",
            "TotalAuthenticatedEntities": 0
        }
    ]
}
```

- In this example, the user accessed S3 recently, Lambda a couple weeks ago, but has **never** accessed DynamoDB — a candidate for permission removal.

### 🆚 Credentials Report vs Access Advisor

| Aspect | Credentials Report | Access Advisor |
| --- | --- | --- |
| **Scope** | All IAM users in the account | One specific user or role |
| **Focus** | Credential status (passwords, keys, MFA) | Service access history |
| **Output** | Downloadable CSV file | Interactive table in Console |
| **Primary question** | "Are credentials configured securely?" | "Is this user using their permissions?" |
| **Use case** | Audit compliance, find stale credentials | Enforce least privilege, remove unused permissions |
| **Tracking period** | Point-in-time snapshot | Last 400 days of activity |
| **Generation limit** | Once per 4 hours | On-demand |

### 🏢 Real-World Audit Workflow

A security team would typically combine both tools:

1. **Run the Credentials Report** → Identify users with:

    - No MFA enabled
    - Access keys older than 90 days
    - Passwords never rotated
    - Inactive accounts
1. **For each flagged user, check Access Advisor** → Determine:

    - Which services they actually use
    - Which permissions can be safely removed
1. **Take action**:

    - Enable MFA for unprotected users
    - Rotate or deactivate old access keys
    - Replace broad policies with scoped-down ones
    - Disable or delete unused accounts

### ⚡ Key Takeaways

- **IAM Credentials Report** = account-level CSV audit of all users' credential statuses (password, access keys, MFA).
- **IAM Access Advisor** = user-level service access history spanning the last 400 days.
- The Credentials Report helps catch **security misconfigurations** (no MFA, stale keys, unused accounts).
- Access Advisor helps enforce **least privilege** by revealing which permissions are actually being used.
- Both tools are **free** and should be used regularly as part of your security hygiene practices.
- The Credentials Report is regenerated at most **once every 4 hours**.

> 🎯 **Exam Tips**:
>
> - Know the difference: **Credentials Report** = account-wide, covers credential status. **Access Advisor** = per-user, covers service access history.
> - If a question asks about auditing MFA status or finding inactive users → **Credentials Report**.
> - If a question asks about reducing permissions or finding unused service access → **Access Advisor**.
> - Access Advisor tracks data for up to **400 days**.

---

## Lecture 27: 🛠️ IAM Security Tools Hands On

> **Overview**: This hands-on lecture walks through using both IAM security tools in the AWS Console — generating and analyzing the **Credentials Report** and navigating the **Access Advisor** for a specific user. These are practical skills for auditing your AWS account's security posture.

### 📊 Hands On: IAM Credentials Report

#### 🔹 Step 1: Navigate to the Report

- Open the **IAM Console** → in the left sidebar, click **Credential report** (under "Access reports").
- Click **Download credential report**.
- A `.csv` file is downloaded to your machine.

#### 🔹 Step 2: Open and Analyze the CSV

- Open the downloaded CSV in a spreadsheet application (Excel, Google Sheets, etc.).
- Each **row** represents one IAM user in your account (including the root account).
- Each **column** represents a credential attribute.

#### 🔹 Step 3: Key Columns to Inspect

> 💡 Here's what a sample row looks like when opened in a spreadsheet:

```text
user, arn, user_creation_time, password_enabled, password_last_used, password_last_changed, mfa_active, access_key_1_active, access_key_1_last_rotated, access_key_1_last_used_date, ...
```

**For the root account row:**

- `user` = `<root_account>`
- Check `mfa_active` — should be `true` (critical!)
- Check `access_key_1_active` — should ideally be `false` (root should not have access keys)

**For each IAM user row:**

- `password_enabled` — does this user have console access?
- `password_last_used` — when did they last log in? If never or months ago, consider disabling.
- `mfa_active` — is MFA turned on? If `false`, this is a security gap.
- `access_key_1_active` / `access_key_2_active` — are access keys active?
- `access_key_1_last_used_date` — when was the key last used? Stale keys should be rotated.
- `access_key_1_last_rotated` — how old is this key?

#### 🔹 Example: Reading the Report

```text
user:                admin
password_enabled:    true
password_last_used:  2026-05-03T10:15:00+00:00
mfa_active:          true          ✅ Good
access_key_1_active: true
access_key_1_last_rotated: 2026-01-10T08:00:00+00:00
access_key_1_last_used:    2026-05-02T14:30:00+00:00

user:                old-developer
password_enabled:    true
password_last_used:  2025-06-15T09:00:00+00:00   ⚠️ Almost a year ago
mfa_active:          false         🚨 No MFA!
access_key_1_active: true
access_key_1_last_rotated: 2024-11-01T08:00:00+00:00  🚨 Over a year old
access_key_1_last_used:    N/A     🚨 Never used
```

> From this report, `old-developer` has three red flags: no MFA, a stale access key that's never been used, and a password last used almost a year ago. Action: disable the account or at minimum enforce MFA and deactivate the unused key.

#### 🔹 Generating via CLI

```bash
# Request report generation
aws iam generate-credential-report
```

```json
{
    "State": "STARTED",
    "Description": "No report exists. Starting a new report generation."
}
```

```bash
# Wait a moment, then download
aws iam get-credential-report --query 'Content' --output text | base64 -d > report.csv
```

```bash
# Quick check: which users lack MFA?
cat report.csv | awk -F',' '{print $1, $8}' | grep false
```

> ⚠️ Remember: this report can only be regenerated **once every 4 hours**. Subsequent requests within that window return the cached version.

### 🔍 Hands On: IAM Access Advisor

#### 🔹 Step 1: Navigate to a User

- IAM Console → **Users** → click on any user (e.g., `admin`).
- Click the **Access Advisor** tab.

#### 🔹 Step 2: Review the Service Access Table

- You'll see a table with columns:

| Column | Meaning |
| --- | --- |
| **Service** | AWS service name (S3, EC2, IAM, Lambda, etc.) |
| **Policies granting permissions** | Which attached policy provides access |
| **Last accessed** | Date and time the user last called this service's API |

#### 🔹 Step 3: Interpreting the Results

**Services with recent "Last accessed" dates:**

- The user actively uses these → keep the permissions.

**Services showing "Not accessed in the tracking period":**

- The user has permission but has **never used it** (within 400 days).
- These are candidates for **permission removal** to tighten security.

#### 🔹 Example Scenario

```text
Service                  Last Accessed              Policy
──────────────────────────────────────────────────────────────
Amazon S3                2026-05-03 (Today)         AdministratorAccess
IAM                      2026-05-02 (Yesterday)     AdministratorAccess
Amazon EC2               2026-04-28 (5 days ago)    AdministratorAccess
AWS Lambda               Not accessed               AdministratorAccess
Amazon DynamoDB          Not accessed               AdministratorAccess
Amazon RDS               Not accessed               AdministratorAccess
Amazon Redshift          Not accessed               AdministratorAccess
AWS CloudFormation       Not accessed               AdministratorAccess
... (200+ more services) Not accessed               AdministratorAccess
```

> 🔑 **Insight**: This user has `AdministratorAccess` (full access to everything), but they only use S3, IAM, and EC2. A least-privilege approach would replace `AdministratorAccess` with specific policies for just those three services.

#### 🔹 Taking Action Based on Access Advisor

1. **Identify** services marked "Not accessed."
1. **Create** a custom policy covering only the services the user actually needs.
1. **Detach** the overly broad policy (e.g., `AdministratorAccess`).
1. **Attach** the new scoped-down policy.
1. **Monitor** Access Advisor again after a few weeks to verify nothing broke.

```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Sid": "AllowS3Full",
            "Effect": "Allow",
            "Action": "s3:*",
            "Resource": "*"
        },
        {
            "Sid": "AllowEC2Full",
            "Effect": "Allow",
            "Action": "ec2:*",
            "Resource": "*"
        },
        {
            "Sid": "AllowIAMReadOnly",
            "Effect": "Allow",
            "Action": [
                "iam:Get*",
                "iam:List*"
            ],
            "Resource": "*"
        }
    ]
}
```

#### 🔹 Access Advisor for Roles

- Access Advisor is not limited to IAM Users — it also works for **IAM Roles**.
- Navigate to **Roles** → click a role → **Access Advisor** tab.
- Especially useful for tightening **EC2 instance roles** and **Lambda execution roles**.

### 🔄 Combining Both Tools: A Practical Audit Workflow

```text
┌─────────────────────────────────────────┐
│  1. Download Credentials Report (CSV)   │
│     → Flag users with:                  │
│        • No MFA                         │
│        • Stale access keys              │
│        • Old/unused passwords           │
└──────────────────┬──────────────────────┘
                   ▼
┌─────────────────────────────────────────┐
│  2. For each flagged user, open         │
│     Access Advisor                      │
│     → Identify unused permissions       │
│     → Determine if account is needed    │
└──────────────────┬──────────────────────┘
                   ▼
┌─────────────────────────────────────────┐
│  3. Take remediation actions:           │
│     • Enable MFA                        │
│     • Rotate/deactivate stale keys      │
│     • Scope down broad policies         │
│     • Disable/delete unused accounts    │
└─────────────────────────────────────────┘
```

### ⚡ Key Takeaways

- The **Credentials Report** is downloaded as a CSV from `IAM Console → Credential report` — gives a bird's-eye view of every user's credential health.
- **Access Advisor** is found on the detail page of any user or role under the `Access Advisor` tab — reveals which services are actually being used.
- Always check the root account row in the Credentials Report: MFA should be active, and access keys should be disabled.
- Access Advisor data spans the **last 400 days**, giving a generous window to evaluate usage patterns.
- Use both tools together for a complete security audit: Credentials Report identifies *credential risks*, Access Advisor identifies *permission bloat*.

> 🎯 **Exam Tip**: If a question describes a scenario where you need to find users without MFA or with old access keys → **Credentials Report**. If the scenario involves determining whether a user actually needs certain permissions → **Access Advisor**. The hands-on familiarity with where these tools live in the Console is also tested.

---
