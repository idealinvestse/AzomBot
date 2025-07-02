import { Loader } from 'lucide-react';
import { cn } from '@/lib/utils';

const Spinner = ({ className }: { className?: string }) => {
  return <Loader className={cn('animate-spin', className)} />;
};

export default Spinner;
