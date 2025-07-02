import * as React from "react";
import { clsx } from "clsx";

export interface AlertProps extends React.HTMLAttributes<HTMLDivElement> {}

export const Alert: React.FC<AlertProps> = ({ className, ...props }) => (
  <div
    className={clsx(
      "relative w-full rounded-lg border border-destructive bg-destructive/20 p-4 text-destructive",
      className
    )}
    role="alert"
    {...props}
  />
);
