import PageShell from '../components/Layout/PageShell';
import { DASHBOARD_CARDS } from '../config/dashboard';
import HealthPulse from '../components/Dashboard/HealthPulse';
import StatCard from '../components/Dashboard/StatCard';
import ProgressRing from '../components/Dashboard/ProgressRing';
import DonutChart from '../components/Dashboard/DonutChart';
import BarChart from '../components/Dashboard/BarChart';

export function DashboardPage() {
  const renderCard = (card) => {
    switch (card.type) {
      case 'health-pulse':
        return <HealthPulse key={card.id} label={card.label} description={card.description} />;
      case 'stat-card':
        return (
          <StatCard
            key={card.id}
            label={card.label}
            endpoint={card.endpoint}
            dataKey={card.dataKey}
            iconName={card.iconName}
            description={card.description}
          />
        );
      case 'progress-ring':
        return (
          <ProgressRing
            key={card.id}
            label={card.label}
            endpoint={card.endpoint}
            description={card.description}
          />
        );
      case 'donut-chart':
        return (
          <DonutChart
            key={card.id}
            label={card.label}
            endpoint={card.endpoint}
            dataKey={card.dataKey}
            description={card.description}
          />
        );
      case 'bar-chart':
        return (
          <BarChart
            key={card.id}
            label={card.label}
            endpoint={card.endpoint}
            dataKey={card.dataKey}
            description={card.description}
          />
        );
      default:
        return null;
    }
  };

  return (
    <PageShell
      title="System Overview Dashboard"
      description="Live metrics of candidate pipelines, job embeddings, and vector matching results calculated locally."
    >
      <div 
        style={{
          display: 'grid',
          gridTemplateColumns: 'repeat(4, minmax(0, 1fr))',
          gap: '1.5rem',
          gridAutoRows: 'minmax(180px, auto)'
        }}
      >
        {DASHBOARD_CARDS.map((card) => (
          <div key={card.id} style={{ gridArea: card.gridArea }}>
            {renderCard(card)}
          </div>
        ))}
      </div>
    </PageShell>
  );
}

export default DashboardPage;
