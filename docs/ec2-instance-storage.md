# EC2 Instance Storage

## Lecture 45: 💾 EBS Overview

> **Section 6: EC2 Instance Storage** — Ultimate AWS Certified Developer Associate DVA-C02 2026

### 📌 Overview

- EBS stands for **Elastic Block Store** — it is a **network-attached storage** service for EC2 instances
- Think of it as a **virtual USB drive** that you can attach to your EC2 instances over the network
- EBS volumes allow your data to **persist** even after the EC2 instance is terminated
- They are a core building block of nearly every EC2-based architecture in AWS

### 🔌 What Is an EBS Volume?

- An EBS volume is a **network drive** (not a physical drive) that you attach to an EC2 instance
- It uses the AWS network to communicate with the instance, so there is **slight latency** compared to a local disk
- Because it's network-attached, it can be **detached** from one instance and **reattached** to another quickly
- This makes EBS volumes ideal for **failover scenarios** — move a volume to a healthy instance in minutes

```text
EBS Conceptual Model:

┌──────────────┐          Network          ┌──────────────┐
│  EC2 Instance │ ◄═══════════════════════► │  EBS Volume  │
│  (us-east-1a) │     (attached via        │  (us-east-1a) │
│               │      AWS network)        │  30 GiB, gp3  │
└──────────────┘                           └──────────────┘
```

### 🔒 EBS Volume — Key Characteristics

#### 📍 Locked to an Availability Zone

- An EBS volume is created in a **specific Availability Zone** (AZ)
- It can **only** be attached to EC2 instances in the **same AZ**
- A volume in `us-east-1a` **cannot** be attached to an instance in `us-east-1b`
- To move a volume across AZs, you need to create a **snapshot** first, then restore it in the target AZ

```text
❌ Cross-AZ Attachment (NOT possible):

  EC2 in us-east-1a ←✕→ EBS Volume in us-east-1b

✅ Same-AZ Attachment:

  EC2 in us-east-1a ←══→ EBS Volume in us-east-1a
```

#### 📏 Provisioned Capacity

- When you create an EBS volume, you specify:

    - **Size** in GiB (e.g., 8 GiB, 100 GiB, 16 TiB max)
    - **Volume type** (gp2, gp3, io1, io2, st1, sc1)
    - **IOPS** (for certain volume types like io1/io2 and gp3)
- You are **billed for the provisioned capacity**, not for how much data you actually store
- You can **increase the capacity** over time without downtime

#### 1️⃣ One-to-One Attachment (Default)

- By default, an EBS volume can be attached to **only one EC2 instance** at a time
- One EC2 instance can have **multiple EBS volumes** attached simultaneously

```text
✅ Multiple volumes to one instance:

  ┌──────────────┐
  │  EC2 Instance │ ◄── EBS Volume A (root, 8 GiB)
  │               │ ◄── EBS Volume B (data, 100 GiB)
  │               │ ◄── EBS Volume C (logs, 50 GiB)
  └──────────────┘

❌ One volume to multiple instances (default):

  EC2 Instance 1 ◄──┐
                     ├── EBS Volume ← NOT allowed (by default)
  EC2 Instance 2 ◄──┘
```

> 💡 There is an advanced feature called **EBS Multi-Attach** (for io1/io2 volumes only) that allows attaching a single volume to multiple instances — covered in Lecture 53.

#### 🔓 Unattached Volumes

- An EBS volume does **not** have to be attached to an instance at all times
- You can create a volume and leave it unattached — it just sits in your AZ, ready to be attached when needed
- You still **pay** for unattached volumes based on their provisioned size

### 🗑️ Delete on Termination Attribute

- Each EBS volume attached to an instance has a **"Delete on Termination"** flag
- This controls what happens to the volume when the EC2 instance is **terminated**

| Volume | Default Behavior | What It Means |
| --- | --- | --- |
| **Root volume** (`/dev/xvda` or `/dev/sda1`) | Delete on Termination = **✅ Enabled** | Volume is deleted when the instance is terminated |
| **Additional volumes** | Delete on Termination = **❌ Disabled** | Volume persists after instance termination |

```text
Instance Termination Behavior:

  EC2 Instance (terminated)
    ├── Root EBS Volume (8 GiB)    → 🗑️ DELETED (default)
    ├── EBS Volume B (100 GiB)     → 💾 PRESERVED (default)
    └── EBS Volume C (50 GiB)      → 💾 PRESERVED (default)
```

#### Modifying the Flag

- You can change this setting during **instance launch** or while the instance is running
- Common use case: **Disable** "Delete on Termination" on the root volume to preserve the OS disk even after terminating the instance (useful for data recovery)

```text
AWS Console → Launch Instance → Storage section:
  Root volume → Delete on Termination → Change to "No"

OR via CLI:
```

```bash
aws ec2 modify-instance-attribute \\
  --instance-id i-0abc123def456 \\
  --block-device-mappings '[{
    "DeviceName": "/dev/xvda",
    "Ebs": {"DeleteOnTermination": false}
  }]'
```

### 🆓 EBS and the Free Tier

- The AWS Free Tier includes **30 GiB** of EBS General Purpose (gp2/gp3) storage per month
- This is shared across all your EBS volumes in a region
- If you create a single `t2.micro` instance with an 8 GiB root volume, you have 22 GiB remaining for additional volumes

```text
Free Tier EBS Allocation:
  Total: 30 GiB/month of gp2/gp3 storage
  Root volume: 8 GiB  → 22 GiB remaining
```

### 🧩 EBS Volume in an EC2 Architecture

```text
            Availability Zone: us-east-1a
  ┌─────────────────────────────────────────────┐
  │                                             │
  │  ┌──────────────┐    ┌──────────────┐       │
  │  │  EC2 Inst. A  │◄──│ EBS Vol 1    │       │
  │  │               │   │ (root, gp3)  │       │
  │  │               │◄──│ EBS Vol 2    │       │
  │  └──────────────┘   │ (data, gp3)  │       │
  │                      └──────────────┘       │
  │                                             │
  │  ┌──────────────┐    ┌──────────────┐       │
  │  │  EC2 Inst. B  │◄──│ EBS Vol 3    │       │
  │  └──────────────┘   │ (root, gp3)  │       │
  │                      └──────────────┘       │
  │                                             │
  │                      ┌──────────────┐       │
  │                      │ EBS Vol 4    │       │
  │                      │ (unattached) │       │
  │                      └──────────────┘       │
  │                                             │
  └─────────────────────────────────────────────┘
```

- **Vol 1 & Vol 2** are attached to Instance A (multi-volume)
- **Vol 3** is attached to Instance B
- **Vol 4** exists but is **unattached** — ready to be mounted to any instance in `us-east-1a`

### 📸 Moving EBS Across AZs (Preview)

- Since volumes are locked to an AZ, you use **EBS Snapshots** to move data:

```text
Step 1: Create a snapshot of the volume in us-east-1a
Step 2: Create a new volume from the snapshot in us-east-1b
Step 3: Attach the new volume to an instance in us-east-1b

  us-east-1a                    us-east-1b
  ┌──────────┐   Snapshot    ┌──────────┐
  │ EBS Vol  │ ──────────►  │ EBS Vol  │ (restored copy)
  └──────────┘   (S3 backed) └──────────┘
```

> 💡 Snapshots are covered in detail in Lectures 47–48.

### 🆚 EBS vs Instance Store (Preview)

| Feature | EBS Volume | Instance Store |
| --- | --- | --- |
| **Persistence** | Data persists after stop/terminate | Data is **lost** when instance stops |
| **Network** | Network-attached (slight latency) | Physically attached (very high IOPS) |
| **Detachable** | Yes — can move between instances | No — tied to the physical host |
| **Use case** | Databases, boot volumes, persistent data | Caches, buffers, temporary scratch data |

> 💡 Instance Store is covered in Lecture 51.

### 🧠 Exam Tips & Key Takeaways

- EBS = **network-attached block storage** for EC2 — think "virtual hard drive"
- Volumes are **locked to a single AZ** — use snapshots to move across AZs or regions
- By default, the **root volume is deleted** on instance termination; additional volumes are **preserved**
- One EBS volume attaches to **one instance** at a time (except Multi-Attach io1/io2)
- One instance can have **multiple EBS volumes** attached
- You are billed for **provisioned capacity**, not actual usage
- Free Tier: **30 GiB** of gp2/gp3 per month
- EBS volumes have configurable **size, type, and IOPS** — volume types are covered in Lecture 52
- Network-attached = slight latency, but massive flexibility (detach, reattach, snapshot, resize)
- If an exam question mentions needing to **preserve data after instance termination** → EBS with "Delete on Termination" disabled

---

## Lecture 46: 🛠️ EBS Hands On

> **Section 6: EC2 Instance Storage** — Ultimate AWS Certified Developer Associate DVA-C02 2026

### 📌 Overview

- This hands-on lecture walks through creating, attaching, and managing EBS volumes in the AWS Console
- You'll see the root volume that comes with every EC2 instance, create a new standalone volume, attach it, and observe the "Delete on Termination" behavior
- These practical skills reinforce the EBS concepts from Lecture 45

### 🔍 Step 1: Viewing Existing EBS Volumes on Your Instance

#### Via the EC2 Instance Details

1. Navigate to **EC2 Dashboard** → **Instances** → select your running instance
1. Scroll down to the **Storage** tab
1. You'll see the **Block devices** section listing all attached EBS volumes

```text
Storage Tab — Block Devices:

  Device Name     Volume ID            Size     Status      Delete on Termination
  /dev/xvda       vol-0abc123def456    8 GiB    In-use      Yes
```

- `/dev/xvda` is the **root volume** — it contains the operating system
- **Delete on Termination = Yes** means this volume will be destroyed when you terminate the instance

#### Via the Volumes Dashboard

1. Click on the **Volume ID** link (e.g., `vol-0abc123def456`) to go directly to the volume
1. Or navigate to **EC2** → **Elastic Block Store** → **Volumes** in the left sidebar
1. Here you can see **all EBS volumes** in the current region

```text
Volumes Dashboard:

  Volume ID           Size    Type   AZ           State      Attached Instance
  vol-0abc123def456   8 GiB   gp3    us-east-1a   in-use     i-0abc123def456
```

### 🆕 Step 2: Creating a New EBS Volume

#### Walkthrough

1. Go to **EC2** → **Elastic Block Store** → **Volumes**
1. Click **Create volume**
1. Configure the following settings:

| Setting | Value | Notes |
| --- | --- | --- |
| **Volume Type** | General Purpose SSD (gp2) | Free Tier eligible; gp3 also works |
| **Size (GiB)** | 2 | Small size for testing |
| **Availability Zone** | us-east-1a | Must match your EC2 instance's AZ |
| **Encryption** | Not encrypted | Default for this demo |
| **Tags** | Name = "my-test-volume" | Optional but recommended |

1. Click **Create volume**

```text
New Volume Created:

  Volume ID:    vol-0xyz789ghi012
  Size:         2 GiB
  Type:         gp2
  AZ:           us-east-1a
  State:        available   ← Not attached to any instance yet
```

> ⚠️ **Critical**: The Availability Zone of the new volume must **exactly match** the AZ of the EC2 instance you want to attach it to. If your instance is in `us-east-1a`, the volume must also be in `us-east-1a`.

### 🔗 Step 3: Attaching the Volume to an Instance

1. Select the newly created volume (checkbox)
1. Click **Actions** → **Attach volume**
1. In the **Instance** dropdown, select your running EC2 instance
1. The **Device name** is auto-populated (e.g., `/dev/sdf` or `/dev/xvdf`)
1. Click **Attach volume**

```text
After Attachment:

  Volume ID           Size    State    Attached To          Device
  vol-0xyz789ghi012   2 GiB   in-use   i-0abc123def456     /dev/sdf
```

- The volume state changes from `available` to `in-use`
- It now appears in the instance's **Storage** tab alongside the root volume

#### What You'd See on the Instance (If You SSH In)

```bash
# List all block devices
lsblk

# Expected output:
NAME    MAJ:MIN RM SIZE RO TYPE MOUNTPOINT
xvda    202:0    0   8G  0 disk
└─xvda1 202:1    0   8G  0 part /
xvdf    202:80   0   2G  0 disk            ← New volume (not mounted yet)
```

> 💡 The volume is attached but **not mounted**. To use it, you'd need to format it and mount it to a directory. This is a Linux administration step, not covered in detail in this lecture.

#### Quick Mount Commands (For Reference)

```bash
# Create a filesystem on the new volume
sudo mkfs -t ext4 /dev/xvdf

# Create a mount point
sudo mkdir /data

# Mount the volume
sudo mount /dev/xvdf /data

# Verify
df -h | grep data
# Output: /dev/xvdf  2.0G  6.0M  1.9G  1% /data
```

### ❌ Step 4: Demonstrating Cross-AZ Limitation

- Try creating a volume in a **different AZ** (e.g., `us-east-1b`) while your instance is in `us-east-1a`
- When you attempt to attach it:

```text
Actions → Attach volume → Instance dropdown:

  ⚠️ Your instance does NOT appear in the dropdown!
  (Because the volume and instance are in different AZs)
```

- This confirms that EBS volumes are **locked to their Availability Zone**
- To move data across AZs, you must use **EBS Snapshots** (covered in Lectures 47–48)

### 🔌 Step 5: Detaching a Volume

1. Select the volume you want to detach
1. Click **Actions** → **Detach volume**
1. Confirm the detachment
1. The volume state changes back to `available`

```text
Before Detach:  vol-0xyz789ghi012 → State: in-use
After Detach:   vol-0xyz789ghi012 → State: available
```

- The volume still exists with all its data — it's just not connected to any instance
- You can reattach it to the same or a different instance (in the same AZ) at any time

> ⚠️ **Warning**: You should **unmount** the volume inside the OS before detaching it to avoid data corruption. For the root volume, you must stop the instance first.

### 🗑️ Step 6: Observing Delete on Termination

#### Check the Setting

- Go to your EC2 instance → **Storage** tab → look at the **Delete on Termination** column

```text
Block Devices:
  /dev/xvda (root)    → Delete on Termination: Yes ✅
  /dev/sdf  (extra)   → Delete on Termination: No  ❌
```

#### What Happens When You Terminate the Instance

1. Select the instance → **Instance State** → **Terminate instance**
1. After termination completes, go to **Volumes**

```text
After Instance Termination:

  vol-0abc123def456 (root, 8 GiB)    → 🗑️ DELETED (gone from the list)
  vol-0xyz789ghi012 (extra, 2 GiB)   → 💾 STILL EXISTS (state: available)
```

- The root volume was **automatically deleted** because Delete on Termination was enabled
- The additional volume **persists** because Delete on Termination was disabled by default

### 🧹 Step 7: Cleaning Up

- After the demo, delete any unused volumes to avoid ongoing charges:

1. Select the unattached volume
1. Click **Actions** → **Delete volume**
1. Confirm deletion

```text
⚠️ Always clean up unattached EBS volumes!
You are billed for provisioned EBS storage even if the volume is not attached.
```

### 💰 Cost Awareness

- EBS pricing is based on **provisioned capacity per month**
- Even **unattached** volumes incur charges

```text
Example gp3 pricing (us-east-1):
  $0.08 per GiB per month

  2 GiB volume for 30 days = 2 × $0.08 = $0.16/month
  8 GiB root volume for 30 days = 8 × $0.08 = $0.64/month
```

- The **Free Tier** provides 30 GiB of gp2/gp3 storage per month — stay within this to avoid charges

### 🧠 Exam Tips & Key Takeaways

- Every EC2 instance gets a **root EBS volume** by default — it contains the OS
- You can create and attach **additional volumes** for extra storage
- Volumes must be in the **same AZ** as the instance — cross-AZ attachment is impossible
- The root volume has **Delete on Termination = Yes** by default; additional volumes have it set to **No**
- After terminating an instance, check for **orphaned volumes** to avoid unnecessary costs
- Volumes in the `available` state are **not attached** to any instance but still cost money
- To use a new volume on Linux, you must **format** it (`mkfs`) and **mount** it — attaching alone is not enough
- You can **detach** and **reattach** volumes freely within the same AZ without data loss

---

## Lecture 47: 📸 EBS Snapshots

> **Section 6: EC2 Instance Storage** — Ultimate AWS Certified Developer Associate DVA-C02 2026

### 📌 Overview

- An EBS Snapshot is a **point-in-time backup** of an EBS volume
- Snapshots are the primary mechanism for **migrating data** across Availability Zones and Regions
- They are stored in **Amazon S3** behind the scenes (though you never interact with the S3 bucket directly)
- Understanding snapshots is essential for disaster recovery, data migration, and volume management

### 📷 What Is an EBS Snapshot?

- A snapshot captures the **exact state** of an EBS volume at the moment the snapshot is taken
- It records only the **blocks that have data** — empty space is not stored
- Subsequent snapshots are **incremental** — only the blocks that have changed since the last snapshot are saved

```text
Snapshot Lifecycle:

  EBS Volume (100 GiB, 40 GiB used)
       │
       ▼
  Snapshot 1: Captures 40 GiB of data blocks
       │
       │  (You write 5 GiB of new data)
       ▼
  Snapshot 2: Captures only the 5 GiB that changed (incremental)
```

> 💡 Even though snapshots are incremental, each snapshot is **self-contained** — you can restore a full volume from any single snapshot. AWS manages the chain of incremental blocks internally.

### 🔑 Key Properties of EBS Snapshots

- **Not required** to detach a volume before snapshotting — but **recommended** for data consistency
- Snapshots are stored in **S3** (AWS-managed, not visible in your S3 console)
- Snapshots are **regional** — they exist within the region where the volume lives
- You can **copy** a snapshot to another region for cross-region disaster recovery
- You can **create a new volume** from a snapshot in **any AZ** within the region

```text
Cross-AZ Migration via Snapshots:

  us-east-1a                              us-east-1b
  ┌──────────┐                            ┌──────────┐
  │ EBS Vol  │ ──► Snapshot ──► Restore ──►│ EBS Vol  │
  │ (source) │     (regional)              │  (copy)  │
  └──────────┘                            └──────────┘
```

### 🌍 Cross-Region Snapshot Copy

- Snapshots can be **copied to a different AWS region** entirely
- This enables **cross-region disaster recovery** and data migration

```text
Cross-Region Migration:

  us-east-1                    eu-west-1
  ┌──────────┐                ┌──────────┐
  │ Snapshot │ ──── Copy ───► │ Snapshot │ ──► Restore ──► New EBS Volume
  └──────────┘  (across       └──────────┘                in eu-west-1
                 regions)
```

- Use cases:

    - **Disaster recovery** — keep backups in a geographically separate region
    - **Migration** — move workloads from one region to another
    - **Compliance** — store backups in a specific geography

### ♻️ EBS Snapshot Recycle Bin

- When you delete a snapshot, it's gone **permanently** by default
- The **Recycle Bin** feature allows you to set up **retention rules** to protect against accidental deletion
- Deleted snapshots go to the Recycle Bin and can be **recovered** within the retention period

```text
Recycle Bin Flow:

  Snapshot ──► Delete ──► Recycle Bin (retained for X days) ──► Permanent Deletion
                              │
                              └──► Recover (if within retention period)
```

#### Retention Rules

- You create a **retention rule** specifying how long deleted snapshots should be kept
- Retention period can range from **1 day to 1 year**
- Rules can apply to **all snapshots** or only those matching specific **tags**

| Setting | Options |
| --- | --- |
| **Resource type** | EBS Snapshots (or AMIs) |
| **Retention period** | 1 day to 365 days |
| **Tag filters** | Optional — target specific snapshots by tag |
| **Rule lock** | Optional — prevent the rule from being modified or deleted |

### ⚡ EBS Snapshot Archive

- By default, snapshots are stored in the **Standard tier** — instant restore
- You can move a snapshot to the **Archive tier** for **75% cheaper storage**
- Trade-off: restoring from archive takes **24 to 72 hours**

```text
Snapshot Storage Tiers:

  Standard Tier                         Archive Tier
  ┌──────────────────┐                 ┌──────────────────┐
  │ • Instant restore │  ──── Move ──► │ • 75% cheaper     │
  │ • Higher cost     │                │ • 24–72hr restore │
  └──────────────────┘                 └──────────────────┘
```

- **Best for**: Long-term backups that you rarely need to access (compliance archives, quarterly backups)
- **Not suitable for**: Snapshots you might need to restore quickly for disaster recovery

### 🔄 Fast Snapshot Restore (FSR)

- By default, when you create a volume from a snapshot, the data is loaded **lazily** — blocks are fetched from S3 as they are accessed
- This can cause **latency on first access** (the "first touch penalty")
- **Fast Snapshot Restore (FSR)** eliminates this latency by **pre-initializing** the volume with all snapshot data
- The volume is fully provisioned at creation — no performance hit on first read

| Feature | Without FSR | With FSR |
| --- | --- | --- |
| **First access latency** | High (blocks loaded on demand) | None (fully initialized) |
| **Volume ready time** | Instant, but slow first reads | Instant with full performance |
| **Cost** | Standard snapshot cost | **Very expensive** — charged per AZ per hour |

- FSR is enabled **per snapshot, per AZ**
- Pricing example: roughly **$0.75/hour per AZ** per enabled snapshot

> ⚠️ FSR is **costly** — use it only for critical production workloads where first-read latency is unacceptable (e.g., database volumes that must perform immediately after restore).

### 📊 Snapshot Summary Diagram

```text
                    ┌──────────────────────────┐
                    │       EBS Volume          │
                    │     (us-east-1a)          │
                    └──────────┬───────────────┘
                               │
                          Create Snapshot
                               │
                    ┌──────────▼───────────────┐
                    │     EBS Snapshot          │
                    │   (Regional, in S3)       │
                    └──┬──────┬──────┬─────────┘
                       │      │      │
              ┌────────┘      │      └────────┐
              ▼               ▼               ▼
     Create Volume      Copy to Region    Archive
     (any AZ in         (e.g., eu-west-1)  (75% cheaper,
      the region)                          24-72hr restore)
              │               │
              ▼               ▼
     New EBS Volume     Snapshot in
     (us-east-1b)      eu-west-1
                              │
                              ▼
                       New EBS Volume
                       (eu-west-1a)
```

### 💻 CLI Commands for Snapshots

```bash
# Create a snapshot of an EBS volume
aws ec2 create-snapshot \\
  --volume-id vol-0abc123def456 \\
  --description "Backup before migration"

# Copy a snapshot to another region
aws ec2 copy-snapshot \\
  --source-region us-east-1 \\
  --source-snapshot-id snap-0abc123def456 \\
  --destination-region eu-west-1 \\
  --description "DR copy in EU"

# Create a volume from a snapshot in a specific AZ
aws ec2 create-volume \\
  --snapshot-id snap-0abc123def456 \\
  --availability-zone us-east-1b \\
  --volume-type gp3

# Delete a snapshot
aws ec2 delete-snapshot \\
  --snapshot-id snap-0abc123def456

# List all snapshots owned by your account
aws ec2 describe-snapshots --owner-ids self
```

### 🧠 Exam Tips & Key Takeaways

- Snapshots are **point-in-time backups** of EBS volumes stored in S3 (AWS-managed)
- Snapshots are **incremental** — only changed blocks are stored after the first snapshot
- You don't need to detach a volume to snapshot it, but it's **recommended** for consistency
- Snapshots unlock **cross-AZ** and **cross-region** data migration
- **Recycle Bin** protects against accidental snapshot deletion with configurable retention (1 day – 1 year)
- **Snapshot Archive** saves 75% on storage but takes 24–72 hours to restore
- **Fast Snapshot Restore (FSR)** eliminates first-read latency but is **very expensive**
- For the exam: "move an EBS volume to another AZ" → **snapshot it, then create a new volume from the snapshot in the target AZ**
- For the exam: "move data to another region" → **copy the snapshot to the target region, then restore**
- Snapshot pricing: you pay for the **actual data stored** (not the full volume size), plus any archive or FSR charges

---

## Lecture 48: 📸 EBS Snapshots - Hands On

> **Section 6: EC2 Instance Storage** \| Ultimate AWS Certified Developer Associate DVA-C02 2026

### 📋 Overview

> This hands-on lecture walks through the practical steps of creating, managing, copying, and restoring EBS Snapshots in the AWS Console. You'll learn how to snapshot a volume, move it across Availability Zones, set up the EBS Snapshot Recycle Bin for accidental deletion recovery, and create an EBS Snapshot Archive for cost savings.

### 🔧 Creating an EBS Snapshot

- Navigate to **EC2 → Elastic Block Store → Volumes** in the AWS Console
- Select the EBS volume you want to snapshot
- Click **Actions → Create Snapshot**
- Add a **Description** (e.g., `demo snapshot`) to identify it later
- Click **Create Snapshot**
- Navigate to **EC2 → Elastic Block Store → Snapshots** to view your snapshot
- The snapshot will transition from `pending` to `completed` status

```bash
# You can also create a snapshot via CLI
aws ec2 create-snapshot \\
  --volume-id vol-0123456789abcdef0 \\
  --description "demo snapshot"
```

#### 🔑 Key Details

- The snapshot captures the **point-in-time state** of the volume
- Snapshots are stored in **Amazon S3** (managed by AWS, not visible in your S3 buckets)
- You can continue using the volume while the snapshot is being created
- Each snapshot gets a unique **Snapshot ID** (e.g., `snap-0abc123def456`)

### 🔄 Restoring a Snapshot (Create Volume from Snapshot)

- Go to **EC2 → Snapshots**
- Select your snapshot
- Click **Actions → Create Volume from Snapshot**
- Choose the **Volume Type** (e.g., `gp2`, `gp3`, `io1`)
- Choose the **Availability Zone** — this is where you can move data across AZs

    - If your original volume was in `us-east-1a`, you can now create the new volume in `us-east-1b`
- Set the **Size** (can be equal to or larger than the original)
- Click **Create Volume**

```bash
# CLI equivalent
aws ec2 create-volume \\
  --snapshot-id snap-0abc123def456 \\
  --availability-zone us-east-1b \\
  --volume-type gp3
```

> **💡 Exam Tip**: Creating a volume from a snapshot in a different AZ is the standard way to **migrate an EBS volume across Availability Zones**. You snapshot it, then restore it in the target AZ.

### 🌍 Copying Snapshots Across Regions

- Select the snapshot in the console
- Click **Actions → Copy Snapshot**
- Choose a **Destination Region** (e.g., `eu-west-1`)
- Optionally enable **encryption** during the copy
- Click **Copy Snapshot**
- Navigate to the destination region's **Snapshots** section to see the copied snapshot

```bash
# CLI equivalent
aws ec2 copy-snapshot \\
  --source-region us-east-1 \\
  --source-snapshot-id snap-0abc123def456 \\
  --destination-region eu-west-1 \\
  --description "Cross-region copy"
```

> **💡 Exam Tip**: Copying a snapshot to another region is the method to **migrate EBS data across AWS Regions**. This is also how you set up **disaster recovery** for EBS volumes.

### 🗑️ EBS Snapshot Recycle Bin

The Recycle Bin protects against **accidental deletion** of EBS snapshots by retaining deleted snapshots for a configurable period.

#### Setting Up a Retention Rule

- Navigate to **EC2 → Snapshots → Recycle Bin** (or search for "Recycle Bin" in the console)
- Click **Create Retention Rule**
- Configure the rule:

    - **Name**: e.g., `demo-retention-rule`
    - **Resource Type**: Select `EBS Snapshots`
    - **Retention Period**: Set the duration (e.g., `1 day`)
    - **Resource Tags** (optional): Apply only to snapshots with specific tags, or leave empty for all snapshots
    - **Rule Lock Settings**: Optionally lock the rule to prevent modification
- Click **Create Retention Rule**

#### Testing the Recycle Bin

1. **Delete a snapshot** — select your snapshot → **Actions → Delete Snapshot**
1. Go to the **Recycle Bin → Resources** section
1. Your deleted snapshot will appear here with a **retention expiry date**
1. To recover it, select the snapshot → click **Recover Resources**
1. The snapshot reappears in your regular **Snapshots** list

```bash
# CLI: Create a retention rule
aws rbin create-rule \\
  --retention-period RetentionPeriodValue=1,RetentionPeriodUnit=DAYS \\
  --resource-type EBS_SNAPSHOT \\
  --description "Retain deleted snapshots for 1 day"

# CLI: List resources in recycle bin
aws rbin list-rules --resource-type EBS_SNAPSHOT
```

> **⚠️ Important**: If no retention rule is set, deleted snapshots are **permanently removed immediately** and cannot be recovered.

### 📦 EBS Snapshot Archive

The Snapshot Archive tier offers up to **75% cheaper** storage for snapshots you rarely need but want to keep long-term.

#### Moving a Snapshot to Archive

- Select the snapshot in the console
- Click **Actions → Archive Snapshot**
- Confirm the archive operation
- The snapshot's **Storage Tier** changes from `standard` to `archive`

#### Restoring from Archive

- Select the archived snapshot
- Click **Actions → Restore Snapshot** (or create a volume from it)
- Restoration takes **24 to 72 hours** — this is NOT instant
- Once restored, the snapshot returns to the `standard` tier

```bash
# CLI: Archive a snapshot
aws ec2 modify-snapshot-tier \\
  --snapshot-id snap-0abc123def456 \\
  --storage-tier archive

# CLI: Restore from archive
aws ec2 restore-snapshot-tier \\
  --snapshot-id snap-0abc123def456
```

> **💡 Exam Tip**: Archive is ideal for **compliance snapshots** or backups you must retain but don't need quick access to. Remember the **24–72 hour restore time** — this is a common exam question.

### 📊 Summary of Hands-On Actions

| Action | Where in Console | Key Notes |
| --- | --- | --- |
| Create Snapshot | Volumes → Actions → Create Snapshot | Point-in-time backup to S3 |
| Create Volume from Snapshot | Snapshots → Actions → Create Volume | Can change AZ, type, and size |
| Copy Snapshot | Snapshots → Actions → Copy Snapshot | Enables cross-region migration |
| Recycle Bin Setup | Recycle Bin → Create Retention Rule | Protects against accidental deletion |
| Archive Snapshot | Snapshots → Actions → Archive Snapshot | 75% cheaper, 24–72h restore |

### 🧹 Cleanup Steps

- **Delete any volumes** created from snapshots that you no longer need (you are charged for provisioned EBS volumes)
- **Delete snapshots** you no longer need (standard tier snapshots incur storage costs)
- **Delete Recycle Bin retention rules** if you don't want to retain deleted snapshots
- **Check for archived snapshots** — archived snapshots still incur (reduced) storage costs

### ✅ Key Takeaways

- EBS Snapshots are the primary mechanism for **backing up**, **migrating**, and **restoring** EBS volumes
- You can move volumes across **Availability Zones** and **Regions** using snapshots
- The **Recycle Bin** provides a safety net against accidental snapshot deletion with configurable retention
- **Snapshot Archive** reduces storage costs by 75% but has a 24–72 hour restore window
- Snapshots are **incremental** — only changed blocks are saved after the first snapshot, keeping costs low
- Always clean up unused snapshots and volumes to avoid unnecessary charges

---

## Lecture 49: 🖼️ AMI Overview

> **Section 6: EC2 Instance Storage** \| Ultimate AWS Certified Developer Associate DVA-C02 2026

### 📋 Overview

> An **AMI (Amazon Machine Image)** is a customization of an EC2 instance. It's a pre-configured template that packages the operating system, application software, configurations, and launch settings needed to spin up instances. AMIs are fundamental to how EC2 works and are a heavily tested topic on the DVA-C02 exam.

### 🔍 What Exactly is an AMI?

- **AMI = Amazon Machine Image**
- Every single EC2 instance you launch is based on an AMI — even when you pick "Amazon Linux 2" from the console, that's an AMI
- An AMI packages together:

    - A **root volume template** (OS + pre-installed software)
    - **Launch permissions** controlling which AWS accounts can use it
    - **Block device mappings** specifying which EBS volumes to attach at launch
- Each AMI has a unique **AMI ID** (e.g., `ami-0abcdef1234567890`) that is specific to a region

### 🏗️ Why Build Custom AMIs?

> The primary motivation is **speed and consistency**. Instead of running a 10-minute User Data bootstrap script on every new instance, you bake everything into an AMI once and launch pre-configured instances in seconds.

#### 🐢 Without a Custom AMI

```bash
#!/bin/bash
# User Data script — runs at EVERY instance launch
yum update -y
yum install -y httpd php mysql-server
systemctl start httpd
systemctl enable httpd
# Install monitoring agents...
# Download application code from S3...
# Apply security patches...
# Total time: 5-10 minutes before the instance is usable
```

#### 🚀 With a Custom AMI

```text
1. Launch one EC2 instance
2. Run your setup (install software, configure, harden)
3. Create an AMI from that instance
4. All future launches from this AMI → ready in ~30 seconds!
```

#### 🎯 Key Benefits

- **Faster boot / configuration time** — software is pre-packaged, no runtime installation
- **Consistent environments** — every instance from the same AMI is identical (no configuration drift)
- **Security hardening** — pre-bake firewall rules, security agents, and OS patches
- **Auto Scaling friendly** — ASGs can launch fully-configured instances rapidly during scale-out events
- **Disaster recovery** — AMIs serve as golden images you can redeploy anywhere

> **💡 Exam Tip**: When the exam mentions "reducing instance launch time" or "ensuring all instances in an ASG have identical configurations," the answer is almost always **create a custom AMI** (sometimes called a "Golden AMI").

### 🌍 AMI Region Scope

- AMIs are **region-specific resources** — an AMI built in `us-east-1` only exists in `us-east-1`
- You **cannot** directly launch an instance in `eu-west-1` using an AMI from `us-east-1`
- To use an AMI in another region, you must **copy** it:

```bash
# Copy an AMI from us-east-1 to eu-west-1
aws ec2 copy-image \\
  --source-region us-east-1 \\
  --source-image-id ami-0abc123def456 \\
  --name "My App AMI - EU Copy" \\
  --region eu-west-1

# The copy gets a NEW AMI ID in the destination region
# e.g., ami-0xyz789ghi012 in eu-west-1
```

- The underlying **EBS snapshots** are also copied to the destination region
- This is the standard approach for **multi-region deployments** and **disaster recovery**

### 📦 Three Sources of AMIs

| Source | Description | Examples |
| --- | --- | --- |
| **AWS-provided (Public)** | Maintained by Amazon, regularly patched | Amazon Linux 2023, Ubuntu, Windows Server, Red Hat |
| **AWS Marketplace** | Published by third-party vendors, may carry additional license fees | Cisco firewalls, Splunk, custom Kubernetes distros |
| **Custom (Your Own)** | Created by you from your configured EC2 instances | Your hardened app server, your golden image |

#### 🟢 AWS-Provided AMIs

- Free to use (you pay only for the EC2 instance and storage)
- Always up-to-date with latest security patches
- Great starting point before building your own custom AMI

#### 🔵 AWS Marketplace AMIs

- Come with pre-installed **commercial software**
- Pricing model: EC2 cost + software license fee (billed per hour or via contract)
- Useful when you need enterprise software without manual installation

#### 🟠 Your Own Custom AMIs

- **Private by default** — only visible to your AWS account
- Can be **shared** with specific accounts or made **public**
- You are responsible for patching and maintaining them

### 🔄 AMI Creation Process (Lifecycle)

```text
┌──────────────┐     ┌──────────────┐     ┌──────────────┐
│  Launch EC2  │────▶│  Customize   │────▶│ Stop Instance│
│  Instance    │     │  (install,   │     │ (data        │
│              │     │   configure) │     │  integrity)  │
└──────────────┘     └──────────────┘     └──────┬───────┘
                                                 │
                                                 ▼
┌──────────────┐     ┌──────────────┐     ┌──────────────┐
│ Launch new   │◀────│  AMI is      │◀────│ Create AMI   │
│ instances    │     │  available!  │     │ (EBS snapshot │
│ from AMI     │     │              │     │  is created) │
└──────────────┘     └──────────────┘     └──────────────┘
```

1. **Launch** a base EC2 instance (from an AWS-provided AMI)
1. **Customize** it — install software, apply patches, configure settings
1. **Stop** the instance (recommended for data integrity, though not strictly required)
1. **Create AMI** — AWS takes EBS snapshots of attached volumes and registers the image
1. **Launch** new instances from your custom AMI — they come up fully configured

> **⚠️ Important**: You can create an AMI from a running instance (without stopping it), but stopping first guarantees a **consistent filesystem state**. For production golden images, always stop first.

### 🔐 AMI Sharing and Permissions

- **Private** (default): Only your AWS account can see and use the AMI
- **Shared with specific accounts**: You grant launch permissions to other AWS account IDs
- **Public**: Anyone with an AWS account can find and use the AMI
- When sharing an AMI backed by **encrypted EBS snapshots**, you must also share the KMS key used for encryption

```bash
# Share an AMI with another AWS account
aws ec2 modify-image-attribute \\
  --image-id ami-0abc123def456 \\
  --launch-permission "Add=[{UserId=123456789012}]"
```

### 🆚 AMI vs EBS Snapshot

| Feature | AMI | EBS Snapshot |
| --- | --- | --- |
| **What it captures** | Full instance blueprint (OS, volumes, permissions, metadata) | Single EBS volume at a point in time |
| **Can launch an instance?** | ✅ Yes, directly | ❌ No — must create a volume first, then attach |
| **Includes boot config?** | ✅ Yes (kernel, boot loader, block device mapping) | ❌ No |
| **Contains snapshots?** | ✅ Internally references one or more EBS snapshots | N/A — it IS the snapshot |

> **💡 Exam Tip**: An AMI is NOT just a snapshot. It's a snapshot + metadata + launch configuration. You can create a volume from a snapshot, but you can only **launch an instance** from an AMI.

### ✅ Key Takeaways

- AMIs are the **foundation** for launching any EC2 instance — every instance requires one
- Custom AMIs provide **faster boot times** and **consistent configurations** vs. User Data scripts
- AMIs are **region-scoped** — copy them to use in other regions
- Three AMI sources: **AWS-provided**, **Marketplace**, and **Custom**
- The lifecycle is: Launch → Customize → Stop → Create AMI → Launch from AMI
- AMIs internally contain **EBS snapshots** but add launch metadata on top
- Custom AMIs are **private by default** but can be shared or made public

---

## Lecture 50: 🛠️ AMI Hands On

> **Section 6: EC2 Instance Storage** \| Ultimate AWS Certified Developer Associate DVA-C02 2026

### 📋 Overview

> This hands-on lecture demonstrates the complete workflow of creating a custom AMI from an existing EC2 instance and launching a brand-new instance from that AMI. You'll see firsthand how pre-baking software into an AMI eliminates the need for User Data scripts and dramatically reduces instance startup time.

### 🚀 Step 1: Prepare the Source EC2 Instance

- You should already have a running EC2 instance from previous lectures (with Apache httpd installed via User Data)
- If not, launch a new **Amazon Linux 2** instance with this User Data script:

```bash
#!/bin/bash
yum update -y
yum install -y httpd
systemctl start httpd
systemctl enable httpd
echo "<h1>Hello World from $(hostname -f)</h1>" > /var/www/html/index.html
```

- Verify the instance is running and the web server is accessible by visiting its **public IPv4 address** in your browser
- You should see the "Hello World" page confirming Apache is installed and running

### 📸 Step 2: Create an AMI from the Instance

#### In the AWS Console

1. Go to **EC2 → Instances**
1. Select your running instance (check the box next to it)
1. Click **Actions → Image and templates → Create image**
1. Fill in the details:

    - **Image name**: `DemoImage` (or any descriptive name)
    - **Image description**: (optional) e.g., `Amazon Linux 2 with Apache httpd pre-installed`
    - **No reboot**: Leave **unchecked** (default) — AWS will stop the instance temporarily to ensure data consistency
    - **Instance volumes**: Review the attached EBS volumes (these will be snapshotted)
1. Click **Create image**

```bash
# CLI equivalent
aws ec2 create-image \\
  --instance-id i-0abc123def456 \\
  --name "DemoImage" \\
  --description "Amazon Linux 2 with Apache httpd" \\
  --no-reboot
```

> **⚠️ Note on "No reboot"**: When left unchecked (default behavior), AWS will **stop and restart** the instance during AMI creation to guarantee filesystem integrity. If you check "No reboot," the AMI is created without stopping the instance, but data consistency is not guaranteed.

### ⏳ Step 3: Monitor AMI Creation

1. Navigate to **EC2 → AMIs** (under "Images" in the left sidebar)
1. You'll see your new AMI with status **pending**
1. Wait until the status changes to **available** — this can take a few minutes
1. Notice the details panel shows:

    - **AMI ID** (e.g., `ami-0abc123def456`)
    - **Source instance** ID
    - **Block device mappings** (the EBS snapshot that was created)
    - **Owner** (your AWS account ID)

#### Check the Associated Snapshot

- Go to **EC2 → Elastic Block Store → Snapshots**
- You'll find a new snapshot that was automatically created as part of the AMI
- This snapshot contains the exact state of the root EBS volume at the time of image creation

### 🖥️ Step 4: Launch a New Instance from Your Custom AMI

1. Go to **EC2 → AMIs**
1. Select your newly created AMI
1. Click **Launch instance from AMI**
1. Configure the instance:

    - **Name**: e.g., `From My AMI`
    - **Instance type**: `t2.micro`
    - **Key pair**: Select your existing key pair
    - **Security Group**: Select a group that allows **SSH (22)** and **HTTP (80)**
    - **User Data**: Leave **completely empty** — the whole point is that Apache is already baked in!
1. Click **Launch instance**

```bash
# CLI equivalent — notice no --user-data flag needed
aws ec2 run-instances \\
  --image-id ami-0abc123def456 \\
  --instance-type t2.micro \\
  --key-name my-key-pair \\
  --security-group-ids sg-0abc123 \\
  --count 1
```

### ✅ Step 5: Verify the New Instance

1. Wait for the new instance to reach **running** state
1. Copy the **public IPv4 address** of the new instance
1. Open it in your browser: `http://<public-ip>`
1. You should see the **"Hello World"** page immediately — **without any User Data script**!

> **🎉 Key Observation**: The new instance launched from your custom AMI already has Apache httpd installed, enabled, and serving the web page. No bootstrap script was needed — the software was pre-baked into the AMI. This is significantly faster than running User Data on every launch.

### 🌍 Step 6: Copy AMI to Another Region (Optional)

1. Go to **EC2 → AMIs**
1. Select your AMI
1. Click **Actions → Copy AMI**
1. Choose a **Destination Region** (e.g., `eu-west-1 (Ireland)`)
1. Provide a name and optional description
1. Optionally check **Encrypt target EBS snapshots** to add encryption during the copy
1. Click **Copy AMI**
1. Switch to the destination region in the console to see the copied AMI (it will have a new AMI ID)

```bash
aws ec2 copy-image \\
  --source-region us-east-1 \\
  --source-image-id ami-0abc123def456 \\
  --name "DemoImage-EU-Copy" \\
  --region eu-west-1
```

### 🗑️ Step 7: Deregister an AMI

- When you no longer need a custom AMI, you should **deregister** it to stop storage charges

1. Go to **EC2 → AMIs**
1. Select the AMI
1. Click **Actions → Deregister AMI**
1. Confirm the deregistration

- **Important**: Deregistering the AMI does **NOT** automatically delete the underlying EBS snapshot
- Navigate to **Snapshots** and manually delete the associated snapshot to avoid continued storage costs

```bash
# Deregister the AMI
aws ec2 deregister-image --image-id ami-0abc123def456

# Then delete the orphaned snapshot
aws ec2 delete-snapshot --snapshot-id snap-0abc123def456
```

### 🧹 Cleanup

- **Terminate** the instance launched from your custom AMI (if no longer needed)
- **Deregister** the AMI if you're done experimenting
- **Delete the associated EBS snapshot** after deregistering the AMI
- Keep or terminate the original source instance based on your needs for upcoming lectures

### 📊 Before vs After Comparison

| Aspect | Without Custom AMI | With Custom AMI |
| --- | --- | --- |
| **User Data script** | Required on every launch | Not needed |
| **Boot-to-ready time** | 5–10 minutes (install + configure) | ~30 seconds |
| **Consistency** | Risk of drift if script changes | Identical every time |
| **ASG scale-out speed** | Slow — each new instance runs full setup | Fast — instances are pre-configured |

### ✅ Key Takeaways

- Creating a custom AMI captures your fully-configured instance as a reusable template
- The AMI creation process automatically takes an **EBS snapshot** of all attached volumes
- Instances launched from a custom AMI need **no User Data** — everything is pre-installed
- AMIs are **region-specific** but can be copied across regions via the console or CLI
- Always **deregister** unused AMIs and **delete** their associated snapshots to avoid unnecessary charges
- The "No reboot" option trades data consistency for zero downtime during AMI creation

---

## Lecture 51: 💾 EC2 Instance Store

> **Section 6: EC2 Instance Storage** — Ultimate AWS Certified Developer Associate DVA-C02 2026

### 🔍 What is EC2 Instance Store?

- An **EC2 Instance Store** provides **temporary, high-performance block-level storage** for your EC2 instance
- Unlike **EBS** (which is a **network drive**), Instance Store volumes are **physically attached** to the host computer on which the instance runs
- Because the disk is directly attached to the hardware, it provides **significantly better I/O performance** than network-attached EBS volumes
- Instance Store storage is sometimes referred to as **ephemeral storage** — the data does **not persist** across instance lifecycle events (except reboot)

> 💡 Think of Instance Store as a **local hard drive** inside the physical server your EC2 instance is running on — blazingly fast, but not designed for long-term storage.

### ⚡ Performance Characteristics

- Instance Store provides **very high IOPS** (Input/Output Operations Per Second) because it avoids the network overhead of EBS
- Some Instance Store-backed instances offer **NVMe SSD** drives for ultra-low latency
- Performance varies by instance type — storage-optimized instances like **i3** and **i3en** families can deliver extreme throughput:

| Instance Type | NVMe SSD Storage | Approx. Random Read IOPS |
| --- | --- | --- |
| `i3.large` | 1 x 475 GB | ~100,000 |
| `i3.xlarge` | 1 x 950 GB | ~206,250 |
| `i3.2xlarge` | 1 x 1,900 GB | ~412,500 |
| `i3.4xlarge` | 2 x 1,900 GB | ~825,000 |
| `i3.8xlarge` | 4 x 1,900 GB | ~1,650,000 |
| `i3.16xlarge` | 8 x 1,900 GB | ~3,300,000 |

- For comparison, the **highest-performing EBS volume** (`io2 Block Express`) tops out at **256,000 IOPS**
- Instance Store can deliver **millions of IOPS**, making it ideal for workloads that need extreme throughput

> ⚠️ **Exam Tip:** If a question mentions needing the **highest possible disk IOPS** or **best I/O performance**, think **EC2 Instance Store** — not EBS.

### 🔄 Data Persistence — The Ephemeral Rule

- This is the **most critical concept** for the exam regarding Instance Store
- Instance Store is **ephemeral** — the data lifecycle is directly tied to the instance

| Scenario | Does Data Persist? |
| --- | --- |
| ✅ **Reboot** the instance | **Yes** — data survives |
| ❌ **Stop** the instance | **No** — data is **lost** |
| ❌ **Terminate** the instance | **No** — data is **lost** |
| ❌ **Hibernate** the instance | **No** — data is **lost** |
| ❌ **Underlying hardware failure** | **No** — data is **lost** |

> 🚨 **Key Rule:** If you stop or terminate an EC2 instance that has Instance Store volumes, all data on those volumes is **permanently erased**. Only a **reboot** preserves the data.

### 🛡️ Risk, Backup & Responsibility

- Since Instance Store data can be lost at any time due to hardware failure, **you are responsible** for:

    - **Replication** — Replicate data across multiple instances if fault tolerance is needed
    - **Backups** — Regularly back up critical data to durable storage (e.g., Amazon S3 or EBS)
- Instance Store does **NOT support snapshots** like EBS does
- There is no built-in redundancy — if the physical disk fails, data is gone

```bash
# Example: Manually backing up instance store data to S3
aws s3 sync /mnt/instance-store-data s3://my-backup-bucket/instance-store-backup/
```

### 🆚 Instance Store vs EBS — Comparison

| Feature | EC2 Instance Store | Amazon EBS |
| --- | --- | --- |
| **Type** | Physically attached (local) | Network-attached (remote) |
| **Persistence** | ❌ Ephemeral (lost on stop/terminate) | ✅ Persistent (independent lifecycle) |
| **Performance** | ⚡ Very high (millions of IOPS) | 🔄 Good (up to 256K IOPS on io2 BE) |
| **Latency** | Ultra-low (no network hop) | Low (but involves network) |
| **Snapshots** | ❌ Not supported | ✅ Supported (backed by S3) |
| **Attach/Detach** | ❌ Only at launch time | ✅ Can attach/detach anytime |
| **Cost** | Included in instance price | Billed separately |
| **Resize** | ❌ Cannot resize | ✅ Can resize (Elastic Volumes) |
| **Boot Volume** | ❌ Cannot be a root/boot volume | ✅ Can be a root/boot volume |
| **Encryption** | ✅ Supported (hardware-level) | ✅ Supported (KMS integration) |
| **Best For** | Caches, buffers, scratch data, HPC | Databases, boot volumes, durability |

### 🎯 Ideal Use Cases for Instance Store

- **Buffer / Cache / Scratch Data** — Temporary data that is frequently read/written and can be regenerated
- **Temporary Content** — Media processing scratch space, video transcoding intermediate files
- **High-Performance Computing (HPC)** — Distributed workloads like Hadoop, Spark where data is replicated across a cluster
- **High-Performance Databases** — In-memory databases or NoSQL databases (e.g., Cassandra) that handle replication at the application level
- **Load-Balanced Web Servers** — Where session data or local caches can be lost without impacting the overall application

### 🧠 Important Details for the Exam

- **Not all instance types** come with Instance Store — it depends on the instance family and size
- Instance Store volumes **must be specified at launch time** — you cannot attach them to a running instance later
- The **number and size** of available Instance Store volumes depends on the instance type you choose
- Instance Store volumes are **not listed under the EBS section** in the AWS Console — they appear in the instance's block device mapping
- If an instance type supports Instance Store, the volumes are **automatically available** — no additional provisioning is needed
- Instance Store is **free** — the cost is included in the price of the EC2 instance itself

```bash
# Check available instance store volumes on a running instance
lsblk

# Example output showing both EBS and Instance Store volumes:
# NAME    MAJ:MIN RM   SIZE RO TYPE MOUNTPOINT
# xvda    202:0    0     8G  0 disk              <-- EBS root volume
# nvme0n1 259:0    0 475.8G  0 disk              <-- Instance Store (NVMe)
```

### 📝 Key Takeaways

- EC2 Instance Store = **physically attached**, **ephemeral**, **high-performance** block storage
- Data is **lost** on stop, terminate, hibernate, or hardware failure — only survives a **reboot**
- Delivers the **highest I/O performance** of any EC2 storage option (millions of IOPS)
- **You** are responsible for backups, replication, and fault tolerance
- Best suited for **caches, buffers, scratch data**, and **temporary processing workloads**
- Cannot be used as a **boot volume** — always need EBS for that
- No snapshots, no detach/reattach, no resizing — it's tied to the instance lifecycle

---

## Lecture 52: 📦 EBS Volume Types

> **Section 6: EC2 Instance Storage** — Ultimate AWS Certified Developer Associate DVA-C02 2026

### 🔍 Overview

- EBS Volumes come in **6 types**, split into two categories: **SSD-based** and **HDD-based**
- EBS Volumes are characterized by **Size**, **Throughput**, and **IOPS** (I/O Operations Per Second)
- Only **SSD volumes** (gp2, gp3, io1, io2) can be used as **boot volumes** for EC2 instances
- **HDD volumes** (st1, sc1) **cannot** be boot volumes — they are designed for data workloads only

> 💡 For the exam, you need to understand **when to use which volume type** based on the workload requirements described in the question.

### 🟢 General Purpose SSD (gp2 & gp3)

- Cost-effective storage that balances **price and performance**
- Suitable for a wide variety of workloads

#### 🔹 gp3 — Current Generation (Recommended)

- **Baseline performance:** 3,000 IOPS and 125 MiB/s throughput — included **regardless of volume size**
- IOPS and throughput can be scaled **independently** of storage size
- **Max IOPS:** 16,000 (can go up to 80,000 on supported configurations)
- **Max Throughput:** 1,000 MiB/s
- **Max Volume Size:** 16 TiB
- **No burst credit model** — consistent baseline performance at all times
- **Up to 20% cheaper** per GB than gp2
- **Latency:** Single-digit milliseconds

```text
gp3 Performance Scaling:
━━━━━━━━━━━━━━━━━━━━━━━
  Storage Size  →  Can be set independently (1 GiB – 16 TiB)
  IOPS          →  3,000 baseline, scale up to 16,000 (pay extra)
  Throughput    →  125 MiB/s baseline, scale up to 1,000 MiB/s (pay extra)

  ✅ You control IOPS, throughput, and size SEPARATELY
```

#### 🔸 gp2 — Previous Generation

- Performance is **tied to volume size** — 3 IOPS per GiB
- **Burst capability:** Volumes under 1 TiB can burst up to **3,000 IOPS** using a credit system
- At **5,334 GiB**, the volume reaches the max of **16,000 IOPS** (5,334 × 3 = 16,002)
- **Max Throughput:** 250 MiB/s
- **Max Volume Size:** 16 TiB
- **Latency:** Single-digit milliseconds

```text
gp2 Performance Model (Credit-Based):
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  Volume Size      Baseline IOPS     Can Burst To
  ─────────────    ─────────────     ────────────
  1 GiB            3 IOPS            3,000 IOPS (burst)
  100 GiB          300 IOPS          3,000 IOPS (burst)
  1,000 GiB        3,000 IOPS       3,000 IOPS (no burst needed)
  5,334 GiB        16,000 IOPS      16,000 IOPS (MAX — no burst)
```

> ⚠️ **Exam Tip:** If a question asks about **cost optimization** or migrating from gp2 → gp3, the answer is almost always **gp3** because it's cheaper and offers independent scaling.

### 🔴 Provisioned IOPS SSD (io1 & io2)

- Designed for **mission-critical, I/O-intensive** applications that need **sustained IOPS performance**
- Best for workloads that need **more than 16,000 IOPS**
- Ideal for **database workloads** sensitive to storage performance and consistency
- Supports **EBS Multi-Attach** (attach the same volume to multiple EC2 instances)

#### 🔹 io1 — Previous Generation

- **Max IOPS:** 64,000 (on Nitro instances), 32,000 on others
- **Max Throughput:** 1,000 MiB/s
- **Volume Size:** 4 GiB – 16 TiB
- **IOPS-to-Size ratio:** Up to 50 IOPS per GiB
- **Durability:** 99.8% – 99.9%

#### 🔸 io2 — Current Generation (Recommended)

- **Max IOPS:** 64,000 (on Nitro instances)
- **IOPS-to-Size ratio:** Up to **500 IOPS per GiB** (10x more than io1!)
- **Durability:** 99.999% (significantly higher than io1)
- Same price as io1 but with much better durability and IOPS density
- **Volume Size:** 4 GiB – 16 TiB

#### 🔥 io2 Block Express — Ultra High Performance

- Built on the **AWS Nitro System** architecture
- **Max IOPS:** 256,000
- **Max Throughput:** 4,000 MiB/s
- **Max Volume Size:** 64 TiB
- **IOPS-to-Size ratio:** Up to 1,000 IOPS per GiB
- **Latency:** Sub-millisecond
- **Durability:** 99.999%
- Requires Nitro-based EC2 instances (e.g., R5b, R6i, M6i, C7g)

```text
Provisioned IOPS Comparison:
━━━━━━━━━━━━━━━━━━━━━━━━━━━
                   io1           io2          io2 Block Express
  Max IOPS         64,000        64,000       256,000
  Max Throughput   1,000 MiB/s   1,000 MiB/s  4,000 MiB/s
  Max Size         16 TiB        16 TiB       64 TiB
  IOPS/GiB         50:1          500:1        1,000:1
  Durability       99.8-99.9%    99.999%      99.999%
  Latency          single-digit  single-digit sub-millisecond
  Multi-Attach     ✅            ✅           ✅
```

> 🚨 **Exam Tip:** If the question mentions needing **sustained IOPS &gt; 16,000**, **sub-millisecond latency**, **multi-attach**, or **mission-critical databases** → choose **io2 / io2 Block Express**.

### 🟡 Throughput Optimized HDD (st1)

- Designed for **frequently accessed**, throughput-intensive workloads with **large sequential I/O**
- **Cannot be a boot volume**
- **Volume Size:** 125 GiB – 16 TiB
- **Max Throughput:** 500 MiB/s
- **Max IOPS:** 500
- **Baseline Throughput:** 40 MiB/s per TiB
- **Burst Throughput:** Up to 250 MiB/s per TiB
- Uses a **burst credit model** for throughput (similar to gp2's IOPS burst)

#### Use Cases for st1:

- Big Data processing (EMR, Hadoop)
- Data warehousing
- Log processing
- Apache Kafka

```text
st1 Performance Scaling (Throughput-Based):
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  Volume Size     Baseline Throughput     Burst Throughput
  ───────────     ───────────────────     ────────────────
  1 TiB           40 MiB/s               250 MiB/s
  2 TiB           80 MiB/s               500 MiB/s (MAX)
  5 TiB           200 MiB/s              500 MiB/s (MAX)
```

### ⚪ Cold HDD (sc1)

- The **cheapest** EBS volume option — designed for infrequently accessed data
- **Cannot be a boot volume**
- **Volume Size:** 125 GiB – 16 TiB
- **Max Throughput:** 250 MiB/s
- **Max IOPS:** 250
- **Baseline Throughput:** 12 MiB/s per TiB
- **Burst Throughput:** Up to 80 MiB/s per TiB

#### Use Cases for sc1:

- Data that is rarely accessed
- Scenarios where **lowest storage cost** is the priority
- Archival data that still needs to be accessible (not Glacier)

> 💡 **Exam Tip:** If a question mentions **lowest cost** storage with **infrequent access** and it's block storage (not object storage like S3) → choose **sc1**.

### 📊 Master Comparison Table — All 6 EBS Volume Types

| Feature | gp3 | gp2 | io2 | io1 | st1 | sc1 |
| --- | --- | --- | --- | --- | --- | --- |
| **Category** | SSD | SSD | SSD | SSD | HDD | HDD |
| **Boot Volume** | ✅ | ✅ | ✅ | ✅ | ❌ | ❌ |
| **Max Size** | 16 TiB | 16 TiB | 16 TiB | 16 TiB | 16 TiB | 16 TiB |
| **Max IOPS** | 16,000 | 16,000 | 64,000 | 64,000 | 500 | 250 |
| **Max Throughput** | 1,000 MiB/s | 250 MiB/s | 1,000 MiB/s | 1,000 MiB/s | 500 MiB/s | 250 MiB/s |
| **IOPS Model** | Independent | Size-linked | Provisioned | Provisioned | N/A | N/A |
| **Durability** | 99.8-99.9% | 99.8-99.9% | 99.999% | 99.8-99.9% | 99.8-99.9% | 99.8-99.9% |
| **Multi-Attach** | ❌ | ❌ | ✅ | ✅ | ❌ | ❌ |
| **Best For** | General | Legacy | Critical DBs | Legacy DBs | Big Data | Archival |
| **Cost** | 💲 | 💲💲 | 💲💲💲💲 | 💲💲💲💲 | 💲 | 💲 (cheapest) |

### 🔄 Elastic Volumes — Change Without Downtime

- You can **modify** an EBS volume while it is in use (no detach needed):

    - Increase the volume **size**
    - Change the volume **type** (e.g., gp2 → gp3, io1 → io2)
    - Adjust **IOPS** and **throughput** (for gp3, io1, io2)
- After resizing, you need to **repartition** the filesystem on the OS to use the new space

```bash
# Example: Modify a gp2 volume to gp3 with custom IOPS and throughput
aws ec2 modify-volume \\
  --volume-id vol-0123456789abcdef0 \\
  --volume-type gp3 \\
  --iops 5000 \\
  --throughput 250

# After modifying, extend the filesystem on the instance
sudo growpart /dev/xvda 1
sudo resize2fs /dev/xvda1
```

### 🧠 Exam Decision Framework

```text
Question asks about...                    → Choose
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
General purpose / boot volume / dev-test   → gp3
Cost optimization from gp2                 → gp3
IOPS > 16,000 / critical databases         → io2 or io2 Block Express
Sub-millisecond latency / 256K IOPS        → io2 Block Express
Multi-Attach needed                        → io1 or io2
Big Data / logs / streaming / sequential   → st1
Lowest cost / infrequent access (block)    → sc1
Highest possible IOPS (any storage)        → EC2 Instance Store
```

### 📝 Key Takeaways

- **6 EBS volume types:** gp3, gp2 (SSD), io2, io1 (SSD), st1, sc1 (HDD)
- Only **SSD types** can be **boot volumes** — HDD types cannot
- **gp3** is the modern default — independent IOPS/throughput scaling, cheaper than gp2
- **gp2** links performance to size (3 IOPS/GiB) with burst credits
- **io2** provides 99.999% durability and up to 500 IOPS/GiB — ideal for critical databases
- **io2 Block Express** pushes to 256,000 IOPS, 4,000 MiB/s, sub-ms latency on Nitro instances
- **st1** is for throughput-heavy sequential workloads (Big Data, logs)
- **sc1** is the cheapest option for cold, infrequently accessed data
- **Elastic Volumes** let you change type, size, and performance without downtime
- **Multi-Attach** is only supported on io1/io2 (Provisioned IOPS volumes)

---

## Lecture 53: 🔗 EBS Multi-Attach

> **Section 6: EC2 Instance Storage** — Ultimate AWS Certified Developer Associate DVA-C02 2026

### 🔍 What is EBS Multi-Attach?

- EBS Multi-Attach allows you to attach a **single EBS volume** to **multiple EC2 instances** at the same time
- All attached instances get **full read and write** permissions to the shared volume
- This is a feature exclusive to the **Provisioned IOPS SSD** family — only **io1** and **io2** volumes support it
- The volume and all attached instances must be in the **same Availability Zone (AZ)**

> 💡 Think of it as plugging a single high-performance SSD into multiple servers simultaneously — each server can read from and write to the same disk.

### ⚙️ How It Works

```text
                    ┌──────────────────┐
                    │   EBS io2 Volume  │
                    │  (Multi-Attach)   │
                    │   us-east-1a      │
                    └────────┬─────────┘
                             │
              ┌──────────────┼──────────────┐
              │              │              │
        ┌─────▼─────┐ ┌─────▼─────┐ ┌─────▼─────┐
        │  EC2 #1   │ │  EC2 #2   │ │  EC2 #3   │
        │ us-east-1a│ │ us-east-1a│ │ us-east-1a│
        └───────────┘ └───────────┘ └───────────┘

  ✅ All instances in the SAME AZ
  ✅ All instances have full read/write access
  ✅ Up to 16 instances can attach simultaneously
```

- Each attached instance can read and write **concurrently**
- A Multi-Attach enabled volume can be attached to up to **16 EC2 instances** at a time
- All instances must be **Nitro-based** EC2 instances

### 📋 Requirements & Constraints

| Requirement | Detail |
| --- | --- |
| **Volume Type** | Only **io1** and **io2** (Provisioned IOPS SSD) |
| **Availability Zone** | All instances must be in the **same AZ** as the volume |
| **Instance Type** | Must be **Nitro-based** EC2 instances |
| **Max Instances** | Up to **16** instances simultaneously |
| **Boot Volume** | ❌ **Cannot** be used as a boot/root volume |
| **Enable Timing** | Must be enabled **at volume creation time** |
| **Post-Creation** | ❌ Cannot enable or disable Multi-Attach after the volume is created |

### ⚠️ Critical Concept: Cluster-Aware File Systems

- When multiple instances write to the **same volume simultaneously**, there is a risk of **data corruption**
- AWS does **not** provide built-in write coordination or locking
- **You must** use a **cluster-aware file system** to manage concurrent access safely

#### ❌ NOT Cluster-Aware (Will Cause Corruption)

- `ext4` — Standard Linux file system
- `XFS` — Standard Linux file system
- `NTFS` — Standard Windows file system

#### ✅ Cluster-Aware (Safe for Multi-Attach)

- **OCFS2** — Oracle Cluster File System 2
- **GFS2** — Global File System 2 (Red Hat)
- Application-level locking managed by the application itself

```text
⚠️ DANGER: Using a standard file system with Multi-Attach

  Instance A writes block 100 → "Hello"
  Instance B writes block 100 → "World"    (at the same time!)

  Result: DATA CORRUPTION — no coordination!

✅ SAFE: Using a cluster-aware file system

  Instance A wants block 100 → acquires lock → writes "Hello" → releases lock
  Instance B wants block 100 → waits for lock → acquires lock → writes "World"

  Result: Consistent, ordered writes
```

> 🚨 **Exam Tip:** If a question mentions sharing an EBS volume between instances using `ext4` or `XFS` without any coordination mechanism — that is an **incorrect** approach. Always look for "cluster-aware file system" in the correct answer.

### 🎯 Use Cases

#### 🏗️ High Availability Clustered Applications

- Applications like **Teradata** that manage their own data consistency and locking across nodes
- Active-active or active-standby database clusters that need shared persistent storage

#### 🔄 Failover Scenarios

- A **standby instance** needs immediate access to the same data as the primary instance
- When the primary instance fails, the standby can instantly take over without copying data
- Achieves **higher application availability** compared to traditional failover mechanisms

#### 📂 Concurrent Processing

- Multiple instances processing different parts of the same dataset stored on a shared volume
- Distributed applications that need shared block-level storage within a single AZ

### 🆚 EBS Multi-Attach vs Amazon EFS

- This is a **very common exam comparison** — know the differences clearly

| Feature | EBS Multi-Attach | Amazon EFS |
| --- | --- | --- |
| **Storage Type** | Block storage | File storage (NFS) |
| **Protocol** | Block-level access | NFS v4.1 protocol |
| **AZ Scope** | ❌ Single AZ only | ✅ Multi-AZ (Regional) |
| **Max Connections** | 16 instances | Hundreds/Thousands |
| **Volume Types** | io1 / io2 only | N/A (managed service) |
| **File System** | Requires cluster-aware FS | POSIX-compliant (works natively) |
| **Performance** | Very high IOPS (Provisioned) | Varies by mode (Bursting/Provisioned) |
| **Use Case** | Low-level block sharing, clustered DBs | Shared file storage, web serving, CMS |
| **Cost** | io1/io2 pricing (higher) | Pay per use (can be cheaper) |
| **Management** | You manage FS and coordination | Fully managed by AWS |

```text
Decision Guide:
━━━━━━━━━━━━━━
Need shared storage across MULTIPLE AZs?        → Use EFS
Need shared BLOCK storage in a SINGLE AZ?       → Use EBS Multi-Attach
Need simple shared files (NFS) for Linux?        → Use EFS
Need extreme IOPS for clustered databases?       → Use EBS Multi-Attach (io2)
Need to share with 100+ instances?               → Use EFS
```

> 💡 **Exam Tip:** If the question asks for **shared storage across AZs** or for a **managed file system**, the answer is **EFS**, not EBS Multi-Attach. Multi-Attach is limited to a single AZ.

### 🛠️ Creating a Multi-Attach Volume via CLI

```bash
# Create an io2 volume with Multi-Attach enabled
aws ec2 create-volume \\
  --volume-type io2 \\
  --size 100 \\
  --iops 10000 \\
  --availability-zone us-east-1a \\
  --multi-attach-enabled

# Attach the volume to the first instance
aws ec2 attach-volume \\
  --volume-id vol-0123456789abcdef0 \\
  --instance-id i-0abc111111111111 \\
  --device /dev/sdf

# Attach the SAME volume to a second instance
aws ec2 attach-volume \\
  --volume-id vol-0123456789abcdef0 \\
  --instance-id i-0abc222222222222 \\
  --device /dev/sdf
```

### 📝 Key Takeaways

- EBS Multi-Attach lets you attach **one io1/io2 volume** to **up to 16 Nitro-based instances** in the **same AZ**
- All instances get **full read/write access** — but AWS provides **no built-in locking**
- You **must** use a **cluster-aware file system** (OCFS2, GFS2) or application-level coordination to prevent data corruption
- Multi-Attach must be enabled **at volume creation** — cannot be toggled afterwards
- Multi-Attach volumes **cannot** be boot volumes
- Only works with **io1** and **io2** — not gp2, gp3, st1, or sc1
- For **cross-AZ shared storage**, use **Amazon EFS** instead
- Primary use cases: **HA clusters**, **failover architectures**, and **clustered databases**

---

## Lecture 54: 📁 Amazon EFS (Elastic File System)

> **Section 6: EC2 Instance Storage** — Ultimate AWS Certified Developer Associate DVA-C02 2026

### 🔍 What is Amazon EFS?

- Amazon EFS is a **managed Network File System (NFS)** that can be mounted on **many EC2 instances** simultaneously
- Unlike EBS (which is locked to a single AZ), EFS works across **multiple Availability Zones** — making it a **regional** service
- EFS is **highly available**, **scalable**, and **expensive** (~3x the cost of gp2) — but you can reduce costs with storage classes
- It is a **fully managed** service — AWS handles all infrastructure, patching, and scaling
- EFS scales **automatically** — you don't need to provision capacity in advance; it grows and shrinks as you add/remove files
- Supports **petabyte-scale** storage

> 💡 EFS = **shared file storage** that multiple instances across multiple AZs can access concurrently via NFS. Think of it as a "shared network drive" in the cloud.

### ⚙️ How EFS Works — Architecture

```text
              ┌─────────────────────────────────────────┐
              │            AWS Region (e.g. us-east-1)  │
              │                                         │
              │  ┌──────────────────────────────────┐   │
              │  │        Amazon EFS File System     │   │
              │  │     (Regional — Multi-AZ)         │   │
              │  └──────┬──────────┬──────────┬──────┘   │
              │         │          │          │           │
              │   ┌─────▼────┐ ┌──▼───────┐ ┌▼────────┐ │
              │   │Mount Tgt │ │Mount Tgt │ │Mount Tgt│ │
              │   │us-east-1a│ │us-east-1b│ │us-east-1c│ │
              │   └─────┬────┘ └──┬───────┘ └┬────────┘ │
              │         │         │          │           │
              │   ┌─────▼────┐ ┌──▼───────┐ ┌▼────────┐ │
              │   │  EC2 #1  │ │  EC2 #2  │ │  EC2 #3 │ │
              │   │  EC2 #4  │ │  EC2 #5  │ │  EC2 #6 │ │
              │   └──────────┘ └──────────┘ └─────────┘ │
              └─────────────────────────────────────────┘

  ✅ One file system shared across ALL AZs
  ✅ Mount targets in each AZ act as entry points
  ✅ Hundreds of instances can connect simultaneously
```

- **Mount Targets** are created in each AZ's subnet — they provide the network endpoint (IP/DNS) for EC2 instances to connect
- EC2 instances connect to the mount target in their AZ via **NFS v4.1** protocol

### 📋 Key Characteristics

| Feature | Detail |
| --- | --- |
| **Protocol** | NFS v4.1 |
| **OS Support** | **Linux only** (not Windows!) |
| **File System** | POSIX-compliant (standard Linux permissions) |
| **Scaling** | Automatic — grows/shrinks with usage |
| **Max Size** | Petabyte scale |
| **Concurrency** | Hundreds/thousands of concurrent NFS clients |
| **Scope** | Regional (Multi-AZ) by default |
| **Encryption** | At rest (KMS) and in transit (TLS) |
| **Cost Model** | Pay per use (no pre-provisioning) |

> ⚠️ **Exam Tip:** EFS only works with **Linux-based AMIs** — it does NOT support Windows. If the question mentions Windows instances, EFS is **not** the answer (consider FSx for Windows instead).

### 🎯 Use Cases

- **Content management** and web serving — multiple web servers sharing the same content
- **Data sharing** — shared home directories across multiple Linux instances
- **WordPress** — shared media/uploads directory
- **Big data and analytics** — shared datasets for Hadoop, Spark
- **Container storage** — shared volumes for ECS, EKS, and Fargate tasks
- **Lambda** — EFS can be mounted by Lambda functions for persistent file access

### ⚡ Performance Modes

- Chosen **at creation time** — cannot be changed afterward

| Performance Mode | Latency | Use Case |
| --- | --- | --- |
| **General Purpose** (default) | Lowest per-operation latency | Web servers, CMS, home directories — most workloads |
| **Max I/O** | Higher latency | Big data, media processing — highly parallelized workloads needing maximum IOPS |

> 💡 **General Purpose** is recommended for the vast majority of workloads. Only choose **Max I/O** if you have massively parallel applications that need higher aggregate throughput.

### 🔄 Throughput Modes

- Determines how much data can be read/written per second

| Throughput Mode | How It Works | Best For |
| --- | --- | --- |
| **Elastic** (Recommended) | Automatically scales up/down based on workload; pay only for what you use | Unpredictable or spiky workloads |
| **Provisioned** | You specify a fixed throughput (e.g., 1 GiB/s) regardless of storage size | Predictable, consistently high-throughput needs |
| **Bursting** | Throughput scales with file system size; uses burst credits | Cost-effective for larger file systems with moderate usage |

```text
Throughput Mode Examples:
━━━━━━━━━━━━━━━━━━━━━━━━

Bursting Mode (scales with size):
  1 TiB storage  →  50 MiB/s baseline, burst to 100 MiB/s

Provisioned Mode (you set it):
  Any size       →  You pick: e.g., 1 GiB/s throughput

Elastic Mode (auto-scales):
  Any size       →  Scales automatically up to 10+ GiB/s
                     Pay only for throughput consumed
```

### 💰 Storage Classes & Lifecycle Management

- EFS offers multiple **storage classes** to optimize costs based on access patterns
- Use **Lifecycle Policies** to automatically move files between classes

#### 📦 Storage Classes

| Storage Class | Redundancy | Cost | Use Case |
| --- | --- | --- | --- |
| **EFS Standard** | Multi-AZ | 💲💲💲 | Frequently accessed data |
| **EFS Standard-IA** | Multi-AZ | 💲💲 | Infrequently accessed (few times/quarter) |
| **EFS One Zone** | Single AZ | 💲💲 | Dev/test, data that can be recreated |
| **EFS One Zone-IA** | Single AZ | 💲 (cheapest) | Infrequent access + single AZ tolerance |

```text
Cost Savings Breakdown:
━━━━━━━━━━━━━━━━━━━━━━━
  Standard         → Full price, Multi-AZ redundancy
  Standard-IA      → Up to 92% cheaper than Standard (retrieval fee applies)
  One Zone         → ~47% cheaper than Standard
  One Zone-IA      → Cheapest option (Single AZ + IA discount)
```

#### 🔄 Lifecycle Policies

- Automatically move files to IA classes after a configured period of inactivity
- Available transition periods: **7, 14, 30, 60, or 90 days** without access
- Can also configure a policy to **move files back** to Standard when they are accessed again

```bash
# Example: Mount EFS with the mount helper (recommended)
sudo yum install -y amazon-efs-utils

# Mount with TLS encryption in transit
sudo mount -t efs -o tls fs-0123456789abcdef0:/ /mnt/efs

# Or add to /etc/fstab for persistent mount
echo "fs-0123456789abcdef0:/ /mnt/efs efs _netdev,tls 0 0" | sudo tee -a /etc/fstab
```

### 🔐 Security

#### 🌐 Network Security (Security Groups)

- Each **mount target** has an associated **security group**
- The security group must allow **inbound NFS traffic on port 2049** from the EC2 instances' security group

```text
Security Group Rules:
━━━━━━━━━━━━━━━━━━━━

Mount Target SG (Inbound):
  Protocol: TCP | Port: 2049 | Source: EC2 Security Group

EC2 Instance SG (Outbound):
  Protocol: TCP | Port: 2049 | Destination: Mount Target SG
```

#### 🔑 Encryption

- **At rest:** Enable using **AWS KMS** (can use default key or custom CMK)
- **In transit:** Use the `tls` mount option with the **EFS mount helper** (`amazon-efs-utils`)

#### 👤 Access Control

- **IAM Policies:** Control which IAM principals can perform EFS API actions or mount the file system
- **POSIX Permissions:** Standard Linux user/group permissions (UID/GID) apply to all files and directories
- **EFS Access Points:** Application-specific entry points that enforce a specific UID/GID and root directory

```bash
# Mount using an EFS Access Point with IAM authorization
sudo mount -t efs -o tls,accesspoint=fsap-0123456789abcdef0,iam fs-0123456789abcdef0:/ /mnt/app
```

### 🏗️ EFS Access Points

- Provide **application-specific entry points** into the file system
- Enforce a specific **POSIX identity** (UID, GID) for all requests — regardless of the actual NFS client identity
- Can restrict access to a specific **root directory** — applications only see their designated path
- Useful for **multi-tenant** setups or **container workloads** where each app needs its own isolated view

```text
EFS Access Points Example:
━━━━━━━━━━━━━━━━━━━━━━━━━

  Access Point: App-A
    → UID: 1001, GID: 1001
    → Root Path: /app-a-data
    → App A can ONLY see /app-a-data/*

  Access Point: App-B
    → UID: 1002, GID: 1002
    → Root Path: /app-b-data
    → App B can ONLY see /app-b-data/*
```

### 🆚 Quick Comparison: EFS vs EBS vs Instance Store

| Feature | Amazon EFS | Amazon EBS | EC2 Instance Store |
| --- | --- | --- | --- |
| **Type** | File storage (NFS) | Block storage | Block storage (local) |
| **Scope** | Multi-AZ (Regional) | Single AZ | Single instance |
| **Sharing** | Hundreds of instances | 1 instance (or 16 with Multi-Attach) | 1 instance |
| **Scaling** | Automatic | Manual (Elastic Volumes) | Fixed at launch |
| **Persistence** | ✅ Persistent | ✅ Persistent | ❌ Ephemeral |
| **OS Support** | Linux only | Linux + Windows | Linux + Windows |
| **Performance** | Varies by mode | Up to 256K IOPS (io2 BE) | Millions of IOPS |
| **Cost** | Pay per use | Pay per provisioned | Included in instance |
| **Best For** | Shared files, CMS | Databases, boot volumes | Caches, scratch data |

### 📝 Key Takeaways

- Amazon EFS is a **managed NFS** file system — shared across **multiple AZs** and **hundreds of instances**
- Works only with **Linux** (POSIX-compliant) — not Windows
- **Scales automatically** — no capacity planning needed; supports petabyte scale
- **Performance modes:** General Purpose (low latency) vs Max I/O (high parallelism)
- **Throughput modes:** Elastic (auto-scales), Provisioned (fixed), Bursting (size-linked)
- **Storage classes:** Standard, Standard-IA, One Zone, One Zone-IA — use lifecycle policies to save costs
- **Security:** Security groups (port 2049), KMS encryption, IAM policies, POSIX permissions, Access Points
- **Access Points** enforce POSIX identity and root directory per application — great for multi-tenant and containers
- Use EFS when you need **shared file storage across AZs** — use EBS for single-instance block storage

---

## Lecture 55: 🛠️ Amazon EFS - Hands On

> **Section 6: EC2 Instance Storage** — Ultimate AWS Certified Developer Associate DVA-C02 2026

### 🔍 Overview

- In this hands-on lab, we will:

    - Create an **EFS file system** via the AWS Console
    - Configure **security groups** to allow NFS traffic (port 2049)
    - Launch **two EC2 instances** in different Availability Zones
    - **Mount** the same EFS file system on both instances
    - Verify that files created on one instance are **visible on the other**

> 💡 This lab demonstrates the core value of EFS — a **shared file system** accessible from multiple instances across multiple AZs simultaneously.

### 📋 Step 1: Create a Security Group for EFS

- Before creating the EFS file system, we need a security group that allows **NFS inbound traffic on port 2049**
- Navigate to **EC2 Console → Security Groups → Create Security Group**

| Field | Value |
| --- | --- |
| **Name** | `efs-demo-sg` |
| **Description** | Allow NFS access for EFS |
| **VPC** | Default VPC |

- **Inbound Rule:**

| Type | Protocol | Port | Source |
| --- | --- | --- | --- |
| NFS | TCP | 2049 | The security group of your EC2 instances (e.g., `launch-wizard-1`) |

```text
Security Group Architecture:
━━━━━━━━━━━━━━━━━━━━━━━━━━━

  EC2 Instance SG (launch-wizard-1)
       │
       │  Outbound → port 2049
       ▼
  EFS Mount Target SG (efs-demo-sg)
       │
       │  Inbound ← port 2049 from EC2 SG
       ▼
  EFS File System
```

> ⚠️ **Important:** The EFS security group's inbound rule should reference the **EC2 instances' security group** as the source — not a specific IP. This way, any instance using that SG can connect.

### 📋 Step 2: Create the EFS File System

- Navigate to **EFS Console → Create file system**
- Click **Customize** for full configuration options

#### General Settings

| Setting | Value |
| --- | --- |
| **Name** | `demo-efs` |
| **Storage class** | Standard (Multi-AZ) |
| **Automatic backups** | Uncheck (to save costs in this demo) |
| **Lifecycle management** | Choose a transition policy (e.g., 30 days to IA) or None |
| **Encryption** | Enable encryption at rest (uses default AWS KMS key) |

#### Performance Settings

| Setting | Value |
| --- | --- |
| **Throughput mode** | Elastic (recommended) or Bursting |
| **Performance mode** | General Purpose (default) |

#### Network Access (Mount Targets)

- This is where you configure **mount targets** in each AZ
- For each Availability Zone, AWS creates a mount target with a network interface
- **Assign the EFS security group** (`efs-demo-sg`) to each mount target
- **Remove** any default security groups and add only your EFS security group

```text
Mount Target Configuration:
━━━━━━━━━━━━━━━━━━━━━━━━━━

  AZ: us-east-1a  →  Subnet: default  →  SG: efs-demo-sg
  AZ: us-east-1b  →  Subnet: default  →  SG: efs-demo-sg
  AZ: us-east-1c  →  Subnet: default  →  SG: efs-demo-sg
```

- Leave **File system policy** as default (no additional IAM policies for now)
- Click **Create** — the file system will take a moment to become available

### 📋 Step 3: Launch Two EC2 Instances in Different AZs

- Navigate to **EC2 Console → Launch Instance**
- Launch **2 instances** with these settings:

| Setting | Value |
| --- | --- |
| **Name** | `efs-demo-1` and `efs-demo-2` |
| **AMI** | Amazon Linux 2023 |
| **Instance type** | t2.micro (free tier) |
| **Key pair** | Select or create one |
| **AZs** | Place each instance in a **different AZ** (e.g., `us-east-1a` and `us-east-1b`) |
| **Security group** | Use the same SG (e.g., `launch-wizard-1`) that you referenced in the EFS SG |
| **User data** | (Optional) Install EFS utilities — see below |

#### User Data Script (Install EFS Mount Helper)

```bash
#!/bin/bash
yum update -y
yum install -y amazon-efs-utils
```

> 💡 The `amazon-efs-utils` package provides the **EFS mount helper** which simplifies mounting and supports TLS encryption in transit.

### 📋 Step 4: Mount EFS on Both Instances

- SSH into **each EC2 instance** using EC2 Instance Connect or your SSH key

#### On Each Instance, Run:

```bash
# Install EFS utilities (if not installed via user data)
sudo yum install -y amazon-efs-utils

# Create a mount point directory
sudo mkdir /mnt/efs

# Mount the EFS file system using the mount helper
# Replace fs-0123456789abcdef0 with your actual EFS file system ID
sudo mount -t efs fs-0123456789abcdef0:/ /mnt/efs

# Verify the mount
df -h | grep efs
```

- You can find the **exact mount command** in the EFS Console:

    - Go to **EFS → Your file system → Attach**
    - Choose **Mount via DNS** → using the **EFS mount helper**

#### Alternative: Mount with TLS (Encryption in Transit)

```bash
# Mount with TLS encryption enabled
sudo mount -t efs -o tls fs-0123456789abcdef0:/ /mnt/efs
```

#### Alternative: Mount Using NFS Client (Without EFS Utils)

```bash
# Install NFS client
sudo yum install -y nfs-utils

# Mount using standard NFS
sudo mount -t nfs4 -o nfsvers=4.1,rsize=1048576,wsize=1048576,hard,timeo=600,retrans=2 \\
  fs-0123456789abcdef0.efs.us-east-1.amazonaws.com:/ /mnt/efs
```

### 📋 Step 5: Test Shared File Access

- This is the key test — proving that both instances share the same file system

#### On Instance 1 (us-east-1a):

```bash
# Navigate to the EFS mount
cd /mnt/efs

# Create a test file
sudo touch hello-from-instance-1.txt
sudo sh -c 'echo "Hello from AZ-1!" > hello-from-instance-1.txt'

# List files
ls -la
```

#### On Instance 2 (us-east-1b):

```bash
# Navigate to the EFS mount
cd /mnt/efs

# List files — you should see the file created by Instance 1!
ls -la

# Read the file
cat hello-from-instance-1.txt
# Output: Hello from AZ-1!

# Create another file from this instance
sudo sh -c 'echo "Hello from AZ-2!" > hello-from-instance-2.txt'
```

#### Back on Instance 1:

```bash
# You should now see BOTH files
ls -la /mnt/efs

# Output:
# hello-from-instance-1.txt
# hello-from-instance-2.txt

cat hello-from-instance-2.txt
# Output: Hello from AZ-2!
```

```text
Result: Files Shared Across AZs! ✅
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

  Instance 1 (us-east-1a)          Instance 2 (us-east-1b)
  ┌────────────────────┐           ┌────────────────────┐
  │  /mnt/efs/         │           │  /mnt/efs/         │
  │  ├── hello-..1.txt │  ◄═══►   │  ├── hello-..1.txt │
  │  └── hello-..2.txt │  SHARED   │  └── hello-..2.txt │
  └────────────────────┘           └────────────────────┘
              │                              │
              └──────────┬───────────────────┘
                         ▼
              ┌──────────────────┐
              │  Amazon EFS      │
              │  (Single shared  │
              │   file system)   │
              └──────────────────┘
```

> 🎉 Both instances see the **exact same files** in real time — this is the power of EFS!

### 📋 Step 6: Make the Mount Persistent (Optional)

- By default, the EFS mount is lost when the instance reboots
- To make it persistent, add an entry to `/etc/fstab`:

```bash
# Add EFS mount to fstab for persistence across reboots
echo "fs-0123456789abcdef0:/ /mnt/efs efs _netdev,tls 0 0" | sudo tee -a /etc/fstab

# Verify fstab entry
cat /etc/fstab
```

### 🧹 Step 7: Cleanup

- **Important:** Clean up resources to avoid unexpected charges

```bash
# On each instance — unmount EFS
sudo umount /mnt/efs
```

- In the AWS Console:

    1. **Terminate** both EC2 instances
    1. **Delete** the EFS file system (EFS Console → Select file system → Delete)
    1. **Delete** the EFS security group (`efs-demo-sg`)

> ⚠️ EFS charges are **pay-per-use** based on the amount of data stored. Even a small amount of data left mounted will incur charges over time.

### 🔧 Troubleshooting Common Issues

| Issue | Solution |
| --- | --- |
| **Mount hangs / times out** | Check that the EFS SG allows inbound NFS (TCP 2049) from the EC2 SG |
| **Connection refused** | Ensure mount targets exist in the same AZ as your EC2 instance |
| **mount.nfs4: No such device** | Install `amazon-efs-utils` or `nfs-utils` package |
| **Permission denied** | Check POSIX permissions on the EFS root directory; use `sudo` |
| **Mount lost after reboot** | Add the mount entry to `/etc/fstab` with `_netdev` option |

```bash
# Quick debug: Check if NFS port is reachable from your instance
telnet fs-0123456789abcdef0.efs.us-east-1.amazonaws.com 2049

# Check current mounts
mount | grep efs

# Check EFS mount helper logs
cat /var/log/amazon/efs/mount.log
```

### 📝 Key Takeaways

- EFS creation involves: file system settings, performance/throughput mode, network (mount targets + security groups)
- **Security group** for EFS mount targets must allow **inbound TCP port 2049** from EC2 instance SGs
- Use `amazon-efs-utils` package for the simplest mount experience (supports TLS encryption)
- The **same file system** is accessible from instances in **different AZs** — files are shared in real time
- Add the mount to `/etc/fstab` with the `_netdev` flag to persist across reboots
- Always **clean up** EFS, EC2 instances, and security groups after hands-on labs to avoid charges

---

## Lecture 56: ⚖️ EFS vs EBS

> **Section 6: EC2 Instance Storage** — Ultimate AWS Certified Developer Associate DVA-C02 2026

### 🔍 Why This Comparison Matters

- This is one of the **most frequently tested topics** on the AWS Developer Associate exam
- You must be able to quickly identify which storage option fits a given scenario
- This lecture compares **EBS**, **EFS**, and **Instance Store** — the three EC2 storage options covered in this section

### 📦 Amazon EBS — Recap

- **Elastic Block Store** — network-attached block storage for a single EC2 instance
- EBS volumes are **locked to a specific Availability Zone** (AZ)
- To migrate an EBS volume to another AZ, you must create a **snapshot** and restore it in the target AZ
- By default, the **root EBS volume** is terminated when the instance is terminated (can be disabled via "Delete on Termination" attribute)
- An EBS volume can only be attached to **one instance at a time** (except io1/io2 with Multi-Attach)

```text
EBS Volume Lifecycle — AZ Migration:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

  ┌──────────────┐         ┌──────────────┐         ┌──────────────┐
  │  EBS Volume  │  ───►   │  EBS         │  ───►   │  EBS Volume  │
  │  us-east-1a  │ Snapshot │  Snapshot    │ Restore │  us-east-1b  │
  └──────────────┘         │  (S3-backed) │         └──────────────┘
                           └──────────────┘
```

#### 🔹 EBS Key Points for Comparison

- **Scope:** Single AZ
- **Attachment:** 1 instance (or up to 16 with Multi-Attach on io1/io2)
- **Persistence:** ✅ Survives instance termination (if configured)
- **Provisioning:** Must provision size and type in advance
- **Scaling:** Manual — use Elastic Volumes to resize
- **Backup:** Snapshots (stored in S3, can copy cross-AZ/cross-Region)
- **Boot volume:** ✅ Yes
- **OS Support:** Linux and Windows
- **Volume Types:** gp2, gp3, io1, io2, st1, sc1

### 📁 Amazon EFS — Recap

- **Elastic File System** — managed NFS (Network File System) for shared access
- Works across **multiple AZs** simultaneously — it is a **regional** service
- Can be mounted on **hundreds or thousands** of instances concurrently
- **Linux only** — uses POSIX file system permissions
- **More expensive** than EBS (~3x gp2 price) — but lifecycle policies can reduce costs significantly
- **Pay per use** — no need to provision capacity; it auto-scales

#### 🔹 EFS Key Points for Comparison

- **Scope:** Multi-AZ (Regional)
- **Attachment:** Hundreds/thousands of instances
- **Persistence:** ✅ Always persistent
- **Provisioning:** No provisioning needed — auto-scales
- **Scaling:** Automatic — grows and shrinks with data
- **Backup:** AWS Backup integration
- **Boot volume:** ❌ No
- **OS Support:** Linux only (POSIX)
- **Storage Classes:** Standard, Standard-IA, One Zone, One Zone-IA, Archive

### 💾 EC2 Instance Store — Recap

- **Physically attached** local disk on the host server
- **Highest I/O performance** of any EC2 storage option
- **Ephemeral** — data is lost on stop, terminate, or hardware failure
- Only survives a **reboot**

#### 🔹 Instance Store Key Points for Comparison

- **Scope:** Single instance
- **Attachment:** 1 instance only
- **Persistence:** ❌ Ephemeral
- **Provisioning:** Fixed — determined by instance type
- **Scaling:** Cannot resize
- **Backup:** No snapshots — manual backup only
- **Boot volume:** ❌ No
- **OS Support:** Linux and Windows

### 📊 Master Comparison Table

| Feature | Amazon EBS | Amazon EFS | EC2 Instance Store |
| --- | --- | --- | --- |
| **Storage Type** | Block | File (NFS) | Block (local) |
| **Scope** | Single AZ | Multi-AZ (Regional) | Single Instance |
| **Attachment** | 1 instance (16 with Multi-Attach) | 1,000s of instances | 1 instance |
| **Protocol** | Block device | NFS v4.1 | Block device |
| **OS Support** | Linux + Windows | ⚠️ Linux only | Linux + Windows |
| **Persistence** | ✅ Persistent | ✅ Persistent | ❌ Ephemeral |
| **Boot Volume** | ✅ Yes | ❌ No | ❌ No |
| **Scaling** | Manual (Elastic Volumes) | Automatic | Fixed |
| **Max Performance** | 256K IOPS (io2 BE) | Elastic throughput | Millions of IOPS |
| **Snapshots** | ✅ Yes (S3-backed) | ❌ No (use AWS Backup) | ❌ No |
| **Encryption at Rest** | ✅ KMS | ✅ KMS | ✅ Hardware-level |
| **Encryption in Transit** | ✅ (between EC2 and EBS) | ✅ TLS mount option | N/A (local) |
| **Cost Model** | Pay per provisioned GB + IOPS | Pay per use (GB stored) | Included in instance price |
| **Relative Cost** | 💲💲 | 💲💲💲 (but IA classes save $) | Free (included) |
| **Use Cases** | Databases, boot volumes | Shared files, CMS, web | Caches, buffers, scratch |

### 🧠 Exam Scenario Decision Guide

```text
Scenario                                              → Answer
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Boot volume / root volume for EC2                      → EBS
Database storage (single instance)                     → EBS (gp3 or io2)
Shared storage across multiple AZs                     → EFS
Shared content for web servers (Linux)                 → EFS
WordPress shared media uploads                         → EFS
Windows file share                                     → ❌ NOT EFS → Use FSx for Windows
Highest possible I/O performance                       → EC2 Instance Store
Temporary cache / buffer / scratch data                → EC2 Instance Store
Data must survive instance stop/termination            → EBS or EFS (NOT Instance Store)
Need to migrate storage to another AZ                  → EBS Snapshot + Restore OR use EFS
Shared storage for containers (ECS/EKS/Fargate)        → EFS
Lambda needs persistent file access                    → EFS
Cost-optimized infrequent access file storage          → EFS with IA storage classes
Single AZ shared block storage for clustered DB        → EBS Multi-Attach (io1/io2)
```

### 💰 Cost Comparison Deep Dive

```text
Cost Comparison (approximate, us-east-1):
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

  EBS gp3:            ~$0.08/GB/month  (must provision full size upfront)
  EBS io2:            ~$0.125/GB/month + $0.065/provisioned IOPS/month

  EFS Standard:       ~$0.30/GB/month  (pay only for data stored)
  EFS Standard-IA:    ~$0.016/GB/month (up to 92% cheaper!)
  EFS One Zone:       ~$0.16/GB/month  (~47% cheaper than Standard)
  EFS One Zone-IA:    ~$0.008/GB/month (cheapest EFS option)

  Instance Store:     $0.00           (included in instance price)

Key Insight:
  EFS Standard is ~3x more expensive than EBS gp3
  BUT with Lifecycle Policies moving data to IA classes,
  EFS can become MORE cost-effective than EBS for mixed workloads
```

> 💡 **Exam Tip:** EFS is expensive at face value, but **EFS-IA storage classes** (Infrequent Access) can reduce costs dramatically. If a question mentions cost optimization for EFS, look for **lifecycle policies** that transition files to IA.

### 🔄 EBS vs EFS — Architecture Comparison

```text
EBS Architecture (Single AZ):
━━━━━━━━━━━━━━━━━━━━━━━━━━━━
                   us-east-1a              us-east-1b
               ┌───────────────┐       ┌───────────────┐
               │   EC2 + EBS   │       │   EC2 + EBS   │
               │  (Volume A)   │       │  (Volume B)   │
               └───────────────┘       └───────────────┘
               Volume A ≠ Volume B  (separate, independent volumes)


EFS Architecture (Multi-AZ):
━━━━━━━━━━━━━━━━━━━━━━━━━━━━
                   us-east-1a              us-east-1b
               ┌───────────────┐       ┌───────────────┐
               │   EC2 #1      │       │   EC2 #2      │
               │   EC2 #3      │       │   EC2 #4      │
               └───────┬───────┘       └───────┬───────┘
                       │                       │
                       └───────────┬───────────┘
                                   │
                          ┌────────▼────────┐
                          │   Amazon EFS    │
                          │ (Shared FS)     │
                          │ Same data for   │
                          │ ALL instances   │
                          └─────────────────┘
```

### ⚡ Performance Comparison

| Metric | EBS (best case) | EFS | Instance Store |
| --- | --- | --- | --- |
| **Max IOPS** | 256,000 (io2 Block Express) | Scales with Elastic mode | 3,300,000+ (i3.16xlarge) |
| **Max Throughput** | 4,000 MiB/s (io2 BE) | 10+ GiB/s (Elastic) | Depends on instance |
| **Latency** | Sub-millisecond (io2 BE) | Single-digit ms | Ultra-low (local disk) |
| **Best Pattern** | Random + Sequential | Sequential, shared reads | Random, high IOPS |

### 🔑 Critical Differences to Remember

#### 1️⃣ AZ Scope

- **EBS** = locked to ONE AZ → need snapshots to move
- **EFS** = spans ALL AZs in a region → mount from anywhere

#### 2️⃣ OS Compatibility

- **EBS** = Linux AND Windows
- **EFS** = **Linux ONLY** (POSIX) → for Windows use **Amazon FSx**

#### 3️⃣ Scaling

- **EBS** = you must manually provision and resize
- **EFS** = fully automatic, no provisioning needed

#### 4️⃣ Sharing

- **EBS** = generally one instance (Multi-Attach is limited to io1/io2, same AZ, max 16)
- **EFS** = designed for sharing across thousands of instances and multiple AZs

#### 5️⃣ Cost Structure

- **EBS** = pay for **provisioned** capacity (even if unused)
- **EFS** = pay for **actual data stored** (true pay-per-use)

### 📝 Key Takeaways

- **EBS** = block storage, single AZ, one instance, great for databases and boot volumes
- **EFS** = file storage (NFS), multi-AZ, many instances, great for shared content — **Linux only**
- **Instance Store** = local block storage, highest performance, ephemeral — great for caches
- EFS is ~3x more expensive than EBS but offers **auto-scaling** and **multi-AZ sharing** — use **IA classes** to cut costs
- EBS requires **snapshots** to move across AZs; EFS is natively cross-AZ
- Only **EBS** can be a **boot volume** — EFS and Instance Store cannot
- For **Windows** shared file storage → use **Amazon FSx for Windows File Server**, not EFS
- The exam loves questions that test EBS vs EFS vs Instance Store — know the key differentiators cold

---
