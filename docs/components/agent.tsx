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
  agentClassName: string;
  pipName: string;
  agentDescription: string;
  videoUrl?: string;
  agentUseCases?: UseCase[];
  registerAgentModule?: string;
  executionDefinitionClassName?: string;
}

const mdxComponents = getMDXComponents({});
const H1 = mdxComponents.h1;
const H2 = mdxComponents.h2;
const P = mdxComponents.p;
const UL = mdxComponents.ul;
const LI =  mdxComponents.li;

export default async function Agent(props: IntegrationProps) {
  const installationInstructions = await compileMdx(`\`\`\`bash\npoetry add ${props.pipName}\n\`\`\``);
  const buildRegisterInstructionMd = (key: string, module: string) => {
    return `\`\`\`python
AVAILABLE_AGENTS = [
    '${module}.${props.agentClassName}',
]
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
      <MDXRemote compiledSource={installationInstructions} />
      <P>{props.agentDescription}</P>
      <H2>Use Cases</H2>
      <UL>
        {props.agentUseCases?.map((item, idx) => (
          <LI key={idx}>
            <strong>{item.title}</strong> – {item.description}
          </LI>
        ))}
      </UL>
      <H2>Installing {props.name} Agent</H2>
      <P>
        This agent is built on the Enthusiast vertical, so a Suvereo instance with the vertical installed is required.
        If you haven't set it up yet, follow the <Link href="/docs/getting-started/installation">installation guide</Link> first.
      </P>
      <P>
        In the Suvereo starter, add the package to your server package in server/src.
      </P>
      <MDXRemote compiledSource={installationInstructions} />
      <P>
        Then, register the agent in server/config/settings_override.py.
      </P>
      {props.registerAgentModule && <MDXRemote compiledSource={await compileMdx(buildRegisterInstructionMd("AVAILABLE_AGENTS", props.registerAgentModule))}/>}
      {props.registerAgentModule && props.executionDefinitionClassName && (
        <>
          <P>
            To run the agent as an agentic execution through the API, also register its execution definition.
          </P>
          <MDXRemote compiledSource={await compileMdx(`\`\`\`python\nAVAILABLE_AGENTIC_EXECUTION_DEFINITIONS = [\n    '${props.registerAgentModule}.${props.executionDefinitionClassName}',\n]\n\`\`\``)}/>
        </>
      )}
      <P>Then, rebuild and restart the containers (docker compose build && docker compose up) for the newly installed agent to become available.</P>
    </>
  )
}
