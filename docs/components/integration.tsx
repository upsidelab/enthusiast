import { useMDXComponents as getMDXComponents } from "@/mdx-components";
import { MDXRemote } from "nextra/mdx-remote";
import { compileMdx } from "nextra/compile";
import Link from "next/link";
import Image from "next/image";

export interface IntegrationProps {
  name: string;
  integrationKey: string;
  pipName: string;
  registerProductModule?: string;
  registerDocumentModule?: string;
  registerLanguageModelModule?: string;
  registerEmbeddingsModule?: string;
  envVariables?: string[]
}

const mdxComponents = getMDXComponents({});
const H1 = mdxComponents.h1;
const H2 = mdxComponents.h2;
const P = mdxComponents.p;

export default async function Integration(props: IntegrationProps) {
  const installationInstructions = await compileMdx(`\`\`\`bash\npoetry add ${props.pipName}\n\`\`\``);
  const buildRegisterDictInstructionMd = (key: string, module: string) => {
    return `\`\`\`python\n${key} = {\n    ...\n    "${props.name}": "${module}",\n}\n\`\`\``;
  }
  const buildRegisterListInstructionMd = (key: string, module: string) => {
    return `\`\`\`python\n${key} = [\n    ...\n    "${module}",\n]\n\`\`\``;
  }
  const buildEnvInstructionMd = (keys: string[]) => {
      const lines = keys.map((key) => `${key}=<value_here>`).join("\n");
      return `\`\`\`python\n${lines}\n\`\`\``;
    };

  return (
    <>
      <Image className="x:py-4" src={`/tools/enthusiast/img/integrations/${props.integrationKey}.png`} alt={props.name} width={256} height={256} />
      <H1 className="x:hidden">{props.name}</H1>
      <H2>Installation</H2>
      <P>
        Run the following command inside your application directory.<br />
        If you're using <Link href="/docs/getting-started/installation">Enthusiast Starter</Link>, that's inside enthusiast-starter/src/
      </P>
      <MDXRemote compiledSource={installationInstructions} />
    {props.envVariables && (
      <>
        <P>
          Set variables inside .env file.
        </P>
        <MDXRemote
          compiledSource={await compileMdx(buildEnvInstructionMd(props.envVariables))}
        />
      </>
    )}
      <P>
        Then, register the integration in your config/settings_override.py.
      </P>
      {props.registerProductModule && <MDXRemote compiledSource={await compileMdx(buildRegisterListInstructionMd("CATALOG_PRODUCT_SOURCE_PLUGINS", props.registerProductModule))}/>}
      {props.registerDocumentModule && <MDXRemote compiledSource={await compileMdx(buildRegisterListInstructionMd("CATALOG_DOCUMENT_SOURCE_PLUGINS", props.registerDocumentModule))}/>}
      {props.registerLanguageModelModule && <MDXRemote compiledSource={await compileMdx(buildRegisterDictInstructionMd("CATALOG_LANGUAGE_MODEL_PROVIDERS", props.registerLanguageModelModule))}/>}
      {props.registerEmbeddingsModule && <MDXRemote compiledSource={await compileMdx(buildRegisterDictInstructionMd("CATALOG_EMBEDDING_PROVIDERS", props.registerEmbeddingsModule))}/>}
    </>
  )
}
