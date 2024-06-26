import { defineConfig } from 'astro/config';
import starlight from '@astrojs/starlight';

// https://astro.build/config
export default defineConfig({
	site: 'https://as.krauch.net',
	integrations: [
		starlight({
			title: 'Autonome Systeme',
			social: {
				github: 'https://github.com/Lennart01/AutonomeSysteme',
			},
			sidebar: [
				{
					label: 'Semesterplan',
					autogenerate: { directory: 'semesterplan' },
				
				},
				{
					label: 'Überblick',
					autogenerate: { directory: 'overview' },
					
				},
				{
					label: 'Teil 1',
					autogenerate: { directory: 'teil_1' },
				},
				{
					label: 'Teil 2',
					autogenerate: { directory: 'teil_2' },
				},
				{
					label: 'UPPAAL Labor',
					autogenerate: { directory: 'uppaal' },
				},
			],
		}),
	],
});
