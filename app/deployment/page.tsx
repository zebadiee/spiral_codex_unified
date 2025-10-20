
import { ComingSoonModule } from '@/components/coming-soon-module';

export default function DeploymentPage() {
  return (
    <ComingSoonModule
      title="Deployment"
      iconName="cloud"
      description="Deploy your applications seamlessly to cloud platforms"
      features={[
        'One-click deployment to multiple platforms',
        'Automated CI/CD pipelines',
        'Infrastructure as code',
        'Environment management',
        'Performance monitoring',
        'Automated scaling and load balancing'
      ]}
      gradient="from-purple-500 to-pink-500"
    />
  );
}
