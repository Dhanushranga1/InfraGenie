"""
Infrastructure Templates for Complex Architecture Generation

This module contains detailed templates and completeness checklists for
complex infrastructure patterns that LLMs frequently generate incompletely.

Problem: When asked to "create a Kubernetes cluster", LLMs often generate
only the VPC/networking layer and stop, missing the actual cluster resource.

Solution: Provide explicit templates showing ALL required components.
"""

# Kubernetes Cluster Template
K8S_CLUSTER_TEMPLATE = """
═══════════════════════════════════════════════════════════════════
🚨 KUBERNETES CLUSTER REQUIREMENTS - ALWAYS INCLUDE ALL OF THESE:
═══════════════════════════════════════════════════════════════════

AWS EKS (Elastic Kubernetes Service):
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
**NETWORKING LAYER (4 resources minimum):**
1. ✅ aws_vpc - VPC with CIDR block
2. ✅ aws_subnet - Public subnets (2+ for HA across AZs)
3. ✅ aws_subnet - Private subnets (2+ for node groups)
4. ✅ aws_internet_gateway - For public subnet internet access
5. ✅ aws_nat_gateway - For private subnet outbound (1 per AZ)
6. ✅ aws_route_table - Public route table
7. ✅ aws_route_table - Private route table(s)

**IAM/SECURITY LAYER (3 resources minimum):**
8. ✅ aws_iam_role - EKS cluster role with trust policy:
   ```
   assume_role_policy = jsonencode({
     Statement = [{
       Action = "sts:AssumeRole"
       Effect = "Allow"
       Principal = { Service = "eks.amazonaws.com" }
     }]
   })
   ```
9. ✅ aws_iam_role_policy_attachment - Attach AmazonEKSClusterPolicy
10. ✅ aws_iam_role - EKS node group role with trust policy:
    ```
    assume_role_policy = jsonencode({
      Statement = [{
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = { Service = "ec2.amazonaws.com" }
      }]
    })
    ```
11. ✅ aws_iam_role_policy_attachment - AmazonEKSWorkerNodePolicy
12. ✅ aws_iam_role_policy_attachment - AmazonEKS_CNI_Policy
13. ✅ aws_iam_role_policy_attachment - AmazonEC2ContainerRegistryReadOnly
14. ✅ aws_security_group - EKS cluster security group
15. ✅ aws_security_group - Node group security group

**CLUSTER LAYER (2 resources minimum) - ⚠️ MOST CRITICAL!:**
16. ✅ aws_eks_cluster - THE ACTUAL KUBERNETES CLUSTER
    ```
    resource "aws_eks_cluster" "main" {
      name     = "my-eks-cluster"
      role_arn = aws_iam_role.eks_cluster.arn
      version  = "1.28"
      
      vpc_config {
        subnet_ids         = [aws_subnet.private[0].id, aws_subnet.private[1].id]
        endpoint_private_access = true
        endpoint_public_access  = true
      }
      
      depends_on = [
        aws_iam_role_policy_attachment.eks_cluster_policy
      ]
    }
    ```

17. ✅ aws_eks_node_group - THE WORKER NODES
    ```
    resource "aws_eks_node_group" "main" {
      cluster_name    = aws_eks_cluster.main.name
      node_group_name = "main-nodes"
      node_role_arn   = aws_iam_role.eks_node_group.arn
      subnet_ids      = [aws_subnet.private[0].id, aws_subnet.private[1].id]
      
      scaling_config {
        desired_size = 2
        max_size     = 4
        min_size     = 1
      }
      
      instance_types = ["t3.medium"]
      
      depends_on = [
        aws_iam_role_policy_attachment.eks_worker_node_policy,
        aws_iam_role_policy_attachment.eks_cni_policy,
        aws_iam_role_policy_attachment.eks_container_registry_policy
      ]
    }
    ```

⚠️ **CRITICAL MISTAKE TO AVOID:**
DO NOT generate only resources #1-7 (networking) and stop!
You MUST include resources #16-17 (the actual cluster and nodes).
A VPC without a cluster is NOT a Kubernetes cluster!

**MINIMUM RESOURCE COUNT:** 17 resources for a basic EKS cluster
**Typical count:** 20-25 resources for production-ready setup

Azure AKS (Azure Kubernetes Service):
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
1. ✅ azurerm_resource_group - Container for all resources
2. ✅ azurerm_virtual_network - VPC equivalent
3. ✅ azurerm_subnet - Subnet for cluster
4. ✅ azurerm_kubernetes_cluster - THE ACTUAL CLUSTER
   ```
   resource "azurerm_kubernetes_cluster" "main" {
     name                = "my-aks-cluster"
     location            = azurerm_resource_group.main.location
     resource_group_name = azurerm_resource_group.main.name
     dns_prefix          = "myaks"
     
     default_node_pool {
       name       = "default"
       node_count = 2
       vm_size    = "Standard_D2_v2"
     }
     
     identity {
       type = "SystemAssigned"
     }
   }
   ```

**MINIMUM RESOURCE COUNT:** 4 resources

GCP GKE (Google Kubernetes Engine):
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
1. ✅ google_compute_network - VPC
2. ✅ google_compute_subnetwork - Subnet with secondary IP ranges
3. ✅ google_service_account - For node identity
4. ✅ google_container_cluster - THE ACTUAL CLUSTER
   ```
   resource "google_container_cluster" "main" {
     name     = "my-gke-cluster"
     location = "us-central1"
     
     remove_default_node_pool = true
     initial_node_count       = 1
     
     network    = google_compute_network.main.name
     subnetwork = google_compute_subnetwork.main.name
   }
   ```
5. ✅ google_container_node_pool - Node pool
   ```
   resource "google_container_node_pool" "main" {
     cluster    = google_container_cluster.main.name
     location   = "us-central1"
     node_count = 2
     
     node_config {
       machine_type = "e2-medium"
       oauth_scopes = [
         "https://www.googleapis.com/auth/cloud-platform"
       ]
     }
   }
   ```

**MINIMUM RESOURCE COUNT:** 5 resources
"""

# Completeness Checklist
COMPLETENESS_CHECKLIST = """
═══════════════════════════════════════════════════════════════════
🔍 BEFORE RETURNING CODE - COMPLETENESS VALIDATION CHECKLIST:
═══════════════════════════════════════════════════════════════════

Run through this checklist BEFORE outputting your code. If ANY checkbox
is unchecked, GO BACK and add the missing resources!

For "Kubernetes cluster" / "K8s" / "EKS" / "AKS" / "GKE":
□ Network/VPC resource exists
□ Subnets exist (2+ for HA)
□ IAM roles exist (cluster role + node role for AWS)
□ ✅ THE ACTUAL CLUSTER RESOURCE EXISTS (aws_eks_cluster, azurerm_kubernetes_cluster, google_container_cluster)
□ ✅ NODE GROUP/POOL RESOURCE EXISTS (aws_eks_node_group, default_node_pool, google_container_node_pool)
□ Security groups configured (AWS only)
□ All resources have proper dependencies (depends_on if needed)
□ Total resource count is 10+ (AWS EKS should be 15-20)

For "EC2 instance" / "virtual machine" / "web server":
□ VPC exists (or using default_vpc data source)
□ Security group exists with proper ingress rules
□ SSH key pair resources exist (tls_private_key, aws_key_pair, local_file)
□ EC2 instance resource exists with key_name attribute
□ AMI is dynamic (data source, NOT hardcoded ami-xxxxx)
□ Elastic IP exists (if public access required)
□ IAM instance profile attached (for AWS API access)

For "RDS database" / "PostgreSQL" / "MySQL":
□ VPC with private subnets exists
□ DB subnet group exists
□ Security group exists with proper ingress from app tier
□ ✅ RDS INSTANCE RESOURCE EXISTS (aws_db_instance, azurerm_postgresql_server)
□ DB parameter group configured (optional but recommended)
□ Backup retention configured
□ Encryption enabled (storage_encrypted = true)

For "S3 bucket" / "blob storage":
□ ✅ BUCKET RESOURCE EXISTS (aws_s3_bucket, azurerm_storage_account)
□ Versioning enabled (aws_s3_bucket_versioning)
□ Encryption configured (aws_s3_bucket_server_side_encryption_configuration)
□ Public access block configured (aws_s3_bucket_public_access_block)
□ Logging enabled (aws_s3_bucket_logging)

For "load balancer" / "ALB" / "NLB":
□ VPC and subnets exist
□ Security group exists
□ ✅ LOAD BALANCER RESOURCE EXISTS (aws_lb, aws_alb)
□ Target group exists (aws_lb_target_group)
□ Listener exists (aws_lb_listener)
□ Target group attachment exists (links instances/IPs to target group)

For "ECS cluster" / "Fargate" / "containers":
□ VPC and subnets exist
□ ✅ ECS CLUSTER RESOURCE EXISTS (aws_ecs_cluster)
□ Task definition exists (aws_ecs_task_definition)
□ ECS service exists (aws_ecs_service)
□ IAM roles configured (task execution role, task role)
□ Security groups configured

⚠️ CRITICAL RULES:
1. If even ONE checkbox for the user's request type is unchecked, DO NOT return code yet!
2. The checkboxes marked with ✅ are MANDATORY - these are the core resources users expect
3. Generating networking without the actual service resource (cluster, instance, database, etc.) 
   is considered INCOMPLETE and will be rejected
4. When in doubt, generate MORE resources rather than fewer

**COMPLETENESS THRESHOLD BY COMPLEXITY:**
- Simple (EC2, S3): 4-6 resources minimum
- Medium (RDS, ALB): 6-10 resources minimum  
- Complex (EKS, multi-tier): 15-25 resources minimum

If your resource count is below the threshold for the requested complexity,
you are likely missing critical components!
"""

# Database Infrastructure Template
DATABASE_TEMPLATE = """
═══════════════════════════════════════════════════════════════════
DATABASE INFRASTRUCTURE REQUIREMENTS:
═══════════════════════════════════════════════════════════════════

AWS RDS:
━━━━━━━━
1. ✅ aws_vpc - VPC for isolation
2. ✅ aws_subnet - Private subnets (2+ across AZs for Multi-AZ)
3. ✅ aws_db_subnet_group - Logical grouping of subnets for RDS
   ```
   resource "aws_db_subnet_group" "main" {
     name       = "main-db-subnet"
     subnet_ids = [aws_subnet.private[0].id, aws_subnet.private[1].id]
   }
   ```
4. ✅ aws_security_group - Control database access
5. ✅ aws_db_instance - THE ACTUAL DATABASE
   ```
   resource "aws_db_instance" "main" {
     identifier           = "myapp-db"
     engine               = "postgres"
     engine_version       = "15.4"
     instance_class       = "db.t3.micro"
     allocated_storage    = 20
     storage_encrypted    = true  # Security best practice
     
     db_name  = "myappdb"
     username = "admin"
     password = var.db_password  # Use variable, not hardcoded!
     
     db_subnet_group_name   = aws_db_subnet_group.main.name
     vpc_security_group_ids = [aws_security_group.db.id]
     
     backup_retention_period = 7  # Security requirement
     multi_az                = true  # Production best practice
     deletion_protection     = true  # Prevent accidents
     
     skip_final_snapshot = false
     final_snapshot_identifier = "myapp-db-final-snapshot"
   }
   ```

**MINIMUM RESOURCE COUNT:** 5 resources

NEVER generate just a security group and say "database is ready"!
"""

# Multi-Tier Application Template
MULTI_TIER_TEMPLATE = """
═══════════════════════════════════════════════════════════════════
MULTI-TIER APPLICATION REQUIREMENTS:
═══════════════════════════════════════════════════════════════════

For "3-tier app" / "web application" / "full stack":

**NETWORK TIER:**
- VPC with public and private subnets
- Internet Gateway + NAT Gateway
- Route tables

**WEB TIER (Public):**
- Application Load Balancer
- Target group for web servers
- Security group (allow 80/443 from internet)
- EC2 instances OR ECS tasks for web servers

**APPLICATION TIER (Private):**
- EC2 instances OR ECS tasks for app logic
- Security group (allow traffic only from web tier)
- Auto Scaling group (optional but recommended)

**DATABASE TIER (Private):**
- RDS instance OR managed database service
- Security group (allow traffic only from app tier)
- DB subnet group

**MINIMUM RESOURCE COUNT:** 15-20 resources

This is NOT optional - users requesting a "multi-tier app" expect
ALL tiers to be present, not just networking!
"""
