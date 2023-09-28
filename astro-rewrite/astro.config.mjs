import { defineConfig } from 'astro/config';
import starlight from '@astrojs/starlight';

// https://astro.build/config
export default defineConfig({
	site: 'https://as.krauch.net',
	integrations: [
		starlight({
			title: 'Autonome Systeme',
			social: {
				github: 'https://github.com/withastro/starlight',
			},
			sidebar: [
				{
					label: 'Überblick',
					autogenerate: { directory: 'overview' },
					
				},
				{
					label: 'Teil 1',
					autogenerate: { directory: 'teil_1' },
				},
			],
		}),
	],
});
