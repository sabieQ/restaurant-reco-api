# Restaurant Recommender Frontend (Next.js)

Next.js-based frontend for the Restaurant Recommendation API.

## Prerequisites
- Node.js (v18 or higher)
- npm or yarn

## Installation

```bash
cd frontend
npm install
```

## Development

Start the development server:
```bash
npm run dev
```

The app will open at [http://localhost:3000](http://localhost:3000)

## Backend Setup

Ensure the backend API is running:
```bash
# From the project root
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

The backend should be running at [http://localhost:8000](http://localhost:8000)

## Features

- **Location-based search**: Find restaurants by city or area
- **Budget filtering**: Low, Medium, or High budget options
- **Cuisine preferences**: Specify preferred cuisine type
- **Rating filters**: Set minimum rating requirements
- **AI-powered explanations**: LLM-generated personalized recommendations
- **Fallback support**: Graceful degradation if LLM services are unavailable
- **Modern UI**: Built with Next.js and Tailwind CSS
- **TypeScript**: Full type safety
- **Responsive design**: Works on all screen sizes

## API Integration

The frontend communicates with the backend via the v1 API endpoint:
- URL: `http://localhost:8000/api/v1/recommendations`
- Method: POST
- Content-Type: application/json

## Build for Production

```bash
npm run build
npm start
```

The production build will be optimized and ready for deployment.
