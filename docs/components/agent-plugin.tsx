import { useMDXComponents as getMDXComponents } from "@/mdx-components";
import { MDXRemote } from "nextra/mdx-remote";
import { compileMdx } from "nextra/compile";
import Link from "next/link";
import Image from "next/image";

export interface IntegrationProps {
  name: string;
  integrationKey: string;
  pipName: string;
  agentDescription: string;
  registerAgentModule?: string;
}

const mdxComponents = getMDXComponents({});
const H1 = mdxComponents.h1;
const H2 = mdxComponents.h2;
const P = mdxComponents.p;

export default async function AgentPlugin(props: IntegrationProps) {
  const installationInstructions = await compileMdx(`\`\`\`bash\npoetry add ${props.pipName}\n\`\`\``);
  const buildRegisterInstructionMd = (key: string, module: string) => {
    return `\`\`\`python
AVAILABLE_AGENTS = {
    "${props.integrationKey}": {
        "name": "${props.name}",
        "agent_directory_path": "${module}"
    },
}
\`\`\``;
  }

  return (
    <>
      <Image className="x:py-4" src={`/tools/enthusiast/img/integrations/${props.integrationKey}.png`} alt={props.name} width={256} height={256} />
      <H1 className="x:hidden">{props.name}</H1>
      <H2>Description</H2>
        <P>{props.agentDescription}</P>
      <H2>Installation</H2>
      <P>
        Run the following command inside your application directory.<br />
        If you're using <Link href="/docs/getting-started/installation">Enthusiast Starter</Link>, that's inside enthusiast-starter/src/
      </P>
      <MDXRemote compiledSource={installationInstructions} />
      <P>
        Then, register the integration in your config/settings_override.py.
      </P>
      {props.registerAgentModule && <MDXRemote compiledSource={await compileMdx(buildRegisterInstructionMd("AVAILABLE_AGENTS", props.registerAgentModule))}/>}
    </>
  )
}
