import * as React from "react";
import clsx from "clsx";

export interface AvatarProps extends React.HTMLAttributes<HTMLDivElement> {
  src?: string;
  alt?: string;
}

export const Avatar: React.FC<AvatarProps> = ({ src, alt, className, ...props }) => {
  return (
    <div
      className={clsx(
        "relative flex h-8 w-8 shrink-0 overflow-hidden rounded-full bg-muted",
        className
      )}
      {...props}
    >
      {src ? (
        // eslint-disable-next-line @next/next/no-img-element
        <img src={src} alt={alt} className="aspect-square h-full w-full" />
      ) : null}
    </div>
  );
};
