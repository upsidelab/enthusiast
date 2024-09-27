import { Table, TableBody, TableCaption, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table.tsx";
import { useEffect, useState } from "react";
import { SkeletonLoader } from "@/components/util/SkeletonLoader.tsx";
import { Skeleton } from "@/components/ui/skeleton.tsx";
import { ApiClient, Content } from "@/lib/api.ts";
import { authenticationProviderInstance } from "@/lib/authentication-provider.ts";
import { Sheet, SheetContent, SheetHeader, SheetTitle } from "@/components/ui/sheet.tsx";
import { Button } from "@/components/ui/button.tsx";
import { ScrollArea } from "@/components/ui/scroll-area.tsx";
import { useApplicationContext } from "@/lib/use-application-context.ts";

const api = new ApiClient(authenticationProviderInstance);

export function ContentTable() {
  const [contents, setContents] = useState<Content[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const { dataSetId } = useApplicationContext()!;
  const [selectedPreview, setSelectedPreview] = useState<Content | null>(null);

  const extractSlug = (url: string) => {
    if (!URL.canParse(url)) {
      return url;
    }

    return new URL(url).pathname;
  };

  useEffect(() => {
    if (dataSetId === null) {
      return;
    }

    const loadData = async () => {
      const apiContents = await api.getContents(dataSetId);
      setContents(apiContents);
      setSelectedPreview(null);
      setIsLoading(false);
    };

    loadData();
  }, [dataSetId]);

  return (
    <SkeletonLoader skeleton={<Skeleton className="w-full h-[100px]"/>} isLoading={isLoading}>
      <Table>
        <TableCaption>Sync Status: Manual</TableCaption>
        <TableHeader>
          <TableRow>
            <TableHead>URL</TableHead>
            <TableHead>Title</TableHead>
            <TableHead>Content</TableHead>
          </TableRow>
        </TableHeader>
        <TableBody>
          {contents.map((item, index) => (
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
          ))}
        </TableBody>
      </Table>
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
    </SkeletonLoader>
  );
}
