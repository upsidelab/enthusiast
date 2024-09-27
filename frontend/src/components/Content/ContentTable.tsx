import { Table, TableBody, TableCaption, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table.tsx";
import { useEffect, useState } from "react";
import { SkeletonLoader } from "@/components/util/SkeletonLoader.tsx";
import { Skeleton } from "@/components/ui/skeleton.tsx";
import { ApiClient, Content } from "@/lib/api.ts";
import { authenticationProviderInstance } from "@/lib/authentication-provider.ts";

const api = new ApiClient(authenticationProviderInstance);

export function ContentTable() {
  const [contents, setContents] = useState<Content[]>([]);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    const loadData = async () => {
      const apiContents = await api.getContents(1);
      setContents(apiContents);
      setIsLoading(false);
    };

    loadData();
  }, []);

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
              <TableCell>{item.url}</TableCell>
              <TableCell>{item.title}</TableCell>
              <TableCell>{item.content}</TableCell>
            </TableRow>
          ))}
        </TableBody>
      </Table>
    </SkeletonLoader>
  );
}
