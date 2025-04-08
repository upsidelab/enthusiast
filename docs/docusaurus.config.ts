import {themes as prismThemes} from 'prism-react-renderer';
import type {Config} from '@docusaurus/types';
import type * as Preset from '@docusaurus/preset-classic';
import type { Options as GtagPluginOptions } from "@docusaurus/plugin-google-gtag/lib/options";

// This runs in Node.js - Don't use client-side code here (browser APIs, JSX...)

function getGTagConfig() : GtagPluginOptions | undefined {
  if (process.env.GTAG_ID) {
    return {
      trackingID: process.env.GTAG_ID,
      anonymizeIP: true
    }
  }
  return undefined;
}

const config: Config = {
  title: 'Enthusiast',
  tagline: 'Your Open Source E-Commerce AI Agent',
  favicon: 'img/favicon.ico',

  url: 'https://upsidelab.io/',
  baseUrl: '/tools/enthusiast/',

  onBrokenLinks: 'throw',
  onBrokenMarkdownLinks: 'warn',

  i18n: {
    defaultLocale: 'en',
    locales: ['en'],
  },

  presets: [
    [
      'classic',
      {
        docs: {
          sidebarPath: './sidebars.ts',
        },
        theme: {
          customCss: './src/css/custom.css',
        },
        gtag: getGTagConfig(),
      } satisfies Preset.Options,
    ],
  ],

  themeConfig: {
    navbar: {
      title: 'enthusiast.',
      logo: {
        alt: 'Enthusiast',
        src: 'img/logo.png',
        href: '/tools/enthusiast'
      },
      items: [
        {
          type: 'dropdown',
          label: 'Features',
          position: 'left',
          items: [
            {
              label: 'Internal Knowledge Base',
              to: '/features/internal-knowledge-base',
            },
            {
              label: 'Customer Support',
              to: '/features/customer-support',
            },
            {
              label: 'Content Creation',
              to: '/features/content-creation',
            },
            {
              label: 'Product Recommendations',
              to: '/features/product-recommendations',
            },
            {
              label: 'Content Validation',
              to: '/features/content-validation',
            },
            {
              label: 'Open Source AI for E-Commerce',
              to: '/features/open-source-ai-for-ecommerce',
            },
            {
              label: 'RAG for E-Commerce',
              to: '/features/rag-for-ecommerce',
            },
          ],
        },
        {
          type: 'docSidebar',
          sidebarId: 'docsSidebar',
          position: 'left',
          label: 'Documentation',
        },
        {
          href: 'https://github.com/upsidelab/enthusiast',
          label: 'Github',
          position: 'right',
        },
      ],
    },
    footer: {
      style: 'dark',
      links: [
        {
          title: 'Docs',
          items: [
            {
              label: 'Docs',
              to: '/docs',
            },
          ],
        },
        {
          title: 'More',
          items: [
            {
              label: 'Blog',
              to: 'https://upsidelab.io/blog',
            },
            {
              label: 'GitHub',
              href: 'https://github.com/upsidelab/enthusiast',
            },
          ],
        },
      ],
      copyright: `Copyright © ${new Date().getFullYear()} Upside Lab sp. z o.o.`,
    },
    prism: {
      theme: prismThemes.github,
      darkTheme: prismThemes.dracula,
    },
  } satisfies Preset.ThemeConfig,
};

export default config;
