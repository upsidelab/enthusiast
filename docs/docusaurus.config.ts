import {themes as prismThemes} from 'prism-react-renderer';
import type {Config} from '@docusaurus/types';
import type * as Preset from '@docusaurus/preset-classic';

// This runs in Node.js - Don't use client-side code here (browser APIs, JSX...)

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
      } satisfies Preset.Options,
    ],
  ],

  themeConfig: {
    navbar: {
      title: 'Enthusiast',
      logo: {
        alt: 'Upside Logo',
        src: 'img/logo.png',
        href: 'https://upsidelab.io'
      },
      items: [
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
              to: '/docs/introduction',
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
