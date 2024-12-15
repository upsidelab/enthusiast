import { TableCell, TableRow } from "@/components/ui/table.tsx";
import { useState } from "react";
import { ApiClient, Document } from "@/lib/api.ts";
import { authenticationProviderInstance } from "@/lib/authentication-provider.ts";
import { Sheet, SheetContent, SheetHeader, SheetTitle } from "@/components/ui/sheet.tsx";
import { Button } from "@/components/ui/button.tsx";
import { ScrollArea } from "@/components/ui/scroll-area.tsx";
import { useApplicationContext } from "@/lib/use-application-context.ts";
import { PaginatedTable } from "@/components/util/PaginatedTable.tsx";

const api = new ApiClient(authenticationProviderInstance);

export function DocumentTable() {
  const { dataSetId } = useApplicationContext()!;
  const [selectedPreview, setSelectedPreview] = useState<Document | null>(null);

  const extractSlug = (url: string) => {
    if (!URL.canParse(url)) {
      return url;
    }

    return new URL(url).pathname;
  };

  const loadDocuments = async (page: number) => {
    if (dataSetId === null) {
      return;
    }

    setSelectedPreview(null);
    return await api.getDocuments(dataSetId, page);
  };

  return (
    <>
      <PaginatedTable<Document>
        loadItems={loadDocuments}
        itemsReloadDependencies={dataSetId}
        noItemsMessage="No documents available"
        tableFooter="Sync Status: Manual"
        tableHeaders={["URL", "Title", "Content"]}
        tableRow={(item, index) => {
          return (
            <TableRow key={index}>
              <TableCell>
                <Button variant="link" asChild>
                  <a href={item.url} target="_blank">{extractSlug(item.url)}</a>
                </Button>
              </TableCell>
              <TableCell>{item.title}</TableCell>
              <TableCell>
                <Button onClick={() => setSelectedPreview(item)}>Show</Button>
              </TableCell>
            </TableRow>
          )
        }}
      />
      <Sheet open={!!selectedPreview} onOpenChange={() => setSelectedPreview(null)}>
        <SheetContent>
          <SheetHeader>
            <SheetTitle>Preview {selectedPreview?.title}</SheetTitle>
          </SheetHeader>
          <ScrollArea className="h-full w-full pt-4">
            <div>
              {selectedPreview?.content}
            </div>
          </ScrollArea>
        </SheetContent>
      </Sheet>
    </>
  );
}
