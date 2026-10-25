w-Level-System-Design/Live_Deployed_Websites/README.md
# Live Deployed Websites

Two live projects that show my frontend implementation and product thinking. Open the demos to explore, then use the notes below to see how they were built.

## Portfolio

**Live demo:** [pavan9753.github.io/AI-agent-work-and-coding-profiles](https://pavan9753.github.io/AI-agent-work-and-coding-profiles/)

**Source:** [AI-agent-work-and-coding-profiles](https://github.com/pavan9753/AI-agent-work-and-coding-profiles)

### Tech stack

- React and JavaScript for the interactive single-page experience
- Vite for local development and production builds
- Tailwind CSS with custom CSS for responsive styling and visual details
- Lucide React for interface icons
- GitHub Pages for hosting, published with `gh-pages`

### How it is built

1. React components assemble the portfolio into clear sections: introduction, experience, selected work, skills, recognition, and contact.
2. Project, experience, and profile information is organized as data and rendered into consistent page sections and cards.
3. Responsive CSS and Tailwind utilities adapt the layout and navigation for smaller screens; React state controls the mobile menu and copy-email interaction.
4. Vite creates the static production site. Its base path is configured for the GitHub Pages project URL, and the generated `dist` directory is published to the `gh-pages` branch.

### What to look for

- A recruiter-friendly summary of engineering experience, projects, and skills
- A résumé download and links to professional and coding profiles
- Recognition and project details presented in a responsive, navigable layout

## Fitness Tracker

**Live demo:** [pavan9753.github.io/fitness-tracker](https://pavan9753.github.io/fitness-tracker/)

**Source:** [fitness-tracker](https://github.com/pavan9753/fitness-tracker)

### Tech stack

- React and JavaScript for interactive dashboard components
- Vite for development and production builds
- Tailwind CSS for responsive layouts and utility styling, with custom theme configuration
- Lucide React for activity and navigation icons
- GitHub Pages for hosting, published with `gh-pages`

### How it is built

1. A responsive dashboard presents daily activity metrics, weekly activity, hydration, and recent workouts.
2. React state drives workout logging, validation messages, the water counter, and the mobile navigation menu.
3. Small reusable components keep dashboard cards and section headings visually consistent. A lightweight SVG/CSS chart visualizes the sample weekly activity data.
4. Vite builds the static site and `gh-pages` publishes the generated `dist` directory. The current demo keeps sample workouts and hydration state in the browser session; it does not connect to a backend.

### What to look for

- A polished, responsive fitness dashboard with clear metric hierarchy
- Working interactions for logging a workout and adding water
- Thoughtful empty/error feedback and mobile navigation

## Build and run locally

Each project is a standalone Vite app. From its source repository, enter the app directory and run:

```bash
npm install
