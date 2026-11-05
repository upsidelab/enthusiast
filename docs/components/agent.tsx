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
