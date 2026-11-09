import { useMDXComponents as getMDXComponents } from "@/mdx-components";
import { MDXRemote } from "nextra/mdx-remote";
import { compileMdx } from "nextra/compile";
import Link from "next/link";
import Image from "next/image";
import { ReactNode } from "react";

export interface IntegrationProps {
  name: string;
  description?: string | ReactNode;
  integrationKey: string;
  pipName: string;
  registerProductModule?: string;
  registerDocumentModule?: string;
  registerECommerceIntegrationModule?: string;
  envVariables?: string[]
}

const mdxComponents = getMDXComponents({});
const H1 = mdxComponents.h1;
const H2 = mdxComponents.h2;
const P = mdxComponents.p;

export default async function Integration(props: IntegrationProps) {
  const installationInstructions = await compileMdx(`\`\`\`bash\npoetry add ${props.pipName}\n\`\`\``);
  const buildRegisterListInstructionMd = (key: string, module: string) => {
    return `\`\`\`python\n${key} = [\n    ...\n    "${module}",\n]\n\`\`\``;
  }
  const buildEnvInstructionMd = (keys: string[]) => {
      const lines = keys.map((key) => `${key}=<value_here>`).join("\n");
      return `\`\`\`python\n${lines}\n\`\`\``;
    };

  const registerModules = [
    props.registerProductModule,
    props.registerDocumentModule,
    props.registerECommerceIntegrationModule,
  ].filter((module): module is string => !!module);
  const registerInstructions = await Promise.all(
    registerModules.map(async (module) => ({
      module,
      compiledSource: await compileMdx(buildRegisterListInstructionMd("CATALOG_INTEGRATION_PLUGINS", module)),
    }))
  );

  return (
    <>
      <H1>{props.name} Integration</H1>
      <Image className="x:py-4" src={`/tools/enthusiast/img/integrations/${props.integrationKey}.png`} alt={props.name} width={256} height={256} />
      {props.description && <P>{props.description}</P>}
      <H2>Installation</H2>
      <P>
        This integration is part of the Enthusiast domain definition, so a Suvereo instance with the domain definition installed is required.
        If you haven't set it up yet, follow the <Link href="/docs/getting-started/installation">installation guide</Link> first.
      </P>
      <P>
        In the Suvereo starter, add the package to your server package in server/src.
      </P>
      <MDXRemote compiledSource={installationInstructions} />
    {props.envVariables && (
      <>
        <P>
          Set the variables in server/config/.env.
        </P>
        <MDXRemote
          compiledSource={await compileMdx(buildEnvInstructionMd(props.envVariables))}
        />
      </>
    )}
      <P>
        Then, register the integration in server/config/settings_override.py.
      </P>
      {registerInstructions.map(({ module, compiledSource }) => (
        <MDXRemote key={module} compiledSource={compiledSource} />
      ))}
      <P>Then, rebuild and restart the containers (docker compose build && docker compose up) for the newly installed plugin to become available.</P>
      <P>Finally, sign in to the Suvereo admin UI, go to the Integrations tab and configure the required credentials.</P>
    </>
  )
}
