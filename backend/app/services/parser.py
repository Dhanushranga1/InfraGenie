import hcl2
from typing import Dict, Any, List
import re
import logging

logger = logging.getLogger(__name__)

def parse_hcl_to_graph(hcl_content: str) -> dict:
    """
    Parse Terraform HCL code and extract infrastructure graph with relationships.
    Detects parent-child relationships and connections between resources.
    """
    try:
        parsed = hcl2.loads(hcl_content)
    except Exception as e:
        logger.error(f"Failed to parse HCL: {e}")
        return {"nodes": [], "edges": []}
    
    nodes = []
    edges = []
    resource_lookup = {}
    
    # Extract all resources
    for block in parsed.get('resource', []):
        for r_type, r_dict in block.items():
            for r_name, r_props in r_dict.items():
                node_id = f"{r_type}.{r_name}"
                resource_lookup[node_id] = {
                    "type": r_type,
                    "name": r_name,
                    "props": r_props
                }
                
                # Detect parent relationships (VPC, Subnet hierarchy)
                parent_id = None
                
                # If this has a vpc_id, it belongs to that VPC
                if 'vpc_id' in r_props:
                    vpc_ref = r_props['vpc_id']
                    if isinstance(vpc_ref, str):
                        # Extract VPC resource reference
                        match = re.search(r'(aws_vpc\.[a-z_][a-z0-9_]*)', vpc_ref)
                        if match:
                            parent_id = match.group(1)
                
                # If this has a subnet_id, it belongs to that Subnet
                if 'subnet_id' in r_props and not parent_id:
                    subnet_ref = r_props['subnet_id']
                    if isinstance(subnet_ref, str):
                        match = re.search(r'(aws_subnet\.[a-z_][a-z0-9_]*)', subnet_ref)
                        if match:
                            parent_id = match.group(1)
                
                nodes.append({
                    "id": node_id,
                    "type": r_type,
                    "label": r_name,
                    "parent": parent_id,
                    "properties": r_props
                })
                
                logger.info(f"  Node: {node_id} (parent: {parent_id or 'none'})")
    
    # Detect relationships and create edges
    edge_counter = 0
    
    for node in nodes:
        node_id = node["id"]
        props = resource_lookup[node_id]["props"]
        
        # Find all references to other resources in properties
        references = extract_resource_references(props)
        
        for ref in references:
            ref_id = f"{ref['type']}.{ref['name']}"
            if ref_id in resource_lookup:
                edge_counter += 1
                edges.append({
                    "id": f"edge_{edge_counter}",
                    "source": ref_id,
                    "target": node_id,
                    "label": ref.get('attribute', '')
                })
                logger.info(f"  Edge: {ref_id} -> {node_id} ({ref.get('attribute', '')})")
    
    # Add implicit relationships for better visualization
    # These help show logical groupings even without explicit references
    implicit_edges = create_implicit_edges(nodes, resource_lookup)
    for implicit_edge in implicit_edges:
        edge_counter += 1
        edges.append({
            "id": f"edge_{edge_counter}",
            "source": implicit_edge["source"],
            "target": implicit_edge["target"],
            "label": implicit_edge.get("label", ""),
        })
        logger.info(f"  Implicit Edge: {implicit_edge['source']} -> {implicit_edge['target']}")
    
    logger.info(f"Parsed graph: {len(nodes)} nodes, {len(edges)} edges ({len(implicit_edges)} implicit)")
    return {"nodes": nodes, "edges": edges}


def create_implicit_edges(nodes: List[Dict], resource_lookup: Dict) -> List[Dict]:
    """
    Create implicit edges for better visualization when explicit references don't exist.
    Example: EC2 instances can implicitly connect to S3 buckets, VPCs contain subnets, etc.
    """
    implicit_edges = []
    
    # Group resources by type
    vpcs = [n for n in nodes if n["type"] == "aws_vpc"]
    subnets = [n for n in nodes if n["type"] == "aws_subnet"]
    instances = [n for n in nodes if n["type"] in ["aws_instance", "aws_ec2_instance"]]
    security_groups = [n for n in nodes if n["type"] == "aws_security_group"]
    s3_buckets = [n for n in nodes if n["type"] == "aws_s3_bucket"]
    igws = [n for n in nodes if n["type"] == "aws_internet_gateway"]
    
    # VPC -> Subnet (if no explicit reference)
    if vpcs and subnets and len(vpcs) == 1:
        vpc = vpcs[0]
        for subnet in subnets:
            # Only if no explicit vpc_id reference already exists
            implicit_edges.append({
                "source": vpc["id"],
                "target": subnet["id"],
                "label": "contains"
            })
    
    # VPC -> Internet Gateway (if no explicit reference)
    if vpcs and igws and len(vpcs) == 1:
        vpc = vpcs[0]
        for igw in igws:
            implicit_edges.append({
                "source": vpc["id"],
                "target": igw["id"],
                "label": "attached"
            })
    
    # Security Group -> EC2 Instance (if they exist together)
    if security_groups and instances:
        for sg in security_groups:
            for instance in instances:
                # Check if this instance doesn't already reference this SG
                props = resource_lookup[instance["id"]]["props"]
                refs = extract_resource_references(props)
                has_sg_ref = any(r["type"] == "aws_security_group" for r in refs)
                
                if not has_sg_ref:
                    implicit_edges.append({
                        "source": sg["id"],
                        "target": instance["id"],
                        "label": "protects"
                    })
    
    return implicit_edges


def extract_resource_references(obj: Any, path: str = "") -> List[Dict[str, str]]:
    """
    Recursively extract Terraform resource references from properties.
    Supports: aws_vpc.main.id, ${aws_subnet.public.id}, etc.
    """
    references = []
    
    if isinstance(obj, str):
        # Pattern 1: ${resource_type.resource_name.attribute}
        matches = re.findall(r'\$\{(aws_[a-z_]+)\.([a-z_][a-z0-9_]*)\.([a-z_]+)\}', obj)
        for match in matches:
            references.append({
                "type": match[0],
                "name": match[1],
                "attribute": match[2]
            })
        
        # Pattern 2: resource_type.resource_name.attribute (direct reference)
        matches = re.findall(r'(aws_[a-z_]+)\.([a-z_][a-z0-9_]*)\.([a-z_]+)', obj)
        for match in matches:
            references.append({
                "type": match[0],
                "name": match[1],
                "attribute": match[2]
            })
    
    elif isinstance(obj, dict):
        for key, value in obj.items():
            references.extend(extract_resource_references(value, f"{path}.{key}"))
    
    elif isinstance(obj, list):
        for item in obj:
            references.extend(extract_resource_references(item, path))
    
    return references
