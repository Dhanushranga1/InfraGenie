/**
 * Security Panel Component
 * 
 * Detailed security violations panel with Checkov policy information
 */

"use client";

import { useState } from 'react';
import { ShieldAlert, ShieldCheck, ChevronDown, ChevronUp, ExternalLink } from 'lucide-react';
import { useProjectStore } from '@/lib/store';
import { cn } from '@/lib/utils';

// Checkov policy descriptions
const CHECKOV_POLICIES: Record<string, { title: string; description: string; fix: string }> = {
  'CKV_AWS_8': {
    title: 'EBS Encryption',
    description: 'Ensure all data stored in EC2 instance EBS volumes is securely encrypted',
    fix: 'Add encrypted = true to root_block_device configuration'
  },
  'CKV_AWS_79': {
    title: 'IMDSv2 Required',
    description: 'Ensure Instance Metadata Service Version 1 is not enabled (enforce IMDSv2)',
    fix: 'Add metadata_options block with http_tokens = "required"'
  },
  'CKV_AWS_126': {
    title: 'Detailed Monitoring',
    description: 'Ensure that detailed monitoring is enabled for EC2 instances',
    fix: 'Add monitoring = true to instance configuration'
  },
  'CKV_AWS_135': {
    title: 'EBS Optimization',
    description: 'Ensure that EC2 is EBS optimized for better performance',
    fix: 'Add ebs_optimized = true to instance configuration'
  },
  'CKV2_AWS_41': {
    title: 'IAM Role Required',
    description: 'Ensure an IAM role is attached to EC2 instance for secure AWS API access',
    fix: 'Create IAM role and attach via iam_instance_profile'
  },
  'CKV_AWS_18': {
    title: 'S3 Access Logging',
    description: 'Ensure S3 bucket has access logging enabled for audit trails',
    fix: 'Add logging configuration to S3 bucket'
  },
  'CKV_AWS_21': {
    title: 'S3 Versioning',
    description: 'Ensure S3 bucket has versioning enabled to prevent accidental data loss',
    fix: 'Enable versioning on S3 bucket'
  },
  'CKV_AWS_19': {
    title: 'S3 Encryption',
    description: 'Ensure S3 buckets have server-side encryption enabled',
    fix: 'Add server_side_encryption_configuration block'
  },
  'CKV_AWS_16': {
    title: 'RDS Encryption',
    description: 'Ensure RDS database has encryption at rest enabled',
    fix: 'Add storage_encrypted = true to RDS instance'
  },
  'CKV_AWS_17': {
    title: 'RDS Backup Retention',
    description: 'Ensure RDS has automated backup with retention period configured',
    fix: 'Set backup_retention_period to at least 7 days'
  },
  'CKV_AWS_129': {
    title: 'RDS Deletion Protection',
    description: 'Ensure RDS has deletion protection enabled',
    fix: 'Add deletion_protection = true to RDS instance'
  },
};

export function SecurityPanel() {
  const securityRisks = useProjectStore((state) => state.securityRisks);
  const [isExpanded, setIsExpanded] = useState(false);

  if (securityRisks.length === 0) {
    return (
      <div className="w-full rounded-lg border border-emerald-500/20 bg-emerald-500/5 p-4">
        <div className="flex items-center gap-3">
          <ShieldCheck className="w-5 h-5 text-emerald-500" />
          <div>
            <h3 className="font-semibold text-emerald-500">All Security Checks Passed</h3>
            <p className="text-sm text-zinc-400 mt-0.5">
              Your infrastructure meets all Checkov security policies
            </p>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="w-full rounded-lg border border-rose-500/20 bg-rose-500/5">
      <button
        onClick={() => setIsExpanded(!isExpanded)}
        className="w-full p-4 flex items-center justify-between hover:bg-rose-500/10 transition-colors rounded-lg"
      >
        <div className="flex items-center gap-3">
          <ShieldAlert className="w-5 h-5 text-rose-500" />
          <div className="text-left">
            <h3 className="font-semibold text-rose-500">
              {securityRisks.length} Security {securityRisks.length === 1 ? 'Issue' : 'Issues'} Found
            </h3>
            <p className="text-sm text-zinc-400 mt-0.5">
              Review and fix these violations before deployment
            </p>
          </div>
        </div>
        {isExpanded ? (
          <ChevronUp className="w-5 h-5 text-zinc-400" />
        ) : (
          <ChevronDown className="w-5 h-5 text-zinc-400" />
        )}
      </button>

      {isExpanded && (
        <div className="px-4 pb-4 space-y-3">
          <div className="h-px bg-rose-500/20 mb-3" />
          
          {securityRisks.map((riskId, index) => {
            const policy = CHECKOV_POLICIES[riskId] || {
              title: riskId,
              description: 'Security policy violation detected',
              fix: 'Review Checkov documentation for remediation steps'
            };

            return (
              <div
                key={index}
                className="p-3 rounded-lg bg-zinc-900/50 border border-zinc-800 hover:border-zinc-700 transition-colors"
              >
                <div className="flex items-start justify-between gap-3">
                  <div className="flex-1">
                    <div className="flex items-center gap-2 mb-1">
                      <code className="text-xs font-mono text-rose-400 bg-rose-500/10 px-2 py-0.5 rounded">
                        {riskId}
                      </code>
                      <h4 className="font-medium text-zinc-200">{policy.title}</h4>
                    </div>
                    
                    <p className="text-sm text-zinc-400 mb-2">
                      {policy.description}
                    </p>
                    
                    <div className="text-sm">
                      <span className="text-emerald-500 font-medium">Fix: </span>
                      <span className="text-zinc-300">{policy.fix}</span>
                    </div>
                  </div>
                  
                  <a
                    href={`https://docs.checkov.io/5.Policy%20Index/${riskId}.html`}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="text-zinc-400 hover:text-zinc-200 transition-colors"
                    title="View policy documentation"
                  >
                    <ExternalLink className="w-4 h-4" />
                  </a>
                </div>
              </div>
            );
          })}

          <div className="mt-4 p-3 rounded-lg bg-amber-500/5 border border-amber-500/20">
            <p className="text-sm text-amber-300">
              <strong>Note:</strong> These security issues do not prevent deployment but should be addressed 
              for production environments. The system attempted 3 automatic fix iterations.
            </p>
          </div>
        </div>
      )}
    </div>
  );
}
