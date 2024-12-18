import { useEffect, useState } from "react";
import { Form, FormControl, FormDescription, FormField, FormItem, FormLabel } from "@/components/ui/form.tsx";
import { z } from "zod";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { Input } from "@/components/ui/input.tsx";
import { Button } from "@/components/ui/button.tsx";
import { Separator } from "@/components/ui/separator.tsx";
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogDescription, DialogFooter } from "@/components/ui/dialog.tsx";
import { ApiClient } from "@/lib/api.ts";
import { authenticationProviderInstance } from "@/lib/authentication-provider.ts";
import { useNavigate } from "react-router-dom";
import { checkServiceNameAvailability } from "@/components/util/CheckServiceNameAvailability.tsx";

const api = new ApiClient(authenticationProviderInstance);

const formSchema = z.object({
  name: z.string().trim().min(1).refine(async (name) => {
    return await checkServiceNameAvailability(name);
  }, {
    message: "Service account name is already taken"
  }),
  datasets: z.array(z.string())
});
type CreateServiceAccountFormSchema = z.infer<typeof formSchema>;

export function CreateService() {
  const form = useForm<CreateServiceAccountFormSchema>({
    resolver: zodResolver(formSchema),
    defaultValues: {
      name: "",
      datasets: []
    }
  });

  const [availableDatasets, setAvailableDatasets] = useState<{ id: string, name: string }[]>([]);
  const [selectedDatasets, setSelectedDatasets] = useState<string[]>([]);
  const [isDialogOpen, setIsDialogOpen] = useState(false);
  const [generatedToken, setGeneratedToken] = useState("");
  const navigate = useNavigate();

  useEffect(() => {
    const fetchData = async () => {
      const datasets = await api.dataSets().getDataSets();
      setAvailableDatasets(datasets.map(ds => ({ id: ds.id?.toString() || '', name: ds.name })));
    };

    fetchData();
  }, []);

  const handleDatasetClick = (datasetId: string) => {
    setSelectedDatasets((prev) =>
      prev.includes(datasetId) ? prev.filter((id) => id !== datasetId) : [...prev, datasetId]
    );
  };

  const handleSubmit = async (values: CreateServiceAccountFormSchema) => {
    console.log("Form submitted with values:", values);
    try {
      const serviceAccount = await api.serviceAccounts().createServiceAccount(values.name, selectedDatasets);
      console.log("Service account created:", serviceAccount);
      setGeneratedToken(serviceAccount.token || "");
      setIsDialogOpen(true);
    } catch (error) {
      console.error("Error creating service account:", error);
    }
  };

  const handleCopyToken = () => {
    navigator.clipboard.writeText(generatedToken);
  };

  const handleDialogClose = () => {
    setIsDialogOpen(false);
    navigate('/api-connection');
  };

  return (
    <>
      <Form {...form}>
        <form onSubmit={form.handleSubmit(handleSubmit)}>
          <FormField
            control={form.control}
            name="name"
            render={({ field }) => (
              <FormItem>
                <FormLabel htmlFor="name">Name</FormLabel>
                <FormControl>
                  <Input id="name" {...field} autoComplete="name" />
                </FormControl>
                <FormDescription>
                  Enter the name of the service account.
                </FormDescription>
              </FormItem>
            )}
          />
          <Separator className="my-6" />
          <FormLabel>Datasets</FormLabel>
          <div className="space-y-2">
            {availableDatasets.map((dataset) => (
              <Button
                key={dataset.id}
                variant={selectedDatasets.includes(dataset.id) ? "default" : "outline"}
                type="button"
                onClick={() => handleDatasetClick(dataset.id)}
              >
                {dataset.name}
              </Button>
            ))}
          </div>
          <Separator className="my-6" />
          <Button type="submit">Create</Button>
        </form>
      </Form>
      <Dialog open={isDialogOpen} onOpenChange={handleDialogClose}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Service Account Created</DialogTitle>
            <DialogDescription>
              The service account has been created successfully. Here is the generated token. You will only see this once, so please copy it to a safe place.
            </DialogDescription>
          </DialogHeader>
          <div className="my-4 p-2 border rounded">
            {generatedToken}
          </div>
          <DialogFooter>
            <Button onClick={handleCopyToken}>Copy Token</Button>
            <Button variant="default" onClick={handleDialogClose}>Close</Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </>
  );
}