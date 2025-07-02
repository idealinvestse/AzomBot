import * as React from "react";

export const ScrollArea: React.FC<React.HTMLAttributes<HTMLDivElement>> = ({
  children,
  style,
  ...props
}) => {
  return (
    <div
      style={{ overflowY: "auto", ...style }}
      className="h-full w-full"
      {...props}
    >
      {children}
    </div>
  );
};
