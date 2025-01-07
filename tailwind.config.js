
/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    './templates/**/*.html',
    './wagtail_templates/**/*.html',
    './static/js/**/*.js',
    './wagtail_blocks/**/*.html', // Add paths to Wagtail block templates
  ],
  theme: {
      extend: {},
  },
  plugins: [],
};