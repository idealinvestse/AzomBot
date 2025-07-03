# Frontend Teknisk Specifikation - AZOM AI Agent

Detta dokument beskriver den tekniska arkitekturen, projektstrukturen och de designprinciper som används i frontend-applikationen för AZOM AI Agent.

## 1. Teknologistack

Frontend är byggd med en modern, typ-säker stack för att säkerställa hög prestanda, skalbarhet och en god utvecklarupplevelse.

- **Framework:** [React 18](https://reactjs.org/) (med funktionella komponenter och hooks)
- **Byggverktyg:** [Vite](https://vitejs.dev/) (för snabb utveckling och optimerad paketering)
- **Programmeringsspråk:** [TypeScript 5](https://www.typescriptlang.org/) (för typsäkerhet och bättre kodkvalitet)
- **Styling:** [Tailwind CSS](https://tailwindcss.com/) (utility-first CSS-ramverk för snabb UI-utveckling)
- **UI-komponenter:** [shadcn/ui](https://ui.shadcn.com/) (samling av återanvändbara och tillgänglighetsanpassade komponenter)
- **Routing:** [React Router DOM](https://reactrouter.com/) (för deklarativ routing i applikationen)
- **Validering:** [Zod](https://zod.dev/) (för typsäker validering av API-data och formulär)
- **Ikoner:** [Lucide React](https://lucide.dev/)

## 2. Projektstruktur

Projektet följer en funktionsorienterad struktur inom `src/`-katalogen för att hålla relaterad kod samlad.

```
frontend/
├── public/            # Statiska tillgångar
├── src/
│   ├── assets/          # Bilder, fonter och andra statiska filer
│   ├── components/      # Återanvändbara UI-komponenter
│   │   └── ui/          # Bas-komponenter från shadcn/ui
│   ├── hooks/           # Anpassade React-hooks
│   ├── lib/             # Hjälpfunktioner och konstanter (t.ex. cn-utility)
│   ├── pages/           # Huvudsidor/vyer för varje route
│   ├── services/        # Moduler för extern kommunikation (t.ex. API-anrop)
│   ├── styles/          # Globala CSS-stilar
│   ├── types/           # Globala TypeScript-typer och interfaces
│   ├── App.tsx          # Huvudkomponent med routing-konfiguration
│   └── main.tsx         # Applikationens startpunkt
├── .env                 # Miljövariabler (ej versionshanterad)
├── package.json         # Projektberoenden och skript
├── tailwind.config.cjs  # Konfiguration för Tailwind CSS
└── vite.config.ts       # Konfiguration för Vite (inkl. proxy)
```

## 3. Komponentarkitektur

- **Bas-UI (`components/ui`):** Innehåller grundläggande, stil-lösa komponenter som genererats av `shadcn/ui`. Dessa anpassas via Tailwind CSS.
- **Sammansatta komponenter (`components`):** Mer komplexa, applikationsspecifika komponenter som byggs genom att kombinera bas-komponenter. Exempel: `Sidebar`, `ChatMessage`.
- **Sidor (`pages`):** Kompletta vyer som representerar en specifik URL-route. Sidorna ansvarar för att hämta data och sätta ihop layouten med hjälp av sammansatta komponenter.

## 4. State Management

- **Lokalt state:** `useState` och `useReducer` används för att hantera komponent-specifikt state.
- **Globalt state:** För enklare globalt state (t.ex. användarinfo, tema) används `useContext`. För mer komplext globalt state rekommenderas `Zustand` som ett lättviktigt alternativ till Redux.
- **Server-cache:** Data som hämtas från API:et hanteras med `useEffect` och lokalt state. För mer avancerade behov som caching, re-fetching och optimistiska uppdateringar kan `TanStack Query` (tidigare React Query) implementeras.

## 5. API-kommunikation

All kommunikation med backend-API:et centraliseras i `src/services/api.ts`.

- **Centraliserad API-logik:** En `fetch`-wrapper hanterar grundläggande anrop, headers och felhantering.
- **Typsäkerhet med Zod:** Varje API-endpoint har ett Zod-schema för både request och response. Detta säkerställer att data som skickas och tas emot matchar förväntat format, vilket minskar risken för runtime-fel.
- **Proxy:** Vite-konfigurationen (`vite.config.ts`) använder en proxy för att omdirigera alla `/api`-anrop till backend-servern under utveckling. Detta undviker CORS-problem.

## 6. Styling

- **Tailwind CSS:** Används för all styling. Klasser appliceras direkt i JSX-koden. Detta gör det enkelt att bygga och underhålla ett konsekvent designsystem.
- **CSS-variabler:** Globala design-tokens (färger, typsnitt, avstånd) definieras i `src/styles/globals.css` och i `tailwind.config.cjs` för att säkerställa enhetlighet.
- **`cn`-utility:** En hjälpfunktion i `src/lib/utils.ts` används för att villkorligt slå samman Tailwind-klasser, vilket är särskilt användbart för komponentvarianter.

## 7. Routing

Navigering hanteras av `react-router-dom`. Alla tillgängliga routes definieras i `App.tsx` inuti en `Routes`-komponent. Detta ger en central och tydlig överblick över applikationens sidstruktur.

## 8. Utvecklingsmiljö

För att starta utvecklingsmiljön:

1.  **Installera beroenden:**
    ```bash
    npm install
    ```

2.  **Starta Vite-servern:**
    ```bash
    npm run dev
    ```

Servern startas med Hot Module Replacement (HMR), vilket innebär att ändringar i koden omedelbart syns i webbläsaren utan att sidan behöver laddas om.
