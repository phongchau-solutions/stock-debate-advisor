## Stock Debate Advisor v6 Frontend

Production-ready React + Vite + TypeScript frontend for the Stock Debate Advisor.

### Features

- **Responsive layout** with `Header`, `Sidebar`, `Footer`, and routed pages for Financials, Stocks, Debate & Analysis, News, and Watchlist.
- **Tailwind CSS** with **light/dark theme toggle** and **FontAwesome Free** icons.
- **Jotai** state for theme and selected symbol shared across pages.
- **Storybook** stories for core layout components.
- **Testing**: Jest unit tests, Cypress e2e, and Playwright cross-browser tests.

### Scripts

- `npm run dev` – start Vite dev server
- `npm run build` – production build
- `npm run preview` – preview production build
- `npm run lint` – run eslint
- `npm test` / `npm run test:watch` – Jest unit tests
- `npm run storybook` / `npm run build-storybook` – Storybook
- `npm run cypress` / `npm run cypress:run` – Cypress e2e (requires `npm run dev` in another terminal)
- `npm run playwright:test` – Playwright tests (requires `npm run dev` in another terminal)

### Getting Started

```bash
cd v6/frontend
npm install
npm run dev
```
