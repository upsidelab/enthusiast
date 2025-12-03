import { useMDXComponents as getMDXComponents } from "@/mdx-components";
import { MDXRemote } from "nextra/mdx-remote";
import { compileMdx } from "nextra/compile";
import Link from "next/link";

export interface UseCase {
  title: string;
  description: string;
}
export interface IntegrationProps {
  name: string;
  integrationKey: string;
  pipName: string;
  agentDescription: string;
  videoUrl?: string;
  agentUseCases?: UseCase[];
  registerAgentModule?: string;
}

const mdxComponents = getMDXComponents({});
const H1 = mdxComponents.h1;
const H2 = mdxComponents.h2;
const P = mdxComponents.p;
const UL = mdxComponents.ul;
const LI =  mdxComponents.li;

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
      <H1>{props.name} Agent</H1>
      {props.videoUrl &&
        <div className="x:my-4">
          <video autoPlay={true} controls={true} src={props.videoUrl} />
        </div>
      }
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
      <H2>Use cases</H2>
        <UL>
          {props.agentUseCases?.map((item, idx) => (
            <LI key={idx}>
              <strong>{item.title}</strong> – {item.description}
            </LI>
          ))}
        </UL>
    </>
  )
}
