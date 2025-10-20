
import { type ClassValue, clsx } from "clsx"
import { twMerge } from "tailwind-merge"

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs))
}

// ============================================
// Date Utilities
// ============================================

export function formatDate(date: Date | string | null | undefined): string {
  if (!date) return 'N/A';
  
  try {
    const d = typeof date === 'string' ? new Date(date) : date;
    if (isNaN(d?.getTime?.())) return 'Invalid Date';
    
    return new Intl.DateTimeFormat('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
    }).format(d);
  } catch {
    return 'Invalid Date';
  }
}

export function formatDateTime(date: Date | string | null | undefined): string {
  if (!date) return 'N/A';
  
  try {
    const d = typeof date === 'string' ? new Date(date) : date;
    if (isNaN(d?.getTime?.())) return 'Invalid Date';
    
    return new Intl.DateTimeFormat('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
    }).format(d);
  } catch {
    return 'Invalid Date';
  }
}

export function formatRelativeTime(date: Date | string | null | undefined): string {
  if (!date) return 'N/A';
  
  try {
    const d = typeof date === 'string' ? new Date(date) : date;
    if (isNaN(d?.getTime?.())) return 'Invalid Date';
    
    const now = new Date();
    const diffMs = now.getTime() - d.getTime();
    const diffMins = Math.floor(diffMs / 60000);
    const diffHours = Math.floor(diffMs / 3600000);
    const diffDays = Math.floor(diffMs / 86400000);
    
    if (diffMins < 1) return 'Just now';
    if (diffMins < 60) return `${diffMins}m ago`;
    if (diffHours < 24) return `${diffHours}h ago`;
    if (diffDays < 7) return `${diffDays}d ago`;
    
    return formatDate(d);
  } catch {
    return 'Invalid Date';
  }
}

// ============================================
// Text Utilities
// ============================================

export function truncate(text: string | null | undefined, maxLength: number = 100): string {
  if (!text) return '';
  if (text.length <= maxLength) return text;
  return text.slice(0, maxLength).trim() + '...';
}

export function slugify(text: string | null | undefined): string {
  if (!text) return '';
  
  return text
    .toLowerCase()
    .trim()
    .replace(/[^\w\s-]/g, '')
    .replace(/[\s_-]+/g, '-')
    .replace(/^-+|-+$/g, '');
}

export function capitalize(text: string | null | undefined): string {
  if (!text) return '';
  return text.charAt(0).toUpperCase() + text.slice(1).toLowerCase();
}

// ============================================
// Array Utilities
// ============================================

export function groupBy<T>(array: T[] | null | undefined, key: keyof T): Record<string, T[]> {
  if (!array) return {};
  
  return array.reduce((result, item) => {
    const groupKey = String(item?.[key] ?? 'undefined');
    if (!result[groupKey]) {
      result[groupKey] = [];
    }
    result[groupKey].push(item);
    return result;
  }, {} as Record<string, T[]>);
}

export function unique<T>(array: T[] | null | undefined): T[] {
  if (!array) return [];
  return Array.from(new Set(array));
}

// ============================================
// Color Utilities
// ============================================

export const TAG_COLORS = [
  '#6366f1', // indigo
  '#8b5cf6', // violet
  '#ec4899', // pink
  '#f59e0b', // amber
  '#10b981', // emerald
  '#06b6d4', // cyan
  '#ef4444', // red
  '#f97316', // orange
];

export function getRandomTagColor(): string {
  return TAG_COLORS[Math.floor(Math.random() * TAG_COLORS.length)] ?? TAG_COLORS[0];
}

export function getContrastColor(hexColor: string | null | undefined): string {
  if (!hexColor) return '#ffffff';
  
  try {
    const hex = hexColor.replace('#', '');
    const r = parseInt(hex.substr(0, 2), 16);
    const g = parseInt(hex.substr(2, 2), 16);
    const b = parseInt(hex.substr(4, 2), 16);
    const brightness = (r * 299 + g * 587 + b * 114) / 1000;
    
    return brightness > 128 ? '#000000' : '#ffffff';
  } catch {
    return '#ffffff';
  }
}

// ============================================
// Status Utilities
// ============================================

export function getStatusColor(status: string | null | undefined): string {
  const statusMap: Record<string, string> = {
    active: 'bg-green-500/20 text-green-400 border-green-500/30',
    archived: 'bg-gray-500/20 text-gray-400 border-gray-500/30',
    exported: 'bg-blue-500/20 text-blue-400 border-blue-500/30',
    planning: 'bg-yellow-500/20 text-yellow-400 border-yellow-500/30',
    'in-progress': 'bg-blue-500/20 text-blue-400 border-blue-500/30',
    completed: 'bg-green-500/20 text-green-400 border-green-500/30',
    'on-hold': 'bg-orange-500/20 text-orange-400 border-orange-500/30',
    pending: 'bg-gray-500/20 text-gray-400 border-gray-500/30',
  };
  
  return statusMap[status?.toLowerCase() ?? ''] ?? 'bg-gray-500/20 text-gray-400 border-gray-500/30';
}

// ============================================
// Validation Utilities
// ============================================

export function isValidEmail(email: string | null | undefined): boolean {
  if (!email) return false;
  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
  return emailRegex.test(email);
}

export function isValidUrl(url: string | null | undefined): boolean {
  if (!url) return false;
  try {
    new URL(url);
    return true;
  } catch {
    return false;
  }
}

// ============================================
// Number Utilities
// ============================================

export function clamp(value: number, min: number, max: number): number {
  return Math.min(Math.max(value, min), max);
}

export function percentage(value: number, total: number): number {
  if (total === 0) return 0;
  return Math.round((value / total) * 100);
}
