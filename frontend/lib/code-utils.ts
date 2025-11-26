export function extractResourceSnippet(hcl: string, resourceId: string): string {
  if (!hcl || !resourceId) return "Code snippet not available.";
  const [type, name] = resourceId.split('.');
  if (!type || !name) return "Code snippet not available.";
  // Regex: resource "type" "name" { ... }
  // Greedy match for block, not perfect for nested braces but works for most Terraform
  const regex = new RegExp(`resource\s+"${type}"\s+"${name}"\s*{([\s\S]*?)}\s*`, 'g');
  const match = regex.exec(hcl);
  if (match) {
    return `resource "${type}" "${name}" {${match[1]}}`;
  }
  return "Code snippet not available.";
}
