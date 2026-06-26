import { ENDPOINTS } from './endpoints';

// Configuration-driven dashboard cards layout
export const DASHBOARD_CARDS = [
  {
    id: 'health',
    type: 'health-pulse',
    endpoint: ENDPOINTS.health,
    gridArea: 'span 1 / span 1',
    label: 'System Health',
    description: 'Status of local FastAPI server'
  },
  {
    id: 'total-jobs',
    type: 'stat-card',
    endpoint: ENDPOINTS.jobsEmbeddingStatus,
    dataKey: 'total_jobs',
    gridArea: 'span 1 / span 1',
    label: 'Total Jobs Catalogs',
    iconName: 'Briefcase',
    description: 'Active job postings in database'
  },
  {
    id: 'embedding-progress',
    type: 'progress-ring',
    endpoint: ENDPOINTS.jobsEmbeddingStatus,
    gridArea: 'span 1 / span 2',
    label: 'Job Embeddings Status',
    description: 'Background vector generation progress'
  },
  {
    id: 'pipeline-stats',
    type: 'donut-chart',
    endpoint: ENDPOINTS.metrics,
    dataKey: 'pipeline_status_counts',
    gridArea: 'span 2 / span 2',
    label: 'Parsing Pipeline Statuses',
    description: 'Breakdown of resume parsing states'
  },
  {
    id: 'match-categories',
    type: 'donut-chart',
    endpoint: ENDPOINTS.metrics,
    dataKey: 'match_category_counts',
    gridArea: 'span 2 / span 2',
    label: 'Match Categories Distribution',
    description: 'Breakdown of AI fit assessment matches'
  },
  {
    id: 'match-confidence',
    type: 'bar-chart',
    endpoint: ENDPOINTS.metrics,
    dataKey: 'match_confidence_distribution',
    gridArea: 'span 2 / span 4',
    label: 'Match Confidence Scores Distribution',
    description: 'Candidate compatibility matching levels'
  }
];
