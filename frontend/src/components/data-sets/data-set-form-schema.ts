import { z } from "zod";

export const formSchema = z.object({
  name: z.string().trim().min(1),
  languageModelProvider: z.string().min(1),
  languageModel: z.string().min(1),
  embeddingProvider: z.string().min(1),
  embeddingModel: z.string().min(1),
  embeddingVectorSize: z.coerce.number().min(1).max(3072),
});

export type DataSetFormSchema = z.infer<typeof formSchema>;
