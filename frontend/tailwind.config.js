/** @type {import('tailwindcss').Config} */
export default {
    content: [
        "./index.html",
        "./src/**/*.{js,ts,jsx,tsx}",
    ],
    theme: {
        extend: {
            colors: {
                // Custom monochrome/dark palette
                background: '#0a0a0a',
                surface: '#121212',
                primary: '#ffffff',
                secondary: '#a1a1aa',
                accent: '#00ced1', // Dark Turksish / Cyan
                'accent-glow': 'rgba(0, 206, 209, 0.5)',
            },
        },
    },
    plugins: [],
}
