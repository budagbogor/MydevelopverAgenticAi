import { LucideIcon } from 'lucide-react';

export interface BentoGridItem {
  id: number;
  title: string;
  description: string;
  icon: LucideIcon;
  className: string;
}