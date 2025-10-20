
import { ComingSoonModule } from '@/components/coming-soon-module';

export default function SubscriptionPage() {
  return (
    <ComingSoonModule
      title="Subscription"
      iconName="credit-card"
      description="Manage subscriptions and monetize your deployed solutions"
      features={[
        'Flexible pricing models',
        'Payment gateway integration',
        'Subscription analytics and insights',
        'Customer management dashboard',
        'Automated billing and invoicing',
        'Revenue tracking and forecasting'
      ]}
      gradient="from-indigo-500 to-violet-500"
    />
  );
}
