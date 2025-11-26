import { Sheet, SheetContent, SheetHeader, SheetTitle } from "@/components/ui/sheet";
import { Tabs, TabsList, TabsTrigger, TabsContent } from "@/components/ui/tabs";
import { Alert, AlertTitle, AlertDescription } from "@/components/ui/alert";
import { useProjectStore } from "@/lib/store";
import { extractResourceSnippet } from "@/lib/code-utils";
import { useMemo } from "react";

export default function NodeInspector() {
  const selectedNodeId = useProjectStore((s) => s.selectedNodeId);
  const setSelectedNode = useProjectStore((s) => s.setSelectedNode);
  const terraformCode = useProjectStore((s) => s.terraformCode);
  const securityRisks = useProjectStore((s) => s.securityRisks);

  const codeSnippet = useMemo(() => {
    if (!selectedNodeId || !terraformCode) return "Code snippet not available.";
    return extractResourceSnippet(terraformCode, selectedNodeId);
  }, [selectedNodeId, terraformCode]);

  const nodeRisks = useMemo(() => {
    if (!selectedNodeId || !securityRisks) return [];
    return securityRisks.filter((risk) => risk.includes(selectedNodeId.split(".")[0]) || risk.includes(selectedNodeId.split(".")[1]));
  }, [selectedNodeId, securityRisks]);

  return (
    <Sheet open={!!selectedNodeId} onOpenChange={(open) => !open && setSelectedNode(null)}>
      <SheetContent side="right" className="w-[420px] bg-zinc-950 text-zinc-100">
        <SheetHeader>
          <SheetTitle className="flex items-center gap-2">
            <span className="inline-block w-6 h-6 bg-violet-700 rounded-full mr-2" />
            {selectedNodeId}
          </SheetTitle>
        </SheetHeader>
        <Tabs defaultValue="code" className="mt-6">
          <TabsList className="mb-4">
            <TabsTrigger value="code">Code</TabsTrigger>
            <TabsTrigger value="security">Security</TabsTrigger>
            <TabsTrigger value="cost">Cost</TabsTrigger>
          </TabsList>
          <TabsContent value="code">
            <pre className="bg-zinc-900 p-4 rounded-md font-mono text-xs overflow-auto whitespace-pre-wrap">
              {codeSnippet}
            </pre>
          </TabsContent>
          <TabsContent value="security">
            {nodeRisks.length > 0 ? (
              nodeRisks.map((risk, idx) => (
                <Alert key={idx} className="mb-2 bg-zinc-900 border-violet-700">
                  <AlertTitle>Security Risk</AlertTitle>
                  <AlertDescription>{risk}</AlertDescription>
                </Alert>
              ))
            ) : (
              <div className="text-zinc-400">No specific risks detected.</div>
            )}
          </TabsContent>
          <TabsContent value="cost">
            <div className="text-zinc-400">Resource-level cost breakdown coming in v2.</div>
          </TabsContent>
        </Tabs>
      </SheetContent>
    </Sheet>
  );
}
