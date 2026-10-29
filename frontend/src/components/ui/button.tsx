import type { ComponentProps } from 'react';
import { cn } from '../../lib/utils';
/** Native accessible button, following shadcn's locally owned component pattern. */
export function Button({ className, type = 'button', ...props }: ComponentProps<'button'>) {
  return <button type={type} className={cn('button', className)} {...props} />;
}
