# LMS Frontend - HLD & LLD Course

A modern, feature-rich Learning Management System (LMS) frontend built with Next.js 14, TypeScript, and Tailwind CSS. This application provides a beautiful and intuitive interface for tracking progress through High-Level Design (HLD) and Low-Level Design (LLD) courses.

## Features

### Progress-Focused Design
- **Interactive Dashboard**: Large donut chart showing overall completion percentage
- **Detailed Statistics**:
  - Lessons completed count
  - Time spent and remaining
  - Completion percentage
  - Learning streak tracker
- **Visual Progress**: Charts and progress bars for each week
- **Activity Tracking**: Real-time timer for lesson engagement

### Course Navigation
- **Smart Sidebar**:
  - Collapsible week sections
  - Progress bars for each week
  - Lesson status indicators (completed, bookmarked)
  - Search and filter functionality
- **Lesson Cards**: Show completion status, bookmarks, and estimated time
- **Easy Navigation**: Previous/Next lesson buttons

### Lesson Features
- **YouTube Video Integration**: Embedded video player
- **Markdown Content**: Beautiful rendering with syntax highlighting
- **Note Taking**: Auto-save notes with visual feedback
- **Progress Tracking**:
  - Mark lessons as complete
  - Bookmark important lessons
  - Automatic time tracking
- **Timer**: Active timer showing time spent on current lesson

### UI/UX
- **Fully Responsive**: Optimized for mobile, tablet, and desktop
- **Dark Mode**: Toggle between light and dark themes
- **Beautiful Design**: Built with shadcn/ui components and Tailwind CSS
- **Fast Performance**: Next.js 14 App Router for optimal loading

## Tech Stack

- **Framework**: Next.js 14 (App Router)
- **Language**: TypeScript
- **Styling**: Tailwind CSS
- **UI Components**: shadcn/ui (Radix UI primitives)
- **Charts**: Chart.js with react-chartjs-2
- **Markdown**: react-markdown with remark-gfm
- **Syntax Highlighting**: react-syntax-highlighter
- **Icons**: Lucide React

## Project Structure

```
frontend/
├── app/
│   ├── layout.tsx              # Root layout with theme toggle
│   ├── page.tsx                # Dashboard/home page
│   ├── lesson/[id]/page.tsx    # Dynamic lesson viewer
│   └── globals.css             # Global styles and Tailwind imports
├── components/
│   ├── ui/                     # shadcn/ui components
│   │   ├── button.tsx
│   │   ├── card.tsx
│   │   ├── progress.tsx
│   │   ├── badge.tsx
│   │   ├── textarea.tsx
│   │   ├── separator.tsx
│   │   ├── collapsible.tsx
│   │   ├── input.tsx
│   │   └── switch.tsx
│   ├── Sidebar.tsx             # Course navigation sidebar
│   ├── ProgressDashboard.tsx   # Main dashboard with charts
│   ├── LessonContent.tsx       # Markdown renderer
│   ├── VideoPlayer.tsx         # YouTube embed
│   ├── NotesEditor.tsx         # Auto-save notes editor
│   ├── ProgressBar.tsx         # Reusable progress bar
│   └── LessonCard.tsx          # Lesson item display
├── lib/
│   ├── api.ts                  # API client functions
│   ├── types.ts                # TypeScript interfaces
│   └── utils.ts                # Utility functions
├── package.json
├── tsconfig.json
├── tailwind.config.ts
├── next.config.js
├── postcss.config.js
└── README.md
```

## Prerequisites

- Node.js 18+
- npm or yarn
- Backend API running on `http://localhost:5000` (or configure via env variable)

## Installation

1. **Install dependencies**:
   ```bash
   npm install
   ```

2. **Configure API URL** (optional):
   Create a `.env.local` file if you need to change the backend URL:
   ```bash
   NEXT_PUBLIC_API_URL=http://localhost:5000
   ```

## Development

Run the development server:

```bash
npm run dev
```

Open [http://localhost:3000](http://localhost:3000) in your browser.

The page will auto-reload when you make changes.

## Build for Production

Build the application:

```bash
npm run build
```

Start the production server:

```bash
npm start
```

## API Integration

The frontend expects the following API endpoints from the backend:

### Course Structure
- `GET /api/course-structure` - Get all weeks and lessons
- `GET /api/lessons` - Get all lessons
- `GET /api/lessons/:id` - Get specific lesson

### Progress Tracking
- `GET /api/progress` - Get overall progress and statistics
- `POST /api/lessons/:id/toggle-complete` - Toggle lesson completion
- `POST /api/lessons/:id/toggle-bookmark` - Toggle lesson bookmark
- `POST /api/lessons/:id/time-spent` - Update time spent on lesson

### Notes
- `GET /api/lessons/:id/notes` - Get notes for a lesson
- `POST /api/lessons/:id/notes` - Save/update notes

### Content
- `GET /api/content/:filename` - Get markdown content file

## Key Components

### ProgressDashboard
Displays overall course progress with:
- Donut chart for completion percentage
- Stats cards for key metrics
- Bar chart for weekly progress
- Detailed week-by-week breakdown
- "Continue Learning" call-to-action

### Sidebar
Provides course navigation with:
- Search functionality
- Filter by completion status and bookmarks
- Collapsible week sections
- Progress bars for each week
- Lesson status indicators

### Lesson Page
Individual lesson view featuring:
- YouTube video player (if available)
- Active timer tracking time spent
- Markdown content with code syntax highlighting
- Mark complete toggle
- Bookmark functionality
- Auto-save notes section
- Previous/Next navigation

### NotesEditor
Rich notes taking experience:
- Auto-saves after 2 seconds of inactivity
- Visual save status indicator
- Persists notes to backend
- Clean, distraction-free interface

## Customization

### Theme Colors
Edit `app/globals.css` to customize the color scheme. The app uses CSS variables for theming.

### API URL
Set `NEXT_PUBLIC_API_URL` environment variable to point to your backend.

### Layout
Modify `app/layout.tsx` to adjust the overall layout structure.

## Browser Support

- Chrome (latest)
- Firefox (latest)
- Safari (latest)
- Edge (latest)

## Performance Optimizations

- Next.js automatic code splitting
- Image optimization for YouTube thumbnails
- Client-side caching of course structure
- Efficient re-rendering with React hooks
- Debounced auto-save for notes

## Troubleshooting

### Backend Connection Issues
Ensure your backend is running and the API URL is correct in your environment variables.

### Build Errors
Clear the `.next` cache:
```bash
rm -rf .next
npm run dev
```

### TypeScript Errors
Ensure all dependencies are installed:
```bash
rm -rf node_modules package-lock.json
npm install
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## License

MIT

## Support

For issues or questions, please open an issue on the repository.

---

Built with ❤️ using Next.js 14, TypeScript, and Tailwind CSS
