import * as React from "react";
import { clsx } from "clsx";

export interface BadgeProps extends React.HTMLAttributes<HTMLSpanElement> {}

export const Badge: React.FC<BadgeProps> = ({ className, ...props }) => (
  <span
    className={clsx(
      "inline-flex items-center rounded-full border px-2 py-0.5 text-xs font-semibold transition-colors",
      className
    )}
    {...props}
  />
);
