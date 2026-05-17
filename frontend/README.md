# Compliance Verification System - Frontend

Next.js 14 + React 18 + TypeScript frontend for contract compliance verification.

## Setup

### Installation

1. **Install dependencies**
   ```bash
   npm install
   ```

2. **Configure environment**
   ```bash
   cp .env.local.example .env.local
   # Edit .env.local if needed (default points to localhost:8000)
   ```

### Development Server

```bash
npm run dev
```

Application runs on `http://localhost:3000`

### Build for Production

```bash
npm run build
npm start
```

## Project Structure

```
frontend/
├── src/
│   ├── pages/
│   │   ├── _app.tsx         # Next.js app wrapper
│   │   ├── index.tsx        # Home page
│   │   ├── dashboard.tsx    # Dashboard (optional)
│   │   └── api/             # API routes
│   ├── components/
│   │   ├── Layout.tsx       # Main layout wrapper
│   │   ├── UploadArea.tsx   # File upload component
│   │   ├── ResultsDisplay.tsx # Results display
│   │   └── ComplianceReport.tsx # Report viewer
│   ├── hooks/
│   │   └── useCompliance.ts # API integration hook
│   ├── types/
│   │   └── index.ts         # TypeScript types
│   └── styles/
│       └── globals.css      # Global styles (Tailwind)
├── public/                  # Static assets
├── package.json
├── tsconfig.json
├── next.config.js
├── tailwind.config.js
├── postcss.config.js
└── .env.local.example
```

## Components

### Layout
Main layout wrapper with header, footer, and content area.

```tsx
import { Layout } from '@/components/Layout';

export default function Page() {
  return (
    <Layout title="Page Title">
      {/* Content */}
    </Layout>
  );
}
```

### UploadArea
File upload component with drag-and-drop support.

```tsx
import { UploadArea } from '@/components/UploadArea';

<UploadArea 
  onFileSelect={(file, documentType) => {
    // Handle file upload
  }}
  loading={false}
  error={null}
/>
```

### ResultsDisplay
Displays compliance analysis results.

```tsx
import { ResultsDisplay } from '@/components/ResultsDisplay';

<ResultsDisplay report={complianceReport} loading={false} />
```

## Hooks

### useCompliance
Custom hook for API integration:

```tsx
const {
  loading,
  error,
  report,
  uploadContract,
  verifyCompliance,
  getComplianceReport,
  queryCompliance
} = useCompliance();

// Upload and verify
const response = await uploadContract(file, 'statuts_entreprise');
const report = await verifyCompliance(response.contract_id);

// Get existing report
const existingReport = await getComplianceReport(contractId);

// Interactive Q&A
const answer = await queryCompliance(contractId, 'What are the missing clauses?');
```

## Styling

Uses Tailwind CSS for styling. Custom colors defined in `tailwind.config.js`:

```js
colors: {
  compliance: {
    green: '#10b981',
    red: '#ef4444',
    yellow: '#f59e0b',
    blue: '#3b82f6',
  }
}
```

## Environment Variables

`NEXT_PUBLIC_API_URL` — Backend API URL (default: `http://localhost:8000`)

## API Integration

The frontend communicates with the backend via:

```typescript
const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

// Example API call
axios.post(`${API_URL}/api/v1/contracts/upload`, formData)
```

## Pages

### Home (index.tsx)
Main page with contract upload and compliance results display.

### Dashboard (dashboard.tsx)
Optional dashboard for viewing multiple contracts and reports.

## Type Definitions

All TypeScript types defined in `src/types/index.ts`:

```typescript
interface ComplianceReport {
  contract_id: string;
  overall_status: 'compliant' | 'non_compliant' | 'partially_compliant';
  compliance_score: number;
  issues: ComplianceIssue[];
  // ...
}
```

## Responsive Design

- Mobile-first approach
- Breakpoints: `sm`, `md`, `lg`, `xl`, `2xl`
- Responsive grid layouts for charts and reports

## Performance

- Next.js Image optimization
- Dynamic imports for large components
- Code splitting per route
- CSS-in-JS with Tailwind

## Testing

### Run Tests
```bash
npm test
```

### Build Check
```bash
npm run build
```

### Type Check
```bash
npm run type-check
```

## Linting

### Check Code
```bash
npm run lint
```

### Fix Issues
```bash
npm run lint:fix
```

## Docker

Build image:
```bash
docker build -f ../Dockerfile.frontend -t compliance-frontend .
```

Run container:
```bash
docker run -p 3000:3000 \
  -e NEXT_PUBLIC_API_URL=http://backend:8000 \
  compliance-frontend
```

## Debugging

### Console Logs
Open browser DevTools (F12) → Console tab

### Network Tab
Monitor API requests to the backend

### React DevTools
Install React DevTools extension for Chrome/Firefox

## Common Issues

### CORS Errors
- Check `NEXT_PUBLIC_API_URL` matches backend CORS configuration
- Ensure backend is running and accessible

### Form Submission Issues
- Verify file size doesn't exceed `MAX_UPLOAD_SIZE_MB` (50 MB default)
- Check file format (PDF or DOCX)

### Styling Issues
- Clear Next.js cache: `rm -rf .next`
- Rebuild: `npm run build`

## Deployment

### Vercel (Recommended)
```bash
vercel deploy
```

### Docker
```bash
docker build -f Dockerfile.frontend -t compliance-frontend .
docker run -p 3000:3000 compliance-frontend
```

### Manual
```bash
npm run build
npm start
```

## Next Steps

- [ ] Add real-time progress updates for compliance analysis
- [ ] Implement report export (PDF/DOCX)
- [ ] Add contract history and management
- [ ] Implement user authentication
- [ ] Add dark mode support
- [ ] Create dashboard with analytics
- [ ] Add multi-language support (French/Arabic)
